import requests
import json
import datetime
import pymongo
import os
import traceback
import sys

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目根目录添加到Python路径
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 导入配置
import config

def fetch_access_token():
    """
    获取飞书应用的访问令牌
    
    返回:
        str: 访问令牌
    """
    url = "https://open.larksuite.com/open-apis/auth/v3/app_access_token/internal"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
    }
    payload = {
        'app_id': config.LARK_APP_ID,
        'app_secret': config.LARK_APP_SECRET
    }
    response = requests.post(url, json=payload, headers=headers)
    return json.loads(response.text)['app_access_token']

def get_access_token():
    """
    获取并刷新飞书的访问令牌
    
    返回:
        str: 访问令牌
    """
    try:
        client = pymongo.MongoClient(config.MONGODB_URI)
        collection = client[config.MONGODB_DB][config.MONGODB_COLLECTION]
        refresh_data = collection.find({'_id': 'yedan_record'})[0]['record']
        client.close()
        
        new_access_token = fetch_access_token()
        url = "https://open.larksuite.com/open-apis/authen/v1/refresh_access_token"
        headers = {
            "Content-Type": "application/json; charset=utf-8", 
            "Authorization": f"Bearer {new_access_token}",
        }
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_data['refresh_token']
        }
        
        response = requests.post(url, json=payload, headers=headers)
        if eval(response.text)['code'] == 20001:
            headers['Authorization'] = "Bearer " + fetch_access_token()
            response = requests.post(url, json=payload, headers=headers)
        
        response_data = json.loads(response.text)['data']
        refresh_data.update({
            'access_token': response_data['access_token'],
            'refresh_token': response_data['refresh_token'],
            'update_time': datetime.datetime.now(datetime.timezone.utc).strftime('%m-%d-%Y,%H:%M:%S')
        })
            
        client = pymongo.MongoClient(config.MONGODB_URI)
        collection = client[config.MONGODB_DB][config.MONGODB_COLLECTION]
        collection.update_one(
            {'_id': 'yedan_record'},
            {'$set': {'record': refresh_data}},
            upsert=True
        )
        client.close()
        
        return refresh_data['access_token']
    except Exception as e:
        print(f"获取访问令牌失败: {str(e)}")
        print(traceback.format_exc())
        return fetch_access_token()  # 失败时直接返回一个新的访问令牌

def upload_image_to_sheets(spreadsheet_token, sheet_id, cell_range, image_path, access_token):
    """
    将图片上传到飞书表格的指定单元格
    
    参数:
        spreadsheet_token (str): 表格的token，例如"LaX5s2EMwhbDJDtDTNLlnh58gVg"
        sheet_id (str): 工作表的ID，例如"Q7PlXT"
        cell_range (str): 单元格范围，例如"H7:H7"
        image_path (str): 图片文件路径
        access_token (str): 访问令牌
    
    返回:
        dict: API响应
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
            
        # 构建API URL
        url = f"https://open.larksuite.com/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values_image"
        
        # 设置请求头
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # 读取图片文件为二进制数据
        with open(image_path, "rb") as image_file:
            image_binary = image_file.read()
        
        # 将二进制数据转换为字节数组
        image_bytes = list(image_binary)
        
        # 确保文件名处理兼容Windows和Unix路径
        file_name = os.path.basename(image_path)
        
        # 构建请求体
        payload = {
            "range": f"{sheet_id}!{cell_range}",
            "image": image_bytes,
            "name": file_name  # 使用文件名作为图片名称
        }
        
        print(f"上传图片到单元格范围: {sheet_id}!{cell_range}")
        
        # 发送POST请求
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # 解析并返回响应
        result = response.json()
        
        # 检查响应状态
        if result.get("code") and result.get("code") != 0:
            print(f"上传图片失败: {result.get('msg', '未知错误')}")
        else:
            print("上传图片成功!")
            
        return result
        
    except Exception as e:
        print(f"上传图片到表格时出错: {str(e)}")
        traceback.print_exc()
        return {"error": str(e), "success": False}

def upload_image_to_sheet_cell(image_path, spreadsheet_token, sheet_id, cell_range=None):
    """
    将图片上传到飞书表格的指定单元格的简化包装函数
    
    参数:
        image_path (str): 图片文件路径
        spreadsheet_token (str): 表格的token
        sheet_id (str): 工作表的ID
        cell_range (str, optional): 单元格范围，默认为"A1:A1"
    
    返回:
        dict: API响应
    """
    if cell_range is None:
        cell_range = "A1:A1"  # 默认上传到A1单元格
        
    # 获取访问令牌
    access_token = get_access_token()
    
    # 上传图片
    return upload_image_to_sheets(
        spreadsheet_token=spreadsheet_token,
        sheet_id=sheet_id,
        cell_range=cell_range,
        image_path=image_path,
        access_token=access_token
    )

def update_record(app_token, table_id, record_id, access_token, payload):
    """
    更新飞书多维表格中的记录
    
    参数:
        app_token (str): 应用令牌
        table_id (str): 表格ID
        record_id (str): 记录ID
        access_token (str): 访问令牌
        payload (dict): 更新数据
    
    返回:
        dict: API响应
    """
    url = f'https://open.larksuite.com/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}'
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    response = requests.put(url, headers=headers, json=payload)
    return json.loads(response.text)['data']

def update_lark(field_name, record_id, put_value, app_token=None, table_id=None):
    """
    更新飞书多维表格中的指定字段
    
    参数:
        field_name (str): 字段名称
        record_id (str): 记录ID
        put_value (str): 要更新的值
        app_token (str, optional): 应用令牌，如不提供则使用配置中的值
        table_id (str, optional): 表格ID，如不提供则使用配置中的值
    
    返回:
        dict: API响应
    """
    if app_token is None:
        app_token = config.LARK_APP_TOKEN
    
    if table_id is None:
        table_id = config.LARK_TABLE_ID
        
    access_token = get_access_token()
    payload = {
        "fields": {
            f"{field_name}": put_value,
        }
    }
    return update_record(app_token, table_id, record_id, access_token, payload)

def update_poster_url(record_id, poster_url, field_name=None, app_token=None, table_id=None):
    """
    更新飞书多维表格中的海报URL字段
    
    参数:
        record_id (str): 记录ID
        poster_url (str): 海报URL
        field_name (str, optional): 字段名称，如不提供则使用配置中的值
        app_token (str, optional): 应用令牌，如不提供则使用配置中的值
        table_id (str, optional): 表格ID，如不提供则使用配置中的值
    
    返回:
        dict: API响应
    """
    if field_name is None:
        field_name = config.LARK_FIELD_NAME
        
    return update_lark(field_name, record_id, poster_url, app_token, table_id)

# 使用示例
if __name__ == "__main__":
    # 测试更新记录
    try:
        # 测试参数
        record_id = "OcrAroeKgeQEm5cEqmLlTfUOgGc"  # 记录ID
        test_url = "https://example.com/test.png"  # 测试URL
        
        # 使用默认配置更新记录
        result = update_poster_url(record_id, test_url)
        print("成功更新记录:")
        print(f"更新结果: {result}")
    except Exception as e:
        print(f"发生错误: {str(e)}")
        traceback.print_exc()
            
        
        
        
        