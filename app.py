from flask import Flask, request, send_file, jsonify, render_template, after_this_request
import os
import time
import threading
from services.image_generator import generate_offer_poster
from services.exchange_rate import ExchangeRateService
from utils.file_handler import FileHandler

app = Flask(__name__)

# Create a directory for storing generated images
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize file handler
file_handler = FileHandler(OUTPUT_DIR)

# 用于存储待删除的文件及其删除时间
files_to_delete = {}

# 清理线程函数
def cleanup_thread():
    """后台线程，定期检查并删除过期的文件"""
    while True:
        current_time = time.time()
        files_to_remove = []
        
        # 查找需要删除的文件
        for file_path, delete_time in files_to_delete.items():
            if current_time >= delete_time:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"已删除文件: {file_path}")
                    files_to_remove.append(file_path)
                except Exception as e:
                    print(f"删除文件时出错: {file_path}, 错误: {e}")
        
        # 从字典中移除已处理的文件
        for file_path in files_to_remove:
            files_to_delete.pop(file_path, None)
            
        # 休眠一段时间
        time.sleep(10)  # 每10秒检查一次

# 启动清理线程
cleanup_thread_instance = threading.Thread(target=cleanup_thread, daemon=True)
cleanup_thread_instance.start()

# 添加文件到待删除列表
def schedule_file_deletion(file_path, delay_seconds=60):
    """安排文件在指定延迟后删除"""
    delete_time = time.time() + delay_seconds
    files_to_delete[file_path] = delete_time
    print(f"文件 {file_path} 将在 {delay_seconds} 秒后删除")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form')
def form():
    """Render the form for generating posters"""
    return render_template('form.html')

@app.route('/api/exchange-rates', methods=['GET'])
def get_all_exchange_rates():
    """Get all available exchange rates"""
    exchange_service = ExchangeRateService()
    rates = exchange_service.get_all_rates()
    return jsonify(rates)

@app.route('/api/exchange-rate/<currency_code>', methods=['GET'])
def get_exchange_rate(currency_code):
    """Get exchange rate for a specific currency"""
    exchange_service = ExchangeRateService()
    rate = exchange_service.get_exchange_rate(currency_code)
    
    if rate is None:
        return jsonify({"error": f"Exchange rate for {currency_code} not available"}), 404
    
    return jsonify({
        "currency": currency_code,
        "rate": rate,
        "description": exchange_service.currencies.get(currency_code, "Unknown currency")
    })

@app.route('/api/generate-poster', methods=['POST'])
def create_poster():
    """Generate an offer poster with the provided information"""
    # Get parameters from request
    data = request.json or {}
    
    print(f"Received request data: {data}")
    
    recipient_name = data.get('recipient_name')
    offer_amount = data.get('offer_amount')
    team_name = data.get('team_name')
    team_name2 = data.get('team_name2', None)  # Optional second team
    
    # Validate required parameters
    if not all([recipient_name, offer_amount, team_name]):
        print(f"Missing required parameters: {data}")
        return jsonify({
            "error": "Missing required parameters. Please provide recipient_name, offer_amount, and team_name."
        }), 400
    
    try:
        print(f"Generating poster with: recipient={recipient_name}, amount={offer_amount}, team={team_name}")
        print(f"Output directory: {OUTPUT_DIR}")
        
        # 查找assets目录中的banner图片
        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, "assets")
        banner_path = None
        
        # 尝试查找banner图片
        possible_banner_paths = [
            os.path.join(assets_dir, "images", "offer_banner.png"),
            os.path.join(assets_dir, "images", "banner.png"),
            # 添加其他可能的路径
        ]
        
        for path in possible_banner_paths:
            if os.path.exists(path):
                banner_path = path
                print(f"找到banner图片: {banner_path}")
                break
                
        if not banner_path:
            # 如果找不到banner图片，搜索assets目录下的所有图片
            for root, dirs, files in os.walk(assets_dir):
                for file in files:
                    if file.endswith(('.png', '.jpg', '.jpeg')):
                        banner_path = os.path.join(root, file)
                        print(f"使用找到的图片作为banner: {banner_path}")
                        break
                if banner_path:
                    break
        
        if not banner_path:
            return jsonify({"error": "找不到banner图片，请确保assets/images目录中有图片文件"}), 500
        
        # Generate the poster
        poster_path = generate_offer_poster(
            recipient_name=recipient_name,
            offer_amount=offer_amount,
            team_name=team_name,
            team_name2=team_name2,
            banner_path=banner_path,
            output_dir=OUTPUT_DIR,
            font_path=None,
            save_interim=False
        )
        
        print(f"Generated poster path: {poster_path}")
        
        if not poster_path:
            print("Failed to generate poster: No path returned")
            return jsonify({"error": "Failed to generate poster"}), 500
        
        # 确保文件存在
        if not os.path.exists(poster_path):
            print(f"Generated file does not exist: {poster_path}")
            return jsonify({"error": f"Generated file not found: {poster_path}"}), 500
        
        # 安排文件在下载后删除（60秒后）
        schedule_file_deletion(poster_path, 60)
        
        # Return the file for download
        return send_file(poster_path, as_attachment=True)
    
    except Exception as e:
        import traceback
        print(f"Error generating poster: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup_old_files():
    """Clean up old generated files"""
    try:
        # Get the max age in hours (default: 24)
        data = request.json or {}
        max_age_hours = int(data.get('max_age_hours', 24))
        
        # Clean up old files
        deleted_count, message = file_handler.clean_old_files(max_age_hours)
        
        return jsonify({
            "success": True,
            "deleted_count": deleted_count,
            "message": message
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)