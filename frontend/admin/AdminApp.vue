<template>
  <div>
    <!-- 登录页 -->
    <div v-if="!isLoggedIn" class="login-container">
      <div class="login-box">
        <h2 class="login-title">❤️ 爱心柜</h2>
        <p class="login-subtitle">公益售货机管理后台</p>
        <el-form @submit.prevent="login">
          <el-form-item>
            <el-input v-model="loginForm.phone" placeholder="手机号" size="large" prefix-icon="User"></el-input>
          </el-form-item>
          <el-form-item>
            <el-input v-model="loginForm.otp" placeholder="验证码" size="large" prefix-icon="Lock"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" style="width: 100%; height: 48px; font-size: 16px;" @click="login" :loading="loading">🚀 登录</el-button>
          </el-form-item>
          <p style="text-align: center; color: #95a5a6; margin-top: 20px;">
            测试验证码: <strong style="color: var(--primary);">123456</strong>
          </p>
        </el-form>
      </div>
    </div>
    
    <!-- 管理后台 -->
    <div v-else class="admin-layout">
      <!-- 侧边栏 -->
      <div class="sidebar">
        <div class="logo">❤️ 爱心柜</div>
        <div class="menu">
          <div v-for="item in menuItems" :key="item.key"
               :class="['menu-item', currentView === item.key ? 'active' : '']"
               @click="currentView = item.key">
            <span class="menu-icon">{{ item.icon }}</span> {{ item.label }}
          </div>
        </div>
      </div>
      
      <!-- 主体 -->
      <div class="main">
        <div class="header">
          <h2 class="header-title">{{ viewTitle }}</h2>
          <div class="header-right">
            <div class="user-info">
              <span>👤</span>
              <span>{{ userInfo.name }}</span>
            </div>
            <el-button @click="logout" size="small">退出</el-button>
          </div>
        </div>
        
        <div class="content">
          <!-- 数据概览 -->
          <div v-if="currentView === 'dashboard'">
            <div class="stats-grid">
              <div v-for="(stat, index) in statCards" :key="index" :class="['stat-card', stat.class]">
                <div class="stat-icon">{{ stat.icon }}</div>
                <div class="stat-value">{{ stat.value }}</div>
                <div class="stat-label">{{ stat.label }}</div>
              </div>
            </div>
            
            <div class="chart-card">
              <h3 class="table-title">📈 领取趋势（最近7天）</h3>
              <div id="trendChart" class="chart-container"></div>
            </div>
          </div>
          
          <!-- 用户管理 -->
          <div v-if="currentView === 'users'">
            <div class="table-card">
              <div class="toolbar">
                <el-select v-model="userFilter.role" placeholder="角色" clearable style="width: 140px;">
                  <el-option label="特殊群体" value="special_group"></el-option>
                  <el-option label="商户" value="merchant"></el-option>
                  <el-option label="管理员" value="admin"></el-option>
                </el-select>
                <el-input v-model="userFilter.phone" placeholder="搜索手机号" clearable style="width: 180px;"></el-input>
                <el-button type="primary" @click="fetchUsers">🔍 搜索</el-button>
                <el-button type="success" @click="showImportDialog = true">➕ 导入用户</el-button>
              </div>
              
              <el-table :data="users" border stripe>
                <el-table-column prop="phone" label="手机号" width="130"></el-table-column>
                <el-table-column prop="name" label="姓名" width="100"></el-table-column>
                <el-table-column prop="role" label="角色" width="100">
                  <template #default="{row}">
                    <span :class="['tag', roleTagClass(row.role)]">{{ roleText(row.role) }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="category" label="类别"></el-table-column>
                <el-table-column prop="community" label="社区"></el-table-column>
                <el-table-column prop="daily_limit" label="每日限额" width="80"></el-table-column>
                <el-table-column prop="used_today" label="今日使用" width="80"></el-table-column>
                <el-table-column prop="created_at" label="创建时间">
                  <template #default="{row}">{{ formatDate(row.created_at) }}</template>
                </el-table-column>
              </el-table>
              
              <el-pagination style="margin-top: 20px; text-align: right;"
                v-model:current-page="userPage" :page-size="20" :total="userTotal" @current-change="fetchUsers">
              </el-pagination>
            </div>
          </div>
          
          <!-- 柜机管理 -->
          <div v-if="currentView === 'machines'">
            <div class="table-card">
              <el-table :data="machines" border stripe>
                <el-table-column prop="id" label="柜机ID" width="120"></el-table-column>
                <el-table-column prop="name" label="名称"></el-table-column>
                <el-table-column prop="location" label="位置"></el-table-column>
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="{row}">
                    <span :class="['tag', row.status === 'online' ? 'tag-green' : 'tag-red']">
                      {{ row.status === 'online' ? '🟢 在线' : '🔴 离线' }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="last_communication" label="最后通信">
                  <template #default="{row}">{{ row.last_communication ? formatDate(row.last_communication) : '-' }}</template>
                </el-table-column>
              </el-table>
            </div>
          </div>
          
          <!-- 捐赠管理 -->
          <div v-if="currentView === 'donations'">
            <div class="table-card">
              <div class="toolbar">
                <el-select v-model="donationFilter.status" placeholder="状态" clearable style="width: 140px;">
                  <el-option label="进行中" value="active"></el-option>
                  <el-option label="已过期" value="expired"></el-option>
                  <el-option label="已领完" value="all_claimed"></el-option>
                </el-select>
                <el-button type="primary" @click="fetchDonations">🔍 筛选</el-button>
              </div>
              
              <el-table :data="donations" border stripe>
                <el-table-column prop="id" label="ID" width="60"></el-table-column>
                <el-table-column prop="machine_id" label="柜机" width="90"></el-table-column>
                <el-table-column prop="item_name" label="商品"></el-table-column>
                <el-table-column prop="quantity" label="数量" width="70"></el-table-column>
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="{row}">
                    <span :class="['tag', donationStatusClass(row.status)]">{{ donationStatusText(row.status) }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="expiry_time" label="截止时间">
                  <template #default="{row}">{{ formatDate(row.expiry_time) }}</template>
                </el-table-column>
                <el-table-column prop="created_at" label="投放时间">
                  <template #default="{row}">{{ formatDate(row.created_at) }}</template>
                </el-table-column>
              </el-table>
            </div>
          </div>
          
          <!-- 领取记录 -->
          <div v-if="currentView === 'pickups'">
            <div class="table-card">
              <el-table :data="pickups" border stripe>
                <el-table-column prop="id" label="ID" width="60"></el-table-column>
                <el-table-column prop="user_id" label="用户ID" width="80"></el-table-column>
                <el-table-column prop="machine_id" label="柜机" width="90"></el-table-column>
                <el-table-column prop="item_name" label="商品" min-width="120"></el-table-column>
                <el-table-column prop="quantity" label="数量" width="70"></el-table-column>
                <el-table-column prop="is_compliant" label="合规状态" width="100">
                  <template #default="{row}">
                    <span :class="['tag', row.is_compliant ? 'tag-green' : 'tag-red']">
                      {{ row.is_compliant ? '✅ 合规' : '❌ 违规' }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="violation_reason" label="违规原因" min-width="120">
                  <template #default="{row}">{{ row.violation_reason || '-' }}</template>
                </el-table-column>
                <el-table-column prop="pickup_time" label="领取时间" width="160">
                  <template #default="{row}">{{ formatDate(row.pickup_time) }}</template>
                </el-table-column>
              </el-table>
            </div>
          </div>
          
          <!-- 数据分析 -->
          <div v-if="currentView === 'analysis'">
            <div class="analysis-grid">
              <div class="chart-card">
                <h3 class="table-title">👥 用户角色分布</h3>
                <div id="roleChart" class="chart-container-sm"></div>
              </div>
              <div class="chart-card">
                <h3 class="table-title">📂 用户类别分布</h3>
                <div id="categoryChart" class="chart-container-sm"></div>
              </div>
            </div>
            <div class="chart-card chart-card-full">
              <h3 class="table-title">📍 柜机需求热力图</h3>
              <div id="heatmapChart" class="chart-container"></div>
            </div>
          </div>
          
          <!-- 规则配置 -->
          <div v-if="currentView === 'rules'">
            <div class="rules-container">
              <div class="rules-card">
                <div class="rules-header">
                  <span class="rules-icon">⚙️</span>
                  <h3>领取规则配置</h3>
                </div>
                <p class="rules-desc">设置特殊群体每日领取物资的次数和数量限制</p>
                
                <div class="rules-form">
                  <div class="rule-item">
                    <div class="rule-label">
                      <span class="rule-icon">📊</span>
                      <span>每日领取次数上限</span>
                    </div>
                    <div class="rule-control">
                      <el-input-number v-model="ruleForm.daily_limit" :min="1" :max="10" size="large"></el-input-number>
                      <span class="rule-unit">次/天</span>
                    </div>
                  </div>
                  
                  <div class="rule-item">
                    <div class="rule-label">
                      <span class="rule-icon">🍚</span>
                      <span>食品类每日限额</span>
                    </div>
                    <div class="rule-control">
                      <el-input-number v-model="ruleForm.food_limit" :min="1" :max="10" size="large"></el-input-number>
                      <span class="rule-unit">件/天</span>
                    </div>
                  </div>
                  
                  <div class="rule-item">
                    <div class="rule-label">
                      <span class="rule-icon">🥤</span>
                      <span>饮品类每日限额</span>
                    </div>
                    <div class="rule-control">
                      <el-input-number v-model="ruleForm.drink_limit" :min="1" :max="10" size="large"></el-input-number>
                      <span class="rule-unit">件/天</span>
                    </div>
                  </div>
                </div>
                
                <div class="rules-actions">
                  <el-button type="primary" size="large" @click="saveRules">
                    💾 保存规则
                  </el-button>
                </div>
              </div>
              
              <div class="rules-tips">
                <h4>📋 规则说明</h4>
                <ul>
                  <li>每日领取次数：特殊群体每天最多可领取物资的次数</li>
                  <li>食品类限额：包括大米、食用油、方便面等食品</li>
                  <li>饮品类限额：包括矿泉水、牛奶、饮料等</li>
                  <li>规则修改后立即生效，适用于所有特殊群体用户</li>
                </ul>
              </div>
            </div>
          </div>
          
          <!-- 通知中心 -->
          <div v-if="currentView === 'notifications'">
            <div class="table-card">
              <div v-for="n in notifications" :key="n.id" :class="['notification-item', !n.is_read ? 'unread' : '']">
                <div class="notification-title">{{ n.title }}</div>
                <div class="notification-content">{{ n.content }}</div>
                <div class="notification-time">{{ formatDate(n.created_at) }}</div>
              </div>
              <p v-if="notifications.length === 0" class="empty-tip">暂无通知</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 导入弹窗 -->
    <el-dialog v-model="showImportDialog" title="📥 导入用户" width="500px">
      <el-form>
        <el-form-item label="角色">
          <el-select v-model="importForm.role" style="width: 100%;">
            <el-option label="特殊群体" value="special_group"></el-option>
            <el-option label="商户" value="merchant"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="用户数据 (JSON格式)">
          <el-input v-model="importForm.data" type="textarea" rows="10" placeholder='[{"phone": "13800000001", "name": "张三", "category": "残疾人", "community": "朝阳区"}]'></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="importUsers">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

const API_BASE = '/api'

// 菜单配置
const menuItems = [
  { key: 'dashboard', icon: '📊', label: '数据概览' },
  { key: 'users', icon: '👥', label: '用户管理' },
  { key: 'machines', icon: '📦', label: '柜机管理' },
  { key: 'donations', icon: '🎁', label: '捐赠管理' },
  { key: 'pickups', icon: '📝', label: '领取记录' },
  { key: 'analysis', icon: '📈', label: '数据分析' },
  { key: 'rules', icon: '⚙️', label: '规则配置' },
  { key: 'notifications', icon: '🔔', label: '通知中心' }
]

// 状态
const isLoggedIn = ref(false)
const loading = ref(false)
const currentView = ref('dashboard')
const userInfo = ref(null)
const token = ref(localStorage.getItem('admin_token') || '')

// 表单
const loginForm = ref({ phone: '', otp: '' })
const showImportDialog = ref(false)
const importForm = ref({ role: 'special_group', data: '' })
const ruleForm = ref({ daily_limit: 3, food_limit: 2, drink_limit: 2 })

// 数据
const dashboard = ref({
  users: { total: 0, special_group: 0, merchant: 0, admin: 0 },
  machines: { total: 0, online: 0, offline: 0 },
  donations: { active: 0, expired: 0 },
  pickups: { total: 0, today: 0, compliant: 0, violations: 0 }
})
const users = ref([])
const userTotal = ref(0)
const userPage = ref(1)
const userFilter = ref({ role: '', phone: '' })
const machines = ref([])
const donations = ref([])
const donationFilter = ref({ status: '' })
const pickups = ref([])
const notifications = ref([])

// 计算属性
const viewTitle = computed(() => {
  const item = menuItems.find(m => m.key === currentView.value)
  return item ? `${item.icon} ${item.label}` : ''
})

const statCards = computed(() => [
  { class: 'blue', icon: '👥', value: dashboard.value.users.total, label: '用户总数' },
  { class: 'green', icon: '📦', value: dashboard.value.machines.online, label: '在线柜机' },
  { class: 'orange', icon: '🎁', value: dashboard.value.donations.active, label: '进行中捐赠' },
  { class: 'red', icon: '📝', value: dashboard.value.pickups.today, label: '今日领取' },
  { class: 'purple', icon: '', value: dashboard.value.users.special_group, label: '特殊群体' },
  { class: '', icon: '', value: dashboard.value.users.merchant, label: '爱心商户' },
  { class: '', icon: '', value: dashboard.value.pickups.violations, label: '违规次数' },
  { class: '', icon: '', value: dashboard.value.machines.offline, label: '离线柜机' }
])

// 辅助函数
const roleText = (role) => ({ special_group: '特殊群体', merchant: '商户', admin: '管理员' }[role] || role)
const roleTagClass = (role) => ({ special_group: 'tag-blue', merchant: 'tag-green', admin: 'tag-purple' }[role] || '')
const donationStatusText = (status) => ({ active: '进行中', expired: '已过期', all_claimed: '已领完' }[status] || status)
const donationStatusClass = (status) => ({ active: 'tag-green', expired: 'tag-red', all_claimed: 'tag-orange' }[status] || '')

const formatDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

// API调用
const login = async () => {
  if (!loginForm.value.phone || !loginForm.value.otp) return
  loading.value = true
  try {
    const res = await axios.post(`${API_BASE}/auth/login`, loginForm.value)
    if (res.data.role === 'admin') {
      token.value = res.data.token
      userInfo.value = res.data
      isLoggedIn.value = true
      localStorage.setItem('admin_token', token.value)
      localStorage.setItem('admin_user', JSON.stringify(res.data))
      fetchDashboard()
    } else {
      alert('非管理员账号无法登录后台')
    }
  } catch (e) {
    alert(e.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

const logout = () => {
  isLoggedIn.value = false
  token.value = ''
  localStorage.removeItem('admin_token')
  localStorage.removeItem('admin_user')
}

const fetchDashboard = async () => {
  try {
    const res = await axios.get(`${API_BASE}/admin/dashboard`)
    dashboard.value = res.data
  } catch (e) { console.error(e) }
}

const fetchUsers = async () => {
  try {
    const params = { skip: (userPage.value - 1) * 20, limit: 20 }
    if (userFilter.value.role) params.role = userFilter.value.role
    const res = await axios.get(`${API_BASE}/admin/users`, { params })
    users.value = res.data.users || []
    userTotal.value = res.data.total || 0
  } catch (e) { console.error(e) }
}

const fetchMachines = async () => {
  try {
    const res = await axios.get(`${API_BASE}/admin/machines`)
    machines.value = res.data.machines || []
  } catch (e) { console.error(e) }
}

const fetchDonations = async () => {
  try {
    const params = {}
    if (donationFilter.value.status) params.status = donationFilter.value.status
    const res = await axios.get(`${API_BASE}/admin/donations`, { params })
    donations.value = res.data.donations || []
  } catch (e) { console.error(e) }
}

const fetchPickups = async () => {
  try {
    const res = await axios.get(`${API_BASE}/admin/pickups`)
    pickups.value = res.data.pickups || []
  } catch (e) { console.error(e) }
}

const fetchNotifications = async () => {
  try {
    const res = await axios.get(`${API_BASE}/admin/notifications`)
    notifications.value = res.data.notifications || []
  } catch (e) { console.error(e) }
}

const importUsers = async () => {
  try {
    const data = JSON.parse(importForm.value.data)
    await axios.post(`${API_BASE}/admin/users/import`, { users: data })
    showImportDialog.value = false
    importForm.value.data = ''
    fetchUsers()
    alert('导入成功')
  } catch (e) {
    alert('导入失败: ' + (e.response?.data?.detail || e.message))
  }
}

const saveRules = async () => {
  try {
    await axios.post(`${API_BASE}/admin/rules`, {
      name: 'default',
      daily_limit: ruleForm.value.daily_limit,
      category_limits: JSON.stringify({ food: ruleForm.value.food_limit, drink: ruleForm.value.drink_limit })
    })
    alert('规则保存成功')
  } catch (e) { alert('保存失败') }
}

// 图表初始化
const initCharts = async () => {
  await nextTick()
  
  if (currentView.value === 'dashboard') {
    try {
      const res = await axios.get(`${API_BASE}/admin/analysis/user-portrait`)
      const trendData = res.data.pickup_trend || []
      const chart = echarts.init(document.getElementById('trendChart'))
      chart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: trendData.map(d => d.date) },
        yAxis: { type: 'value' },
        series: [{
          data: trendData.map(d => d.count),
          type: 'line',
          smooth: true,
          areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(255, 107, 107, 0.3)' }, { offset: 1, color: 'rgba(255, 107, 107, 0.05)' }] } },
          itemStyle: { color: '#FF6B6B' }
        }]
      })
    } catch (e) { console.error(e) }
  }
  
  if (currentView.value === 'analysis') {
    try {
      const [portraitRes, heatmapRes] = await Promise.all([
        axios.get(`${API_BASE}/admin/analysis/user-portrait`),
        axios.get(`${API_BASE}/admin/analysis/demand-heatmap`)
      ])
      
      const roleChart = echarts.init(document.getElementById('roleChart'))
      roleChart.setOption({
        tooltip: { trigger: 'item' },
        series: [{ type: 'pie', radius: ['40%', '70%'], itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
          data: Object.entries(portraitRes.data.role_distribution || {}).map(([name, value]) => ({ name: roleText(name), value })) }]
      })
      
      const categoryChart = echarts.init(document.getElementById('categoryChart'))
      categoryChart.setOption({
        tooltip: { trigger: 'item' },
        series: [{ type: 'pie', radius: ['40%', '70%'], itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
          data: Object.entries(portraitRes.data.category_distribution || {}).map(([name, value]) => ({ name, value })) }]
      })
      
      const heatmapChart = echarts.init(document.getElementById('heatmapChart'))
      const heatmapData = (heatmapRes.data.by_machine || []).map(m => [m.location, m.pickup_count])
      heatmapChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: heatmapData.map(d => d[0]), axisLabel: { rotate: 30 } },
        yAxis: { type: 'value' },
        series: [{ data: heatmapData.map(d => d[1]), type: 'bar',
          itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#FF6B6B' }, { offset: 1, color: '#FF8E53' }] } },
          borderRadius: [8, 8, 0, 0] }]
      })
    } catch (e) { console.error(e) }
  }
}

watch(currentView, async (newView) => {
  const fetchMap = { dashboard: fetchDashboard, users: fetchUsers, machines: fetchMachines, donations: fetchDonations, pickups: fetchPickups, notifications: fetchNotifications }
  if (fetchMap[newView]) fetchMap[newView]()
  if (['dashboard', 'analysis'].includes(newView)) setTimeout(initCharts, 100)
})

onMounted(() => {
  const saved = localStorage.getItem('admin_user')
  const savedToken = localStorage.getItem('admin_token')
  if (saved && savedToken) {
    userInfo.value = JSON.parse(saved)
    token.value = savedToken
    isLoggedIn.value = true
    fetchDashboard()
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
  --gradient-purple: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --shadow: 0 4px 20px rgba(255, 107, 107, 0.12);
  --shadow-hover: 0 8px 30px rgba(255, 107, 107, 0.2);
}

* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif; background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%); min-height: 100vh; }

.admin-layout { display: flex; min-height: 100vh; }

.sidebar { width: 240px; background: linear-gradient(180deg, var(--dark) 0%, #1a252f 100%); color: #fff; position: fixed; height: 100vh; box-shadow: 4px 0 20px rgba(0,0,0,0.15); }
.logo { height: 70px; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 700; border-bottom: 1px solid rgba(255,255,255,0.1); background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.menu { padding: 20px 0; }
.menu-item { padding: 14px 24px; cursor: pointer; display: flex; align-items: center; gap: 12px; color: rgba(255,255,255,0.7); font-weight: 500; transition: all 0.3s; }
.menu-item:hover { background: rgba(255,255,255,0.1); color: #fff; }
.menu-item.active { background: linear-gradient(90deg, var(--primary) 0%, #FF8E53 100%); color: #fff; box-shadow: var(--shadow); }
.menu-icon { font-size: 18px; }

.main { flex: 1; margin-left: 240px; }
.header { height: 70px; background: #fff; display: flex; align-items: center; justify-content: space-between; padding: 0 32px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.header-title { font-size: 22px; font-weight: 700; background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.header-right { display: flex; align-items: center; gap: 16px; }
.user-info { display: flex; align-items: center; gap: 10px; padding: 8px 16px; background: var(--primary-light); border-radius: 25px; color: var(--primary); font-weight: 500; }

.content { padding: 28px 32px; }

.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.stat-card { background: #fff; border-radius: 16px; padding: 24px; box-shadow: var(--shadow); transition: all 0.3s; position: relative; overflow: hidden; }
.stat-card::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; border-radius: 4px 0 0 4px; }
.stat-card.blue::before { background: var(--gradient-blue); }
.stat-card.green::before { background: #27AE60; }
.stat-card.orange::before { background: #F39C12; }
.stat-card.red::before { background: var(--primary); }
.stat-card.purple::before { background: var(--gradient-purple); }
.stat-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-hover); }
.stat-value { font-size: 32px; font-weight: 700; background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.stat-label { font-size: 14px; color: #7f8c8d; margin-top: 8px; font-weight: 500; }
.stat-icon { position: absolute; right: 20px; top: 50%; transform: translateY(-50%); font-size: 48px; opacity: 0.15; }

.table-card { background: #fff; border-radius: 16px; padding: 24px; margin-top: 24px; box-shadow: var(--shadow); }
.table-title { font-size: 18px; font-weight: 700; color: var(--dark); margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
.toolbar { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }

.tag { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.tag-blue { background: #e8f4fc; color: #3498db; }
.tag-green { background: #e8f8f0; color: #27ae60; }
.tag-orange { background: #fef5e7; color: #f39c12; }
.tag-red { background: #fdedec; color: #e74c3c; }
.tag-purple { background: #f4ecf7; color: #9b59b6; }

.chart-card { background: #fff; border-radius: 16px; padding: 24px; margin-top: 24px; box-shadow: var(--shadow); }
.chart-container { height: 350px; }

.login-container { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 50%, #667eea 100%); background-size: 200% 200%; animation: gradientBG 15s ease infinite; }
@keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
.login-box { width: 420px; background: #fff; border-radius: 24px; padding: 48px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); }
.login-title { text-align: center; font-size: 28px; font-weight: 700; margin-bottom: 12px; background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.login-subtitle { text-align: center; color: #7f8c8d; margin-bottom: 36px; }

.notification-item { padding: 20px; border-bottom: 1px solid #f0f0f0; cursor: pointer; transition: all 0.3s; border-radius: 12px; margin-bottom: 8px; }
.notification-item:hover { background: #fafafa; transform: translateX(4px); }
.notification-item.unread { background: linear-gradient(90deg, #fff5f5 0%, #fff 100%); border-left: 4px solid var(--primary); }
.notification-title { font-weight: 600; color: var(--dark); margin-bottom: 6px; }
.notification-content { color: #7f8c8d; font-size: 14px; }
.notification-time { color: #bdc3c7; font-size: 12px; margin-top: 8px; }
.empty-tip { text-align: center; color: #95a5a6; padding: 40px; }

/* 数据分析页面 */
.analysis-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }
.chart-container-sm { height: 280px; }
.chart-card-full { margin-top: 24px; }

/* 规则配置页面 */
.rules-container { display: grid; grid-template-columns: 1fr 350px; gap: 24px; }
.rules-card { background: #fff; border-radius: 16px; padding: 32px; box-shadow: var(--shadow); }
.rules-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.rules-icon { font-size: 28px; }
.rules-header h3 { font-size: 22px; font-weight: 700; color: var(--dark); margin: 0; }
.rules-desc { color: #7f8c8d; font-size: 14px; margin-bottom: 28px; }
.rules-form { display: flex; flex-direction: column; gap: 24px; }
.rule-item { display: flex; justify-content: space-between; align-items: center; padding: 20px; background: #f8f9fa; border-radius: 12px; }
.rule-label { display: flex; align-items: center; gap: 12px; font-size: 15px; font-weight: 600; color: var(--dark); }
.rule-icon { font-size: 20px; }
.rule-control { display: flex; align-items: center; gap: 12px; }
.rule-unit { color: #7f8c8d; font-size: 14px; }
.rules-actions { margin-top: 32px; display: flex; justify-content: center; }
.rules-actions .el-button { padding: 12px 40px; font-size: 16px; }

.rules-tips { background: #fff; border-radius: 16px; padding: 24px; box-shadow: var(--shadow); height: fit-content; }
.rules-tips h4 { font-size: 16px; font-weight: 600; color: var(--dark); margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
.rules-tips ul { list-style: none; padding: 0; margin: 0; }
.rules-tips li { padding: 12px 0; border-bottom: 1px solid #f0f0f0; font-size: 13px; color: #666; line-height: 1.6; }
.rules-tips li:last-child { border-bottom: none; }
.rules-tips li::before { content: '•'; color: var(--primary); font-weight: bold; margin-right: 8px; }

@media (max-width: 1200px) {
  .analysis-grid { grid-template-columns: 1fr; }
  .rules-container { grid-template-columns: 1fr; }
}
</style>
