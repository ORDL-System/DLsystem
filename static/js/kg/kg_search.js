document.addEventListener('DOMContentLoaded', function () {
    async function sendQueryRequest(queryText) {
        const formData = new FormData();
        formData.append('query_text', queryText);

        try {
            const response = await fetch(queryUrl, {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('查询请求出现错误:', error);
            alert('查询请求失败，请稍后再试');
            return null;
        }
    }

    // 使用 Neovis.js 渲染图形
    function renderGraph(cypherQuery) {
        const graphContainer = document.getElementById('neo4j-graph');
        graphContainer.style.display = 'block'; // 显示图形容器

        const config = {
            containerId: "neo4j-graph",
            neo4j: {
                serverUrl: "bolt://localhost:7687", // Neo4j 连接
                serverUser: "neo4j",               // 用户名
                serverPassword: "3080neo4j"        // 密码
            },
            initialCypher: cypherQuery  // Cypher 查询语句
        };

        const viz = new NeoVis.default(config);
        viz.render();
    }

    function submitQuery(event) {
        event.preventDefault();
        const queryText = document.getElementById('query-input').value;

        if (queryText) {
            const queryButton = document.getElementById('query-button');
            queryButton.disabled = true;
            queryButton.textContent = '查询中...';

            sendQueryRequest(queryText)
                .then(data => {
                    queryButton.disabled = false;
                    queryButton.textContent = '查询';

                    const resultContainer = document.getElementById('query-result');
                    resultContainer.innerHTML = ''; // 清空文本结果

                    const graphContainer = document.getElementById('neo4j-graph');
                    graphContainer.style.display = 'none'; // 隐藏图形容器

                    if (data.message) {
                        document.getElementById('message-container').textContent = data.message;
                    }

                    if (data.results) {
                        const results = data.results.join(', ');
                        const queryElement = document.createElement('p');
                        queryElement.textContent = `${data.query}: ${results}`;
                        resultContainer.appendChild(queryElement);
                    }

                    if (data.cypher_query_vs) {
                        renderGraph(data.cypher_query_vs); // 渲染图形
                    }
                })
                .catch(error => {
                    queryButton.disabled = false;
                    queryButton.textContent = '查询';
                    console.error('查询处理错误:', error);
                });
        } else {
            alert('请输入有效的查询内容');
        }
    }

    const queryForm = document.getElementById('query-form');
    queryForm.addEventListener('submit', submitQuery);
});






function showMessage(message) {
  const messageContainer = document.getElementById('message-container');
  messageContainer.textContent = message;
  messageContainer.style.display = 'block';
    }

function hideMessage() {
  const messageContainer = document.getElementById('message-container');
  messageContainer.style.display = 'none';
}