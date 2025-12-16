"""
main.py - 养老金产品搜索与决策工具主程序
程序入口点，协调各模块运行
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import traceback

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入自定义模块
from data_processor import PensionProductAnalyzer
from recommender import PensionProductRecommender
from gui_interface import PensionProductApp


class PensionProductTool:
    """个人养老金产品搜索与决策工具主类"""

    def __init__(self):
        self.analyzer = None
        self.recommender = None
        self.app = None
        self.data_file = None

    def find_data_file(self):
        """查找数据文件"""
        # 可能的文件路径
        possible_paths = [
            '养老保险.xlsx',  # 当前目录
            'data/养老保险.xlsx',  # data子目录
            '../养老保险.xlsx',  # 上级目录
            './养老保险_sample.xlsx',  # 示例文件
            os.path.join(os.path.dirname(__file__), '养老保险.xlsx')
        ]

        for path in possible_paths:
            if os.path.exists(path):
                print(f"找到数据文件: {path}")
                return path

        return None

    def create_sample_data_file(self):
        """创建示例数据文件（如果不存在）"""
        print("未找到数据文件，将使用内置演示数据")
        return None

    def setup(self):
        """设置工具"""
        print("=" * 60)
        print("个人养老金产品搜索与决策工具")
        print("版本 1.0")
        print("=" * 60)

        # 查找数据文件
        self.data_file = self.find_data_file()

        if not self.data_file:
            print("警告: 未找到数据文件 '养老保险.xlsx'")
            print("将使用内置演示数据")
            print("\n如需使用完整数据，请将数据文件放在以下位置之一:")
            for path in ['养老保险.xlsx', 'data/养老保险.xlsx']:
                print(f"  - {path}")
            print()

        # 创建数据处理器
        print("正在初始化数据处理器...")
        self.analyzer = PensionProductAnalyzer(self.data_file)

        # 处理数据
        print("正在处理数据...")
        try:
            self.analyzer.process_data()
            print(
                f"数据处理完成: {len(self.analyzer.processed_df) if self.analyzer.processed_df is not None else 0} 条记录")
        except Exception as e:
            print(f"数据处理出错: {e}")
            traceback.print_exc()
            return False

        # 创建推荐器
        print("正在初始化推荐系统...")
        self.recommender = PensionProductRecommender(self.analyzer)

        print("初始化完成!")
        print("-" * 60)
        return True

    def run_gui(self):
        """运行GUI界面"""
        try:
            root = tk.Tk()

            # 设置窗口标题
            root.title("个人养老金产品搜索与决策工具")

            # 创建应用
            self.app = PensionProductApp(root, self.analyzer, self.recommender)

            # 设置关闭事件处理
            def on_closing():
                if messagebox.askokcancel("退出", "确定要退出程序吗？"):
                    # 保存数据
                    self.save_before_exit()
                    root.destroy()

            root.protocol("WM_DELETE_WINDOW", on_closing)

            # 运行主循环
            print("启动用户界面...")
            root.mainloop()

        except Exception as e:
            print(f"GUI运行出错: {e}")
            traceback.print_exc()
            return False

        return True

    def save_before_exit(self):
        """退出前保存数据"""
        try:
            # 保存处理后的数据
            if self.analyzer and self.analyzer.processed_df is not None:
                self.analyzer.save_processed_data()

            # 保存推荐历史
            if self.recommender:
                self.recommender.save_recommendation_history()

            print("数据已保存")
        except Exception as e:
            print(f"保存数据时出错: {e}")

    def run_command_line(self):
        """运行命令行界面"""
        print("\n命令行模式")
        print("-" * 40)

        if not self.analyzer or self.analyzer.processed_df is None:
            print("错误: 数据未初始化")
            return

        # 显示数据统计
        summary = self.analyzer.get_summary_statistics()
        print(f"产品总数: {summary.get('total_products', 0)}")
        print(f"保险公司数: {summary.get('total_companies', 0)}")

        # 显示产品类型分布
        print("\n产品类型分布:")
        type_dist = summary.get('type_distribution', {})
        for type_name, count in type_dist.items():
            print(f"  {type_name}: {count}")

        # 简单交互
        while True:
            print("\n命令:")
            print("  1. 搜索产品")
            print("  2. 查看产品列表")
            print("  3. 获取推荐")
            print("  4. 退出")

            choice = input("\n请选择 (1-4): ").strip()

            if choice == '1':
                keyword = input("请输入搜索关键词: ").strip()
                if keyword:
                    results = self.analyzer.search_products(keyword)
                    print(f"\n找到 {len(results)} 个产品:")
                    for _, row in results.head(5).iterrows():
                        print(f"  - {row['product_name']} ({row['insurance_company']})")

            elif choice == '2':
                print("\n产品列表 (前10个):")
                for _, row in self.analyzer.processed_df.head(10).iterrows():
                    print(f"  - {row['product_name']} | {row['insurance_company']} | {row['age_range_str']}")

            elif choice == '3':
                print("\n请输入用户信息:")
                try:
                    age = int(input("年龄: "))
                    income = float(input("年收入(万元): "))
                    risk = input("风险偏好(低/中/高): ")
                    ss_type = input("社保类型(城镇职工/城乡居民/无): ")

                    user_profile = {
                        'age': age,
                        'annual_income': income,
                        'risk_tolerance': risk,
                        'social_security_type': ss_type,
                        'expected_retirement_age': 60,
                        'investment_amount': income * 0.5,
                        'location': '全国'
                    }

                    user_id = "cli_user"
                    self.recommender.add_user_profile(user_id, user_profile)
                    result = self.recommender.get_recommendations(user_id, top_n=3)

                    if "recommendations" in result:
                        print(f"\n推荐产品 ({len(result['recommendations'])}个):")
                        for rec in result['recommendations']:
                            print(f"\n  {rec['product_name']}")
                            print(f"    保险公司: {rec['insurance_company']}")
                            print(f"    匹配度: {rec['match_score']}%")
                            print(f"    风险等级: {rec['risk_level']}")
                    else:
                        print(f"错误: {result.get('error', '未知错误')}")

                except ValueError:
                    print("输入错误，请重新输入")

            elif choice == '4':
                print("退出命令行模式")
                break

            else:
                print("无效选择，请重新输入")


def main():
    """主函数"""
    tool = PensionProductTool()

    # 设置工具
    if not tool.setup():
        print("工具初始化失败，请检查数据文件")
        input("按Enter键退出...")
        return

    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        # 命令行模式
        tool.run_command_line()
    else:
        # GUI模式
        if not tool.run_gui():
            print("GUI启动失败")
            input("按Enter键退出...")


if __name__ == "__main__":
    main()