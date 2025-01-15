from flask import Blueprint, render_template, request, jsonify
from apps.neo4j_helper import start_neo4j, perform_query
from utils.kg.response_utils import handle_error_response
from utils.kg.nlp_utils import process_question_with_sliding_window
from py2neo import Graph

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
            entity = converted_query[2]
            relation = converted_query[3]

            if cypher_query_vs:
                graph = Graph("bolt://localhost:7687", auth=("neo4j", "3080neo4j"))
                vs_results = graph.run(cypher_query_vs)
                nodes = []
                relationships = []

                for record in vs_results:
                    # 添加节点
                    for node in [record['m'], record['n']]:
                        if {'label': list(node.labels)[0], 'name': node['name']} not in nodes:
                            nodes.append({
                                'label': list(node.labels)[0],  # 获取节点标签
                                'name': node['name']           # 假设每个节点都有 'name' 属性
                            })

                    # 添加关系
                    relationship = record['r']
                    relationships.append({
                        'type': relationship.__class__.__name__  # 获取关系类型
                    })

                return jsonify({
                    'results': results,  # 返回文本结果
                    'query': query_text,  # 用户输入的查询
                    'cypher_query_vs': cypher_query_vs,
                    'entity': entity,
                    'relation': relation,
                    'queryResults': {
                        'nodes': nodes,
                        'relationships': relationships
                    }
                })
        return handle_error_response("查询执行过程出现问题，请检查输入或联系管理员。")
    return handle_error_response("请输入有效的查询问题")
