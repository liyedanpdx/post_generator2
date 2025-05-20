import boto3
from botocore.exceptions import NoCredentialsError
import io
import os
from dotenv import load_dotenv
import sys

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目根目录添加到Python路径
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 加载环境变量
load_dotenv(os.path.join(BASE_DIR, '.env'))

# 从环境变量获取AWS凭证
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
S3_BUCKET = os.getenv('S3_BUCKET', 'posterimage2025')

def get_s3_client():
    """获取S3客户端"""
    return boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

def upload_to_aws(local_file, bucket=None, s3_file=None):
    """
    上传本地文件到AWS S3
    
    参数:
        local_file (str): 本地文件路径
        bucket (str): S3桶名，如果为None则使用默认桶
        s3_file (str): S3上的文件名，如果为None则使用本地文件名
    
    返回:
        str或bool: 成功时返回文件URL，失败时返回False
    """
    # 使用默认桶（如果未指定）
    if bucket is None:
        bucket = S3_BUCKET
    
    # 如果未指定S3文件名，使用本地文件名
    if s3_file is None:
        s3_file = os.path.basename(local_file)
    
    # 创建S3客户端
    s3 = get_s3_client()

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print(f"成功上传文件 {local_file} 到 {bucket}/{s3_file}")
        
        # 构建并返回文件的公共URL
        file_url = f"https://{bucket}.s3.amazonaws.com/{s3_file}"
        return file_url
    except FileNotFoundError:
        print(f"文件未找到: {local_file}")
        return False
    except NoCredentialsError:
        print("AWS凭证不可用")
        return False
    except Exception as e:
        print(f"上传过程中出错: {str(e)}")
        return False

def upload_fileobj_to_aws(file_obj, bucket=None, s3_file=None, content_type=None):
    """
    上传文件对象（内存中的文件）到AWS S3
    
    参数:
        file_obj (file-like object): 文件对象（如BytesIO）
        bucket (str): S3桶名，如果为None则使用默认桶
        s3_file (str): S3上的文件名
        content_type (str): 文件内容类型，如'image/png'
    
    返回:
        str或bool: 成功时返回文件URL，失败时返回False
    """
    # 使用默认桶（如果未指定）
    if bucket is None:
        bucket = S3_BUCKET
    
    # S3文件名是必需的
    if s3_file is None:
        s3_file = f"upload_{int(datetime.datetime.now().timestamp())}.png"
    
    # 创建S3客户端
    s3 = get_s3_client()
    
    # 准备上传参数
    upload_args = {}
    if content_type:
        upload_args['ContentType'] = content_type
    
    try:
        s3.upload_fileobj(
            file_obj, 
            bucket, 
            s3_file, 
            ExtraArgs=upload_args
        )
        print(f"成功上传内存中的文件到 {bucket}/{s3_file}")
        
        # 构建并返回文件的公共URL
        file_url = f"https://{bucket}.s3.amazonaws.com/{s3_file}"
        return file_url
    except NoCredentialsError:
        print("AWS凭证不可用")
        return False
    except Exception as e:
        print(f"上传过程中出错: {str(e)}")
        return False

def generate_and_upload_image(image_obj, filename=None, bucket=None):
    """
    生成图像并直接上传到S3（无需保存到本地）
    
    参数:
        image_obj (PIL.Image): PIL图像对象
        filename (str): S3上的文件名
        bucket (str): S3桶名，如果为None则使用默认桶
    
    返回:
        str或bool: 成功时返回文件URL，失败时返回False
    """
    import datetime
    from PIL import Image
    
    # 使用默认桶（如果未指定）
    if bucket is None:
        bucket = S3_BUCKET
    
    # 如果未指定文件名，创建一个基于时间戳的唯一文件名
    if filename is None:
        filename = f"poster_{int(datetime.datetime.now().timestamp())}.png"
    
    # 使用下划线替换文件名中的空格
    filename = filename.replace(" ", "_")
    
    try:
        # 将图像保存到内存中的BytesIO对象
        img_byte_arr = io.BytesIO()
        image_obj.convert('RGB').save(img_byte_arr, format='PNG')
        
        # 将指针移回到开头，以便读取
        img_byte_arr.seek(0)
        
        # 上传BytesIO对象到S3
        return upload_fileobj_to_aws(
            file_obj=img_byte_arr,
            bucket=bucket,
            s3_file=filename,
            content_type='image/png'
        )
    except Exception as e:
        print(f"生成并上传图像时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# 使用函数 - 仅在直接运行该脚本时测试
if __name__ == "__main__":
    try:
        # 示例1：上传本地文件
        local_file = 'output_test_12500_engineer_team.png'
        
        # 创建测试图像（如果不存在）
        if not os.path.exists(local_file):
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (800, 600), color=(73, 109, 137))
            d = ImageDraw.Draw(img)
            d.text((300, 300), "测试图片", fill=(255, 255, 0))
            img.save(local_file)
            print(f"已创建测试图片: {local_file}")
        
        # 上传本地文件
        uploaded_url = upload_to_aws(local_file)
        print(f"上传URL: {uploaded_url}")
        
        # 示例2：直接上传内存中的图像
        from PIL import Image, ImageDraw
        # 创建测试图像
        img = Image.new('RGB', (800, 600), color=(100, 150, 200))
        d = ImageDraw.Draw(img)
        d.text((300, 300), "内存中的测试图片", fill=(255, 255, 0))
        
        # 生成并上传图像
        memory_url = generate_and_upload_image(img, filename="memory_test.png")
        print(f"内存图像URL: {memory_url}")
        
    except Exception as e:
        print(f"测试过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()