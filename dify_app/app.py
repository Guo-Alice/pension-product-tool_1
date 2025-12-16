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
    """初始化系统（适配Vercel/本地，指向data1/insurance.xlsx）"""
    global analyzer, recommender

    try:
        # ========== 核心：适配Vercel/本地的Excel路径 ==========
        if "VERCEL" in os.environ:  # 识别Vercel部署环境
            # Vercel项目根路径固定为 /vercel/path0/
            data_path = "/vercel/path0/data1/insurance.xlsx"
        else:  # 本地运行环境
            # 拼接本地路径：当前文件(dify_app) → 上级目录 → data1 → insurance.xlsx
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)  # 上级目录（项目根）
            data_path = os.path.join(project_root, "data1", "insurance.xlsx")
        
        # 打印关键日志（Vercel Runtime Logs可查）
        print(f"📌 Excel文件路径：{data_path}")
        print(f"📌 文件是否存在：{os.path.exists(data_path)}")

        # 验证文件存在性
        if not os.path.exists(data_path):
            print(f"❌ Excel文件不存在！路径：{data_path}")
            return False

        # 加载数据（原有逻辑）
        analyzer = PensionProductAnalyzer(data_path)
        analyzer.process_data()

        # 初始化推荐系统
        recommender = PensionProductRecommender(analyzer)

        print("✅ 系统初始化完成（Excel加载成功）")
        return True
    
    except Exception as e:
        print(f"❌ 系统初始化失败：{str(e)}")
        analyzer = None
        recommender = None
        return False


# ========== 关键修改：全局调用初始化（Vercel启动时自动执行） ==========
init_system()


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
        # 先检查系统是否初始化成功
        if analyzer is None or recommender is None:
            return jsonify({'error': '系统未初始化（Excel加载失败）'}), 500

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
        if analyzer is None or analyzer.processed_df is None:
            return jsonify({'error': 'Data not loaded（Excel未加载）'}), 400

        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search', '')

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
        if analyzer is None:
            return jsonify({'error': 'Data not loaded（Excel未加载）'}), 400
            
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
        if recommender is None:
            return jsonify({'error': '系统未初始化（Excel未加载）'}), 500

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
        if recommender is None:
            return jsonify({'error': '系统未初始化（Excel未加载）'}), 500

        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        advice = recommender.get_personalized_advice(user_id)
        return jsonify(advice)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== 仅本地运行时执行（Vercel部署不触发） ==========
if __name__ == '__main__':
    print("📌 本地运行模式 - 系统已初始化")
    # 启动本地服务
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
