# dify_app/app.py
"""
Dify平台适配的主应用
"""
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import os

# 导入您现有的处理逻辑
from data_processor import PensionProductAnalyzer
from recommender import PensionProductRecommender

app = Flask(__name__)

# 全局变量
analyzer = None
recommender = None


def init_system():
    """初始化系统"""
    global analyzer, recommender

    # 加载数据
    data_path = os.getenv('DATA_PATH', '../data1/养老保险.xlsx')
    analyzer = PensionProductAnalyzer(data_path)
    analyzer.process_data()

    # 初始化推荐系统
    recommender = PensionProductRecommender(analyzer)

    return True


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0',
        'data_loaded': analyzer is not None
    })


@app.route('/analyze', methods=['POST'])
def analyze_user():
    """分析用户需求并推荐产品"""
    try:
        data = request.json

        # 验证必要参数
        required_fields = ['age', 'annual_income', 'risk_tolerance', 'social_security_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # 创建用户画像
        user_profile = {
            'age': int(data['age']),
            'annual_income': float(data['annual_income']),
            'risk_tolerance': data['risk_tolerance'],
            'social_security_type': data['social_security_type'],
            'expected_retirement_age': data.get('expected_retirement_age', 60),
            'investment_amount': data.get('investment_amount', data['annual_income'] * 0.5),
            'location': data.get('location', '全国'),
            'investment_horizon': data.get('investment_horizon', '长期')
        }

        # 添加用户到推荐系统
        user_id = data.get('user_id', f'user_{hash(str(user_profile))}')
        recommender.add_user_profile(user_id, user_profile)

        # 获取推荐结果
        filter_criteria = {}
        if 'insurance_type' in data:
            filter_criteria['insurance_type'] = data['insurance_type']

        result = recommender.get_recommendations(
            user_id=user_id,
            top_n=data.get('top_n', 5),
            filter_criteria=filter_criteria
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/products', methods=['GET'])
def get_products():
    """获取产品列表"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search', '')

        if analyzer is None or analyzer.processed_df is None:
            return jsonify({'error': 'Data not loaded'}), 400

        df = analyzer.processed_df

        # 搜索过滤
        if search:
            mask = (df['product_name'].str.contains(search, case=False) |
                    df['insurance_company'].str.contains(search, case=False) |
                    df['insurance_type'].str.contains(search, case=False))
            df = df[mask]

        # 分页
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
        return jsonify({'error': str(e)}), 500


@app.route('/product/<product_id>', methods=['GET'])
def get_product_detail(product_id):
    """获取产品详情"""
    try:
        product = analyzer.get_product_details(product_id)
        if product:
            return jsonify(product)
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/compare', methods=['POST'])
def compare_products():
    """比较多个产品"""
    try:
        data = request.json
        product_ids = data.get('product_ids', [])

        if len(product_ids) < 2:
            return jsonify({'error': 'At least 2 products required for comparison'}), 400

        comparison = recommender.generate_comparison_table(product_ids)

        return jsonify({
            'product_ids': product_ids,
            'comparison': comparison,
            'count': len(comparison)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/advice', methods=['POST'])
def get_personal_advice():
    """获取个性化建议"""
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        advice = recommender.get_personalized_advice(user_id)
        return jsonify(advice)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # 初始化系统
    init_system()
    print("系统初始化完成")

    # 启动服务
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
