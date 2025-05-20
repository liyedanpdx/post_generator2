from flask import Flask, request, jsonify, send_file
import os
import sys
import json
import traceback
import io

# 将项目根目录添加到Python路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 导入自定义模块
import config
from services.image_generator import generate_offer_poster_to_s3, generate_offer_poster_base64, generate_offer_poster_binary
from utils.lark_function import update_poster_url
from utils.format_utils import format_number

app = Flask(__name__)

@app.route('/')
def index():
    """API根路径，提供API信息"""
    return jsonify({
        "name": "LinkedIn Post Auto Editor API",
        "version": "2.0",
        "description": "生成LinkedIn Offer海报并上传到S3，然后更新飞书表格",
        "endpoints": [
            {
                "path": "/api/generate-poster",
                "method": "POST",
                "description": "Generate poster and upload to S3, optionally update Lark table"
            },
            {
                "path": "/api/generate-poster-direct",
                "method": "POST",
                "description": "Generate poster and return Base64 image data directly"
            },
            {
                "path": "/api/generate-poster-binary",
                "method": "POST",
                "description": "Generate poster and return binary image stream directly"
            }
        ]
    })

@app.route('/api/generate-poster', methods=['POST'])
def generate_poster():
    """
    生成海报、上传到S3并可选更新飞书表格
    
    请求体 (JSON 或 form-data):
    {
        "Recruiter": "Yedan Li",      # 招聘人员名称
        "Number": "12,500",           # 金额
        "Team": "Engineer Team",      # 团队名称
        "RecordID": "1asysatdfwe",    # 飞书记录ID
        "lark_update": false          # 可选参数，是否更新飞书表格，默认为false
    }
    
    响应:
    {
        "success": true,
        "poster_url": "https://posterimage2025.s3.amazonaws.com/output_YedanLi_12500_EngineerTeam_20240514.png",
        "message": "海报已生成并上传"
    }
    """
    try:
        # 获取请求数据（支持JSON和form-data）
        data = None
        if request.is_json:
            data = request.json
        elif request.form:
            # 如果是form-data，尝试解析第一个JSON字段
            for key in request.form:
                try:
                    data = json.loads(key)
                    break
                except:
                    continue
            
            # 如果没有找到JSON，使用form数据
            if data is None:
                data = request.form.to_dict()
        
        # 如果仍然没有数据，检查是否有文件上传
        if data is None and request.files:
            for file_key in request.files:
                try:
                    file_content = request.files[file_key].read().decode('utf-8')
                    data = json.loads(file_content)
                    break
                except:
                    continue
        
        # 最后检查是否有数据
        if not data:
            return jsonify({
                "success": False,
                "error": "Unable to parse request data. Please ensure you submit in JSON or form-data format"
            }), 400
            
        # 提取必要的参数
        recruiter_name = data.get('Recruiter')
        offer_amount = data.get('Number')
        team_name = data.get('Team')
        record_id = data.get('RecordID')
        
        # 提取可选参数：是否更新飞书表格，默认为False
        update_lark = data.get('lark_update', False)
        
        # 如果没有明确指定lark_update但提供了RecordID，则自动设置update_lark为True
        if not update_lark and record_id:
            update_lark = True
            
        # 如果需要更新飞书表格，则必须提供RecordID
        if update_lark and not record_id:
            return jsonify({
                "success": False,
                "error": "RecordID is required when lark_update is set to true"
            }), 400
        
        # 验证必要参数
        if not all([recruiter_name, offer_amount, team_name]):
            return jsonify({
                "success": False,
                "error": "Missing required parameters. Please provide Recruiter, Number, and Team"
            }), 400
        
        # 格式化金额，确保有千位分隔符
        offer_amount = format_number(offer_amount)
            
        print(f"请求参数: recruiter={recruiter_name}, amount={offer_amount}, team={team_name}, record_id={record_id}, update_lark={update_lark}")
        
        # 处理团队名称，如果包含分号，拆分为两个团队
        team_name1 = team_name
        team_name2 = ""
        if ";" in team_name:
            team_parts = team_name.split(";", 1)  # 只拆分第一个分号
            team_name1 = team_parts[0].strip()
            team_name2 = team_parts[1].strip() if len(team_parts) > 1 else ""
            print(f"检测到多个团队: team1={team_name1}, team2={team_name2}")
        
        # 生成文件名（无空格）
        safe_recruiter = recruiter_name.replace(' ', '_').replace('/', '_')
        safe_amount = offer_amount.replace('$', '').replace(',', '').replace('.', '_')
        safe_team = team_name.replace(' ', '_').replace('/', '_')
        filename = f"output_{safe_recruiter}_{safe_amount}_{safe_team}.png"
        
        # 生成海报并直接上传到S3
        poster_url = generate_offer_poster_to_s3(
            recipient_name=recruiter_name,
            offer_amount=offer_amount,
            team_name=team_name1,
            team_name2=team_name2,
            filename=filename
        )
        
        if not poster_url:
            return jsonify({
                "success": False,
                "error": "Failed to generate or upload poster"
            }), 500
            
        print(f"海报已上传到S3，URL: {poster_url}")
        
        # 准备响应数据
        response_data = {
            "success": True,
            "poster_url": poster_url,
        }
        
        # 如果需要更新飞书表格
        if update_lark:
            update_result = update_poster_url(record_id, poster_url)
            print(f"飞书表格更新结果: {update_result}")
            response_data["message"] = "Poster has been generated, uploaded, and Lark table has been updated"
            response_data["lark_update"] = update_result
        else:
            response_data["message"] = "Poster has been generated and uploaded"
        
        # 返回成功响应
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/generate-poster-direct', methods=['POST'])
def generate_poster_direct():
    """
    生成海报并直接返回Base64编码的图像数据，不上传S3和不更新飞书表格
    
    请求体 (JSON 或 form-data):
    {
        "Recruiter": "Yedan Li",      # 招聘人员名称
        "Number": "12,500",           # 金额
        "Team": "Engineer Team"       # 团队名称
    }
    
    响应:
    {
        "success": true,
        "poster_base64": "base64编码的图片数据",
        "message": "Poster has been generated"
    }
    """
    try:
        # 获取请求数据（支持JSON和form-data）
        data = None
        if request.is_json:
            data = request.json
        elif request.form:
            # 如果是form-data，尝试解析第一个JSON字段
            for key in request.form:
                try:
                    data = json.loads(key)
                    break
                except:
                    continue
            
            # 如果没有找到JSON，使用form数据
            if data is None:
                data = request.form.to_dict()
        
        # 如果仍然没有数据，检查是否有文件上传
        if data is None and request.files:
            for file_key in request.files:
                try:
                    file_content = request.files[file_key].read().decode('utf-8')
                    data = json.loads(file_content)
                    break
                except:
                    continue
        
        # 最后检查是否有数据
        if not data:
            return jsonify({
                "success": False,
                "error": "Unable to parse request data. Please ensure you submit in JSON or form-data format"
            }), 400
            
        # 提取必要的参数
        recruiter_name = data.get('Recruiter')
        offer_amount = data.get('Number')
        team_name = data.get('Team')
        team_name2 = data.get('Team2', "")  # 可选的第二个团队名称
        
        # 验证必要参数
        if not all([recruiter_name, offer_amount, team_name]):
            return jsonify({
                "success": False,
                "error": "Missing required parameters. Please provide Recruiter, Number, and Team"
            }), 400
        
        # 格式化金额，确保有千位分隔符
        offer_amount = format_number(offer_amount)
            
        print(f"请求参数: recruiter={recruiter_name}, amount={offer_amount}, team={team_name}, team2={team_name2}")
        
        # 处理团队名称，如果包含分号，拆分为两个团队
        if ";" in team_name and not team_name2:
            team_parts = team_name.split(";", 1)  # 只拆分第一个分号
            team_name = team_parts[0].strip()
            team_name2 = team_parts[1].strip() if len(team_parts) > 1 else ""
            print(f"检测到多个团队: team1={team_name}, team2={team_name2}")
        
        # 生成海报并获取Base64数据
        success, base64_data = generate_offer_poster_base64(
            recipient_name=recruiter_name,
            offer_amount=offer_amount,
            team_name=team_name,
            team_name2=team_name2
        )
        
        if not success:
            return jsonify({
                "success": False,
                "error": f"Failed to generate poster: {base64_data}"
            }), 500
            
        print(f"海报已生成为Base64数据")
        
        # 返回成功响应
        return jsonify({
            "success": True,
            "poster_base64": base64_data,
            "message": "Poster has been generated"
        }), 200
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/generate-poster-binary', methods=['POST'])
def generate_poster_binary():
    """
    生成海报并直接返回二进制图像数据流，不上传S3和不更新飞书表格
    
    请求体 (JSON 或 form-data):
    {
        "Recruiter": "Yedan Li",      # 招聘人员名称
        "Number": "12,500",           # 金额
        "Team": "Engineer Team"       # 团队名称
    }
    
    响应:
    直接返回PNG二进制图像数据流
    """
    try:
        # 获取请求数据（支持JSON和form-data）
        data = None
        if request.is_json:
            data = request.json
        elif request.form:
            # 如果是form-data，尝试解析第一个JSON字段
            for key in request.form:
                try:
                    data = json.loads(key)
                    break
                except:
                    continue
            
            # 如果没有找到JSON，使用form数据
            if data is None:
                data = request.form.to_dict()
        
        # 如果仍然没有数据，检查是否有文件上传
        if data is None and request.files:
            for file_key in request.files:
                try:
                    file_content = request.files[file_key].read().decode('utf-8')
                    data = json.loads(file_content)
                    break
                except:
                    continue
        
        # 最后检查是否有数据
        if not data:
            return jsonify({
                "success": False,
                "error": "Unable to parse request data. Please ensure you submit in JSON or form-data format"
            }), 400
            
        # 提取必要的参数
        recruiter_name = data.get('Recruiter')
        offer_amount = data.get('Number')
        team_name = data.get('Team')
        team_name2 = data.get('Team2', "")  # 可选的第二个团队名称
        
        # 验证必要参数
        if not all([recruiter_name, offer_amount, team_name]):
            return jsonify({
                "success": False,
                "error": "Missing required parameters. Please provide Recruiter, Number, and Team"
            }), 400
        
        # 格式化金额，确保有千位分隔符
        offer_amount = format_number(offer_amount)
            
        print(f"请求参数: recruiter={recruiter_name}, amount={offer_amount}, team={team_name}, team2={team_name2}")
        
        # 处理团队名称，如果包含分号，拆分为两个团队
        if ";" in team_name and not team_name2:
            team_parts = team_name.split(";", 1)  # 只拆分第一个分号
            team_name = team_parts[0].strip()
            team_name2 = team_parts[1].strip() if len(team_parts) > 1 else ""
            print(f"检测到多个团队: team1={team_name}, team2={team_name2}")
        
        # 生成海报并获取二进制数据
        success, binary_or_error = generate_offer_poster_binary(
            recipient_name=recruiter_name,
            offer_amount=offer_amount,
            team_name=team_name,
            team_name2=team_name2
        )
        
        if not success:
            return jsonify({
                "success": False,
                "error": f"Failed to generate poster: {binary_or_error}"
            }), 500
            
        print(f"海报已生成为二进制数据")
        
        # 创建内存文件对象
        memory_file = io.BytesIO(binary_or_error)
        memory_file.seek(0)
        
        # 生成文件名（用于Content-Disposition头）
        safe_recruiter = recruiter_name.replace(' ', '_').replace('/', '_')
        safe_amount = offer_amount.replace('$', '').replace(',', '').replace('.', '_')
        safe_team = team_name.replace(' ', '_').replace('/', '_')
        filename = f"offer_{safe_recruiter}_{safe_amount}_{safe_team}.png"
        
        # 返回文件流
        return send_file(
            memory_file,
            mimetype='image/png',
            as_attachment=True,
            download_name=filename,
            conditional=True
        )
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # 从配置中读取调试模式和端口
    debug_mode = config.DEBUG
    port = config.PORT
    
    print(f"启动LinkedIn Post Auto Editor API，端口: {port}，调试模式: {debug_mode}")
    app.run(debug=debug_mode, host='0.0.0.0', port=port) 