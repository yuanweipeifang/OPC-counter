import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import TesterApp from './TesterApp.vue'

const app = createApp(TesterApp)
app.use(ElementPlus)
app.mount('#app')
