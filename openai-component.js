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
                const response = await fetch('http://localhost:5000/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ prompt: this.prompt })
                })

                const data = await response.json()

                if (!response.ok) {
                    throw new Error(`API 錯誤: ${data.error || response.statusText}`)
                }

                this.response = data.response
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

// 添加樣式（保持不變）
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