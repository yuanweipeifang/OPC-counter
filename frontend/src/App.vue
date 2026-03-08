<template>
  <div class="app-container">
    <!-- 登录页 -->
    <div v-if="!isLoggedIn">
      <div class="header">
        <h1><span class="heart-icon">❤️</span> 爱心柜</h1>
        <p>为爱续航，让温暖传递</p>
      </div>
      
      <div class="card">
        <div class="input-group">
          <label>📱 手机号</label>
          <input type="tel" v-model="loginForm.phone" placeholder="请输入手机号" maxlength="11">
        </div>
        
        <div class="input-group">
          <label>🔐 验证码</label>
          <div class="otp-row">
            <input type="text" v-model="loginForm.otp" placeholder="请输入验证码" class="otp-input">
            <button @click="requestOtp" :disabled="otpCountdown > 0" class="btn otp-btn">
              {{ otpCountdown > 0 ? otpCountdown + 's' : '获取验证码' }}
            </button>
          </div>
        </div>
        
        <button class="btn btn-primary" @click="login">🚀 立即登录</button>
        
        <p class="tip">测试验证码: <strong>123456</strong></p>
      </div>
      
      <div class="card">
        <div class="section-title">📍 附近柜机</div>
        <div v-for="m in machines" :key="m.id" class="machine-card" @click="selectMachine(m)">
          <div class="machine-info">
            <h3>🏪 {{ m.name }}</h3>
            <p>{{ m.location }}</p>
          </div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="machine-status" :class="m.status"></span>
            <span class="status-text">{{ m.status === 'online' ? '在线' : '离线' }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 用户首页 -->
    <div v-else>
      <div class="header">
        <h1><span class="heart-icon">❤️</span> 爱心柜</h1>
        <p>欢迎回来, {{ userInfo.name }}</p>
        <div class="user-badge">
          <span>🎭</span>
          <span>{{ roleText }}</span>
        </div>
      </div>
      
      <!-- 特殊群体界面 -->
      <div v-if="userInfo.role === 'special_group'">
        <div class="card card-stats">
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ userInfo.daily_limit - userInfo.used_today }}</div>
              <div class="stat-label">今日剩余次数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ userInfo.daily_limit }}</div>
              <div class="stat-label">每日限额</div>
            </div>
          </div>
        </div>
        
        <div class="quick-actions">
          <div class="quick-action" @click="activeTab = 'machines'">
            <div class="quick-action-icon">📦</div>
            <div class="quick-action-label">领取物资</div>
          </div>
          <div class="quick-action" @click="activeTab = 'pickups'" style="background: var(--gradient-blue);">
            <div class="quick-action-icon">📋</div>
            <div class="quick-action-label">领取记录</div>
          </div>
        </div>
        
        <div class="tabs">
          <div :class="['tab', activeTab === 'pickups' ? 'active' : '']" @click="activeTab = 'pickups'">📝 我的领取</div>
          <div :class="['tab', activeTab === 'machines' ? 'active' : '']" @click="activeTab = 'machines'">🏪 领取物资</div>
        </div>
        
        <div v-if="activeTab === 'pickups'" class="card">
          <div class="section-title">📋 领取记录</div>
          <div v-for="p in myPickups" :key="p.id" class="list-item">
            <div>
              <div class="item-name">{{ p.item_name }}</div>
              <div class="item-time">{{ formatDate(p.pickup_time) }}</div>
            </div>
            <span :class="['status-tag', p.is_compliant ? 'status-active' : 'status-expired']">
              {{ p.is_compliant ? '✅ 合规' : '⚠️ 违规' }}
            </span>
          </div>
          <p v-if="myPickups.length === 0" class="empty-tip">暂无领取记录</p>
        </div>
        
        <div v-if="activeTab === 'machines'" class="card">
          <div class="section-title">🏪 选择柜机</div>
          <div v-for="m in machines" :key="m.id" class="machine-card" @click="openMachine(m)">
            <div class="machine-info">
              <h3>{{ m.name }}</h3>
              <p>{{ m.location }}</p>
            </div>
            <button class="btn btn-primary btn-sm">🚪 开门</button>
          </div>
        </div>
        
        <div class="card">
          <div class="section-title">🤝 志愿者代领</div>
          <div v-if="!userInfo.volunteer_phone">
            <div class="input-group">
              <label>志愿者手机号</label>
              <input type="tel" v-model="volunteerPhone" placeholder="请输入志愿者手机号">
            </div>
            <button class="btn btn-success" @click="bindVolunteer">✨ 绑定志愿者</button>
          </div>
          <div v-else class="bind-success">
            <div class="bind-icon">🤝</div>
            <p class="bind-label">已绑定志愿者</p>
            <p class="bind-phone">{{ userInfo.volunteer_phone }}</p>
            <button class="btn btn-outline" @click="unbindVolunteer">解除绑定</button>
          </div>
        </div>
      </div>
      
      <!-- 商户界面 -->
      <div v-else-if="userInfo.role === 'merchant'">
        <div class="quick-actions">
          <div class="quick-action" @click="activeTab = 'new'" style="background: var(--gradient-blue);">
            <div class="quick-action-icon">➕</div>
            <div class="quick-action-label">新增投放</div>
          </div>
          <div class="quick-action" @click="activeTab = 'donations'" style="background: var(--gradient);">
            <div class="quick-action-icon">📋</div>
            <div class="quick-action-label">我的投放</div>
          </div>
        </div>
        
        <div v-if="activeTab === 'donations'" class="card">
          <div class="section-title">🎁 投放记录</div>
          <div v-for="d in myDonations" :key="d.id" class="list-item">
            <div>
              <div class="item-name">{{ d.item_name }}</div>
              <div class="item-time">数量: {{ d.quantity }} | 截止: {{ formatDate(d.expiry_time) }}</div>
            </div>
            <span :class="['status-tag', 
              d.status === 'active' ? 'status-active' : 
              d.status === 'expired' ? 'status-expired' : 'status-pending']">
              {{ donationStatusText(d.status) }}
            </span>
          </div>
          <p v-if="myDonations.length === 0" class="empty-tip">暂无投放记录</p>
        </div>
        
        <div v-if="activeTab === 'new'" class="card">
          <div class="section-title">➕ 新增投放</div>
          
          <div class="input-group">
            <label>选择柜机</label>
            <select v-model="donationForm.machine_id">
              <option value="">请选择柜机</option>
              <option v-for="m in machines" :key="m.id" :value="m.id">{{ m.name }}</option>
            </select>
          </div>
          
          <div class="input-group">
            <label>商品名称</label>
            <input type="text" v-model="donationForm.item_name" placeholder="请输入商品名称">
          </div>
          
          <div class="input-group">
            <label>商品数量</label>
            <input type="number" v-model="donationForm.quantity" placeholder="请输入数量">
          </div>
          
          <div class="input-group">
            <label>领用截止天数</label>
            <input type="number" v-model="donationForm.expiry_days" placeholder="默认7天" value="7">
          </div>
          
          <button class="btn btn-success" @click="createDonation">✨ 确认投放</button>
        </div>
      </div>
      
      <div v-else class="card">
        <div class="empty-state">
          <div class="empty-icon">🔒</div>
          <p>请联系管理员分配角色</p>
        </div>
      </div>
      
      <div class="footer">
        <button class="btn btn-outline" @click="logout">🚪 退出登录</button>
      </div>
    </div>
    
    <!-- 开门确认弹窗 -->
    <div v-if="showOpenModal" class="modal-overlay" @click.self="showOpenModal = false">
      <div class="modal">
        <div class="modal-icon">🚪</div>
        <h3>确认开门</h3>
        <p class="modal-text">柜机: <strong>{{ selectedMachine?.name }}</strong></p>
        <button class="btn btn-primary" @click="confirmOpen" :disabled="opening">
          {{ opening ? '开门中...' : '✨ 确认开门' }}
        </button>
        <button class="btn btn-outline" @click="showOpenModal = false">取消</button>
      </div>
    </div>
    
    <!-- 消息提示 -->
    <div v-if="message" class="message-toast">{{ message }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const API_BASE = '/api'

// 状态
const isLoggedIn = ref(false)
const userInfo = ref(null)
const token = ref(localStorage.getItem('token') || '')
const activeTab = ref('machines')
const message = ref('')

// 表单
const loginForm = ref({ phone: '', otp: '' })
const volunteerPhone = ref('')
const donationForm = ref({ machine_id: '', item_name: '', quantity: 1, expiry_days: 7 })
const machines = ref([])
const myPickups = ref([])
const myDonations = ref([])

// UI状态
const otpCountdown = ref(0)
const showOpenModal = ref(false)
const selectedMachine = ref(null)
const opening = ref(false)

const roleText = computed(() => {
  const map = { special_group: '特殊群体', merchant: '爱心商户' }
  return map[userInfo.value?.role] || '用户'
})

const donationStatusText = (status) => {
  const map = { active: '进行中', expired: '已过期', all_claimed: '已领完' }
  return map[status] || status
}

const showMessage = (msg) => {
  message.value = msg
  setTimeout(() => message.value = '', 3000)
}

const fetchMachines = async () => {
  try {
    const res = await axios.get(`${API_BASE}/admin/machines`)
    machines.value = res.data.machines || []
  } catch (e) {
    console.error(e)
  }
}

const requestOtp = async () => {
  if (!loginForm.value.phone) {
    showMessage('请输入手机号')
    return
  }
  try {
    await axios.post(`${API_BASE}/auth/request_otp`, null, { params: { phone: loginForm.value.phone } })
    otpCountdown.value = 60
    const timer = setInterval(() => {
      otpCountdown.value--
      if (otpCountdown.value <= 0) clearInterval(timer)
    }, 1000)
    showMessage('验证码已发送')
  } catch (e) {
    showMessage('发送失败')
  }
}

const login = async () => {
  if (!loginForm.value.phone || !loginForm.value.otp) {
    showMessage('请填写完整')
    return
  }
  try {
    const res = await axios.post(`${API_BASE}/auth/login`, loginForm.value)
    token.value = res.data.token
    userInfo.value = res.data
    isLoggedIn.value = true
    localStorage.setItem('token', token.value)
    localStorage.setItem('userInfo', JSON.stringify(res.data))
    showMessage('登录成功')
    
    if (res.data.role === 'special_group') fetchMyPickups()
    else if (res.data.role === 'merchant') fetchMyDonations()
  } catch (e) {
    showMessage(e.response?.data?.detail || '登录失败')
  }
}

const logout = () => {
  isLoggedIn.value = false
  userInfo.value = null
  token.value = ''
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  activeTab.value = 'machines'
  showMessage('已退出登录')
}

const fetchMyPickups = async () => {
  try {
    const res = await axios.get(`${API_BASE}/special/my-pickups`, { params: { token: token.value } })
    myPickups.value = res.data.pickups || []
  } catch (e) {
    console.error(e)
  }
}

const fetchMyDonations = async () => {
  try {
    const res = await axios.get(`${API_BASE}/merchant/donations`, { params: { token: token.value } })
    myDonations.value = res.data.donations || []
  } catch (e) {
    console.error(e)
  }
}

const openMachine = (machine) => {
  selectedMachine.value = machine
  showOpenModal.value = true
}

const confirmOpen = async () => {
  if (!token.value) {
    showMessage('请先登录')
    return
  }
  opening.value = true
  try {
    await axios.post(`${API_BASE}/machine/open`, {
      machine_id: selectedMachine.value.id,
      token: token.value
    })
    showMessage('开门成功！请取货')
    showOpenModal.value = false
    
    setTimeout(async () => {
      try {
        await axios.post(`${API_BASE}/mock/device/callback/pickup`, {
          machine_id: selectedMachine.value.id,
          operator: userInfo.value.phone
        })
        if (userInfo.value.role === 'special_group') fetchMyPickups()
        else if (userInfo.value.role === 'merchant') fetchMyDonations()
      } catch (e) {
        console.error(e)
      }
    }, 2000)
  } catch (e) {
    showMessage(e.response?.data?.detail || '开门失败')
  } finally {
    opening.value = false
  }
}

const createDonation = async () => {
  if (!donationForm.value.machine_id || !donationForm.value.item_name) {
    showMessage('请填写完整')
    return
  }
  try {
    await axios.post(`${API_BASE}/merchant/donate`, donationForm.value, { params: { token: token.value } })
    showMessage('投放成功')
    donationForm.value = { machine_id: '', item_name: '', quantity: 1, expiry_days: 7 }
    fetchMyDonations()
    activeTab.value = 'donations'
  } catch (e) {
    showMessage(e.response?.data?.detail || '投放失败')
  }
}

const bindVolunteer = async () => {
  if (!volunteerPhone.value) {
    showMessage('请输入志愿者手机号')
    return
  }
  try {
    await axios.post(`${API_BASE}/special/bind-volunteer`, null, { params: { token: token.value, volunteer_phone: volunteerPhone.value } })
    showMessage('绑定成功')
    userInfo.value.volunteer_phone = volunteerPhone.value
  } catch (e) {
    showMessage(e.response?.data?.detail || '绑定失败')
  }
}

const unbindVolunteer = () => {
  userInfo.value.volunteer_phone = null
  volunteerPhone.value = ''
  showMessage('已解除绑定')
}

const formatDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

onMounted(() => {
  fetchMachines()
  if (token.value) {
    const saved = localStorage.getItem('userInfo')
    if (saved) {
      userInfo.value = JSON.parse(saved)
      isLoggedIn.value = true
      if (userInfo.value.role === 'special_group') fetchMyPickups()
      else if (userInfo.value.role === 'merchant') fetchMyDonations()
    }
  }
})
</script>

<style>
:root {
  --primary: #FF6B6B;
  --primary-light: #FFE8E8;
  --secondary: #4ECDC4;
  --accent: #FFE66D;
  --dark: #2C3E50;
  --light: #F8F9FA;
  --gradient: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  --gradient-blue: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
  --shadow: 0 8px 32px rgba(255, 107, 107, 0.15);
  --shadow-hover: 0 12px 40px rgba(255, 107, 107, 0.25);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body { 
  font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif; 
  background: linear-gradient(180deg, #FFF5F5 0%, #F8F9FA 100%);
  min-height: 100vh;
}

.app-container { 
  max-width: 480px; 
  margin: 0 auto; 
  min-height: 100vh; 
  background: #fff;
  box-shadow: 0 0 40px rgba(0,0,0,0.08);
}

.header { 
  background: var(--gradient); 
  color: #fff; 
  padding: 32px 24px; 
  text-align: center;
  position: relative;
}

.header::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
}

.header h1 { font-size: 28px; margin-bottom: 8px; font-weight: 700; position: relative; }
.header p { font-size: 14px; opacity: 0.95; position: relative; }

.heart-icon { display: inline-block; animation: heartbeat 1.5s ease-in-out infinite; }
@keyframes heartbeat { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }

.card { background: #fff; border-radius: 20px; padding: 20px; margin: 16px; box-shadow: var(--shadow); }

.btn { width: 100%; padding: 16px; border: none; border-radius: 14px; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s; }
.btn-primary { background: var(--gradient); color: #fff; box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3); }
.btn-primary:hover { box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4); }
.btn-success { background: var(--gradient-blue); color: #fff; box-shadow: 0 4px 15px rgba(78, 205, 196, 0.3); }
.btn-outline { background: transparent; color: var(--primary); border: 2px solid var(--primary); }
.btn-sm { width: auto; padding: 10px 20px; font-size: 14px; }
.btn:active { transform: scale(0.98); }

.input-group { margin-bottom: 18px; }
.input-group label { display: block; margin-bottom: 10px; color: var(--dark); font-weight: 600; font-size: 14px; }
.input-group input, .input-group select { width: 100%; padding: 14px 16px; border: 2px solid #FFE8E8; border-radius: 12px; font-size: 15px; background: #FFFCFC; }
.input-group input:focus, .input-group select:focus { outline: none; border-color: var(--primary); background: #fff; box-shadow: 0 0 0 4px rgba(255, 107, 107, 0.1); }

.otp-btn { background: var(--primary-light); color: var(--primary); border: 2px solid var(--primary); font-weight: 600; width: auto; padding: 14px 16px; white-space: nowrap; flex-shrink: 0; }
.otp-row { display: flex; gap: 10px; align-items: center; }
.otp-input { flex: 1; min-width: 0; padding: 14px 16px; border: 2px solid #FFE8E8; border-radius: 12px; font-size: 15px; background: #FFFCFC; }
.otp-input:focus { outline: none; border-color: var(--primary); background: #fff; box-shadow: 0 0 0 4px rgba(255, 107, 107, 0.1); }

.list-item { padding: 16px 0; border-bottom: 2px dashed #FFE8E8; display: flex; justify-content: space-between; align-items: center; }
.list-item:last-child { border-bottom: none; }
.item-name { font-weight: 600; color: var(--dark); }
.item-time { font-size: 12px; color: #95A5A6; }

.status-tag { padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.status-active { background: #E8F8F5; color: #27AE60; }
.status-expired { background: #FDEDEC; color: #E74C3C; }
.status-pending { background: #FEF9E7; color: #F39C12; }

.tabs { display: flex; background: #F8F9FA; padding: 4px; border-radius: 14px; margin: 16px; }
.tab { flex: 1; text-align: center; padding: 12px; border-radius: 10px; cursor: pointer; font-weight: 600; color: #7F8C8D; transition: all 0.3s; }
.tab.active { background: #fff; color: var(--primary); box-shadow: 0 2px 8px rgba(0,0,0,0.08); }

.machine-card { background: #fff; border-radius: 16px; padding: 18px; margin: 10px 16px; box-shadow: var(--shadow); display: flex; justify-content: space-between; align-items: center; transition: all 0.3s; border: 2px solid transparent; }
.machine-card:hover { border-color: var(--primary); transform: translateX(4px); }
.machine-info h3 { font-size: 16px; margin-bottom: 6px; color: var(--dark); }
.machine-info p { font-size: 13px; color: #95A5A6; }
.machine-status { width: 12px; height: 12px; border-radius: 50%; display: inline-block; margin-right: 6px; }
.machine-status.online { background: #27AE60; box-shadow: 0 0 8px #27AE60; }
.machine-status.offline { background: #E74C3C; }
.status-text { font-size: 12px; color: #95A5A6; }

.stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.stat-item { background: linear-gradient(135deg, #FFF5F5 0%, #FFF 100%); padding: 20px; border-radius: 16px; text-align: center; border: 2px solid #FFE8E8; }
.stat-value { font-size: 32px; font-weight: 700; background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.stat-label { font-size: 13px; color: #95A5A6; margin-top: 6px; font-weight: 500; }

.section-title { font-size: 18px; font-weight: 700; color: var(--dark); margin-bottom: 16px; padding-left: 12px; border-left: 4px solid var(--primary); }

.quick-actions { display: flex; gap: 12px; margin: 16px; }
.quick-action { flex: 1; background: var(--gradient); color: #fff; padding: 16px; border-radius: 14px; text-align: center; cursor: pointer; transition: all 0.3s; }
.quick-action:hover { transform: translateY(-3px); box-shadow: var(--shadow-hover); }
.quick-action-icon { font-size: 24px; margin-bottom: 6px; }
.quick-action-label { font-size: 13px; font-weight: 600; }

.user-badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.2); padding: 6px 14px; border-radius: 20px; font-size: 14px; margin-top: 12px; }

.bind-success { text-align: center; padding: 16px; }
.bind-icon { font-size: 40px; margin-bottom: 12px; }
.bind-label { color: var(--dark); font-weight: 600; }
.bind-phone { color: var(--primary); font-size: 18px; font-weight: 700; margin: 8px 0; }

.empty-tip, .empty-state p { text-align: center; color: #95A5A6; padding: 24px; }
.empty-icon { font-size: 48px; margin-bottom: 16px; }
.empty-state { text-align: center; padding: 24px; }

.tip { margin-top: 18px; font-size: 13px; color: #95A5A6; text-align: center; }
.tip strong { color: var(--primary); }

.footer { padding: 16px; }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(44, 62, 80, 0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #fff; border-radius: 24px; padding: 28px; width: 90%; max-width: 360px; text-align: center; }
.modal-icon { font-size: 48px; margin-bottom: 12px; }
.modal h3 { color: var(--dark); margin-bottom: 8px; }
.modal-text { color: #7F8C8D; margin-bottom: 24px; }
.modal-text strong { color: var(--primary); }
.modal .btn { margin-top: 12px; }

.message-toast { position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: var(--dark); color: #fff; padding: 14px 28px; border-radius: 12px; z-index: 2000; font-weight: 500; }
</style>
