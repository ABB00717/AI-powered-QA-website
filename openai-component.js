const OpenAIComponent = {
    template: `
        <div>
            <h1>OpenAI API Vue 示例</h1>
            <p>輸入一個提示，然後點擊 "生成" 按鈕來獲取 AI 生成的回應。</p>
            <textarea v-model="prompt" placeholder="在這裡輸入你的提示..."></textarea>
            <button @click="generateResponse" :disabled="isLoading">{{ buttonText }}</button>
            <div :class="{ 'error': isError }" class="response">{{ response }}</div>
        </div>
    `,
    data() {
        return {
            prompt: '',
            response: '',
            isLoading: false,
            isError: false
        }
    },
    computed: {
        buttonText() {
            return this.isLoading ? '生成中...' : '生成'
        }
    },
    methods: {
        async generateResponse() {
            this.isLoading = true
            this.isError = false
            this.response = '正在生成回應...'

            try {
                const response = await fetch('https://api.openai.com/v1/chat/completions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer Your-api-key'  // 請替換為你的實際 API 密鑰
                    },
                    body: JSON.stringify({
                        model: "gpt-3.5-turbo",
                        messages: [
                            {role: "system", content: "You are a helpful assistant."},
                            {role: "user", content: this.prompt}
                        ]
                    })
                })

                const data = await response.json()

                if (!response.ok) {
                    throw new Error(`API 錯誤: ${data.error?.message || response.statusText}`)
                }

                if (data.choices && data.choices.length > 0 && data.choices[0].message) {
                    this.response = data.choices[0].message.content
                } else {
                    throw new Error('API 回應格式不符合預期')
                }
            } catch (error) {
                this.response = '發生錯誤：' + error.message
                this.isError = true
                console.error('錯誤詳情：', error)
            } finally {
                this.isLoading = false
            }
        }
    }
}

// 添加樣式
const style = document.createElement('style')
style.textContent = `
    body {
        font-family: Arial, sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        line-height: 1.6;
    }
    textarea {
        width: 100%;
        height: 100px;
        margin-bottom: 10px;
    }
    button {
        padding: 10px 20px;
        background-color: #007bff;
        color: white;
        border: none;
        cursor: pointer;
    }
    button:hover:not(:disabled) {
        background-color: #0056b3;
    }
    button:disabled {
        background-color: #cccccc;
        cursor: not-allowed;
    }
    .response {
        margin-top: 20px;
        border: 1px solid #ddd;
        padding: 10px;
        white-space: pre-wrap;
    }
    .error {
        color: red;
    }
`
document.head.appendChild(style)