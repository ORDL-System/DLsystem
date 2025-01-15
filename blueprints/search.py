from flask import Blueprint, render_template, request, jsonify 
from apps.neo4j_helper import start_neo4j, perform_query
from utils.kg.response_utils import  handle_error_response
from utils.kg.nlp_utils import process_question_with_sliding_window

# 创建名为'search'的蓝图，设置前缀为'/kg'
bp = Blueprint('search', __name__, url_prefix='/kg')


@bp.route('/query_page')
def query_page():
    start_neo4j()  # 初始化 Neo4j 连接或其他必要的操作
    return render_template('templates_kg/search.html')


@bp.route('/kg_search', methods=['POST'])
def kg_search():
    query_text = request.form.get('query_text')
    if query_text:
        results = perform_query(query_text)
        if results is not None:
            converted_query = process_question_with_sliding_window(query_text)
            cypher_query_vs = converted_query[1]
            
            return jsonify({
                'results': results,  # 返回文本结果
                'query': query_text,  # 用户输入的查询
                'cypher_query_vs': cypher_query_vs,
                'message': '查询成功'
            })
        return handle_error_response("查询执行过程出现问题，请检查输入或联系管理员。")
    return handle_error_response("请输入有效的查询问题")

