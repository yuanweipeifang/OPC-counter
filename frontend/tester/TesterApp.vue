<template>
  <div class="page">
    <header class="header">
      <h1>本地联调测试端</h1>
      <p>用于无公网场景下模拟比赛测试流程（第三端）</p>
      <div class="quick-links">
        <a href="/" target="_blank" rel="noopener noreferrer">打开用户端</a>
        <a href="/admin/" target="_blank" rel="noopener noreferrer">打开管理端</a>
      </div>
    </header>

    <main class="main">
      <section class="card">
        <h2>测试配置</h2>
        <el-form label-width="130px">
          <el-form-item label="回调基础地址">
            <el-input v-model="form.callback_base_url" placeholder="http://localhost:8000" />
          </el-form-item>
          <el-form-item label="测试设备编号">
            <el-input v-model="form.device_code" placeholder="91120149" />
          </el-form-item>
          <el-form-item label="测试用户ID">
            <el-input v-model="form.user_id" placeholder="u_local_001" />
          </el-form-item>
          <el-form-item label="测试手机号">
            <el-input v-model="form.phone" placeholder="13800138000" />
          </el-form-item>
        </el-form>
        <div class="actions">
          <el-button type="primary" @click="saveConfig">保存配置</el-button>
          <el-button @click="loadStatus">刷新状态</el-button>
        </div>
      </section>

      <section class="card">
        <h2>比赛回调地址（可直接提供）</h2>
        <div class="kv"><span>门状态推送</span><code>{{ callbackUrls.door_status }}</code></div>
        <div class="kv"><span>订单完结</span><code>{{ callbackUrls.settlement }}</code></div>
        <div class="kv"><span>补扣推送</span><code>{{ callbackUrls.retry_settlement }}</code></div>
        <div class="kv"><span>退款地址</span><code>{{ callbackUrls.refund }}</code></div>
      </section>

      <section class="card">
        <h2>本地联调动作</h2>
        <div class="actions wrap">
          <el-button type="success" @click="trigger('door-status')">触发门状态回调</el-button>
          <el-button type="success" @click="trigger('settlement')">触发订单完结回调</el-button>
          <el-button type="warning" @click="trigger('retry-settlement')">触发补扣回调</el-button>
          <el-button type="danger" @click="trigger('refund')">触发退款回调</el-button>
          <el-button type="primary" plain @click="simulateFlow">模拟开门全流程</el-button>
        </div>
      </section>

      <section class="card">
        <h2>联调日志</h2>
        <div class="actions">
          <el-button @click="loadLogs">刷新日志</el-button>
          <el-button type="danger" plain @click="clearLogs">清空日志</el-button>
        </div>
        <pre class="logs">{{ logsText }}</pre>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_BASE = '/api'

const form = ref({
  callback_base_url: 'http://localhost:8000',
  device_code: '91120149',
  user_id: 'u_local_001',
  phone: '13800138000'
})

const status = ref(null)
const logs = ref([])

const callbackUrls = computed(() => {
  return status.value?.callbacks || {
    door_status: '-',
    settlement: '-',
    retry_settlement: '-',
    refund: '-'
  }
})

const logsText = computed(() => {
  if (!logs.value.length) return '暂无日志'
  return JSON.stringify(logs.value, null, 2)
})

const loadStatus = async () => {
  const res = await axios.get(`${API_BASE}/local-test/status`)
  status.value = res.data
  form.value.callback_base_url = res.data.callback_base_url || form.value.callback_base_url
  form.value.device_code = res.data.device_code || form.value.device_code
}

const saveConfig = async () => {
  await axios.post(`${API_BASE}/local-test/config`, form.value)
  ElMessage.success('配置已保存')
  await loadStatus()
}

const trigger = async (kind) => {
  const res = await axios.post(`${API_BASE}/local-test/trigger/${kind}`, {})
  ElMessage.success(`${kind} 已触发`)
  logs.value.unshift({
    timestamp: new Date().toISOString(),
    action: `manual-${kind}`,
    response: res.data
  })
}

const simulateFlow = async () => {
  const res = await axios.post(`${API_BASE}/local-test/simulate-open-flow`, {})
  ElMessage.success('全流程模拟已触发')
  logs.value.unshift({
    timestamp: new Date().toISOString(),
    action: 'simulate-open-flow',
    response: res.data
  })
}

const loadLogs = async () => {
  const res = await axios.get(`${API_BASE}/local-test/logs`)
  logs.value = res.data.logs || []
}

const clearLogs = async () => {
  await axios.delete(`${API_BASE}/local-test/logs`)
  logs.value = []
  ElMessage.success('日志已清空')
}

onMounted(async () => {
  try {
    await loadStatus()
    await loadLogs()
  } catch (err) {
    ElMessage.error(err?.response?.data?.detail || '初始化失败，请检查后端是否启动')
  }
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.page {
  min-height: 100vh;
  font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #f5f7fb;
  color: #1f2937;
}

.header {
  background: linear-gradient(135deg, #2563eb, #14b8a6);
  color: #fff;
  padding: 24px;
}

.header h1 {
  margin: 0;
  font-size: 28px;
}

.header p {
  margin: 8px 0 0;
  opacity: 0.95;
}

.quick-links {
  display: flex;
  gap: 12px;
  margin-top: 14px;
}

.quick-links a {
  color: #fff;
  text-decoration: none;
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 999px;
  padding: 6px 12px;
}

.main {
  max-width: 980px;
  margin: 18px auto;
  padding: 0 12px 28px;
  display: grid;
  gap: 14px;
}

.card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06);
}

.card h2 {
  margin: 0 0 14px;
  font-size: 18px;
}

.actions {
  display: flex;
  gap: 10px;
}

.actions.wrap {
  flex-wrap: wrap;
}

.kv {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
}

code {
  background: #f3f4f6;
  padding: 6px 8px;
  border-radius: 6px;
  word-break: break-all;
}

.logs {
  margin: 12px 0 0;
  background: #0f172a;
  color: #d1fae5;
  border-radius: 10px;
  padding: 12px;
  min-height: 160px;
  max-height: 380px;
  overflow: auto;
}
</style>
