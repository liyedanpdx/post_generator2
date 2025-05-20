from psd_tools import PSDImage
from psd_tools.constants import Resource
import math

# 加载 PSD 文件
psd_file = PSDImage.open('../assets/psd/源文件.psd')

# 遍历所有图层，找到并打印文字图层的内容
text_layers = []
for layer in psd_file:
    if layer.is_group():
        # 如果是图层组，递归遍历子图层
        for sublayer in layer:
            if sublayer.kind == 'type':  # 检查是否为文字图层
                print(f"图层名称: {sublayer.name}, 文字内容: {sublayer.text}")
                text_layers.append(sublayer)
    elif layer.kind == 'type':  # 检查是否为文字图层
        print(f"图层名称: {layer.name}, 文字内容: {layer.text}")
        text_layers.append(layer)


# 遍历所有图层，查找文字图层并打印其位置
# 遍历所有图层，查找文字图层并打印其位置、倾斜角度、字体大小和字体类型
for layer in psd_file:
    if layer.is_group():
        # 如果是图层组，递归遍历子图层
        for sublayer in layer:
            if sublayer.kind == 'type':  # 检查是否为文字图层
                print(f"图层名称: {sublayer.name}")
                print(f"文字内容: {sublayer.text}")
                
                # 获取位置（使用 offset 或 bbox）
                if hasattr(sublayer, 'offset'):
                    x, y = sublayer.offset  # 偏移量，通常是左上角的坐标
                    print(f"位置 (x, y): ({x}, {y})")
                elif hasattr(sublayer, 'bbox'):
                    bbox = sublayer.bbox  # 边界框，包含左、上、右、下的坐标
                    print(f"边界框 (left, top, right, bottom): {bbox}")
                
                # 尝试获取倾斜角度
                shear_angle = None
                if hasattr(sublayer, 'transform'):
                    transform = sublayer.transform
                    print(f"变换矩阵: {transform}")
                    if len(transform) >= 6:  # 确保矩阵有足够元素
                        a, b, c, d, tx, ty = transform[:6]  # 提取前6个元素
                        if abs(d) > 0:  # 避免除以零
                            shear_angle = math.degrees(math.atan2(b, d))  # 使用 atan2 计算角度（单位：度）
                        elif abs(c) > 0:
                            shear_angle = math.degrees(math.atan2(c, a))
                        else:
                            shear_angle = 0  # 默认无倾斜
                elif hasattr(sublayer, '_engine_data'):
                    engine_data = sublayer._engine_data
                    if 'Transform' in engine_data:
                        transform_data = engine_data['Transform']
                        print(f"变换数据: {transform_data}")
                        if isinstance(transform_data, dict):
                            if 'a' in transform_data and 'b' in transform_data:
                                a, b = transform_data['a'], transform_data['b']
                                shear_angle = math.degrees(math.atan2(b, a))  # 假设 a, b 表示倾斜
                    if 'Warp' in engine_data:  # 扭曲（可能包含倾斜）
                        warp_data = engine_data['Warp']
                        print(f"扭曲数据: {warp_data}")
                else:
                    print("无法获取倾斜角度，请检查 transform 或 engine_data")

                if shear_angle is not None:
                    print(f"倾斜角度: {shear_angle:.2f} 度")
                else:
                    print("未找到倾斜角度信息")
                
                # 尝试获取字体大小和字体类型
                font_size = None
                font_type = None
                if hasattr(sublayer, '_engine_data'):
                    engine_data = sublayer._engine_data
                    if 'EngineDict' in engine_data:
                        engine_dict = engine_data['EngineDict']
                        if 'Editor' in engine_dict:
                            editor = engine_dict['Editor']
                            # 查找字体大小
                            if 'FontSize' in editor:
                                font_size = editor['FontSize']
                            elif 'Size' in editor:  # 可能使用其他键
                                font_size = editor['Size']
                            # 查找字体类型
                            if 'FontSet' in engine_dict:
                                font_set = engine_dict['FontSet']
                                if isinstance(font_set, dict) and 'Name' in font_set:
                                    font_type = font_set['Name']
                                elif isinstance(font_set, list) and len(font_set) > 0:
                                    font_type = font_set[0].get('Name', '未知字体')
                            elif 'FontName' in editor:  # 可能使用其他键
                                font_type = editor['FontName']
                    elif 'Transform' in engine_data:  # 某些情况下字体大小可能在 Transform 中
                        transform_data = engine_data['Transform']
                        if isinstance(transform_data, dict) and 'FontSize' in transform_data:
                            font_size = transform_data['FontSize']
                elif hasattr(sublayer, 'engine_dict'):
                    engine_dict = sublayer.engine_dict
                    if 'Editor' in engine_dict:
                        editor = engine_dict['Editor']
                        if 'FontSize' in editor:
                            font_size = editor['FontSize']
                        if 'FontSet' in engine_dict:
                            font_set = engine_dict['FontSet']
                            if isinstance(font_set, dict) and 'Name' in font_set:
                                font_type = font_set['Name']
                            elif isinstance(font_set, list) and len(font_set) > 0:
                                font_type = font_set[0].get('Name', '未知字体')

                if font_size is not None:
                    print(f"字体大小: {font_size} px")
                else:
                    print("未找到字体大小信息")
                
                if font_type is not None:
                    print(f"字体类型: {font_type}")
                else:
                    print("未找到字体类型信息")
    elif layer.kind == 'type':  # 检查是否为文字图层
        print(f"图层名称: {layer.name}")
        print(f"文字内容: {layer.text}")
        
        # 获取位置
        if hasattr(layer, 'offset'):
            x, y = layer.offset
            print(f"位置 (x, y): ({x}, {y})")
        elif hasattr(layer, 'bbox'):
            bbox = layer.bbox
            print(f"边界框 (left, top, right, bottom): {bbox}")
        
        # 尝试获取倾斜角度
        shear_angle = None
        if hasattr(layer, 'transform'):
            transform = layer.transform
            print(f"变换矩阵: {transform}")
            if len(transform) >= 6:
                a, b, c, d, tx, ty = transform[:6]
                if abs(d) > 0:
                    shear_angle = math.degrees(math.atan2(b, d))
                elif abs(c) > 0:
                    shear_angle = math.degrees(math.atan2(c, a))
                else:
                    shear_angle = 0
        elif hasattr(layer, '_engine_data'):
            engine_data = layer._engine_data
            if 'Transform' in engine_data:
                transform_data = engine_data['Transform']
                print(f"变换数据: {transform_data}")
                if isinstance(transform_data, dict):
                    if 'a' in transform_data and 'b' in transform_data:
                        a, b = transform_data['a'], transform_data['b']
                        shear_angle = math.degrees(math.atan2(b, a))
            if 'Warp' in engine_data:
                warp_data = engine_data['Warp']
                print(f"扭曲数据: {warp_data}")
        else:
            print("无法获取倾斜角度，请检查 transform 或 engine_data")

        if shear_angle is not None:
            print(f"倾斜角度: {shear_angle:.2f} 度")
        else:
            print("未找到倾斜角度信息")
        
        # 尝试获取字体大小和字体类型
        font_size = None
        font_type = None
        if hasattr(layer, '_engine_data'):
            engine_data = layer._engine_data
            if 'EngineDict' in engine_data:
                engine_dict = engine_data['EngineDict']
                if 'Editor' in engine_dict:
                    editor = engine_dict['Editor']
                    if 'FontSize' in editor:
                        font_size = editor['FontSize']
                    elif 'Size' in editor:
                        font_size = editor['Size']
                    if 'FontSet' in engine_dict:
                        font_set = engine_dict['FontSet']
                        if isinstance(font_set, dict) and 'Name' in font_set:
                            font_type = font_set['Name']
                        elif isinstance(font_set, list) and len(font_set) > 0:
                            font_type = font_set[0].get('Name', '未知字体')
                    elif 'FontName' in editor:
                        font_type = editor['FontName']
            elif 'Transform' in engine_data:
                transform_data = engine_data['Transform']
                if isinstance(transform_data, dict) and 'FontSize' in transform_data:
                    font_size = transform_data['FontSize']
        elif hasattr(layer, 'engine_dict'):
            engine_dict = layer.engine_dict
            if 'Editor' in engine_dict:
                editor = engine_dict['Editor']
                if 'FontSize' in editor:
                    font_size = editor['FontSize']
                if 'FontSet' in engine_dict:
                    font_set = engine_dict['FontSet']
                    if isinstance(font_set, dict) and 'Name' in font_set:
                        font_type = font_set['Name']
                    elif isinstance(font_set, list) and len(font_set) > 0:
                        font_type = font_set[0].get('Name', '未知字体')

        if font_size is not None:
            print(f"字体大小: {font_size} px")
        else:
            print("未找到字体大小信息")
        
        if font_type is not None:
            print(f"字体类型: {font_type}")
        else:
            print("未找到字体类型信息")
            
# 保存修改后的 PSD 文件（可选：如果需要保留 PSD 格式）
psd_file.save('测试件_修改后.psd')

# 如果需要生成图片，可以使用以下代码（需要 Pillow）
from PIL import Image
image = psd_file.composite()  # 合成所有图层
image.save('测试件_输出.png', 'PNG')  # 保存为 PNG 文件
print("已生成输出图片：测试件_输出.png")







