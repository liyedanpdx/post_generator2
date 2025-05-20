from PIL import Image, ImageDraw, ImageFont
import os
import datetime
import io
import sys
import base64

# 获取项目根目录（相对于当前文件）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 添加到Python路径
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 导入S3上传功能
from utils.s3upload import generate_and_upload_image

# Create a directory for storing generated images
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_images")
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"Output directory set to: {OUTPUT_DIR}")  # 添加日志

def get_image_size(image_path):
    """
        返回图片的尺寸
        
        参数:
            image_path: 图片文件的路径
            
        返回:
            (width, height): 图片宽度和高度的元组
    """
    try:
        with Image.open(image_path) as img:
            return img.size
    except Exception as e:
        print(f"获取图片尺寸时出错: {e}")
        return None

class ImageEditor:
    def __init__(self, image_path=None, image_obj=None):
        """
        初始化图片编辑器
        
        参数:
            image_path: 图片文件的路径
            image_obj: PIL图像对象
        """
        try:
            # 如果提供了图像对象，直接使用
            if image_obj is not None:
                self.img = image_obj.convert('RGBA')
                self.img_path = None
            # 否则从文件加载图像
            elif image_path is not None:
                self.img_path = image_path
                self.img = Image.open(image_path).convert('RGBA')
            else:
                raise ValueError("必须提供image_path或image_obj其中之一")
                
            self.width, self.height = self.img.size
            print(f"图片尺寸: {self.img.size}")
        except Exception as e:
            print(f"初始化图片编辑器时出错: {e}")
            raise e
    
    def add_text(self, 
                text="测试文本",
                position=(None, None),  # 如果为None，则居中
                right_align_x=None,     # 右对齐的X坐标，优先级高于position的x
                font_name="../assets/fonds/impact.ttf",
                font_size=100,
                text_color="white",
                rotation_angle=0):
        """
        在图片上添加旋转的文字
        
        参数:
            text: 要添加的文字
            position: (x, y)位置坐标，如果是None则居中
            right_align_x: 右对齐的X坐标，如果设置了这个值，文本会以这个点为右边界向左延伸
            font_name: 字体名称或路径
            font_size: 字体大小
            text_color: 文字颜色，可以是名称(如"white")或RGB元组(如(255,255,255))
            rotation_angle: 旋转角度（度数）
        
        返回:
            self: 返回对象本身，支持链式调用
        """
        try:
            # 尝试加载字体
            try:
                font = ImageFont.truetype(font_name, font_size)
                print(f"成功加载字体: {font_name}, 大小: {font_size}")
            except Exception as font_error:
                print(f"加载字体 {font_name} 失败: {font_error}")
                try:
                    # 如果找不到指定字体，尝试加载系统字体
                    import matplotlib.font_manager as fm
                    system_fonts = fm.findSystemFonts()
                    if system_fonts:
                        font = ImageFont.truetype(system_fonts[0], font_size)
                        print(f"使用系统字体: {system_fonts[0]}")
                    else:
                        font = ImageFont.load_default()
                        print("使用默认字体")
                except:
                    font = ImageFont.load_default()
            
            # 创建一个透明图层用于文字
            text_layer = Image.new('RGBA', self.img.size, (0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_layer)
            
            # 获取文本尺寸
            try:
                # 新版Pillow
                text_bbox = text_draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
            except:
                # 旧版Pillow
                text_width, text_height = text_draw.textsize(text, font=font)
            
            # 确定文本位置
            x, y = position
            
            # # 修复右对齐逻辑 - 关键修改部分开始
            # if right_align_x is not None:
            #     # 确保旋转后的文本右对齐点是固定的
            #     # 文本倾斜时，其实际位置会有偏移，所以需要考虑旋转角度的影响
            #     if rotation_angle != 0:
            #         # 对于顺时针旋转(负角度)，文本左上角需要向右偏移
            #         # 对于13度顺时针旋转的粗略修正:
            #         # 文本越长，倾斜造成的偏移越大
            #         if rotation_angle < 0:
            #             # 顺时针旋转
            #             angle_rad = abs(rotation_angle) * 3.14159 / 180
            #             offset = text_height * 0.2 * abs(math.sin(angle_rad))  # 粗略估计偏移量
            #             x = right_align_x - text_width - offset
            #         else:
            #             # 逆时针旋转
            #             x = right_align_x - text_width
            #     else:
            #         x = right_align_x - text_width
            # elif x is None:
            #     # 如果没有设置x坐标和右对齐，则居中
            #     x = (self.width - text_width) // 2
            # # 修复右对齐逻辑 - 关键修改部分结束
            
            # 简化版的右对齐逻辑
            if right_align_x is not None:
                # 直接计算左侧起始位置，不考虑旋转偏移
                x = right_align_x - text_width
            elif x is None:
                # 如果没有设置x坐标和右对齐，则居中
                x = (self.width - text_width) // 2
                
            if y is None:
                y = (self.height - text_height) // 2
            
            # 绘制文本到透明图层
            text_draw.text((x, y), text, fill=text_color, font=font)
            
            # 旋转文本图层
            # 注意：rotation_angle为负数表示顺时针旋转
            rotated_layer = text_layer.rotate(rotation_angle, resample=Image.BICUBIC, expand=False)
            
            # 合并图层
            self.img = Image.alpha_composite(self.img, rotated_layer)
            
            return self
            
        except Exception as e:
            print(f"添加文字时出错: {e}")
            import traceback
            traceback.print_exc()
            return self

    def add_text_adaptive(self, 
                text="测试文本",
                position=(None, None),  # 如果为None，则居中
                right_align_x=None,     # 右对齐的X坐标，优先级高于position的x
                font_name="../assets/fonds/impact.ttf",
                font_size=100,
                text_color="white",
                rotation_angle=0,
                max_width=None,         # 文本最大宽度，超过会自动缩小字体
                min_font_size=50,       # 最小字体大小限制
                width_threshold=0.8     # 宽度阈值，超过这个比例开始缩小字体
                ):
        """
        在图片上添加旋转的文字，支持自适应字体大小
        
        参数:
            text: 要添加的文字
            position: (x, y)位置坐标，如果是None则居中
            right_align_x: 右对齐的X坐标，如果设置了这个值，文本会以这个点为右边界向左延伸
            font_name: 字体名称或路径
            font_size: 初始/最大字体大小
            text_color: 文字颜色，可以是名称(如"white")或RGB元组(如(255,255,255))
            rotation_angle: 旋转角度（度数）
            max_width: 文本最大宽度，超过会自动缩小字体
            min_font_size: 自动缩小的最小字体大小限制
            width_threshold: 宽度阈值，文本宽度超过max_width*width_threshold时开始缩小字体
        
        返回:
            self: 返回对象本身，支持链式调用
        """
        try:
            # 如果设置了right_align_x但没有设置max_width，则计算从右边界到左侧的距离作为max_width
            if right_align_x is not None and max_width is None:
                # 如果右对齐，最大宽度默认为从右边界到图像左边缘的80%
                max_width = right_align_x * width_threshold
            elif max_width is None:
                # 如果没有设置max_width，默认为图像宽度的80%
                max_width = self.width * width_threshold
                
            # 计算适合的字体大小
            current_font_size = font_size
            font = None
            text_width = float('inf')
            
            # 循环尝试字体大小，直到文本宽度适合或达到最小字体大小
            while current_font_size >= min_font_size:
                try:
                    # 尝试加载字体
                    try:
                        font = ImageFont.truetype(font_name, current_font_size)
                    except Exception as font_error:
                        print(f"加载字体 {font_name} 失败: {font_error}")
                        try:
                            # 如果找不到指定字体，尝试加载系统字体
                            import matplotlib.font_manager as fm
                            system_fonts = fm.findSystemFonts()
                            if system_fonts:
                                font = ImageFont.truetype(system_fonts[0], current_font_size)
                            else:
                                font = ImageFont.load_default()
                        except:
                            font = ImageFont.load_default()
                    
                    # 创建临时图层来测量文本尺寸
                    temp_layer = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
                    temp_draw = ImageDraw.Draw(temp_layer)
                    
                    # 获取文本尺寸
                    try:
                        # 新版Pillow
                        text_bbox = temp_draw.textbbox((0, 0), text, font=font)
                        text_width = text_bbox[2] - text_bbox[0]
                    except:
                        # 旧版Pillow
                        text_width, _ = temp_draw.textsize(text, font=font)
                    
                    # 检查文本宽度是否在允许范围内
                    if text_width <= max_width:
                        print(f"最终使用字体大小: {current_font_size}，文本宽度: {text_width}，最大宽度: {max_width}")
                        break
                    
                    # 缩小字体大小并重试
                    current_font_size -= 8  # 每次减小5px
                    
                except Exception as e:
                    print(f"测量文本时出错: {e}")
                    # 如果发生错误，减小字体大小继续尝试
                    current_font_size -= 8
            
            # 确保字体大小不小于最小限制
            current_font_size = max(current_font_size, min_font_size)
            print(f"文本 '{text}' 使用字体大小: {current_font_size}")
            
            # 使用计算出的字体大小调用原始的add_text方法
            return self.add_text(
                text=text,
                position=position,
                right_align_x=right_align_x,
                font_name=font_name,
                font_size=current_font_size,
                text_color=text_color,
                rotation_angle=rotation_angle
            )
            
        except Exception as e:
            print(f"自适应文本大小时出错: {e}")
            import traceback
            traceback.print_exc()
            # 如果自适应失败，尝试使用原始方法和原始字体大小
            return self.add_text(
                text=text,
                position=position,
                right_align_x=right_align_x,
                font_name=font_name,
                font_size=font_size,
                text_color=text_color,
                rotation_angle=rotation_angle
            )
    
    def save_image(self, output_path):
        """
        保存当前编辑的图片
        
        参数:
            output_path: 输出文件的路径
            
        返回:
            output_path: 如果成功，返回输出文件路径；否则返回None
        """
        try:
            # 创建输出目录（如果不存在）
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # 保存结果
            final_img = self.img.convert('RGB')  # 转为RGB模式保存
            final_img.save(output_path)
            print(f"图片已保存到: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"保存图片时出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_current_image(self):
        """
        获取当前编辑的图片对象
        
        返回:
            Image: PIL图片对象
        """
        return self.img
    
    def show_image(self):
        """
        显示当前图片（用于调试）
        """
        self.img.show()
        return self

def calculate_font_size(text, font_path, start_size, min_size, max_width):
    """
    计算文本的合适字体大小
    
    参数:
        text: 要计算的文本
        font_path: 字体路径
        start_size: 起始字体大小
        min_size: 最小字体大小
        max_width: 最大允许宽度
        
    返回:
        适合的字体大小
    """
    from PIL import Image, ImageDraw, ImageFont
    
    # 临时图像用于测量文本尺寸
    temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    
    current_size = start_size
    
    # 逐步减小字体大小直到文本宽度适合
    while current_size >= min_size:
        try:
            font = ImageFont.truetype(font_path, current_size)
            
            # 获取文本宽度
            try:
                # 新版Pillow
                text_bbox = temp_draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
            except:
                # 旧版Pillow
                text_width, _ = temp_draw.textsize(text, font=font)
            
            # 检查是否适合
            if text_width <= max_width:
                print(f"文本 '{text}' 适合的字体大小: {current_size}, 宽度: {text_width}/{max_width}")
                return current_size
            
            # 减小字体大小并重试
            current_size -= 5
            
        except Exception as e:
            print(f"计算字体大小时出错: {e}")
            current_size -= 5
    
    # 如果所有尺寸都不适合，返回最小尺寸
    return min_size

def generate_offer_poster(recipient_name, offer_amount, team_name,
                         team_name2 ="", 
                         banner_path=None,  # 修改为None，后面会设置默认值
                         output_dir=None,   # 修改为None，后面会设置默认值
                         font_path=None,    # 修改为None，后面会设置默认值
                         save_interim=False):
    """
    生成offer海报，支持自适应字体大小
    
    参数:
        recipient_name: 收件人姓名（如 "Cora Xia"）
        offer_amount: offer金额（如 "20,850"）
        team_name: 团队名称（如 "Niki/Vera"）
        team_name2: 第二个团队名称（可选）
        banner_path: offer banner图片路径
        output_dir: 输出目录
        font_path: 字体文件路径
        save_interim: 是否保存中间结果
        
    返回:
        output_path: 生成的海报路径
    """
    try:
        # 设置默认路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if banner_path is None:
            banner_path = os.path.join(base_dir, "assets", "images", "offer_banner.png")
            print(f"使用默认banner路径: {banner_path}")
            
        if output_dir is None:
            output_dir = os.path.join(base_dir, "generated_images")
            print(f"使用默认输出目录: {output_dir}")
            
        if font_path is None:
            font_path = os.path.join(base_dir, "assets", "fonds", "impact.ttf")
            print(f"使用默认字体路径: {font_path}")
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        # 检查banner文件是否存在
        if not os.path.exists(banner_path):
            print(f"警告: Banner图片不存在: {banner_path}")
            # 尝试查找assets目录下的所有图片
            assets_dir = os.path.join(base_dir, "assets")
            if os.path.exists(assets_dir):
                print(f"搜索assets目录中的图片文件...")
                for root, dirs, files in os.walk(assets_dir):
                    for file in files:
                        if file.endswith(('.png', '.jpg', '.jpeg')):
                            print(f"找到图片: {os.path.join(root, file)}")
            
            raise FileNotFoundError(f"Banner图片不存在: {banner_path}")
            
        # 获取当前日期
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        
        # 处理金额格式（确保有$符号）
        if not offer_amount.startswith('$') and not offer_amount.startswith('￥'):
            offer_amount = f"${offer_amount}"
            
        # 创建图片编辑器
        editor = ImageEditor(image_path=banner_path)
        
        # 添加金额文字 - 不使用自适应大小
        editor.add_text(
            text=offer_amount,
            position=(1200, 800),
            font_name=font_path,
            font_size=700,
            text_color="white",
            rotation_angle=-13
        )
        
        # 添加收件人姓名 - 使用自适应字体大小，右对齐
        editor.add_text_adaptive(
            text=f"@{recipient_name}",
            position=(None, 650),  # 只使用y坐标
            right_align_x=3300,    # 右侧固定边界，调整这个值可以改变右对齐位置
            font_name=font_path,
            font_size=200,         # 初始/最大字体大小
            min_font_size=100,     # 最小字体大小限制
            text_color="white",
            rotation_angle=-13,
            width_threshold=0.75   # 宽度阈值，文本宽度超过75%时开始缩小字体
        )
        
        # 确定团队名称的字体大小
        team_text = f"FROM {team_name} Team!"
        team_text2 = f"FROM {team_name2} Team!" if team_name2 else ""

        # 选择较长的团队名称来确定字体大小
        longer_team_text = team_text if len(team_text) >= len(team_text2) else team_text2
        max_team_width = 2400  # 设置团队名称最大宽度

        # 计算合适的字体大小，基于较长的文本
        team_font_size = calculate_font_size(
            text=longer_team_text,
            font_path=font_path,
            start_size=170,
            min_size=100,
            max_width=max_team_width
        )

        print(f"两个团队名称统一使用字体大小: {team_font_size}")

        # 添加第一个团队名称
        editor.add_text(
            text=team_text,
            position=(1100, 1600),
            font_name=font_path,
            font_size=team_font_size,  # 使用计算好的统一字体大小
            text_color="white",
            rotation_angle=-13
        )

        # 添加第二个团队名称（如果有）
        if team_name2:
            editor.add_text(
                text=team_text2,
                position=(1100, 1800),
                font_name=font_path,
                font_size=team_font_size,  # 使用相同的字体大小
                text_color="white",
                rotation_angle=-13
            )
        
        # 生成不带特殊字符的文件名
        safe_recipient = recipient_name.replace(' ', '_').replace('/', '_').replace(';', '_')
        safe_amount = offer_amount.replace('$', '').replace(',', '').replace('.', '_')
        safe_team = team_name.replace('/', '_')
        
        # 保存中间结果（如果需要）
        if save_interim:
            interim_path = os.path.join(output_dir, f"interim_{safe_recipient}_{current_date}.png")
            editor.save_image(interim_path)
            print(f"中间结果已保存: {interim_path}")
        
        # 生成最终输出文件名
        output_filename = f"output_{safe_recipient}_{safe_amount}_{safe_team}_{current_date}.png"
        output_path = os.path.join(output_dir, output_filename)
        
        # 保存最终结果
        editor.save_image(output_path)
        
        return output_path
        
    except Exception as e:
        print(f"生成offer海报时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_offer_poster_to_s3(recipient_name, offer_amount, team_name,
                                team_name2="", 
                                banner_path=None,  
                                font_path=None,    
                                bucket=None,
                                filename=None):
    """
    生成offer海报并直接上传到S3，不保存到本地
    
    参数:
        recipient_name: 收件人姓名（如 "Cora Xia"）
        offer_amount: offer金额（如 "20,850"）
        team_name: 团队名称（如 "Niki/Vera"）
        team_name2: 第二个团队名称（可选）
        banner_path: offer banner图片路径
        font_path: 字体文件路径
        bucket: S3桶名（可选）
        filename: 自定义文件名（可选）
        
    返回:
        str或None: 成功时返回S3 URL，失败时返回None
    """
    try:
        # 设置默认路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if banner_path is None:
            banner_path = os.path.join(base_dir, "assets", "images", "offer_banner.png")
            print(f"使用默认banner路径: {banner_path}")
            
        if font_path is None:
            font_path = os.path.join(base_dir, "assets", "fonds", "impact.ttf")
            print(f"使用默认字体路径: {font_path}")
            
        # 检查banner文件是否存在
        if not os.path.exists(banner_path):
            print(f"警告: Banner图片不存在: {banner_path}")
            # 尝试查找assets目录下的所有图片
            assets_dir = os.path.join(base_dir, "assets")
            if os.path.exists(assets_dir):
                print(f"搜索assets目录中的图片文件...")
                for root, dirs, files in os.walk(assets_dir):
                    for file in files:
                        if file.endswith(('.png', '.jpg', '.jpeg')):
                            print(f"找到图片: {os.path.join(root, file)}")
                            banner_path = os.path.join(root, file)
                            break
                    if os.path.exists(banner_path):
                        break
            
            if not os.path.exists(banner_path):
                raise FileNotFoundError(f"Banner图片不存在，无法继续生成海报")
            
        # 获取当前日期
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        
        # 处理金额格式（确保有$符号）
        if not offer_amount.startswith('$') and not offer_amount.startswith('￥'):
            offer_amount = f"${offer_amount}"
            
        # 创建图片编辑器
        editor = ImageEditor(image_path=banner_path)
        
        # 添加金额文字 - 不使用自适应大小
        editor.add_text(
            text=offer_amount,
            position=(1200, 800),
            font_name=font_path,
            font_size=700,
            text_color="white",
            rotation_angle=-13
        )
        
        # 添加收件人姓名 - 使用自适应字体大小，右对齐
        editor.add_text_adaptive(
            text=f"@{recipient_name}",
            position=(None, 650),  # 只使用y坐标
            right_align_x=3300,    # 右侧固定边界，调整这个值可以改变右对齐位置
            font_name=font_path,
            font_size=200,         # 初始/最大字体大小
            min_font_size=100,     # 最小字体大小限制
            text_color="white",
            rotation_angle=-13,
            width_threshold=0.75   # 宽度阈值，文本宽度超过75%时开始缩小字体
        )
        
        # 确定团队名称的字体大小
        team_text = f"FROM {team_name} Team!"
        team_text2 = f"FROM {team_name2} Team!" if team_name2 else ""

        # 选择较长的团队名称来确定字体大小
        longer_team_text = team_text if len(team_text) >= len(team_text2) else team_text2
        max_team_width = 2400  # 设置团队名称最大宽度

        # 计算合适的字体大小，基于较长的文本
        team_font_size = calculate_font_size(
            text=longer_team_text,
            font_path=font_path,
            start_size=170,
            min_size=100,
            max_width=max_team_width
        )

        print(f"两个团队名称统一使用字体大小: {team_font_size}")

        # 添加第一个团队名称
        editor.add_text(
            text=team_text,
            position=(1100, 1600),
            font_name=font_path,
            font_size=team_font_size,  # 使用计算好的统一字体大小
            text_color="white",
            rotation_angle=-13
        )

        # 添加第二个团队名称（如果有）
        if team_name2:
            editor.add_text(
                text=team_text2,
                position=(1100, 1800),
                font_name=font_path,
                font_size=team_font_size,  # 使用相同的字体大小
                text_color="white",
                rotation_angle=-13
            )
        
        # 生成不带特殊字符的文件名
        safe_recipient = recipient_name.replace(' ', '_').replace('/', '_').replace(';', '_')
        safe_amount = offer_amount.replace('$', '').replace(',', '').replace('.', '_')
        safe_team = team_name.replace('/', '_')
        
        # 如果未提供自定义文件名，创建一个基于用户信息的文件名
        if filename is None:
            filename = f"output_{safe_recipient}_{safe_amount}_{safe_team}_{current_date}.png"
        
        # 获取最终图像
        final_image = editor.get_current_image()
        
        # 直接上传到S3
        s3_url = generate_and_upload_image(
            image_obj=final_image,
            filename=filename,
            bucket=bucket
        )
        
        return s3_url
        
    except Exception as e:
        print(f"生成并上传offer海报时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_offer_poster_base64(recipient_name, offer_amount, team_name,
                               team_name2="", 
                               banner_path=None,  
                               font_path=None):
    """
    生成offer海报并返回Base64编码的图像数据
    
    参数:
        recipient_name: 收件人姓名（如 "Cora Xia"）
        offer_amount: offer金额（如 "20,850"）
        team_name: 团队名称（如 "Niki/Vera"）
        team_name2: 第二个团队名称（可选）
        banner_path: offer banner图片路径
        font_path: 字体文件路径
        
    返回:
        tuple: (成功标志, Base64字符串或错误消息)
    """
    try:
        # 设置默认路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if banner_path is None:
            banner_path = os.path.join(base_dir, "assets", "images", "offer_banner.png")
            print(f"使用默认banner路径: {banner_path}")
            
        if font_path is None:
            font_path = os.path.join(base_dir, "assets", "fonds", "impact.ttf")
            print(f"使用默认字体路径: {font_path}")
            
        # 检查banner文件是否存在
        if not os.path.exists(banner_path):
            print(f"警告: Banner图片不存在: {banner_path}")
            # 尝试查找assets目录下的所有图片
            assets_dir = os.path.join(base_dir, "assets")
            if os.path.exists(assets_dir):
                print(f"搜索assets目录中的图片文件...")
                for root, dirs, files in os.walk(assets_dir):
                    for file in files:
                        if file.endswith(('.png', '.jpg', '.jpeg')):
                            print(f"找到图片: {os.path.join(root, file)}")
                            banner_path = os.path.join(root, file)
                            break
                    if os.path.exists(banner_path):
                        break
            
            if not os.path.exists(banner_path):
                return False, "Banner image not found"
            
        # 处理金额格式（确保有$符号）
        if not offer_amount.startswith('$') and not offer_amount.startswith('￥'):
            offer_amount = f"${offer_amount}"
            
        # 创建图片编辑器
        editor = ImageEditor(image_path=banner_path)
        
        # 添加金额文字 - 不使用自适应大小
        editor.add_text(
            text=offer_amount,
            position=(1200, 800),
            font_name=font_path,
            font_size=700,
            text_color="white",
            rotation_angle=-13
        )
        
        # 添加收件人姓名 - 使用自适应字体大小，右对齐
        editor.add_text_adaptive(
            text=f"@{recipient_name}",
            position=(None, 650),  # 只使用y坐标
            right_align_x=3300,    # 右侧固定边界，调整这个值可以改变右对齐位置
            font_name=font_path,
            font_size=200,         # 初始/最大字体大小
            min_font_size=100,     # 最小字体大小限制
            text_color="white",
            rotation_angle=-13,
            width_threshold=0.75   # 宽度阈值，文本宽度超过75%时开始缩小字体
        )
        
        # 确定团队名称的字体大小
        team_text = f"FROM {team_name} Team!"
        team_text2 = f"FROM {team_name2} Team!" if team_name2 else ""

        # 选择较长的团队名称来确定字体大小
        longer_team_text = team_text if len(team_text) >= len(team_text2) else team_text2
        max_team_width = 2400  # 设置团队名称最大宽度

        # 计算合适的字体大小，基于较长的文本
        team_font_size = calculate_font_size(
            text=longer_team_text,
            font_path=font_path,
            start_size=170,
            min_size=100,
            max_width=max_team_width
        )

        print(f"两个团队名称统一使用字体大小: {team_font_size}")

        # 添加第一个团队名称
        editor.add_text(
            text=team_text,
            position=(1100, 1600),
            font_name=font_path,
            font_size=team_font_size,  # 使用计算好的统一字体大小
            text_color="white",
            rotation_angle=-13
        )

        # 添加第二个团队名称（如果有）
        if team_name2:
            editor.add_text(
                text=team_text2,
                position=(1100, 1800),
                font_name=font_path,
                font_size=team_font_size,  # 使用相同的字体大小
                text_color="white",
                rotation_angle=-13
            )
        
        # 获取最终图像
        final_image = editor.get_current_image()
        
        # 转为base64
        buffer = io.BytesIO()
        final_image.convert('RGB').save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return True, img_str
        
    except Exception as e:
        print(f"生成Base64海报时出错: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)

def generate_offer_poster_binary(recipient_name, offer_amount, team_name,
                               team_name2="", 
                               banner_path=None,  
                               font_path=None):
    """
    生成offer海报并返回二进制图像数据
    
    参数:
        recipient_name: 收件人姓名（如 "Cora Xia"）
        offer_amount: offer金额（如 "20,850"）
        team_name: 团队名称（如 "Niki/Vera"）
        team_name2: 第二个团队名称（可选）
        banner_path: offer banner图片路径
        font_path: 字体文件路径
        
    返回:
        tuple: (成功标志, 二进制数据或错误消息)
    """
    try:
        # 设置默认路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if banner_path is None:
            banner_path = os.path.join(base_dir, "assets", "images", "offer_banner.png")
            print(f"使用默认banner路径: {banner_path}")
            
        if font_path is None:
            font_path = os.path.join(base_dir, "assets", "fonds", "impact.ttf")
            print(f"使用默认字体路径: {font_path}")
            
        # 检查banner文件是否存在
        if not os.path.exists(banner_path):
            print(f"警告: Banner图片不存在: {banner_path}")
            # 尝试查找assets目录下的所有图片
            assets_dir = os.path.join(base_dir, "assets")
            if os.path.exists(assets_dir):
                print(f"搜索assets目录中的图片文件...")
                for root, dirs, files in os.walk(assets_dir):
                    for file in files:
                        if file.endswith(('.png', '.jpg', '.jpeg')):
                            print(f"找到图片: {os.path.join(root, file)}")
                            banner_path = os.path.join(root, file)
                            break
                    if os.path.exists(banner_path):
                        break
            
            if not os.path.exists(banner_path):
                return False, "Banner image not found"
            
        # 处理金额格式（确保有$符号）
        if not offer_amount.startswith('$') and not offer_amount.startswith('￥'):
            offer_amount = f"${offer_amount}"
            
        # 创建图片编辑器
        editor = ImageEditor(image_path=banner_path)
        
        # 添加金额文字 - 不使用自适应大小
        editor.add_text(
            text=offer_amount,
            position=(1200, 800),
            font_name=font_path,
            font_size=700,
            text_color="white",
            rotation_angle=-13
        )
        
        # 添加收件人姓名 - 使用自适应字体大小，右对齐
        editor.add_text_adaptive(
            text=f"@{recipient_name}",
            position=(None, 650),  # 只使用y坐标
            right_align_x=3300,    # 右侧固定边界，调整这个值可以改变右对齐位置
            font_name=font_path,
            font_size=200,         # 初始/最大字体大小
            min_font_size=100,     # 最小字体大小限制
            text_color="white",
            rotation_angle=-13,
            width_threshold=0.75   # 宽度阈值，文本宽度超过75%时开始缩小字体
        )
        
        # 确定团队名称的字体大小
        team_text = f"FROM {team_name} Team!"
        team_text2 = f"FROM {team_name2} Team!" if team_name2 else ""

        # 选择较长的团队名称来确定字体大小
        longer_team_text = team_text if len(team_text) >= len(team_text2) else team_text2
        max_team_width = 2400  # 设置团队名称最大宽度

        # 计算合适的字体大小，基于较长的文本
        team_font_size = calculate_font_size(
            text=longer_team_text,
            font_path=font_path,
            start_size=170,
            min_size=100,
            max_width=max_team_width
        )

        print(f"两个团队名称统一使用字体大小: {team_font_size}")

        # 添加第一个团队名称
        editor.add_text(
            text=team_text,
            position=(1100, 1600),
            font_name=font_path,
            font_size=team_font_size,  # 使用计算好的统一字体大小
            text_color="white",
            rotation_angle=-13
        )

        # 添加第二个团队名称（如果有）
        if team_name2:
            editor.add_text(
                text=team_text2,
                position=(1100, 1800),
                font_name=font_path,
                font_size=team_font_size,  # 使用相同的字体大小
                text_color="white",
                rotation_angle=-13
            )
        
        # 获取最终图像
        final_image = editor.get_current_image()
        
        # 转为二进制数据
        buffer = io.BytesIO()
        final_image.convert('RGB').save(buffer, format='PNG')
        binary_data = buffer.getvalue()
        
        return True, binary_data
        
    except Exception as e:
        print(f"生成二进制海报时出错: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)

# 使用示例
if __name__ == "__main__":
    # 测试直接上传到S3
    poster_url = generate_offer_poster_to_s3(
        recipient_name="Yedan Li", 
        offer_amount="14,320", 
        team_name="Ken"
    )
    
    print(f"海报已上传到S3，URL: {poster_url}")
    
    # 原始方法测试（保存到本地）
    poster_path = generate_offer_poster(
        recipient_name="Yedan Li", 
        offer_amount="14,320", 
        team_name="Ken"
    )
    
    print(f"海报已保存到本地: {poster_path}")
