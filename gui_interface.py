"""
gui_interface.py - 养老金产品搜索与决策工具界面
基于Tkinter的图形用户界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib

matplotlib.use('TkAgg')
import os
import webbrowser
from PIL import Image, ImageTk
import io


class PensionProductApp:
    """个人养老金产品推荐系统界面"""

    def __init__(self, root, analyzer, recommender):
        """
        初始化应用
        Args:
            root: Tkinter根窗口
            analyzer: PensionProductAnalyzer实例
            recommender: PensionProductRecommender实例
        """
        # 设置matplotlib中文字体
        matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        matplotlib.rcParams['axes.unicode_minus'] = False
        self.root = root
        self.analyzer = analyzer
        self.recommender = recommender
        self.current_user_id = "user_001"
        self.selected_products = []  # 用于对比的产品ID列表
        self.current_recommendations = []  # 当前推荐结果

        # 设置窗口
        self.root.title("个人养老金产品搜索与决策工具")
        self.root.geometry("1400x900")

        # 设置图标（如果有的话）
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass

        # 设置样式
        self.setup_styles()

        # 创建主界面
        self.setup_ui()

        # 加载用户历史（如果有）
        self.load_user_history()

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()

        # 使用clam主题
        style.theme_use('clam')

        # 自定义样式
        style.configure('Title.TLabel', font=('微软雅黑', 18, 'bold'))
        style.configure('Heading.TLabel', font=('微软雅黑', 12, 'bold'))
        style.configure('Normal.TLabel', font=('微软雅黑', 10))
        style.configure('Highlight.TLabel', font=('微软雅黑', 10, 'bold'), foreground='#0066cc')

        style.configure('Action.TButton', font=('微软雅黑', 10, 'bold'), padding=5)
        style.configure('Primary.TButton', font=('微软雅黑', 10, 'bold'),
                        background='#0066cc', foreground='white')

        style.configure('Treeview', font=('微软雅黑', 10), rowheight=25)
        style.configure('Treeview.Heading', font=('微软雅黑', 10, 'bold'))

        style.map('Primary.TButton',
                  background=[('active', '#0052a3'), ('pressed', '#003d7a')])

    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 标题栏
        self.create_title_bar(main_frame)

        # 主内容区域
        self.create_main_content(main_frame)

        # 状态栏
        self.create_status_bar(main_frame)

    def create_title_bar(self, parent):
        """创建标题栏"""
        title_frame = ttk.Frame(parent)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 标题
        title_label = ttk.Label(title_frame,
                                text="个人养老金产品搜索与决策工具",
                                style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)

        # 版本信息
        version_label = ttk.Label(title_frame,
                                  text="版本 1.0 | 基于中国个人养老金政策",
                                  style='Normal.TLabel')
        version_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # 快速操作按钮
        button_frame = ttk.Frame(title_frame)
        button_frame.grid(row=0, column=1, rowspan=2, sticky=tk.E, padx=(20, 0))

        ttk.Button(button_frame, text="使用指南",
                   command=self.show_user_guide, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="数据统计",
                   command=self.show_statistics, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="关于",
                   command=self.show_about, width=10).pack(side=tk.LEFT, padx=2)

    def create_main_content(self, parent):
        """创建主内容区域"""
        # 创建笔记本（选项卡）
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # 配置笔记本的网格权重
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)

        # 创建各个标签页
        self.create_user_input_tab()
        self.create_recommendation_tab()
        self.create_product_detail_tab()
        self.create_comparison_tab()
        self.create_analysis_tab()

        # 绑定选项卡切换事件
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)

    def create_user_input_tab(self):
        """创建用户输入标签页"""
        self.input_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.input_tab, text="用户信息输入")

        # 配置网格权重
        self.input_tab.columnconfigure(0, weight=1)
        self.input_tab.rowconfigure(1, weight=1)

        # 创建输入区域
        self.create_user_input_form(self.input_tab)

    def create_user_input_form(self, parent):
        """创建用户输入表单"""
        # 主框架
        main_form_frame = ttk.Frame(parent, padding="20")
        main_form_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        main_form_frame.columnconfigure(1, weight=1)

        # 表单标题
        form_title = ttk.Label(main_form_frame,
                               text="请输入您的个人信息，系统将为您推荐合适的养老金产品",
                               style='Heading.TLabel')
        form_title.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # 基本信息部分
        basic_frame = ttk.LabelFrame(main_form_frame, text="基本信息", padding="15")
        basic_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        basic_frame.columnconfigure(1, weight=1)
        basic_frame.columnconfigure(3, weight=1)
        basic_frame.columnconfigure(5, weight=1)

        row = 0

        # 年龄
        ttk.Label(basic_frame, text="年龄:", style='Normal.TLabel').grid(
            row=row, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.age_var = tk.IntVar(value=30)
        age_spin = ttk.Spinbox(basic_frame, from_=18, to=70, textvariable=self.age_var,
                               width=15)
        age_spin.grid(row=row, column=1, sticky=tk.W, padx=(0, 20), pady=5)
        ttk.Label(basic_frame, text="岁", style='Normal.TLabel').grid(
            row=row, column=2, sticky=tk.W, padx=(0, 20), pady=5)

        # 年收入
        ttk.Label(basic_frame, text="年收入:", style='Normal.TLabel').grid(
            row=row, column=3, sticky=tk.W, padx=(0, 5), pady=5)
        self.income_var = tk.DoubleVar(value=15.0)
        income_spin = ttk.Spinbox(basic_frame, from_=5, to=100, increment=1,
                                  textvariable=self.income_var, width=15)
        income_spin.grid(row=row, column=4, sticky=tk.W, padx=(0, 20), pady=5)
        ttk.Label(basic_frame, text="万元", style='Normal.TLabel').grid(
            row=row, column=5, sticky=tk.W, pady=5)

        row += 1

        # 社保类型
        ttk.Label(basic_frame, text="社保类型:", style='Normal.TLabel').grid(
            row=row, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.ss_type_var = tk.StringVar(value="城镇职工")
        ss_combo = ttk.Combobox(basic_frame, textvariable=self.ss_type_var,
                                values=["城镇职工", "城乡居民", "无", "其他"],
                                width=15, state="readonly")
        ss_combo.grid(row=row, column=1, sticky=tk.W, padx=(0, 20), pady=5)

        # 风险承受能力
        ttk.Label(basic_frame, text="风险承受:", style='Normal.TLabel').grid(
            row=row, column=3, sticky=tk.W, padx=(0, 5), pady=5)
        self.risk_var = tk.StringVar(value="中")
        risk_combo = ttk.Combobox(basic_frame, textvariable=self.risk_var,
                                  values=["低", "中低", "中", "中高", "高"],
                                  width=15, state="readonly")
        risk_combo.grid(row=row, column=4, sticky=tk.W, padx=(0, 20), pady=5)

        row += 1

        # 预期退休年龄
        ttk.Label(basic_frame, text="预期退休年龄:", style='Normal.TLabel').grid(
            row=row, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.retirement_var = tk.IntVar(value=60)
        retirement_spin = ttk.Spinbox(basic_frame, from_=50, to=70,
                                      textvariable=self.retirement_var, width=15)
        retirement_spin.grid(row=row, column=1, sticky=tk.W, padx=(0, 20), pady=5)
        ttk.Label(basic_frame, text="岁", style='Normal.TLabel').grid(
            row=row, column=2, sticky=tk.W, padx=(0, 20), pady=5)

        # 计划投资金额
        ttk.Label(basic_frame, text="计划投资金额:", style='Normal.TLabel').grid(
            row=row, column=3, sticky=tk.W, padx=(0, 5), pady=5)
        self.investment_var = tk.DoubleVar(value=5.0)
        investment_spin = ttk.Spinbox(basic_frame, from_=1, to=50, increment=1,
                                      textvariable=self.investment_var, width=15)
        investment_spin.grid(row=row, column=4, sticky=tk.W, padx=(0, 20), pady=5)
        ttk.Label(basic_frame, text="万元", style='Normal.TLabel').grid(
            row=row, column=5, sticky=tk.W, pady=5)

        row += 1

        # 所在地区
        ttk.Label(basic_frame, text="所在地区:", style='Normal.TLabel').grid(
            row=row, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.location_var = tk.StringVar(value="全国")
        location_combo = ttk.Combobox(basic_frame, textvariable=self.location_var,
                                      values=["全国", "北京", "上海", "广州", "深圳",
                                              "杭州", "南京", "成都", "武汉", "其他"],
                                      width=15, state="readonly")
        location_combo.grid(row=row, column=1, sticky=tk.W, padx=(0, 20), pady=5)

        # 投资期限
        ttk.Label(basic_frame, text="投资期限:", style='Normal.TLabel').grid(
            row=row, column=3, sticky=tk.W, padx=(0, 5), pady=5)
        self.horizon_var = tk.StringVar(value="长期")
        horizon_combo = ttk.Combobox(basic_frame, textvariable=self.horizon_var,
                                     values=["短期(1-3年)", "中期(3-10年)", "长期(10年以上)"],
                                     width=15, state="readonly")
        horizon_combo.grid(row=row, column=4, sticky=tk.W, padx=(0, 20), pady=5)

        # 高级选项部分
        advanced_frame = ttk.LabelFrame(main_form_frame, text="高级选项（可选）", padding="15")
        advanced_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        advanced_frame.columnconfigure(1, weight=1)
        advanced_frame.columnconfigure(3, weight=1)

        row = 0

        # 健康状况
        ttk.Label(advanced_frame, text="健康状况:", style='Normal.TLabel').grid(
            row=row, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.health_var = tk.StringVar(value="良好")
        health_combo = ttk.Combobox(advanced_frame, textvariable=self.health_var,
                                    values=["良好", "一般", "有病史"],
                                    width=15, state="readonly")
        health_combo.grid(row=row, column=1, sticky=tk.W, padx=(0, 20), pady=5)

        # 家庭状况
        ttk.Label(advanced_frame, text="家庭状况:", style='Normal.TLabel').grid(
            row=row, column=2, sticky=tk.W, padx=(0, 5), pady=5)
        self.family_var = tk.StringVar(value="未婚无子女")
        family_combo = ttk.Combobox(advanced_frame, textvariable=self.family_var,
                                    values=["未婚无子女", "已婚无子女", "已婚有子女", "其他"],
                                    width=15, state="readonly")
        family_combo.grid(row=row, column=3, sticky=tk.W, pady=5)

        row += 1

        # 流动性需求
        ttk.Label(advanced_frame, text="流动性需求:", style='Normal.TLabel').grid(
            row=row, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.liquidity_var = tk.StringVar(value="中等")
        liquidity_combo = ttk.Combobox(advanced_frame, textvariable=self.liquidity_var,
                                       values=["高", "中等", "低"],
                                       width=15, state="readonly")
        liquidity_combo.grid(row=row, column=1, sticky=tk.W, padx=(0, 20), pady=5)

        # 已有保险
        ttk.Label(advanced_frame, text="已有商业保险:", style='Normal.TLabel').grid(
            row=row, column=2, sticky=tk.W, padx=(0, 5), pady=5)
        self.existing_insurance_var = tk.StringVar(value="无")
        insurance_combo = ttk.Combobox(advanced_frame, textvariable=self.existing_insurance_var,
                                       values=["无", "有寿险", "有健康险", "有养老险", "有多种保险"],
                                       width=15, state="readonly")
        insurance_combo.grid(row=row, column=3, sticky=tk.W, pady=5)

        # 按钮区域
        button_frame = ttk.Frame(main_form_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))

        # 搜索按钮
        search_button = ttk.Button(button_frame, text="搜索推荐产品",
                                   command=self.search_products,
                                   style='Primary.TButton', width=15)
        search_button.pack(side=tk.LEFT, padx=5)

        # 重置按钮
        reset_button = ttk.Button(button_frame, text="重置",
                                  command=self.reset_inputs, width=10)
        reset_button.pack(side=tk.LEFT, padx=5)

        # 保存配置按钮
        save_button = ttk.Button(button_frame, text="保存用户配置",
                                 command=self.save_user_profile, width=12)
        save_button.pack(side=tk.LEFT, padx=5)

        # 加载配置按钮
        load_button = ttk.Button(button_frame, text="加载用户配置",
                                 command=self.load_user_profile, width=12)
        load_button.pack(side=tk.LEFT, padx=5)

        # 快速填充示例按钮
        example_button = ttk.Button(button_frame, text="快速示例",
                                    command=self.fill_example, width=10)
        example_button.pack(side=tk.LEFT, padx=5)

    def create_recommendation_tab(self):
        """创建推荐结果标签页"""
        self.recommendation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.recommendation_tab, text="产品推荐")

        # 配置网格
        self.recommendation_tab.columnconfigure(0, weight=1)
        self.recommendation_tab.rowconfigure(0, weight=1)

        # 创建推荐结果显示区域
        self.create_recommendation_display(self.recommendation_tab)

    def create_recommendation_display(self, parent):
        """创建推荐结果显示区域"""
        # 主框架
        main_frame = ttk.Frame(parent)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 控制面板
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 推荐数量选择
        ttk.Label(control_frame, text="显示数量:", style='Normal.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        self.recommendation_count_var = tk.IntVar(value=5)
        count_combo = ttk.Combobox(control_frame, textvariable=self.recommendation_count_var,
                                   values=[3, 5, 10, 20], width=8, state="readonly")
        count_combo.pack(side=tk.LEFT, padx=(0, 20))

        # 过滤选项
        ttk.Label(control_frame, text="过滤条件:", style='Normal.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        self.filter_type_var = tk.StringVar(value="全部")
        filter_combo = ttk.Combobox(control_frame, textvariable=self.filter_type_var,
                                    values=["全部", "养老年金", "年金保险", "两全保险", "分红型", "万能型"],
                                    width=12, state="readonly")
        filter_combo.pack(side=tk.LEFT, padx=(0, 20))

        # 排序选项
        ttk.Label(control_frame, text="排序方式:", style='Normal.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        self.sort_by_var = tk.StringVar(value="匹配度")
        sort_combo = ttk.Combobox(control_frame, textvariable=self.sort_by_var,
                                  values=["匹配度", "最低保费", "风险等级", "保险公司"],
                                  width=12, state="readonly")
        sort_combo.pack(side=tk.LEFT, padx=(0, 20))

        # 刷新按钮
        refresh_button = ttk.Button(control_frame, text="刷新",
                                    command=self.refresh_recommendations, width=8)
        refresh_button.pack(side=tk.LEFT)

        # 推荐结果表格
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # 创建Treeview
        columns = ('product_name', 'insurance_company', 'match_score', 'age_range',
                   'insurance_type', 'payment_type', 'min_premium', 'risk_level')

        self.recommendation_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        # 定义列标题
        column_headers = {
            'product_name': '产品名称',
            'insurance_company': '保险公司',
            'match_score': '匹配度',
            'age_range': '适合年龄',
            'insurance_type': '保险类型',
            'payment_type': '缴费方式',
            'min_premium': '最低保费',
            'risk_level': '风险等级'
        }

        for col, header in column_headers.items():
            self.recommendation_tree.heading(col, text=header)

        # 定义列宽
        column_widths = {
            'product_name': 250,
            'insurance_company': 150,
            'match_score': 80,
            'age_range': 100,
            'insurance_type': 100,
            'payment_type': 100,
            'min_premium': 100,
            'risk_level': 80
        }

        for col, width in column_widths.items():
            self.recommendation_tree.column(col, width=width)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                                  command=self.recommendation_tree.yview)
        self.recommendation_tree.configure(yscrollcommand=scrollbar.set)

        self.recommendation_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))

        # 查看详情按钮
        detail_button = ttk.Button(button_frame, text="查看详情",
                                   command=self.show_selected_product_detail, width=10)
        detail_button.pack(side=tk.LEFT, padx=(0, 5))

        # 添加到对比按钮
        compare_button = ttk.Button(button_frame, text="添加到对比",
                                    command=self.add_to_comparison, width=10)
        compare_button.pack(side=tk.LEFT, padx=(0, 5))

        # 个性化建议按钮
        advice_button = ttk.Button(button_frame, text="个性化建议",
                                   command=self.show_personalized_advice, width=10)
        advice_button.pack(side=tk.LEFT, padx=(0, 5))

        # 导出结果按钮
        export_button = ttk.Button(button_frame, text="导出结果",
                                   command=self.export_recommendations, width=10)
        export_button.pack(side=tk.LEFT)

        # 绑定选择事件
        self.recommendation_tree.bind('<<TreeviewSelect>>', self.on_recommendation_select)
        self.recommendation_tree.bind('<Double-Button-1>', lambda e: self.show_selected_product_detail())

    def create_product_detail_tab(self):
        """创建产品详情标签页"""
        self.detail_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.detail_tab, text="产品详情")

        # 配置网格
        self.detail_tab.columnconfigure(0, weight=1)
        self.detail_tab.rowconfigure(0, weight=1)

        # 创建产品详情显示区域
        self.create_product_detail_display(self.detail_tab)

    def create_product_detail_display(self, parent):
        """创建产品详情显示区域"""
        # 主框架
        main_frame = ttk.Frame(parent)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 基本信息区域
        info_frame = ttk.LabelFrame(main_frame, text="产品基本信息", padding="15")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 使用网格布局基本信息
        info_frame.columnconfigure(1, weight=1)
        info_frame.columnconfigure(3, weight=1)

        # 基本信息标签
        self.detail_labels = {}

        fields = [
            ('产品名称:', 'product_name', 0, 0),
            ('保险公司:', 'insurance_company', 0, 2),
            ('产品代码:', 'product_id', 1, 0),
            ('保险类型:', 'insurance_type', 1, 2),
            ('适合年龄:', 'age_range_str', 2, 0),
            ('缴费方式:', 'payment_type', 2, 2),
            ('缴费年限:', 'payment_periods_str', 3, 0),
            ('最低保费:', 'min_premium_str', 3, 2),
            ('风险等级:', 'risk_level', 4, 0),
            ('保障期限:', 'coverage_str', 4, 2),
            ('销售渠道:', 'sales_channel', 5, 0),
            ('销售范围:', 'sales_scope', 5, 2)
        ]

        for i, (label_text, field, row, col) in enumerate(fields):
            # 标签
            ttk.Label(info_frame, text=label_text, style='Normal.TLabel', width=10).grid(
                row=row, column=col, sticky=tk.W, padx=(0, 5), pady=5)

            # 值
            label = ttk.Label(info_frame, text="", style='Highlight.TLabel', width=30)
            label.grid(row=row, column=col + 1, sticky=tk.W, pady=5)
            self.detail_labels[field] = label

        # 产品特色区域
        features_frame = ttk.LabelFrame(main_frame, text="产品特色", padding="15")
        features_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # 配置网格
        features_frame.columnconfigure(0, weight=1)
        features_frame.rowconfigure(0, weight=1)

        # 特色文本
        self.features_text = scrolledtext.ScrolledText(features_frame, height=8,
                                                       font=('微软雅黑', 10))
        self.features_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 推荐理由区域
        reasons_frame = ttk.LabelFrame(main_frame, text="推荐理由", padding="15")
        reasons_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 推荐理由文本
        self.reasons_text = scrolledtext.ScrolledText(reasons_frame, height=4,
                                                      font=('微软雅黑', 10))
        self.reasons_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))

        # 添加到对比按钮
        detail_compare_button = ttk.Button(button_frame, text="添加到对比",
                                           command=self.add_current_to_comparison, width=12)
        detail_compare_button.pack(side=tk.LEFT, padx=(0, 5))

        # 查看原始数据按钮
        raw_data_button = ttk.Button(button_frame, text="查看原始数据",
                                     command=self.show_raw_data, width=12)
        raw_data_button.pack(side=tk.LEFT, padx=(0, 5))

        # 查找类似产品按钮
        similar_button = ttk.Button(button_frame, text="查找类似产品",
                                    command=self.find_similar_products, width=12)
        similar_button.pack(side=tk.LEFT)

    def create_comparison_tab(self):
        """创建产品对比标签页"""
        self.comparison_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.comparison_tab, text="产品对比")

        # 配置网格
        self.comparison_tab.columnconfigure(0, weight=1)
        self.comparison_tab.rowconfigure(0, weight=1)

        # 创建产品对比显示区域
        self.create_comparison_display(self.comparison_tab)

    def create_comparison_display(self, parent):
        """创建产品对比显示区域"""
        # 主框架
        main_frame = ttk.Frame(parent)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 控制面板
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 对比产品列表
        ttk.Label(control_frame, text="对比产品:", style='Normal.TLabel').pack(side=tk.LEFT, padx=(0, 5))

        # 产品选择框
        self.comparison_listbox = tk.Listbox(control_frame, height=3, width=50,
                                             font=('微软雅黑', 10))
        self.comparison_listbox.pack(side=tk.LEFT, padx=(0, 10))

        # 控制按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.LEFT)

        # 移除按钮
        remove_button = ttk.Button(button_frame, text="移除",
                                   command=self.remove_from_comparison, width=8)
        remove_button.pack(side=tk.TOP, pady=(0, 5))

        # 清空按钮
        clear_button = ttk.Button(button_frame, text="清空",
                                  command=self.clear_comparison, width=8)
        clear_button.pack(side=tk.TOP)

        # 对比表格
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # 创建Treeview
        self.comparison_tree = ttk.Treeview(table_frame, height=20)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                                  command=self.comparison_tree.yview)
        self.comparison_tree.configure(yscrollcommand=scrollbar.set)

        self.comparison_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 按钮区域
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))

        # 生成报告按钮
        report_button = ttk.Button(bottom_frame, text="生成对比报告",
                                   command=self.generate_comparison_report, width=12)
        report_button.pack(side=tk.LEFT, padx=(0, 5))

        # 导出对比按钮
        export_button = ttk.Button(bottom_frame, text="导出对比",
                                   command=self.export_comparison, width=12)
        export_button.pack(side=tk.LEFT, padx=(0, 5))

        # 打印按钮
        print_button = ttk.Button(bottom_frame, text="打印",
                                  command=self.print_comparison, width=8)
        print_button.pack(side=tk.LEFT)

    def create_analysis_tab(self):
        """创建统计分析标签页"""
        self.analysis_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_tab, text="统计分析")

        # 配置网格
        self.analysis_tab.columnconfigure(0, weight=1)
        self.analysis_tab.rowconfigure(1, weight=1)

        # 创建统计分析显示区域
        self.create_analysis_display(self.analysis_tab)

    def create_analysis_display(self, parent):
        """创建统计分析显示区域"""
        # 主框架
        main_frame = ttk.Frame(parent)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 控制面板
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 分析类型选择
        ttk.Label(control_frame, text="分析类型:", style='Normal.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        self.analysis_type_var = tk.StringVar(value="产品类型分布")
        analysis_combo = ttk.Combobox(control_frame, textvariable=self.analysis_type_var,
                                      values=["产品类型分布", "风险等级分布", "缴费方式分布",
                                              "保险公司分布", "年龄要求分布", "保费范围分布"],
                                      width=20, state="readonly")
        analysis_combo.pack(side=tk.LEFT, padx=(0, 20))

        # 图表类型选择
        ttk.Label(control_frame, text="图表类型:", style='Normal.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        self.chart_type_var = tk.StringVar(value="柱状图")
        chart_combo = ttk.Combobox(control_frame, textvariable=self.chart_type_var,
                                   values=["柱状图", "饼图", "折线图", "条形图"],
                                   width=12, state="readonly")
        chart_combo.pack(side=tk.LEFT, padx=(0, 20))

        # 生成图表按钮
        generate_button = ttk.Button(control_frame, text="生成图表",
                                     command=self.generate_analysis_charts, width=10)
        generate_button.pack(side=tk.LEFT, padx=(0, 20))

        # 保存图表按钮
        save_button = ttk.Button(control_frame, text="保存图表",
                                 command=self.save_chart, width=10)
        save_button.pack(side=tk.LEFT)

        # 图表显示区域
        chart_frame = ttk.Frame(main_frame)
        chart_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)

        # 创建画布框架
        self.chart_canvas_frame = ttk.Frame(chart_frame)
        self.chart_canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 统计摘要区域
        summary_frame = ttk.LabelFrame(main_frame, text="数据统计摘要", padding="10")
        summary_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        # 摘要文本
        self.summary_text = scrolledtext.ScrolledText(summary_frame, height=6,
                                                      font=('微软雅黑', 10))
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格
        summary_frame.columnconfigure(0, weight=1)
        summary_frame.rowconfigure(0, weight=1)

    def create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = ttk.Frame(parent, relief=tk.SUNKEN)
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                 style='Normal.TLabel')
        status_label.pack(side=tk.LEFT, padx=5)

        # 数据统计
        self.data_stats_var = tk.StringVar(value="")
        stats_label = ttk.Label(status_frame, textvariable=self.data_stats_var,
                                style='Normal.TLabel')
        stats_label.pack(side=tk.RIGHT, padx=5)

        # 更新数据统计
        self.update_data_stats()

    def update_data_stats(self):
        """更新数据统计信息"""
        if self.analyzer.processed_df is not None:
            total_products = len(self.analyzer.processed_df)
            total_companies = len(self.analyzer.processed_df['insurance_company'].unique())
            self.data_stats_var.set(f"产品总数: {total_products} | 保险公司: {total_companies}")

    def get_user_profile(self):
        """获取用户输入的用户画像"""
        profile = {
            'age': self.age_var.get(),
            'annual_income': self.income_var.get(),
            'social_security_type': self.ss_type_var.get(),
            'risk_tolerance': self.risk_var.get(),
            'expected_retirement_age': self.retirement_var.get(),
            'investment_amount': self.investment_var.get(),
            'location': self.location_var.get(),
            'investment_horizon': self.horizon_var.get(),
            'health_status': self.health_var.get(),
            'family_status': self.family_var.get(),
            'liquidity_needs': self.liquidity_var.get(),
            'existing_insurance': self.existing_insurance_var.get()
        }
        return profile

    def search_products(self):
        """搜索推荐产品"""
        try:
            self.status_var.set("正在搜索推荐产品...")
            self.root.update()

            # 获取用户画像
            user_profile = self.get_user_profile()

            # 添加到推荐系统
            self.recommender.add_user_profile(self.current_user_id, user_profile)

            # 获取过滤条件
            filter_criteria = None
            if self.filter_type_var.get() != "全部":
                filter_criteria = {'insurance_type': self.filter_type_var.get()}

            # 获取推荐结果
            result = self.recommender.get_recommendations(
                self.current_user_id,
                top_n=self.recommendation_count_var.get(),
                filter_criteria=filter_criteria
            )

            if "error" in result:
                messagebox.showerror("错误", result["error"])
                self.status_var.set("搜索失败")
                return

            # 保存当前推荐结果
            self.current_recommendations = result["recommendations"]

            # 清空现有数据
            for item in self.recommendation_tree.get_children():
                self.recommendation_tree.delete(item)

            # 显示推荐结果
            for rec in self.current_recommendations:
                self.recommendation_tree.insert('', 'end',
                                                values=(
                                                    rec['product_name'],
                                                    rec['insurance_company'],
                                                    f"{rec['match_score']}%",
                                                    rec['age_range'],
                                                    rec['insurance_type'],
                                                    rec['payment_type'],
                                                    rec['min_premium'],
                                                    rec['risk_level']
                                                ),
                                                tags=(rec['product_id'],)
                                                )

            # 更新状态
            self.status_var.set(f"找到 {len(self.current_recommendations)} 个推荐产品")

            # 切换到推荐标签页
            self.notebook.select(1)

            # 显示成功消息
            messagebox.showinfo("成功", f"已为您找到 {len(self.current_recommendations)} 个匹配产品")

        except Exception as e:
            messagebox.showerror("错误", f"搜索产品时出错: {str(e)}")
            self.status_var.set("搜索失败")
            import traceback
            traceback.print_exc()

    def refresh_recommendations(self):
        """刷新推荐结果"""
        # 根据排序方式重新排序
        if self.current_recommendations:
            sort_by = self.sort_by_var.get()

            if sort_by == "匹配度":
                sorted_recommendations = sorted(self.current_recommendations,
                                                key=lambda x: x['match_score'], reverse=True)
            elif sort_by == "最低保费":
                sorted_recommendations = sorted(self.current_recommendations,
                                                key=lambda x: float(
                                                    x['min_premium'].replace('元', '').replace(',', '')))
            elif sort_by == "风险等级":
                risk_order = {'低': 1, '中低': 2, '中': 3, '中高': 4, '高': 5}
                sorted_recommendations = sorted(self.current_recommendations,
                                                key=lambda x: risk_order.get(x['risk_level'], 3))
            elif sort_by == "保险公司":
                sorted_recommendations = sorted(self.current_recommendations,
                                                key=lambda x: x['insurance_company'])
            else:
                sorted_recommendations = self.current_recommendations

            # 清空现有数据
            for item in self.recommendation_tree.get_children():
                self.recommendation_tree.delete(item)

            # 显示排序后的结果
            for rec in sorted_recommendations:
                self.recommendation_tree.insert('', 'end',
                                                values=(
                                                    rec['product_name'],
                                                    rec['insurance_company'],
                                                    f"{rec['match_score']}%",
                                                    rec['age_range'],
                                                    rec['insurance_type'],
                                                    rec['payment_type'],
                                                    rec['min_premium'],
                                                    rec['risk_level']
                                                ),
                                                tags=(rec['product_id'],)
                                                )

            self.status_var.set(f"已按{sort_by}重新排序")

    def on_recommendation_select(self, event):
        """处理推荐产品选择事件"""
        selection = self.recommendation_tree.selection()
        if selection:
            # 切换到详情标签页
            self.notebook.select(2)
            # 显示产品详情
            self.show_selected_product_detail()

    def show_selected_product_detail(self):
        """显示选中产品的详细信息"""
        selection = self.recommendation_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一个产品")
            return

        try:
            item = self.recommendation_tree.item(selection[0])
            product_name = item['values'][0]  # 产品名称

            # 查找产品详情
            product_details = None

            # 首先从当前推荐结果中查找
            for rec in self.current_recommendations:
                if rec['product_name'] == product_name:
                    product_details = rec
                    break

            # 如果没有找到，尝试获取产品ID并从分析器获取
            if not product_details:
                # 尝试获取产品ID
                product_id = None
                if item['tags']:
                    product_id = item['tags'][0]
                else:
                    # 从产品名称查找ID
                    for rec in self.current_recommendations:
                        if rec['product_name'] == product_name:
                            product_id = rec['product_id']
                            break

                if product_id and self.analyzer:
                    product_details = self.analyzer.get_product_details(product_id)
                    if product_details:
                        # 包装成推荐结果格式
                        product_details = {
                            'product_id': product_id,
                            'product_name': product_name,
                            'product_details': product_details
                        }

            if product_details:
                self.display_product_details(product_details)
                # 切换到详情标签页
                self.notebook.select(2)
            else:
                messagebox.showerror("错误", "无法获取产品详情")

        except Exception as e:
            messagebox.showerror("错误", f"显示产品详情时出错: {str(e)}")

    def display_product_details(self, product_info):
        """显示产品详情"""
        try:
            # 从product_info中提取详细信息
            if 'product_details' in product_info:
                details = product_info['product_details']
            else:
                details = product_info

            # 更新基本信息标签
            for field, label in self.detail_labels.items():
                value = details.get(field, 'N/A')
                if value is None:
                    value = 'N/A'
                label.config(text=str(value))

            # 更新产品特色
            self.features_text.delete(1.0, tk.END)
            features = details.get('features', '')
            if not features and 'product_details' in product_info:
                features = product_info.get('features', '')
            if features:
                self.features_text.insert(1.0, features)
            else:
                self.features_text.insert(1.0, '暂无产品特色描述')

            # 更新推荐理由
            self.reasons_text.delete(1.0, tk.END)
            reasons = product_info.get('recommendation_reasons', [])
            if reasons:
                if isinstance(reasons, list):
                    for reason in reasons:
                        self.reasons_text.insert(tk.END, f"• {reason}\n")
                else:
                    self.reasons_text.insert(1.0, str(reasons))
            else:
                # 如果没有推荐理由，生成基本理由
                basic_reasons = [
                    f"保险类型: {details.get('insurance_type', '未知')}",
                    f"风险等级: {details.get('risk_level', '未知')}",
                    f"保障期限: {details.get('coverage_str', '未知')}",
                    f"适合年龄: {details.get('age_range_str', '未知')}"
                ]
                for reason in basic_reasons:
                    self.reasons_text.insert(tk.END, f"• {reason}\n")

            # 保存当前产品ID
            self.current_product_id = details.get('product_id', '')
            if not self.current_product_id:
                self.current_product_id = product_info.get('product_id', '')

        except Exception as e:
            messagebox.showerror("错误", f"显示产品详情时出错: {str(e)}")

    def add_to_comparison(self):
        """添加推荐列表中的选中产品到对比"""
        selection = self.recommendation_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一个产品")
            return

        try:
            item = self.recommendation_tree.item(selection[0])

            # 获取产品ID - 修复逻辑
            product_id = None

            # 首先尝试从tag获取
            if item['tags']:
                product_id = item['tags'][0]
            else:
                # 如果tag为空，尝试从产品名称匹配
                product_name = item['values'][0]  # 产品名称在第一列
                # 在推荐结果中查找
                for rec in self.current_recommendations:
                    if rec['product_name'] == product_name:
                        product_id = rec['product_id']
                        break

            if not product_id:
                messagebox.showerror("错误", "无法获取产品ID")
                return

            self.add_product_to_comparison(product_id)

        except Exception as e:
            messagebox.showerror("错误", f"添加产品到对比时出错: {str(e)}")

    def add_current_to_comparison(self):
        """添加当前详情页的产品到对比"""
        if hasattr(self, 'current_product_id'):
            self.add_product_to_comparison(self.current_product_id)
        else:
            messagebox.showwarning("提示", "没有当前产品信息")

    def add_product_to_comparison(self, product_id):
        """添加产品到对比列表"""
        if not product_id:
            messagebox.showwarning("提示", "产品ID为空")
            return

        if product_id in self.selected_products:
            messagebox.showinfo("提示", "该产品已在对比列表中")
            return

        if len(self.selected_products) >= 3:
            messagebox.showwarning("提示", "最多只能对比3个产品")
            return

        self.selected_products.append(product_id)

        # 获取产品名称用于显示
        product_name = "未知产品"
        # 从分析器获取
        product = self.analyzer.get_product_details(product_id)
        if product:
            product_name = product.get('product_name', product_id)
        else:
            # 从推荐结果中查找
            for rec in self.current_recommendations:
                if rec.get('product_id') == product_id:
                    product_name = rec.get('product_name', product_id)
                    break

        # 更新对比列表显示
        self.update_comparison_list()
        self.update_comparison_table()

        # 切换到对比标签页
        self.notebook.select(3)

        messagebox.showinfo("成功", f"产品已添加到对比列表: {product_name}")

    def update_comparison_table(self):
        """更新对比表格"""
        # 清空现有数据和列
        self.comparison_tree.delete(*self.comparison_tree.get_children())

        if not self.selected_products:
            # 设置默认列
            self.comparison_tree['columns'] = ('info')
            self.comparison_tree.heading('info', text='对比信息')
            self.comparison_tree.column('info', width=400)
            self.comparison_tree.insert('', 'end', values=('请添加产品到对比列表'))
            return

        # 获取产品详情
        products = []
        for product_id in self.selected_products:
            # 从分析器获取产品详情
            product = self.analyzer.get_product_details(product_id)
            if product:
                products.append(product)
            else:
                # 从当前推荐结果中查找
                for rec in self.current_recommendations:
                    if rec.get('product_id') == product_id or rec.get('product_details', {}).get(
                            'product_id') == product_id:
                        if 'product_details' in rec:
                            products.append(rec['product_details'])
                        else:
                            products.append(rec)
                        break

        if not products:
            self.comparison_tree.insert('', 'end', values=('无法获取产品信息'))
            return

        # 设置列
        columns = ['对比项目'] + [f'产品{i + 1}' for i in range(len(products))]
        self.comparison_tree['columns'] = columns
        self.comparison_tree['show'] = 'headings'

        # 设置列标题
        self.comparison_tree.heading('对比项目', text='对比项目')
        for i in range(len(products)):
            col_name = f'产品{i + 1}'
            product_name = products[i].get('product_name', f'产品{i + 1}')
            if len(product_name) > 20:
                product_name = product_name[:17] + '...'
            self.comparison_tree.heading(col_name, text=product_name)

        # 设置列宽
        self.comparison_tree.column('对比项目', width=120)
        for i in range(len(products)):
            self.comparison_tree.column(f'产品{i + 1}', width=200)

        # 定义对比项目及其对应的产品字段
        comparison_fields = [
            ('产品名称', 'product_name'),
            ('保险公司', 'insurance_company'),
            ('适合年龄', 'age_range_str'),
            ('保险类型', 'insurance_type'),
            ('缴费方式', 'payment_type'),
            ('缴费年限', 'payment_periods_str'),
            ('最低保费', 'min_premium_str'),
            ('风险等级', 'risk_level'),
            ('保障期限', 'coverage_str'),
            ('销售渠道', 'sales_channel'),
            ('销售范围', 'sales_scope')
        ]

        # 添加数据行
        for field_name, field_key in comparison_fields:
            row_values = [field_name]
            for product in products:
                value = product.get(field_key, 'N/A')
                row_values.append(str(value))
            self.comparison_tree.insert('', 'end', values=row_values)

        # 添加产品特色对比
        features_row = ['产品特色']
        for product in products:
            features = product.get('features', '')
            if len(features) > 50:
                features = features[:47] + '...'
            features_row.append(features)
        self.comparison_tree.insert('', 'end', values=features_row)

    def update_comparison_list(self):
        """更新对比产品列表"""
        self.comparison_listbox.delete(0, tk.END)

        for product_id in self.selected_products:
            # 获取产品名称
            product_name = f"产品({product_id})"

            # 从分析器获取
            product = self.analyzer.get_product_details(product_id)
            if product:
                product_name = product.get('product_name', product_id)
            else:
                # 从推荐结果中查找
                for rec in self.current_recommendations:
                    if rec.get('product_id') == product_id:
                        product_name = rec.get('product_name', product_id)
                        break

            self.comparison_listbox.insert(tk.END, product_name)

    def remove_from_comparison(self):
        """从对比列表中移除选中产品"""
        selection = self.comparison_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要移除的产品")
            return

        index = selection[0]
        if 0 <= index < len(self.selected_products):
            removed_id = self.selected_products.pop(index)
            self.update_comparison_list()
            self.update_comparison_table()

            product = self.analyzer.get_product_details(removed_id)
            product_name = product['product_name'] if product else f"产品{removed_id}"
            messagebox.showinfo("成功", f"已移除: {product_name}")

    def clear_comparison(self):
        """清空对比列表"""
        if not self.selected_products:
            return

        if messagebox.askyesno("确认", "确定要清空对比列表吗？"):
            self.selected_products = []
            self.update_comparison_list()
            self.update_comparison_table()

    def show_personalized_advice(self):
        """显示个性化建议"""
        try:
            advice = self.recommender.get_personalized_advice(self.current_user_id)

            if "error" in advice:
                messagebox.showerror("错误", advice["error"])
                return

            # 创建建议窗口
            advice_window = tk.Toplevel(self.root)
            advice_window.title("个性化养老规划建议")
            advice_window.geometry("800x600")

            # 标题
            title_label = ttk.Label(advice_window, text="个性化养老规划建议",
                                    font=('微软雅黑', 16, 'bold'))
            title_label.pack(pady=(20, 10))

            # 用户信息
            user_frame = ttk.LabelFrame(advice_window, text="您的个人信息", padding="15")
            user_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

            user_info = (
                f"年龄: {advice['user_id']}岁 | "
                f"年收入: {self.income_var.get()}万元 | "
                f"风险偏好: {self.risk_var.get()} | "
                f"社保类型: {self.ss_type_var.get()}"
            )
            ttk.Label(user_frame, text=user_info, font=('微软雅黑', 10)).pack()

            # 创建笔记本
            advice_notebook = ttk.Notebook(advice_window)
            advice_notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

            # 通用建议标签页
            general_frame = ttk.Frame(advice_notebook)
            advice_notebook.add(general_frame, text="通用建议")

            general_text = scrolledtext.ScrolledText(general_frame, font=('微软雅黑', 11))
            general_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            for item in advice.get('general_advice', []):
                general_text.insert(tk.END, f"• {item}\n\n")

            general_text.config(state=tk.DISABLED)

            # 产品推荐标签页
            product_frame = ttk.Frame(advice_notebook)
            advice_notebook.add(product_frame, text="产品类型推荐")

            product_text = scrolledtext.ScrolledText(product_frame, font=('微软雅黑', 11))
            product_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            for item in advice.get('product_type_recommendations', []):
                product_text.insert(tk.END, f"• {item}\n\n")

            product_text.config(state=tk.DISABLED)

            # 风险管理标签页
            risk_frame = ttk.Frame(advice_notebook)
            advice_notebook.add(risk_frame, text="风险管理建议")

            risk_text = scrolledtext.ScrolledText(risk_frame, font=('微软雅黑', 11))
            risk_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            for item in advice.get('risk_management_advice', []):
                risk_text.insert(tk.END, f"• {item}\n\n")

            risk_text.config(state=tk.DISABLED)

            # 下一步建议标签页
            next_frame = ttk.Frame(advice_notebook)
            advice_notebook.add(next_frame, text="下一步行动")

            next_text = scrolledtext.ScrolledText(next_frame, font=('微软雅黑', 11))
            next_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            for i, item in enumerate(advice.get('next_steps', []), 1):
                next_text.insert(tk.END, f"{i}. {item}\n\n")

            next_text.config(state=tk.DISABLED)

            # 底部按钮
            button_frame = ttk.Frame(advice_window)
            button_frame.pack(pady=(0, 20))

            ttk.Button(button_frame, text="保存建议",
                       command=lambda: self.save_advice(advice)).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="打印",
                       command=lambda: self.print_advice(advice)).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="关闭",
                       command=advice_window.destroy).pack(side=tk.LEFT, padx=5)

        except Exception as e:
            messagebox.showerror("错误", f"生成个性化建议时出错: {str(e)}")

    def save_advice(self, advice):
        """保存建议到文件"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile=f"养老规划建议_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=" * 50 + "\n")
                    f.write("个性化养老规划建议\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"生成时间: {advice['advice_time']}\n")
                    f.write(f"用户ID: {advice['user_id']}\n\n")

                    f.write("通用建议:\n")
                    f.write("-" * 30 + "\n")
                    for item in advice['general_advice']:
                        f.write(f"• {item}\n")

                    f.write("\n产品类型推荐:\n")
                    f.write("-" * 30 + "\n")
                    for item in advice['product_type_recommendations']:
                        f.write(f"• {item}\n")

                    f.write("\n风险管理建议:\n")
                    f.write("-" * 30 + "\n")
                    for item in advice['risk_management_advice']:
                        f.write(f"• {item}\n")

                    f.write("\n下一步行动:\n")
                    f.write("-" * 30 + "\n")
                    for i, item in enumerate(advice['next_steps'], 1):
                        f.write(f"{i}. {item}\n")

                messagebox.showinfo("成功", f"建议已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存建议时出错: {str(e)}")

    def print_advice(self, advice):
        """打印建议"""
        messagebox.showinfo("提示", "打印功能需要连接打印机。建议已复制到剪贴板。")

        # 复制到剪贴板
        import pyperclip
        try:
            advice_text = "个性化养老规划建议\n\n"
            advice_text += f"生成时间: {advice['advice_time']}\n\n"

            advice_text += "通用建议:\n"
            for item in advice['general_advice']:
                advice_text += f"• {item}\n"

            advice_text += "\n产品类型推荐:\n"
            for item in advice['product_type_recommendations']:
                advice_text += f"• {item}\n"

            pyperclip.copy(advice_text)
            messagebox.showinfo("成功", "建议已复制到剪贴板")
        except:
            messagebox.showwarning("提示", "无法复制到剪贴板，请手动复制")

    def export_recommendations(self):
        """导出推荐结果"""
        if not self.current_recommendations:
            messagebox.showwarning("提示", "没有推荐结果可导出")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("Excel文件", "*.xlsx"), ("文本文件", "*.txt")],
            initialfile=f"养老金产品推荐_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        if filename:
            try:
                # 转换为DataFrame
                export_data = []
                for rec in self.current_recommendations:
                    row = {
                        '产品名称': rec['product_name'],
                        '保险公司': rec['insurance_company'],
                        '匹配度(%)': rec['match_score'],
                        '适合年龄': rec['age_range'],
                        '保险类型': rec['insurance_type'],
                        '缴费方式': rec['payment_type'],
                        '最低保费': rec['min_premium'],
                        '风险等级': rec['risk_level'],
                        '保障期限': rec['coverage'],
                        '推荐理由': ' | '.join(rec['recommendation_reasons']) if isinstance(
                            rec['recommendation_reasons'], list) else rec['recommendation_reasons']
                    }
                    export_data.append(row)

                df = pd.DataFrame(export_data)

                # 根据文件类型保存
                if filename.endswith('.csv'):
                    df.to_csv(filename, index=False, encoding='utf-8-sig')
                elif filename.endswith('.xlsx'):
                    df.to_excel(filename, index=False)
                else:
                    df.to_csv(filename, index=False, encoding='utf-8-sig')

                messagebox.showinfo("成功", f"推荐结果已导出到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"导出推荐结果时出错: {str(e)}")

    def generate_comparison_report(self):
        """生成对比报告"""
        if not self.selected_products:
            messagebox.showwarning("提示", "请先添加要对比的产品")
            return

        # 生成对比数据
        comparison = self.recommender.generate_comparison_table(self.selected_products)

        if not comparison:
            messagebox.showerror("错误", "无法生成对比报告")
            return

        # 创建报告窗口
        report_window = tk.Toplevel(self.root)
        report_window.title("产品对比报告")
        report_window.geometry("1000x700")

        # 标题
        title_label = ttk.Label(report_window, text="养老金产品对比报告",
                                font=('微软雅黑', 16, 'bold'))
        title_label.pack(pady=(20, 10))

        # 报告信息
        info_frame = ttk.Frame(report_window)
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        info_text = f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        info_text += f"对比产品数: {len(self.selected_products)}"
        ttk.Label(info_frame, text=info_text, font=('微软雅黑', 10)).pack()

        # 创建Treeview显示对比
        columns = ['feature'] + [f'product_{i + 1}' for i in range(len(self.selected_products))]

        report_tree = ttk.Treeview(report_window, columns=columns, show='headings', height=20)

        # 设置列标题
        report_tree.heading('feature', text='对比项目')
        for i in range(len(self.selected_products)):
            col_name = f'product_{i + 1}'
            product = self.analyzer.get_product_details(self.selected_products[i])
            product_name = product['product_name'][:25] + '...' if product and len(product['product_name']) > 25 else \
            product['product_name'] if product else f"产品{i + 1}"
            report_tree.heading(col_name, text=product_name)

        # 设置列宽
        report_tree.column('feature', width=150)
        for i in range(len(self.selected_products)):
            report_tree.column(f'product_{i + 1}', width=250)

        # 添加数据
        for row in comparison:
            report_tree.insert('', 'end', values=[row['feature']] +
                                                 [row.get(f'product_{i + 1}', 'N/A') for i in
                                                  range(len(self.selected_products))])

        # 添加滚动条
        scrollbar = ttk.Scrollbar(report_window, orient=tk.VERTICAL, command=report_tree.yview)
        report_tree.configure(yscrollcommand=scrollbar.set)

        report_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=(0, 20))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 20), pady=(0, 20))

        # 底部按钮
        button_frame = ttk.Frame(report_window)
        button_frame.pack(pady=(0, 20))

        ttk.Button(button_frame, text="保存报告",
                   command=lambda: self.save_comparison_report(comparison)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="打印",
                   command=lambda: self.print_comparison_report(comparison)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭",
                   command=report_window.destroy).pack(side=tk.LEFT, padx=5)

    def save_comparison_report(self, comparison):
        """保存对比报告"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("CSV文件", "*.csv"), ("所有文件", "*.*")],
            initialfile=f"产品对比报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("养老金产品对比报告\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"对比产品数: {len(self.selected_products)}\n\n")

                    # 写入产品信息
                    for i, product_id in enumerate(self.selected_products, 1):
                        product = self.analyzer.get_product_details(product_id)
                        if product:
                            f.write(f"产品{i}: {product['product_name']}\n")
                            f.write(f"  保险公司: {product['insurance_company']}\n")
                            f.write(f"  适合年龄: {product['age_range_str']}\n")
                            f.write(f"  风险等级: {product['risk_level']}\n")
                            f.write(f"  最低保费: {product['min_premium_str']}\n\n")

                    f.write("\n" + "=" * 60 + "\n")
                    f.write("详细对比\n")
                    f.write("=" * 60 + "\n\n")

                    # 写入对比表格
                    for row in comparison:
                        f.write(f"{row['feature']}:\n")
                        for i in range(len(self.selected_products)):
                            col_name = f'product_{i + 1}'
                            f.write(f"  产品{i + 1}: {row.get(col_name, 'N/A')}\n")
                        f.write("\n")

                messagebox.showinfo("成功", f"对比报告已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存对比报告时出错: {str(e)}")

    def print_comparison_report(self, comparison):
        """打印对比报告"""
        messagebox.showinfo("提示", "打印功能需要连接打印机。报告内容已复制到剪贴板。")

        # 复制到剪贴板
        import pyperclip
        try:
            report_text = "养老金产品对比报告\n\n"
            report_text += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            report_text += f"对比产品数: {len(self.selected_products)}\n\n"

            for row in comparison[:10]:  # 只复制前10行
                report_text += f"{row['feature']}: "
                for i in range(len(self.selected_products)):
                    col_name = f'product_{i + 1}'
                    report_text += f"产品{i + 1}: {row.get(col_name, 'N/A')} | "
                report_text += "\n"

            pyperclip.copy(report_text)
            messagebox.showinfo("成功", "报告内容已复制到剪贴板")
        except:
            messagebox.showwarning("提示", "无法复制到剪贴板，请手动复制")

    def export_comparison(self):
        """导出对比数据"""
        if not self.selected_products:
            messagebox.showwarning("提示", "没有对比数据可导出")
            return

        comparison = self.recommender.generate_comparison_table(self.selected_products)

        if not comparison:
            messagebox.showerror("错误", "无法生成对比数据")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("Excel文件", "*.xlsx")],
            initialfile=f"产品对比数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        if filename:
            try:
                # 转换为DataFrame
                export_data = []
                for row in comparison:
                    export_data.append(row)

                df = pd.DataFrame(export_data)

                if filename.endswith('.csv'):
                    df.to_csv(filename, index=False, encoding='utf-8-sig')
                else:
                    df.to_excel(filename, index=False)

                messagebox.showinfo("成功", f"对比数据已导出到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"导出对比数据时出错: {str(e)}")

    def print_comparison(self):
        """打印对比表格"""
        if not self.selected_products:
            messagebox.showwarning("提示", "没有对比数据可打印")
            return

        messagebox.showinfo("提示", "打印功能需要连接打印机。\n\n建议先导出为文件再打印。")

    def generate_analysis_charts(self):
        """生成分析图表"""
        try:
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            if self.analyzer.processed_df is None:
                messagebox.showwarning("提示", "请先处理数据")
                return

            # 清除现有图表
            for widget in self.chart_canvas_frame.winfo_children():
                widget.destroy()

            analysis_type = self.analysis_type_var.get()
            chart_type = self.chart_type_var.get()

            # 创建图形
            fig = Figure(figsize=(10, 6), dpi=100)
            ax = fig.add_subplot(111)

            # 根据分析类型获取数据
            if analysis_type == "产品类型分布":
                data = self.analyzer.processed_df['insurance_type'].value_counts()
                title = "产品类型分布"
                xlabel = "产品类型"
                ylabel = "产品数量"

            elif analysis_type == "风险等级分布":
                data = self.analyzer.processed_df['risk_level'].value_counts()
                title = "风险等级分布"
                xlabel = "风险等级"
                ylabel = "产品数量"

            elif analysis_type == "缴费方式分布":
                data = self.analyzer.processed_df['payment_type'].value_counts()
                title = "缴费方式分布"
                xlabel = "缴费方式"
                ylabel = "产品数量"

            elif analysis_type == "保险公司分布":
                data = self.analyzer.processed_df['insurance_company'].value_counts().head(10)
                title = "保险公司产品数量TOP10"
                xlabel = "保险公司"
                ylabel = "产品数量"

            elif analysis_type == "年龄要求分布":
                # 统计最小年龄分布
                age_data = self.analyzer.processed_df['min_age'].dropna()
                if not age_data.empty:
                    bins = [0, 18, 30, 40, 50, 60, 100]
                    labels = ['0-18', '19-30', '31-40', '41-50', '51-60', '61+']
                    age_groups = pd.cut(age_data, bins=bins, labels=labels, right=False)
                    data = age_groups.value_counts().sort_index()
                    title = "最低年龄要求分布"
                    xlabel = "年龄区间"
                    ylabel = "产品数量"
                else:
                    messagebox.showwarning("提示", "年龄数据不足")
                    return

            elif analysis_type == "保费范围分布":
                # 统计保费范围
                premium_data = self.analyzer.processed_df['min_premium'].dropna()
                if not premium_data.empty:
                    bins = [0, 1000, 5000, 10000, 50000, float('inf')]
                    labels = ['<1000', '1000-5000', '5000-10000', '10000-50000', '>50000']
                    premium_groups = pd.cut(premium_data, bins=bins, labels=labels)
                    data = premium_groups.value_counts().sort_index()
                    title = "最低保费分布（元）"
                    xlabel = "保费区间"
                    ylabel = "产品数量"
                else:
                    messagebox.showwarning("提示", "保费数据不足")
                    return

            else:
                messagebox.showwarning("提示", "请选择分析类型")
                return

            # 根据图表类型绘制
            if chart_type == "柱状图":
                x_pos = range(len(data))
                bars = ax.bar(x_pos, data.values)
                ax.set_xticks(x_pos)
                ax.set_xticklabels(data.index, rotation=45, ha='right')

                # 添加数值标签
                for bar, value in zip(bars, data.values):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                            f'{value}', ha='center', va='bottom', fontsize=9)

            elif chart_type == "饼图":
                ax.pie(data.values, labels=data.index, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')  # 保证饼图是圆的

            elif chart_type == "折线图":
                ax.plot(data.index, data.values, marker='o', linewidth=2)
                ax.set_xticks(range(len(data)))
                ax.set_xticklabels(data.index, rotation=45, ha='right')

            elif chart_type == "条形图":
                y_pos = range(len(data))
                bars = ax.barh(y_pos, data.values)
                ax.set_yticks(y_pos)
                ax.set_yticklabels(data.index)

                # 添加数值标签
                for bar, value in zip(bars, data.values):
                    width = bar.get_width()
                    ax.text(width + 0.1, bar.get_y() + bar.get_height() / 2.,
                            f'{value}', ha='left', va='center', fontsize=9)

            # 设置标题和标签
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel(xlabel, fontsize=11)
            ax.set_ylabel(ylabel, fontsize=11)

            # 调整布局
            fig.tight_layout()

            # 将图表嵌入Tkinter
            canvas = FigureCanvasTkAgg(fig, self.chart_canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

            # 配置网格权重
            self.chart_canvas_frame.columnconfigure(0, weight=1)
            self.chart_canvas_frame.rowconfigure(0, weight=1)

            # 更新统计摘要
            self.update_summary_text()

            self.status_var.set(f"已生成{analysis_type}图表")

        except Exception as e:
            messagebox.showerror("错误", f"生成图表时出错: {str(e)}")
            import traceback
            traceback.print_exc()

    def save_chart(self):
        """保存图表"""
        if not hasattr(self, 'current_figure') or self.current_figure is None:
            messagebox.showwarning("提示", "请先生成图表")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG图片", "*.png"), ("JPG图片", "*.jpg"), ("PDF文件", "*.pdf")],
            initialfile=f"养老金分析图表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )

        if filename:
            try:
                self.current_figure.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("成功", f"图表已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存图表时出错: {str(e)}")

    def update_summary_text(self):
        """更新统计摘要文本"""
        if self.analyzer.processed_df is None:
            return

        summary = self.analyzer.get_summary_statistics()

        self.summary_text.delete(1.0, tk.END)

        summary_text = "数据统计摘要\n"
        summary_text += "=" * 30 + "\n\n"
        summary_text += f"产品总数: {summary.get('total_products', 0)}\n"
        summary_text += f"保险公司数: {summary.get('total_companies', 0)}\n\n"

        summary_text += "风险等级分布:\n"
        risk_dist = summary.get('risk_distribution', {})
        for risk, count in risk_dist.items():
            summary_text += f"  {risk}: {count}个\n"

        summary_text += "\n产品类型分布:\n"
        type_dist = summary.get('type_distribution', {})
        for type_name, count in type_dist.items():
            summary_text += f"  {type_name}: {count}个\n"

        self.summary_text.insert(1.0, summary_text)

    def show_raw_data(self):
        """显示原始数据"""
        if not hasattr(self, 'current_product_id'):
            messagebox.showwarning("提示", "没有当前产品信息")
            return

        product_details = self.analyzer.get_product_details(self.current_product_id)
        if not product_details:
            messagebox.showerror("错误", "无法获取产品原始数据")
            return

        # 创建原始数据窗口
        raw_window = tk.Toplevel(self.root)
        raw_window.title("产品原始数据")
        raw_window.geometry("800x600")

        # 标题
        title_label = ttk.Label(raw_window, text="产品原始数据",
                                font=('微软雅黑', 14, 'bold'))
        title_label.pack(pady=(20, 10))

        # 产品信息
        info_frame = ttk.Frame(raw_window)
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        info_text = f"产品名称: {product_details.get('product_name', 'N/A')} | "
        info_text += f"产品代码: {product_details.get('product_id', 'N/A')}"
        ttk.Label(info_frame, text=info_text, font=('微软雅黑', 10)).pack()

        # 原始数据文本
        raw_text = scrolledtext.ScrolledText(raw_window, font=('微软雅黑', 10))
        raw_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # 格式化显示原始数据
        raw_text.insert(1.0, "原始数据详情:\n")
        raw_text.insert(tk.END, "=" * 50 + "\n\n")

        for key, value in product_details.items():
            if key == 'original_data' and isinstance(value, dict):
                raw_text.insert(tk.END, f"\n原始Excel数据:\n")
                for k, v in value.items():
                    raw_text.insert(tk.END, f"  {k}: {str(v)[:100]}...\n")
            else:
                raw_text.insert(tk.END, f"{key}: {str(value)[:200]}\n")

        raw_text.config(state=tk.DISABLED)

        # 关闭按钮
        ttk.Button(raw_window, text="关闭",
                   command=raw_window.destroy).pack(pady=(0, 20))

    def find_similar_products(self):
        """查找类似产品"""
        if not hasattr(self, 'current_product_id'):
            messagebox.showwarning("提示", "没有当前产品信息")
            return

        current_product = self.analyzer.get_product_details(self.current_product_id)
        if not current_product:
            messagebox.showerror("错误", "无法获取当前产品信息")
            return

        # 查找类似产品（同类型、同风险等级）
        similar_products = []
        for _, product in self.analyzer.processed_df.iterrows():
            if product['product_id'] == self.current_product_id:
                continue

            # 相似度评分
            similarity = 0

            if product['insurance_type'] == current_product['insurance_type']:
                similarity += 30

            if product['risk_level'] == current_product['risk_level']:
                similarity += 25

            if product['insurance_company'] == current_product['insurance_company']:
                similarity += 20

            # 保费相近
            current_premium = current_product.get('min_premium', 0)
            product_premium = product.get('min_premium', 0)
            if current_premium > 0 and product_premium > 0:
                ratio = min(current_premium, product_premium) / max(current_premium, product_premium)
                similarity += ratio * 15

            # 年龄要求相近
            if (product['min_age'] == current_product.get('min_age') and
                    product['max_age'] == current_product.get('max_age')):
                similarity += 10

            if similarity > 40:  # 相似度阈值
                similar_products.append((similarity, product.to_dict()))

        # 按相似度排序
        similar_products.sort(key=lambda x: x[0], reverse=True)

        if not similar_products:
            messagebox.showinfo("提示", "未找到类似产品")
            return

        # 显示类似产品
        similar_window = tk.Toplevel(self.root)
        similar_window.title("类似产品推荐")
        similar_window.geometry("800x500")

        # 标题
        title_label = ttk.Label(similar_window,
                                text=f"与'{current_product['product_name']}'类似的产品",
                                font=('微软雅黑', 14, 'bold'))
        title_label.pack(pady=(20, 10))

        # 创建Treeview
        columns = ('product_name', 'insurance_company', 'similarity', 'insurance_type',
                   'risk_level', 'min_premium')

        tree = ttk.Treeview(similar_window, columns=columns, show='headings', height=12)

        # 定义列标题
        column_headers = {
            'product_name': '产品名称',
            'insurance_company': '保险公司',
            'similarity': '相似度',
            'insurance_type': '保险类型',
            'risk_level': '风险等级',
            'min_premium': '最低保费'
        }

        for col, header in column_headers.items():
            tree.heading(col, text=header)

        # 定义列宽
        column_widths = {
            'product_name': 250,
            'insurance_company': 150,
            'similarity': 80,
            'insurance_type': 100,
            'risk_level': 80,
            'min_premium': 100
        }

        for col, width in column_widths.items():
            tree.column(col, width=width)

        # 添加数据
        for similarity, product in similar_products[:10]:  # 最多显示10个
            tree.insert('', 'end',
                        values=(
                            product['product_name'],
                            product['insurance_company'],
                            f"{similarity:.1f}%",
                            product['insurance_type'],
                            product['risk_level'],
                            product['min_premium_str']
                        ),
                        tags=(product['product_id'],)
                        )

        # 添加滚动条
        scrollbar = ttk.Scrollbar(similar_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=(0, 20))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 20), pady=(0, 20))

        # 绑定双击事件
        tree.bind('<Double-Button-1>', lambda e: self.view_similar_product(tree))

        # 按钮区域
        button_frame = ttk.Frame(similar_window)
        button_frame.pack(pady=(0, 20))

        ttk.Button(button_frame, text="查看选中产品",
                   command=lambda: self.view_similar_product(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="添加到对比",
                   command=lambda: self.add_similar_to_comparison(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭",
                   command=similar_window.destroy).pack(side=tk.LEFT, padx=5)

    def view_similar_product(self, tree):
        """查看选中的类似产品"""
        selection = tree.selection()
        if not selection:
            return

        item = tree.item(selection[0])
        product_id = item['tags'][0]

        product_details = self.analyzer.get_product_details(product_id)
        if product_details:
            self.display_product_details(product_details)
            self.notebook.select(2)  # 切换到详情标签页

    def add_similar_to_comparison(self, tree):
        """添加类似产品到对比"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一个产品")
            return

        item = tree.item(selection[0])
        product_id = item['tags'][0]

        self.add_product_to_comparison(product_id)

    def reset_inputs(self):
        """重置输入框"""
        self.age_var.set(30)
        self.income_var.set(15.0)
        self.ss_type_var.set("城镇职工")
        self.risk_var.set("中")
        self.retirement_var.set(60)
        self.investment_var.set(5.0)
        self.location_var.set("全国")
        self.horizon_var.set("长期")
        self.health_var.set("良好")
        self.family_var.set("未婚无子女")
        self.liquidity_var.set("中等")
        self.existing_insurance_var.set("无")

        self.status_var.set("输入已重置")

    def fill_example(self):
        """填充示例数据"""
        # 填充一个典型的用户示例
        self.age_var.set(35)
        self.income_var.set(25.0)  # 25万元
        self.ss_type_var.set("城镇职工")
        self.risk_var.set("中")
        self.retirement_var.set(60)
        self.investment_var.set(12.0)  # 12万元
        self.location_var.set("上海")
        self.horizon_var.set("长期")
        self.health_var.set("良好")
        self.family_var.set("已婚有子女")
        self.liquidity_var.set("中等")
        self.existing_insurance_var.set("有寿险")

        self.status_var.set("已填充示例数据")
        messagebox.showinfo("示例", "已填充示例用户数据，您可以点击'搜索推荐产品'进行测试。")

    def save_user_profile(self):
        """保存用户配置"""
        profile = self.get_user_profile()

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            initialfile=f"用户配置_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(profile, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", f"用户配置已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存用户配置时出错: {str(e)}")

    def load_user_profile(self):
        """加载用户配置"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            title="选择用户配置文件"
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    profile = json.load(f)

                # 加载到界面
                self.age_var.set(profile.get('age', 30))
                self.income_var.set(profile.get('annual_income', 15.0))
                self.ss_type_var.set(profile.get('social_security_type', '城镇职工'))
                self.risk_var.set(profile.get('risk_tolerance', '中'))
                self.retirement_var.set(profile.get('expected_retirement_age', 60))
                self.investment_var.set(profile.get('investment_amount', 5.0))
                self.location_var.set(profile.get('location', '全国'))
                self.horizon_var.set(profile.get('investment_horizon', '长期'))
                self.health_var.set(profile.get('health_status', '良好'))
                self.family_var.set(profile.get('family_status', '未婚无子女'))
                self.liquidity_var.set(profile.get('liquidity_needs', '中等'))
                self.existing_insurance_var.set(profile.get('existing_insurance', '无'))

                messagebox.showinfo("成功", f"用户配置已从 {filename} 加载")
            except Exception as e:
                messagebox.showerror("错误", f"加载用户配置时出错: {str(e)}")

    def load_user_history(self):
        """加载用户历史"""
        try:
            if os.path.exists('recommendation_history.json'):
                self.recommender.load_recommendation_history()
                print("用户历史已加载")
        except:
            print("用户历史加载失败或不存在")

    def on_tab_changed(self, event):
        """处理选项卡切换事件"""
        current_tab = self.notebook.index(self.notebook.select())

        if current_tab == 4:  # 统计分析标签页
            self.update_summary_text()

    def show_user_guide(self):
        """显示使用指南"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("使用指南")
        guide_window.geometry("800x600")

        # 标题
        title_label = ttk.Label(guide_window, text="个人养老金产品搜索与决策工具 - 使用指南",
                                font=('微软雅黑', 16, 'bold'))
        title_label.pack(pady=(20, 10))

        # 创建文本框
        guide_text = scrolledtext.ScrolledText(guide_window, font=('微软雅黑', 11), wrap=tk.WORD)
        guide_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # 指南内容
        guide_content = """
个人养老金产品搜索与决策工具 - 使用指南

一、工具简介
本工具旨在帮助您根据个人情况选择适合的养老金产品。通过输入您的个人信息，系统将智能推荐匹配的养老金产品，并提供详细的产品对比和分析功能。

二、使用步骤
1. 用户信息输入
   - 在"用户信息输入"标签页填写您的个人信息
   - 包括年龄、收入、社保类型、风险偏好等
   - 点击"搜索推荐产品"获取个性化推荐

2. 查看推荐结果
   - 在"产品推荐"标签页查看系统推荐的产品
   - 可按匹配度、保费、风险等级等排序
   - 双击产品或点击"查看详情"查看详细信息

3. 产品详情分析
   - 在"产品详情"标签页查看产品的详细信息
   - 包括基本信息、产品特色、推荐理由等
   - 可将产品添加到对比列表

4. 产品对比
   - 在"产品对比"标签页比较多个产品
   - 最多可同时对比3个产品
   - 可生成详细的对比报告

5. 统计分析
   - 在"统计分析"标签页查看数据统计
   - 可生成各种图表分析
   - 了解产品分布情况

三、主要功能
1. 个性化推荐：根据用户画像智能推荐产品
2. 产品对比：多维度比较不同产品
3. 统计分析：数据可视化分析
4. 报告生成：导出推荐结果和对比报告
5. 数据管理：保存和加载用户配置

四、注意事项
1. 本工具提供的是参考建议，实际投资需谨慎
2. 建议咨询专业理财顾问获取更详细建议
3. 产品信息可能更新，请以保险公司官方信息为准
4. 定期更新数据以获得更准确的推荐

五、技术支持
如遇问题或需要帮助，请联系技术支持团队。
"""

        guide_text.insert(1.0, guide_content)
        guide_text.config(state=tk.DISABLED)

        # 关闭按钮
        ttk.Button(guide_window, text="关闭",
                   command=guide_window.destroy).pack(pady=(0, 20))

    def show_statistics(self):
        """显示数据统计"""
        if self.analyzer.processed_df is None:
            messagebox.showwarning("提示", "请先处理数据")
            return

        stats_window = tk.Toplevel(self.root)
        stats_window.title("数据统计")
        stats_window.geometry("600x500")

        # 标题
        title_label = ttk.Label(stats_window, text="数据统计详情",
                                font=('微软雅黑', 16, 'bold'))
        title_label.pack(pady=(20, 10))

        # 统计信息
        summary = self.analyzer.get_summary_statistics()

        # 创建文本框
        stats_text = scrolledtext.ScrolledText(stats_window, font=('微软雅黑', 11))
        stats_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        stats_content = "数据统计详情\n"
        stats_content += "=" * 40 + "\n\n"

        stats_content += f"产品总数: {summary.get('total_products', 0)}\n"
        stats_content += f"保险公司数: {summary.get('total_companies', 0)}\n\n"

        stats_content += "年龄统计:\n"
        age_stats = summary.get('age_stats', {})
        stats_content += f"  有最低年龄要求的产品: {age_stats.get('has_min_age', 0)}\n"
        stats_content += f"  有最高年龄要求的产品: {age_stats.get('has_max_age', 0)}\n"
        if age_stats.get('avg_min_age'):
            stats_content += f"  平均最低年龄: {age_stats['avg_min_age']:.1f}岁\n"
        if age_stats.get('avg_max_age'):
            stats_content += f"  平均最高年龄: {age_stats['avg_max_age']:.1f}岁\n"
        stats_content += "\n"

        stats_content += "风险等级分布:\n"
        risk_dist = summary.get('risk_distribution', {})
        for risk, count in risk_dist.items():
            percentage = count / summary['total_products'] * 100
            stats_content += f"  {risk}: {count}个 ({percentage:.1f}%)\n"
        stats_content += "\n"

        stats_content += "产品类型分布:\n"
        type_dist = summary.get('type_distribution', {})
        for type_name, count in type_dist.items():
            percentage = count / summary['total_products'] * 100
            stats_content += f"  {type_name}: {count}个 ({percentage:.1f}%)\n"
        stats_content += "\n"

        stats_content += "缴费方式分布:\n"
        payment_dist = summary.get('payment_type_distribution', {})
        for payment_type, count in payment_dist.items():
            percentage = count / summary['total_products'] * 100
            stats_content += f"  {payment_type}: {count}个 ({percentage:.1f}%)\n"
        stats_content += "\n"

        stats_content += "保险公司TOP10:\n"
        top_companies = summary.get('top_companies', {})
        for company, count in top_companies.items():
            stats_content += f"  {company}: {count}个\n"

        stats_text.insert(1.0, stats_content)
        stats_text.config(state=tk.DISABLED)

        # 关闭按钮
        ttk.Button(stats_window, text="关闭",
                   command=stats_window.destroy).pack(pady=(0, 20))

    def show_about(self):
        """显示关于信息"""
        about_window = tk.Toplevel(self.root)
        about_window.title("关于")
        about_window.geometry("500x400")

        # 标题
        title_label = ttk.Label(about_window, text="个人养老金产品搜索与决策工具",
                                font=('微软雅黑', 16, 'bold'))
        title_label.pack(pady=(30, 10))

        # 版本信息
        version_label = ttk.Label(about_window, text="版本 1.0",
                                  font=('微软雅黑', 12))
        version_label.pack(pady=(0, 20))

        # 描述信息
        description = """
基于中国个人养老金政策的智能产品推荐系统

主要功能：
• 个性化养老金产品推荐
• 多维度产品对比分析
• 数据统计与可视化
• 智能匹配算法

适用对象：
• 个人养老金参与者
• 理财规划师
• 保险公司产品经理
• 养老金研究人员

数据来源：
• 中国保险行业协会公开数据
• 各保险公司官方产品信息
• 养老金政策法规

免责声明：
本工具提供的是参考建议，不构成投资建议。
实际投资决策请咨询专业理财顾问。
        """

        desc_label = ttk.Label(about_window, text=description,
                               font=('微软雅黑', 10), justify=tk.LEFT)
        desc_label.pack(pady=(0, 30), padx=20)

        # 版权信息
        copyright_label = ttk.Label(about_window,
                                    text="© 2023 养老金产品研究团队",
                                    font=('微软雅黑', 9))
        copyright_label.pack(pady=(0, 20))

        # 关闭按钮
        ttk.Button(about_window, text="关闭",
                   command=about_window.destroy, width=10).pack(pady=(0, 20))


# 测试函数
def test_gui():
    """测试GUI界面"""
    print("测试GUI界面...")

    # 导入其他模块
    from data_processor import PensionProductAnalyzer
    from recommender import PensionProductRecommender

    # 创建根窗口
    root = tk.Tk()

    # 创建数据处理器
    analyzer = PensionProductAnalyzer()
    analyzer.create_demo_data()
    analyzer.process_data()

    # 创建推荐器
    recommender = PensionProductRecommender(analyzer)

    # 创建应用
    app = PensionProductApp(root, analyzer, recommender)

    # 运行主循环
    root.mainloop()


if __name__ == "__main__":
    test_gui()