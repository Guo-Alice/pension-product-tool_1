"""
Dify平台适配的主应用（适配Vercel Serverless懒加载初始化）
"""
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import os

# 导入自定义处理模块（兼容导入失败场景）
try:
    from data_processor import PensionProductAnalyzer
    from recommender import PensionProductRecommender
except ImportError as e:
    print(f"⚠️ 自定义模块导入失败：{str(e)}")
    PensionProductAnalyzer = None
    PensionProductRecommender = None

# 初始化Flask应用
app = Flask(__name__)

# 全局变量（初始为None，懒加载初始化）
analyzer = None
recommender = None


def init_system():
    """
    初始化系统（适配Vercel/本地环境）
    仅在第一次请求时执行，避免Serverless文件系统未挂载导致的读取失败
    """
    global analyzer, recommender

    # 优先读取Vercel环境变量，兜底使用适配路径
    data_path = os.getenv('DATA_PATH')
    if not data_path:
        if "VERCEL" in os.environ:  # Vercel Serverless环境
            data_path = "/vercel/path0/data1/insurance.xlsx"
        else:  # 本地运行环境
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)  # 项目根目录
            data_path = os.path.join(project_root, "data1", "insurance.xlsx")

    try:
        # 1. 验证自定义模块是否导入成功
        if not PensionProductAnalyzer or not PensionProductRecommender:
            raise ImportError("核心模块缺失：data_processor/recommender.py 未找到")

        # 2. 验证Excel文件是否存在（此时文件系统已挂载）
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Excel文件不存在！路径：{data_path}")

        # 3. 初始化数据分析器（强制指定openpyxl引擎读取xlsx）
        analyzer = PensionProductAnalyzer(data_path)
        analyzer.process_data()

        # 4. 初始化推荐系统
        recommender = PensionProductRecommender(analyzer)

        print(f"✅ 系统初始化成功！Excel路径：{data_path}")
        return True

    except Exception as e:
        print(f"❌ 系统初始化失败：{str(e)}")
        analyzer = None
        recommender = None
        return False


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口（核心：第一次请求时懒加载初始化）"""
    global analyzer, recommender

    # 懒加载：未初始化则执行初始化
    if analyzer is None or recommender is None:
        init_system()

    # 构建当前环境的Excel路径（用于返回状态）
    if "VERCEL" in os.environ:
        data_path = "/vercel/path0/data1/insurance.xlsx"
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        data_path = os.path.join(project_root, "data1", "insurance.xlsx")

    # 返回详细状态（便于排查）
    return jsonify({
        'status': 'healthy',
        'version': '1.0',
        'data_loaded': analyzer is not None,
        'excel_path': data_path,
        'excel_exists': os.path.exists(data_path),
        'module_loaded': PensionProductAnalyzer is not None
    })


@app.route('/analyze', methods=['POST'])
def analyze_user():
    """分析用户需求并推荐产品（懒加载初始化）"""
    global analyzer, recommender

    # 懒加载：未初始化则执行初始化
    if analyzer is None or recommender is None:
        init_system()

    try:
        # 前置校验：系统是否初始化成功
        if analyzer is None or recommender is None:
            return jsonify({'error': '系统初始化失败（Excel/模块加载异常）'}), 500

        # 校验请求体
        data = request.json
        if not data:
            return jsonify({'error': '请求体不能为空（需JSON格式）'}), 400

        # 验证必要参数
        required_fields = ['age', 'annual_income', 'risk_tolerance', 'social_security_type']
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return jsonify({'error': f'缺失必要参数：{", ".join(missing_fields)}'}), 400

        # 参数类型转换（避免类型错误）
        try:
            user_profile = {
                'age': int(data['age']),
                'annual_income': float(data['annual_income']),
                'risk_tolerance': data['risk_tolerance'],
                'social_security_type': data['social_security_type'],
                'expected_retirement_age': int(data.get('expected_retirement_age', 60)),
                'investment_amount': float(data.get('investment_amount', data['annual_income'] * 0.5)),
                'location': data.get('location', '全国'),
                'investment_horizon': data.get('investment_horizon', '长期')
            }
        except (ValueError, TypeError) as e:
            return jsonify({'error': f'参数类型错误：{str(e)}'}), 400

        # 生成用户ID并添加画像
        user_id = data.get('user_id', f'user_{hash(str(user_profile))}')
        recommender.add_user_profile(user_id, user_profile)

        # 构建过滤条件
        filter_criteria = {}
        if 'insurance_type' in data:
            filter_criteria['insurance_type'] = data['insurance_type']

        # 获取推荐结果
        result = recommender.get_recommendations(
            user_id=user_id,
            top_n=int(data.get('top_n', 5)),
            filter_criteria=filter_criteria
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'服务器内部错误：{str(e)}'}), 500


@app.route('/products', methods=['GET'])
def get_products():
    """获取产品列表（懒加载初始化）"""
    global analyzer, recommender

    # 懒加载：未初始化则执行初始化
    if analyzer is None or recommender is None:
        init_system()

    try:
        # 前置校验：数据是否加载成功
        if analyzer is None or getattr(analyzer, 'processed_df', None) is None:
            return jsonify({'error': '数据未加载（Excel解析/处理失败）'}), 400

        # 分页&搜索参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search', '')

        # 搜索过滤（兼容空值）
        df = analyzer.processed_df.copy()
        if search:
            mask = (
                df['product_name'].str.contains(search, case=False, na=False) |
                df['insurance_company'].str.contains(search, case=False, na=False) |
                df['insurance_type'].str.contains(search, case=False, na=False)
            )
            df = df[mask]

        # 分页处理
        total = len(df)
        start = (page - 1) * limit
        end = start + limit
        products = df.iloc[start:end].to_dict('records')

        return jsonify({
            'page': page,
            'limit': limit,
            'total': total,
            'total_pages': (total + limit - 1) // limit,
            'products': products
        })

    except Exception as e:
        return jsonify({'error': f'服务器内部错误：{str(e)}'}), 500


@app.route('/product/<product_id>', methods=['GET'])
def get_product_detail(product_id):
    """获取产品详情（懒加载初始化）"""
    global analyzer, recommender

    # 懒加载：未初始化则执行初始化
    if analyzer is None or recommender is None:
        init_system()

    try:
        # 前置校验：数据是否加载成功
        if analyzer is None:
            return jsonify({'error': '数据未加载（Excel/模块异常）'}), 400

        # 获取产品详情
        product = analyzer.get_product_details(product_id)
        if product:
            return jsonify(product)
        else:
            return jsonify({'error': '产品不存在'}), 404

    except Exception as e:
        return jsonify({'error': f'服务器内部错误：{str(e)}'}), 500


@app.route('/compare', methods=['POST'])
def compare_products():
    """比较多个产品（懒加载初始化）"""
    global analyzer, recommender

    # 懒加载：未初始化则执行初始化
    if analyzer is None or recommender is None:
        init_system()

    try:
        # 前置校验：系统是否初始化成功
        if recommender is None:
            return jsonify({'error': '系统初始化失败（Excel/模块加载异常）'}), 500

        # 校验请求体
        data = request.json
        if not data or 'product_ids' not in data:
            return jsonify({'error': '请求体必须包含product_ids字段'}), 400

        # 校验产品数量
        product_ids = data['product_ids']
        if len(product_ids) < 2:
            return jsonify({'error': '至少需要2个产品进行对比'}), 400

        # 生成对比结果
        comparison = recommender.generate_comparison_table(product_ids)
        return jsonify({
            'product_ids': product_ids,
            'comparison': comparison,
            'count': len(comparison)
        })

    except Exception as e:
        return jsonify({'error': f'服务器内部错误：{str(e)}'}), 500


@app.route('/advice', methods=['POST'])
def get_personal_advice():
    """获取个性化建议（懒加载初始化）"""
    global analyzer, recommender

    # 懒加载：未初始化则执行初始化
    if analyzer is None or recommender is None:
        init_system()

    try:
        # 前置校验：系统是否初始化成功
        if recommender is None:
            return jsonify({'error': '系统初始化失败（Excel/模块加载异常）'}), 500

        # 校验请求体
        data = request.json
        if not data or 'user_id' not in data:
            return jsonify({'error': '请求体必须包含user_id字段'}), 400

        # 获取个性化建议
        advice = recommender.get_personalized_advice(data['user_id'])
        return jsonify(advice)

    except Exception as e:
        return jsonify({'error': f'服务器内部错误：{str(e)}'}), 500


# 本地运行入口（Vercel部署时不会触发）
if __name__ == '__main__':
    # 本地运行时主动初始化（无需懒加载）
    init_system()
    # 启动本地服务
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
