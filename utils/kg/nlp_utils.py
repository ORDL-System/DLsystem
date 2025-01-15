from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

 # 初始化 BERT 模型
tokenizer = AutoTokenizer.from_pretrained("/home/zhanggu/MyDoc/test/kg_model/bert-base-chinese")
model = AutoModel.from_pretrained("/home/zhanggu/MyDoc/test/kg_model/bert-base-chinese")


# 示例实体和关系库
entity_set = {"齿轮",  "检测工具", "传动比", "离合器", "油位", "轴承", "发动机"}
relation_set = {"材质", "检测工具", "功率参数", "寿命", "故障类型"}


# 1. 搜索匹配实体
def search_entity_or_relation(question, entity_or_relation_set):
    """
    在问题中精确匹配实体或关系。
    :param question: 用户输入的问题
    :param entity_or_relation_set: 实体或关系库
    :return: 匹配到的结果列表
    """
    matched = [item for item in entity_or_relation_set if item in question]
    return matched

# 滑动窗口分割实现
def sliding_window_split(text, min_len=2, max_len=4):
    """
    滑动窗口分割输入文本，生成长度在 [min_len, max_len] 范围内的所有片段。
    :param text: 输入文本
    :param min_len: 最小片段长度
    :param max_len: 最大片段长度
    :return: 分割后的片段列表
    """
    n = len(text)
    fragments = []
    for window_size in range(min_len, max_len + 1):  # 窗口长度范围
        for i in range(n - window_size + 1):  # 滑动窗口起始位置
            fragments.append(text[i:i + window_size])
    return fragments



# 更新近义匹配机制
def near_synonym_match_with_highest_similarity(question, entity_or_relation_set):
    """
    根据滑动窗口分割和近义匹配，返回与输入最相似的实体或关系。
    :param question: 用户输入的问题
    :param entity_or_relation_set: 实体或关系库
    :return: 相似度最高的匹配项（如果无匹配则返回空列表）
    """

    # 滑动窗口分割
    fragments = sliding_window_split(question)

    def encode_text(text):
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        outputs = model(**inputs)
        return outputs.last_hidden_state.mean(dim=1)

    # 编码所有片段
    fragment_vectors = [encode_text(fragment) for fragment in fragments]

    # 编码库中的所有实体或关系
    results = []
    for item in entity_or_relation_set:
        item_vec = encode_text(item)
        for fragment, fragment_vec in zip(fragments, fragment_vectors):
            sim = cosine_similarity(fragment_vec.detach().numpy(), item_vec.detach().numpy())[0][0]
            results.append((fragment, item, sim))  # 保存片段、实体或关系、相似度

    # 按相似度排序并返回最高匹配
    results = sorted(results, key=lambda x: x[2], reverse=True)
    
    return results[0] if results else None


# 整体流程
def process_question_with_sliding_window(question):
    """
    根据用户问题生成 Cypher 查询语句（包含滑动窗口和相似度排序）。
    :param question: 用户输入的问题
    :return: 生成的 Cypher 查询语句或无结果提示
    """
    # 1. 匹配实体
    entities = search_entity_or_relation(question, entity_set)
    if not entities:
        match = near_synonym_match_with_highest_similarity(question, entity_set)
        if match:
            entities = [match[1]]  # 取相似度最高的实体
    if not entities:
        return "无查询结果：无法匹配到实体。"

    # 2. 匹配关系
    relations = search_entity_or_relation(question, relation_set)
    if not relations:
        match = near_synonym_match_with_highest_similarity(question, relation_set)
        if match:
            relations = [match[1]]  # 取相似度最高的关系
    if not relations:
        return "无查询结果：无法匹配到关系。"

    # 3. 生成 Cypher 查询语句
    entity = entities[0]  # 假设只取第一个匹配实体
    relation = relations[0]  # 假设只取第一个匹配关系
    cypher_query = f"MATCH (m:{entity})-[r:{relation}]->(n) RETURN n.name"
    cypher_query_vs = f"MATCH (m:{entity})-[r:{relation}]->(n) RETURN m,r,n"
    return [cypher_query,cypher_query_vs]

