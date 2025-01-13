document.addEventListener('DOMContentLoaded', function () {
    // 发送查询请求的函数
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

    function submitQuery(event) {
        event.preventDefault();  // 阻止表单的默认提交
        const queryText = document.getElementById('query-input').value;

        if (queryText) {
            const queryButton = document.getElementById('query-button');
            queryButton.disabled = true;
            queryButton.textContent = '查询中...';

            sendQueryRequest(queryText)
            .then(data => {
                queryButton.disabled = false;
                queryButton.textContent = '查询';

                if (data.message) {
                    document.getElementById('message-container').textContent = data.message;
                }
                if (data.results) {
                    const resultContainer = document.getElementById('result-container');
                    resultContainer.innerHTML = ''; // 清空结果
                    data.results.forEach(record => {
                        const p = document.createElement('p');
                        p.textContent = record;
                        resultContainer.appendChild(p);
                    });
                }
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