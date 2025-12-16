"""
utils.py - 工具函数模块
包含各种辅助函数
"""

import re
import qingli
import pandas as pd
import numpy as np
from typing import Optional, Tuple, Dict, List, Any
from datetime import datetime, date
import hashlib
import os


def extract_numbers(text: str) -> List[int]:
    """
    从文本中提取所有数字
    Args:
        text: 输入文本
    Returns:
        数字列表
    """
    if not text or not isinstance(text, str):
        return []

    numbers = re.findall(r'\d+', text)
    return [int(num) for num in numbers if num.isdigit()]


def extract_age(text: str) -> Tuple[Optional[int], Optional[int]]:
    """
    从文本中提取年龄范围
    Args:
        text: 包含年龄信息的文本
    Returns:
        (min_age, max_age): 最小年龄和最大年龄
    """
    if not text:
        return None, None

    text = str(text).lower()

    # 常见模式
    patterns = [
        r'(\d+)\s*[岁周岁]\s*至\s*(\d+)\s*[岁周岁]',
        r'(\d+)\s*-\s*(\d+)\s*[岁周岁]',
        r'(\d+)\s*到\s*(\d+)\s*[岁周岁]',
        r'(\d+)\s*~\s*(\d+)\s*[岁周岁]',
        r'年龄\s*(\d+)\s*[岁周岁]',
        r'(\d+)\s*[岁周岁]'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                try:
                    min_age = int(groups[0])
                    max_age = int(groups[1])
                    if 0 <= min_age <= 120 and 0 <= max_age <= 120 and min_age <= max_age:
                        return min_age, max_age
                except ValueError:
                    continue
            elif len(groups) == 1:
                try:
                    age = int(groups[0])
                    if 0 <= age <= 120:
                        return age, age
                except ValueError:
                    continue

    return None, None


def format_currency(amount: float, symbol: str = '¥') -> str:
    """
    格式化货币金额
    Args:
        amount: 金额
        symbol: 货币符号
    Returns:
        格式化后的字符串
    """
    if amount is None:
        return "N/A"

    try:
        if amount >= 10000:
            return f"{symbol}{amount / 10000:,.2f}万元"
        else:
            return f"{symbol}{amount:,.2f}元"
    except (TypeError, ValueError):
        return "N/A"


def calculate_age(birth_date: date) -> int:
    """
    计算年龄
    Args:
        birth_date: 出生日期
    Returns:
        年龄
    """
    today = date.today()
    age = today.year - birth_date.year

    # 如果生日还没过，年龄减1
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    return age


def validate_email(email: str) -> bool:
    """
    验证邮箱格式
    Args:
        email: 邮箱地址
    Returns:
        是否有效
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    验证手机号格式
    Args:
        phone: 手机号
    Returns:
        是否有效
    """
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def safe_int(value: Any, default: int = 0) -> int:
    """
    安全转换为整数
    Args:
        value: 输入值
        default: 默认值
    Returns:
        整数结果
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    安全转换为浮点数
    Args:
        value: 输入值
        default: 默认值
    Returns:
        浮点数结果
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_str(value: Any, default: str = '') -> str:
    """
    安全转换为字符串
    Args:
        value: 输入值
        default: 默认值
    Returns:
        字符串结果
    """
    if value is None:
        return default
    return str(value).strip()


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    截断文本
    Args:
        text: 输入文本
        max_length: 最大长度
        suffix: 后缀
    Returns:
        截断后的文本
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """
    扁平化嵌套字典
    Args:
        d: 嵌套字典
        parent_key: 父键
        sep: 分隔符
    Returns:
        扁平化字典
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    将列表分块
    Args:
        lst: 输入列表
        chunk_size: 块大小
    Returns:
        分块后的列表
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def get_file_hash(filepath: str, algorithm: str = 'md5') -> str:
    """
    计算文件哈希值
    Args:
        filepath: 文件路径
        algorithm: 哈希算法
    Returns:
        哈希值
    """
    hash_func = hashlib.new(algorithm)

    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception:
        return ''


def format_timestamp(timestamp: Optional[datetime] = None,
                     format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    格式化时间戳
    Args:
        timestamp: 时间戳
        format_str: 格式字符串
    Returns:
        格式化后的时间字符串
    """
    if timestamp is None:
        timestamp = datetime.now()

    return timestamp.strftime(format_str)


def parse_date(date_str: str, formats: List[str] = None) -> Optional[date]:
    """
    解析日期字符串
    Args:
        date_str: 日期字符串
        formats: 格式列表
    Returns:
        日期对象
    """
    if formats is None:
        formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y年%m月%d日',
            '%d/%m/%Y',
            '%m/%d/%Y'
        ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    return None


def is_valid_date(year: int, month: int, day: int) -> bool:
    """
    检查日期是否有效
    Args:
        year: 年
        month: 月
        day: 日
    Returns:
        是否有效
    """
    try:
        date(year, month, day)
        return True
    except ValueError:
        return False


def calculate_percentage(part: float, total: float) -> float:
    """
    计算百分比
    Args:
        part: 部分值
        total: 总值
    Returns:
        百分比
    """
    if total == 0:
        return 0.0

    return (part / total) * 100


def normalize_text(text: str) -> str:
    """
    标准化文本
    Args:
        text: 输入文本
    Returns:
        标准化后的文本
    """
    if not text:
        return ''

    # 去除首尾空格
    text = text.strip()

    # 替换多个空格为单个空格
    text = re.sub(r'\s+', ' ', text)

    # 替换中文标点
    text = text.replace('，', ',')
    text = text.replace('。', '.')
    text = text.replace('；', ';')
    text = text.replace('：', ':')
    text = text.replace('！', '!')
    text = text.replace('？', '?')
    text = text.replace('（', '(')
    text = text.replace('）', ')')
    text = text.replace('【', '[')
    text = text.replace('】', ']')
    text = text.replace('「', '<')
    text = text.replace('」', '>')

    return text


def generate_id(prefix: str = 'ID', length: int = 8) -> str:
    """
    生成唯一ID
    Args:
        prefix: ID前缀
        length: 长度
    Returns:
        唯一ID
    """
    import random
    import string

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    return f"{prefix}_{timestamp}_{random_str}"


def save_json(data: Any, filepath: str, indent: int = 2) -> bool:
    """
    保存数据为JSON文件
    Args:
        data: 数据
        filepath: 文件路径
        indent: 缩进
    Returns:
        是否成功
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True
    except Exception as e:
        print(f"保存JSON文件失败: {e}")
        return False


def load_json(filepath: str) -> Optional[Any]:
    """
    从JSON文件加载数据
    Args:
        filepath: 文件路径
    Returns:
        数据
    """
    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载JSON文件失败: {e}")
        return None


def dataframe_to_dict(df: pd.DataFrame, orient: str = 'records') -> List[Dict]:
    """
    DataFrame转换为字典列表
    Args:
        df: DataFrame
        orient: 方向
    Returns:
        字典列表
    """
    if df is None or df.empty:
        return []

    return df.to_dict(orient=orient)


def dict_to_dataframe(data: List[Dict]) -> pd.DataFrame:
    """
    字典列表转换为DataFrame
    Args:
        data: 字典列表
    Returns:
        DataFrame
    """
    if not data:
        return pd.DataFrame()

    return pd.DataFrame(data)


def filter_dict(data: Dict, keys: List[str]) -> Dict:
    """
    过滤字典，只保留指定键
    Args:
        data: 输入字典
        keys: 要保留的键列表
    Returns:
        过滤后的字典
    """
    return {k: data.get(k) for k in keys if k in data}


def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    合并两个字典（dict2会覆盖dict1中相同的键）
    Args:
        dict1: 字典1
        dict2: 字典2
    Returns:
        合并后的字典
    """
    result = dict1.copy()
    result.update(dict2)
    return result


def get_nested_value(data: Dict, key_path: str, default: Any = None, sep: str = '.') -> Any:
    """
    获取嵌套字典中的值
    Args:
        data: 嵌套字典
        key_path: 键路径（用分隔符连接）
        default: 默认值
        sep: 分隔符
    Returns:
        值
    """
    keys = key_path.split(sep)
    current = data

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current


def set_nested_value(data: Dict, key_path: str, value: Any, sep: str = '.') -> Dict:
    """
    设置嵌套字典中的值
    Args:
        data: 嵌套字典
        key_path: 键路径（用分隔符连接）
        value: 值
        sep: 分隔符
    Returns:
        更新后的字典
    """
    keys = key_path.split(sep)
    current = data

    for i, key in enumerate(keys[:-1]):
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]

    current[keys[-1]] = value
    return data


def remove_none_values(data: Dict) -> Dict:
    """
    移除字典中的None值
    Args:
        data: 输入字典
    Returns:
        清理后的字典
    """
    return {k: v for k, v in data.items() if v is not None}


def count_words(text: str) -> int:
    """
    统计文本中的单词数（中英文混合）
    Args:
        text: 文本
    Returns:
        单词数
    """
    if not text:
        return 0

    # 中文单词（以字符为单位）
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)

    # 英文单词
    english_words = re.findall(r'\b[a-zA-Z]+\b', text)

    return len(chinese_chars) + len(english_words)


def is_chinese(text: str) -> bool:
    """
    判断文本是否主要为中文
    Args:
        text: 文本
    Returns:
        是否主要为中文
    """
    if not text:
        return False

    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    return len(chinese_chars) / max(len(text), 1) > 0.5


def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名
    Args:
        filename: 文件名
    Returns:
        扩展名（小写）
    """
    return os.path.splitext(filename)[1].lower().strip('.')


def create_directory(dir_path: str) -> bool:
    """
    创建目录（如果不存在）
    Args:
        dir_path: 目录路径
    Returns:
        是否成功
    """
    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建目录失败: {e}")
        return False


def get_file_size(filepath: str) -> int:
    """
    获取文件大小（字节）
    Args:
        filepath: 文件路径
    Returns:
        文件大小
    """
    try:
        return os.path.getsize(filepath)
    except Exception:
        return 0


def human_readable_size(size_bytes: int) -> str:
    """
    将字节大小转换为人类可读的格式
    Args:
        size_bytes: 字节大小
    Returns:
        人类可读的字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


# 测试函数
def test_utils():
    """测试工具函数"""
    print("测试工具函数...")

    # 测试提取数字
    text = "年龄25-60岁，保费10000元"
    numbers = extract_numbers(text)
    print(f"提取数字: {text} -> {numbers}")

    # 测试提取年龄
    age_texts = ["年龄25-60岁", "25周岁至60周岁", "30岁"]
    for t in age_texts:
        min_age, max_age = extract_age(t)
        print(f"提取年龄: {t} -> {min_age}-{max_age}")

    # 测试格式化货币
    amounts = [1000, 15000, 1000000]
    for amt in amounts:
        print(f"格式化货币: {amt} -> {format_currency(amt)}")

    # 测试验证邮箱
    emails = ["test@example.com", "invalid-email", "user@domain.co.uk"]
    for email in emails:
        print(f"验证邮箱: {email} -> {validate_email(email)}")

    # 测试安全转换
    values = ["123", "45.67", "abc", None]
    for val in values:
        print(f"安全转换整数: {val} -> {safe_int(val)}")
        print(f"安全转换浮点数: {val} -> {safe_float(val)}")

    # 测试截断文本
    long_text = "这是一个很长的文本需要被截断显示"
    print(f"截断文本: {long_text} -> {truncate_text(long_text, 10)}")

    # 测试扁平化字典
    nested_dict = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
    flat_dict = flatten_dict(nested_dict)
    print(f"扁平化字典: {nested_dict} -> {flat_dict}")

    # 测试获取嵌套值
    value = get_nested_value(nested_dict, "b.d.e")
    print(f"获取嵌套值: b.d.e -> {value}")

    # 测试统计单词数
    texts = ["Hello World", "你好世界", "Hello 世界"]
    for t in texts:
        print(f"统计单词数: '{t}' -> {count_words(t)}")

    print("\n工具函数测试完成!")


if __name__ == "__main__":
    test_utils()