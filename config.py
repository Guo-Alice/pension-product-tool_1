"""
config.py - 配置文件
存储程序配置参数
"""

import os

# 项目信息
PROJECT_NAME = "个人养老金产品搜索与决策工具"
VERSION = "1.0"
AUTHOR = "养老金产品研究团队"
COPYRIGHT_YEAR = "2023"

# 数据文件配置
DATA_FILE = "pension_product_tool/data/养老保险.xlsx"
PROCESSED_DATA_FILE = "processed_products.json"
HISTORY_FILE = "recommendation_history.json"

# 数据文件搜索路径
DATA_FILE_PATHS = [
    "养老保险.xlsx",                    # 当前目录
    "data/养老保险.xlsx",               # data子目录
    "../养老保险.xlsx",                 # 上级目录
    "./养老保险_sample.xlsx",           # 示例文件
    os.path.join(os.path.dirname(__file__), '养老保险.xlsx')
]

# 推荐算法权重配置
WEIGHTS = {
    'age_match': 0.30,          # 年龄匹配权重
    'income_match': 0.20,       # 收入匹配权重
    'risk_match': 0.20,         # 风险匹配权重
    'retirement_match': 0.15,   # 退休规划匹配权重
    'social_security_match': 0.10,  # 社保匹配权重
    'investment_match': 0.05    # 投资金额匹配权重
}

# 用户默认值
DEFAULT_USER_PROFILE = {
    'age': 30,
    'annual_income': 15.0,      # 万元
    'social_security_type': '城镇职工',
    'risk_tolerance': '中',
    'expected_retirement_age': 60,
    'investment_amount': 5.0,   # 万元
    'location': '全国',
    'investment_horizon': '长期',
    'health_status': '良好',
    'family_status': '未婚无子女',
    'liquidity_needs': '中等',
    'existing_insurance': '无'
}

# 风险等级映射
RISK_LEVEL_MAPPING = {
    '低': 1,
    '中低': 2,
    '中': 3,
    '中高': 4,
    '高': 5,
    '未知': 3
}

# 风险等级颜色
RISK_COLORS = {
    '低': '#4CAF50',    # 绿色
    '中低': '#8BC34A',  # 浅绿色
    '中': '#FFC107',    # 黄色
    '中高': '#FF9800',  # 橙色
    '高': '#F44336'     # 红色
}

# 保险类型分类
INSURANCE_TYPES = {
    '年金保险': ['年金保险', '年金险'],
    '养老年金': ['养老', '退休金', '养老年金'],
    '两全保险': ['两全保险', '两全险'],
    '万能型': ['万能型', '万能险'],
    '分红型': ['分红型', '分红险'],
    '团体保险': ['团体', '团体年金', '团体养老'],
    '终身寿险': ['终身寿险'],
    '附加险': ['附加']
}

# 缴费方式分类
PAYMENT_TYPES = {
    '趸交': ['趸交', '一次交清', '趸缴', '一次性'],
    '期缴': ['期缴', '年交', '分期', '定期'],
    '月缴': ['月交', '月缴', '每月'],
    '季缴': ['季交', '季缴', '每季'],
    '半年缴': ['半年交', '半年缴'],
    '未知': []
}

# 社保类型选项
SOCIAL_SECURITY_TYPES = ["城镇职工", "城乡居民", "无", "其他"]

# 风险偏好选项
RISK_TOLERANCE_OPTIONS = ["低", "中低", "中", "中高", "高"]

# 投资期限选项
INVESTMENT_HORIZON_OPTIONS = ["短期(1-3年)", "中期(3-10年)", "长期(10年以上)"]

# 健康状况选项
HEALTH_STATUS_OPTIONS = ["良好", "一般", "有病史"]

# 家庭状况选项
FAMILY_STATUS_OPTIONS = ["未婚无子女", "已婚无子女", "已婚有子女", "其他"]

# 流动性需求选项
LIQUIDITY_NEEDS_OPTIONS = ["高", "中等", "低"]

# 已有保险选项
EXISTING_INSURANCE_OPTIONS = ["无", "有寿险", "有健康险", "有养老险", "有多种保险"]

# 地区选项
LOCATION_OPTIONS = ["全国", "北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉", "其他"]

# 界面配置
UI_CONFIG = {
    'window_size': '1400x900',
    'min_window_size': '1000x700',
    'font_family': '微软雅黑',
    'title_font_size': 18,
    'heading_font_size': 12,
    'normal_font_size': 10,
    'theme': 'clam',
    'primary_color': '#0066cc',
    'secondary_color': '#f0f0f0',
    'success_color': '#4CAF50',
    'warning_color': '#FF9800',
    'error_color': '#F44336'
}

# 导出配置
EXPORT_CONFIG = {
    'default_format': 'csv',
    'supported_formats': ['csv', 'xlsx', 'txt', 'json'],
    'encoding': 'utf-8-sig'
}

# 图表配置
CHART_CONFIG = {
    'figure_size': (10, 6),
    'dpi': 100,
    'title_fontsize': 14,
    'label_fontsize': 11,
    'legend_fontsize': 10,
    'colors': ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#FF5722', '#607D8B']
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'pension_tool.log',
    'max_file_size': 10485760,  # 10MB
    'backup_count': 5
}

# 性能配置
PERFORMANCE_CONFIG = {
    'max_products_display': 100,
    'max_comparison_products': 3,
    'cache_enabled': True,
    'cache_ttl': 3600  # 1小时
}

# 免责声明
DISCLAIMER = """
免责声明:
1. 本工具提供的推荐结果仅供参考，不构成投资建议。
2. 实际投资决策请咨询专业理财顾问。
3. 产品信息可能更新，请以保险公司官方信息为准。
4. 本工具对因使用推荐结果造成的损失不承担责任。
"""

# 帮助信息
HELP_INFO = {
    'contact': 'support@pension-tool.com',
    'website': 'https://www.pension-tool.com',
    'manual': '用户手册.pdf'
}