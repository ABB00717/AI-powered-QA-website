const app = Vue.createApp({
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
                const apiResponse = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ prompt: this.prompt })
                })

                const data = await apiResponse.json()

                if (!apiResponse.ok) {
                    throw new Error(`API 錯誤: ${data.error || apiResponse.statusText}`)
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
    },
    template: `
        <div>
            <h1>OpenAI API Vue 示例</h1>
            <p>輸入一個提示，然後點擊 "生成" 按鈕來獲取 AI 生成的回應。</p>
            <textarea v-model="prompt" placeholder="在這裡輸入你的提示..."></textarea>
            <button @click="generateResponse" :disabled="isLoading">{{ buttonText }}</button>
            <div :class="{ 'error': isError }" class="response">{{ response }}</div>
        </div>
    `
})

app.mount('#app')