"""
格式化工具函数
"""

def format_number(number_str):
    """
    将数字字符串格式化为带千位分隔符的形式
    
    参数:
        number_str (str): 数字字符串，可以是 "12345" 或 "12,345" 格式
    
    返回:
        str: 格式化后的数字字符串，如 "12,345"
    
    示例:
        >>> format_number("12345")
        "12,345"
        >>> format_number("12,345")
        "12,345"
        >>> format_number("1234567")
        "1,234,567"
    """
    try:
        # 移除所有现有的逗号
        clean_number = number_str.replace(',', '')
        
        # 判断是否以货币符号开头
        prefix = ""
        if clean_number.startswith('$') or clean_number.startswith('￥'):
            prefix = clean_number[0]
            clean_number = clean_number[1:]
        
        # 分离整数部分和小数部分（如果有）
        if '.' in clean_number:
            int_part, decimal_part = clean_number.split('.')
        else:
            int_part, decimal_part = clean_number, None
        
        # 格式化整数部分，每三位添加一个逗号
        formatted_int = ""
        for i, digit in enumerate(reversed(int_part)):
            if i > 0 and i % 3 == 0:
                formatted_int = ',' + formatted_int
            formatted_int = digit + formatted_int
        
        # 添加小数部分（如果有）
        if decimal_part:
            final_number = f"{formatted_int}.{decimal_part}"
        else:
            final_number = formatted_int
        
        # 添加前缀（如果有）
        if prefix:
            final_number = f"{prefix}{final_number}"
        
        return final_number
    
    except Exception as e:
        print(f"格式化数字时出错: {e}")
        # 如果出错，返回原始字符串
        return number_str 