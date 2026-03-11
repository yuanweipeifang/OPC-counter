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
              <div class="toolbar toolbar-machine">
                <el-input v-model="machineFilter.keyword" placeholder="搜索柜机名称、位置或编号" clearable style="width: 260px;"></el-input>
                <el-select v-model="machineFilter.status" placeholder="状态筛选" clearable style="width: 150px;">
                  <el-option label="在线" value="online"></el-option>
                  <el-option label="离线" value="offline"></el-option>
                </el-select>
                <el-button @click="resetMachineFilter">重置筛选</el-button>
              </div>

              <div class="admin-machine-map-card">
                <div class="admin-machine-map-header">
                  <div>
                    <h3>📍 柜机分布预览</h3>
                    <p>根据当前筛选结果自动缩放地图，点击表格中的“地图定位”可快速聚焦某一台柜机。</p>
                  </div>
                  <div class="admin-machine-map-count">共 {{ filteredAdminMachines.length }} 台</div>
                </div>

                <div class="admin-machine-preview-shell">
                  <div ref="adminPreviewMapContainer" class="admin-machine-preview-canvas" :class="{ 'admin-map-canvas-hidden': !!adminPreviewMapError }"></div>
                  <div v-if="adminPreviewMapLoading" class="admin-map-state admin-map-state-overlay">柜机地图加载中...</div>
                  <div v-else-if="adminPreviewMapError" class="admin-map-state admin-map-state-overlay admin-map-state-error">
                    <p>{{ adminPreviewMapError }}</p>
                  </div>
                </div>
              </div>

              <el-table :data="filteredAdminMachines" border stripe>
                <el-table-column prop="id" label="柜机ID" width="120"></el-table-column>
                <el-table-column prop="name" label="名称"></el-table-column>
                <el-table-column prop="location" label="位置"></el-table-column>
                <el-table-column label="坐标" width="180">
                  <template #default="{row}">
                    <span v-if="hasMachineCoordinates(row)" class="machine-coord-text">{{ machineCoordinateText(row) }}</span>
                    <span v-else class="machine-coord-empty">暂无坐标</span>
                  </template>
                </el-table-column>
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
                <el-table-column label="操作" width="200" fixed="right">
                  <template #default="{row}">
                    <div class="machine-action-buttons">
                      <el-button size="small" @click="focusAdminMachineOnPreview(row)">地图定位</el-button>
                      <el-button size="small" type="primary" plain @click="viewAdminMachineMap(row)">地图查看</el-button>
                    </div>
                  </template>
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
          
          <!-- 志愿者绑定管理 -->
          <div v-if="currentView === 'volunteer-binds'">
            <div class="volunteer-stats">
              <div class="stat-card green">
                <div class="stat-icon">✅</div>
                <div class="stat-value">{{ volunteerBinds.total_binded || 0 }}</div>
                <div class="stat-label">已绑定数量</div>
              </div>
              <div class="stat-card orange">
                <div class="stat-icon">⏳</div>
                <div class="stat-value">{{ volunteerBinds.total_unbinded || 0 }}</div>
                <div class="stat-label">未绑定数量</div>
              </div>
              <div class="stat-card blue">
                <div class="stat-icon">👥</div>
                <div class="stat-value">{{ (volunteerBinds.volunteers || []).length }}</div>
                <div class="stat-label">志愿者总数</div>
              </div>
            </div>
            
            <div class="table-card">
              <h3 class="table-title">🤝 绑定关系列表</h3>
              <el-table :data="volunteerBinds.bindings || []" border stripe>
                <el-table-column label="特殊群体" min-width="200">
                  <template #default="{row}">
                    <div v-if="row.special_group">
                      <div style="font-weight: 600;">{{ row.special_group.name }}</div>
                      <div style="font-size: 12px; color: #666;">{{ row.special_group.phone }}</div>
                      <div style="font-size: 12px; color: #999;">{{ row.special_group.category }} · {{ row.special_group.community }}</div>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="绑定关系" width="70" align="center">
                  <template #default>
                    <span style="font-size: 18px;">👉</span>
                  </template>
                </el-table-column>
                <el-table-column label="志愿者" min-width="200">
                  <template #default="{row}">
                    <div v-if="row.volunteer">
                      <div style="font-weight: 600; color: var(--el-color-primary);">{{ row.volunteer.name }}</div>
                      <div style="font-size: 12px; color: #666;">{{ row.volunteer.phone }}</div>
                      <div style="font-size: 12px; color: #999;">{{ row.volunteer.community }}</div>
                    </div>
                    <span v-else style="color: #999;">未绑定</span>
                  </template>
                </el-table-column>
              </el-table>
              <p v-if="(volunteerBinds.bindings || []).length === 0" class="empty-tip">暂无绑定记录</p>
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
                <div class="rules-tips-header">
                  <h4>📋 规则说明</h4>
                  <p>配置提交后即时生效，右侧说明与左侧规则项一一对应。</p>
                </div>

                <div class="rules-tips-body">
                  <div class="tip-block">
                    <div class="tip-block-title">每日领取次数</div>
                    <p>用于控制特殊群体用户每天最多可成功领取物资的次数，超出后当天不可继续领取。</p>
                  </div>

                  <div class="tip-block">
                    <div class="tip-block-title">食品类限额</div>
                    <p>适用于大米、食用油、方便面等常见食品，主要限制同一用户每日食品类领取总量。</p>
                  </div>

                  <div class="tip-block">
                    <div class="tip-block-title">饮品类限额</div>
                    <p>适用于矿泉水、牛奶、饮料等饮品类物资，避免单个品类在短时间内被过度领取。</p>
                  </div>
                </div>

                <div class="rules-note">
                  <span class="rules-note-label">生效规则</span>
                  <span>修改后立即应用到全部特殊群体账号，无需重新登录。</span>
                </div>
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

    <div v-if="showMachineMapModal" class="admin-map-overlay" @click.self="closeAdminMachineMap">
      <div class="admin-map-modal">
        <div class="admin-map-header">
          <div>
            <div class="admin-map-kicker">高德地图</div>
            <h3>{{ adminMapMachine?.name || '柜机位置' }}</h3>
          </div>
          <button class="admin-map-close" @click="closeAdminMachineMap">×</button>
        </div>

        <p class="admin-map-address">{{ adminMapMachine?.location || '暂无地址信息' }}</p>

        <div class="admin-map-shell">
          <div ref="adminMapContainer" class="admin-map-canvas" :class="{ 'admin-map-canvas-hidden': !!adminMapError }"></div>
          <div v-if="adminMapLoading" class="admin-map-state admin-map-state-overlay">地图加载中...</div>
          <div v-else-if="adminMapError" class="admin-map-state admin-map-state-overlay admin-map-state-error">
            <p>{{ adminMapError }}</p>
          </div>
        </div>

        <div class="admin-map-footer">
          <div class="admin-map-tip">{{ adminMapFooterText }}</div>
          <div class="admin-map-links">
            <a v-if="adminMapNavigationUrl" :href="adminMapNavigationUrl" target="_blank" rel="noopener noreferrer" class="admin-map-link-btn">导航到这里</a>
            <a v-if="adminMapWalkingUrl" :href="adminMapWalkingUrl" target="_blank" rel="noopener noreferrer" class="admin-map-link-text">步行路线外链</a>
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
import { ref, computed, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

const API_BASE = '/api'
const AMAP_KEY = import.meta.env.VITE_AMAP_KEY || ''
const AMAP_SECURITY_CODE = import.meta.env.VITE_AMAP_SECURITY_CODE || ''

// 菜单配置
const menuItems = [
  { key: 'dashboard', icon: '📊', label: '数据概览' },
  { key: 'users', icon: '👥', label: '用户管理' },
  { key: 'volunteer-binds', icon: '🤝', label: '志愿者绑定' },
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
const machineFilter = ref({ keyword: '', status: '' })

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
const volunteerBinds = ref({ bindings: [], volunteers: [], total_binded: 0, total_unbinded: 0 })
const showMachineMapModal = ref(false)
const adminMapMachine = ref(null)
const adminMapLoading = ref(false)
const adminMapError = ref('')
const adminMapContainer = ref(null)
const adminPreviewMapContainer = ref(null)
const adminPreviewMapLoading = ref(false)
const adminPreviewMapError = ref('')

let amapLoaderPromise = null
let adminMapInstance = null
let adminPreviewMapInstance = null
let adminPreviewInfoWindow = null

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

const filteredAdminMachines = computed(() => {
  const keyword = machineFilter.value.keyword.trim().toLowerCase()

  return machines.value.filter((machine) => {
    const matchKeyword = !keyword || [machine.id, machine.name, machine.location]
      .some((field) => String(field || '').toLowerCase().includes(keyword))
    const matchStatus = !machineFilter.value.status || machine.status === machineFilter.value.status
    return matchKeyword && matchStatus
  })
})

const filteredAdminMappableMachines = computed(() => filteredAdminMachines.value.filter((machine) => hasMachineCoordinates(machine)))

// 辅助函数
const roleText = (role) => ({ special_group: '特殊群体', merchant: '商户', admin: '管理员' }[role] || role)
const roleTagClass = (role) => ({ special_group: 'tag-blue', merchant: 'tag-green', admin: 'tag-purple' }[role] || '')
const donationStatusText = (status) => ({ active: '进行中', expired: '已过期', all_claimed: '已领完' }[status] || status)
const donationStatusClass = (status) => ({ active: 'tag-green', expired: 'tag-red', all_claimed: 'tag-orange' }[status] || '')
const hasMachineCoordinates = (machine) => Number.isFinite(Number(machine?.latitude)) && Number.isFinite(Number(machine?.longitude))
const machineCoordinateText = (machine) => hasMachineCoordinates(machine)
  ? `${Number(machine.latitude).toFixed(4)}, ${Number(machine.longitude).toFixed(4)}`
  : '暂无坐标'

const adminMapNavigationUrl = computed(() => {
  const machine = adminMapMachine.value
  if (!hasMachineCoordinates(machine)) return ''
  const name = encodeURIComponent(machine.name || '爱心柜')
  return `https://uri.amap.com/navigation?to=${machine.longitude},${machine.latitude},${name}&mode=car&policy=1&src=LoveCabinetAdmin&coordinate=gaode&callnative=0`
})

const adminMapWalkingUrl = computed(() => {
  const machine = adminMapMachine.value
  if (!hasMachineCoordinates(machine)) return ''
  const name = encodeURIComponent(machine.name || '爱心柜')
  return `https://uri.amap.com/navigation?to=${machine.longitude},${machine.latitude},${name}&mode=walk&policy=1&src=LoveCabinetAdmin&coordinate=gaode&callnative=0`
})

const adminMapFooterText = computed(() => {
  if (adminMapError.value) {
    return '当前已切换到外链模式，可直接跳转高德继续查看路线。'
  }

  return hasMachineCoordinates(adminMapMachine.value)
    ? `经纬度 ${machineCoordinateText(adminMapMachine.value)}`
    : '当前柜机暂无坐标信息。'
})

const escapeHtml = (text) => String(text || '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#39;')

const destroyAdminMapInstance = () => {
  if (adminMapInstance) {
    adminMapInstance.destroy()
    adminMapInstance = null
  }
}

const destroyAdminPreviewMapInstance = () => {
  if (adminPreviewMapInstance) {
    adminPreviewMapInstance.destroy()
    adminPreviewMapInstance = null
    adminPreviewInfoWindow = null
  }
}

const ensureAmapLoaded = async () => {
  if (window.AMap) return window.AMap
  if (!AMAP_KEY) throw new Error('missing-amap-key')

  if (AMAP_SECURITY_CODE && !window._AMapSecurityConfig) {
    window._AMapSecurityConfig = { securityJsCode: AMAP_SECURITY_CODE }
  }

  if (!amapLoaderPromise) {
    amapLoaderPromise = new Promise((resolve, reject) => {
      const existingScript = document.querySelector('script[data-amap-sdk="true"]')
      if (existingScript) {
        existingScript.addEventListener('load', () => resolve(window.AMap), { once: true })
        existingScript.addEventListener('error', () => reject(new Error('amap-load-failed')), { once: true })
        return
      }

      const script = document.createElement('script')
      script.src = `https://webapi.amap.com/maps?v=2.0&key=${AMAP_KEY}`
      script.async = true
      script.defer = true
      script.dataset.amapSdk = 'true'
      script.onload = () => resolve(window.AMap)
      script.onerror = () => reject(new Error('amap-load-failed'))
      document.head.appendChild(script)
    })
  }

  return amapLoaderPromise
}

const renderAdminMap = async (machine) => {
  adminMapError.value = ''

  if (!hasMachineCoordinates(machine)) {
    adminMapError.value = '当前柜机暂无坐标信息，无法渲染地图。'
    destroyAdminMapInstance()
    return
  }

  adminMapLoading.value = true

  try {
    const AMap = await ensureAmapLoaded()
    await nextTick()

    if (!adminMapContainer.value) {
      adminMapError.value = '地图容器未就绪，请稍后重试。'
      return
    }

    destroyAdminMapInstance()

    const position = [Number(machine.longitude), Number(machine.latitude)]
    adminMapInstance = new AMap.Map(adminMapContainer.value, {
      zoom: 15,
      center: position,
      resizeEnable: true,
      viewMode: '2D',
      mapStyle: 'amap://styles/whitesmoke'
    })

    const marker = new AMap.Marker({ position, title: machine.name, anchor: 'bottom-center' })
    adminMapInstance.add(marker)
    adminMapInstance.setFitView([marker], false, [48, 48, 48, 48])
    adminMapInstance.resize()

    const infoWindow = new AMap.InfoWindow({
      offset: new AMap.Pixel(0, -28),
      content: `
        <div style="min-width: 180px; padding: 4px 2px; color: #2c3e50;">
          <div style="font-weight: 700; margin-bottom: 6px;">${escapeHtml(machine.name)}</div>
          <div style="font-size: 12px; line-height: 1.6; color: #6b7280;">${escapeHtml(machine.location)}</div>
        </div>
      `
    })
    infoWindow.open(adminMapInstance, position)
  } catch (error) {
    console.error(error)
    destroyAdminMapInstance()
    adminMapError.value = error.message === 'missing-amap-key'
      ? '尚未配置高德地图 Key，当前无法加载内嵌地图。'
      : '高德地图加载失败，请稍后重试。'
  } finally {
    adminMapLoading.value = false
  }
}

const viewAdminMachineMap = async (machine) => {
  adminMapMachine.value = machine
  showMachineMapModal.value = true
  await nextTick()
  await renderAdminMap(machine)
}

const renderAdminPreviewMap = async () => {
  adminPreviewMapError.value = ''

  if (currentView.value !== 'machines') {
    destroyAdminPreviewMapInstance()
    return
  }

  if (!filteredAdminMappableMachines.value.length) {
    adminPreviewMapError.value = '当前筛选结果没有可展示坐标的柜机。'
    destroyAdminPreviewMapInstance()
    return
  }

  adminPreviewMapLoading.value = true

  try {
    const AMap = await ensureAmapLoaded()
    await nextTick()

    if (!adminPreviewMapContainer.value) {
      adminPreviewMapError.value = '预览地图容器未就绪，请稍后再试。'
      return
    }

    destroyAdminPreviewMapInstance()

    const firstMachine = filteredAdminMappableMachines.value[0]
    adminPreviewMapInstance = new AMap.Map(adminPreviewMapContainer.value, {
      zoom: 13,
      center: [Number(firstMachine.longitude), Number(firstMachine.latitude)],
      resizeEnable: true,
      viewMode: '2D',
      mapStyle: 'amap://styles/whitesmoke'
    })

    adminPreviewInfoWindow = new AMap.InfoWindow({ offset: new AMap.Pixel(0, -28) })

    const markers = filteredAdminMappableMachines.value.map((machine) => {
      const marker = new AMap.Marker({
        position: [Number(machine.longitude), Number(machine.latitude)],
        title: machine.name,
        anchor: 'bottom-center'
      })

      marker.on('click', () => {
        adminPreviewInfoWindow.setContent(`
          <div style="min-width: 180px; padding: 4px 2px; color: #2c3e50;">
            <div style="font-weight: 700; margin-bottom: 6px;">${escapeHtml(machine.name)}</div>
            <div style="font-size: 12px; line-height: 1.6; color: #6b7280;">${escapeHtml(machine.location)}</div>
          </div>
        `)
        adminPreviewInfoWindow.open(adminPreviewMapInstance, marker.getPosition())
      })

      marker.__machine = machine
      return marker
    })

    adminPreviewMapInstance.add(markers)
    adminPreviewMapInstance.setFitView(markers, false, [42, 42, 42, 42])
    adminPreviewMapInstance.resize()
  } catch (error) {
    console.error(error)
    destroyAdminPreviewMapInstance()
    adminPreviewMapError.value = error.message === 'missing-amap-key'
      ? '尚未配置高德地图 Key，无法展示柜机预览地图。'
      : '柜机预览地图加载失败，请稍后重试。'
  } finally {
    adminPreviewMapLoading.value = false
  }
}

const focusAdminMachineOnPreview = async (machine) => {
  if (!hasMachineCoordinates(machine)) {
    alert('当前柜机暂无坐标信息')
    return
  }

  if (currentView.value !== 'machines') {
    currentView.value = 'machines'
    await nextTick()
  }

  if (!adminPreviewMapInstance) {
    await renderAdminPreviewMap()
  }

  if (!adminPreviewMapInstance) {
    return
  }

  const position = [Number(machine.longitude), Number(machine.latitude)]
  adminPreviewMapInstance.setZoomAndCenter(15, position)
  adminPreviewInfoWindow?.setContent(`
    <div style="min-width: 180px; padding: 4px 2px; color: #2c3e50;">
      <div style="font-weight: 700; margin-bottom: 6px;">${escapeHtml(machine.name)}</div>
      <div style="font-size: 12px; line-height: 1.6; color: #6b7280;">${escapeHtml(machine.location)}</div>
    </div>
  `)
  adminPreviewInfoWindow?.open(adminPreviewMapInstance, position)
}

const resetMachineFilter = () => {
  machineFilter.value = { keyword: '', status: '' }
}

const closeAdminMachineMap = () => {
  showMachineMapModal.value = false
}

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

const fetchVolunteerBinds = async () => {
  try {
    const res = await axios.get(`${API_BASE}/admin/volunteer-binds`)
    volunteerBinds.value = res.data || { bindings: [], volunteers: [], total_binded: 0, total_unbinded: 0 }
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
  const fetchMap = { dashboard: fetchDashboard, users: fetchUsers, machines: fetchMachines, donations: fetchDonations, pickups: fetchPickups, notifications: fetchNotifications, 'volunteer-binds': fetchVolunteerBinds }
  if (fetchMap[newView]) fetchMap[newView]()
  if (['dashboard', 'analysis'].includes(newView)) setTimeout(initCharts, 100)
  if (newView !== 'machines') {
    destroyAdminPreviewMapInstance()
    adminPreviewMapLoading.value = false
    adminPreviewMapError.value = ''
  }
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

watch(showMachineMapModal, (visible) => {
  if (!visible) {
    destroyAdminMapInstance()
    adminMapMachine.value = null
    adminMapLoading.value = false
    adminMapError.value = ''
  }
})

watch([currentView, filteredAdminMachines], async ([view]) => {
  if (view !== 'machines') {
    return
  }

  await renderAdminPreviewMap()
})

onBeforeUnmount(() => {
  destroyAdminMapInstance()
  destroyAdminPreviewMapInstance()
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
.volunteer-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 24px; }
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
.toolbar-machine { margin-bottom: 16px; }
.machine-coord-text { font-size: 12px; color: #0f766e; font-weight: 600; }
.machine-coord-empty { font-size: 12px; color: #95a5a6; }
.machine-action-buttons { display: flex; gap: 8px; flex-wrap: wrap; }
.admin-machine-map-card {
  margin-bottom: 18px;
  padding: 18px;
  border-radius: 16px;
  background: linear-gradient(180deg, #fafcfe 0%, #ffffff 100%);
  border: 1px solid rgba(78, 205, 196, 0.18);
}
.admin-machine-map-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 14px;
}
.admin-machine-map-header h3 {
  margin: 0 0 6px;
  font-size: 18px;
  color: var(--dark);
}
.admin-machine-map-header p {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: #64748b;
}
.admin-machine-map-count {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(78, 205, 196, 0.12);
  color: #0f766e;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}
.admin-machine-preview-shell {
  position: relative;
  height: 280px;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(44, 62, 80, 0.08);
  background: linear-gradient(180deg, #f7fafc 0%, #eef4f7 100%);
}
.admin-machine-preview-canvas {
  width: 100%;
  height: 100%;
}

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
.rules-container { display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.95fr); gap: 24px; align-items: stretch; }
.rules-card { background: #fff; border-radius: 18px; padding: 30px; box-shadow: var(--shadow); min-height: 100%; }
.rules-header { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.rules-icon { font-size: 28px; }
.rules-header h3 { font-size: 22px; font-weight: 700; color: var(--dark); margin: 0; }
.rules-desc { color: #7f8c8d; font-size: 14px; margin-bottom: 24px; line-height: 1.6; }
.rules-form { display: flex; flex-direction: column; gap: 18px; }
.rule-item { display: flex; justify-content: space-between; align-items: center; padding: 18px 20px; background: linear-gradient(180deg, #fafbfc 0%, #f5f7fa 100%); border-radius: 14px; border: 1px solid #edf1f5; }
.rule-label { display: flex; align-items: center; gap: 12px; font-size: 15px; font-weight: 600; color: var(--dark); }
.rule-icon { font-size: 20px; }
.rule-control { display: flex; align-items: center; gap: 12px; }
.rule-unit { color: #7f8c8d; font-size: 14px; }
.rules-actions { margin-top: 24px; display: flex; justify-content: center; }
.rules-actions .el-button { padding: 12px 40px; font-size: 16px; }

.rules-tips { background: linear-gradient(180deg, #ffffff 0%, #fff8f8 100%); border-radius: 18px; padding: 28px 24px; box-shadow: var(--shadow); min-height: 100%; display: flex; flex-direction: column; }
.rules-tips-header { margin-bottom: 18px; }
.rules-tips h4 { font-size: 18px; font-weight: 700; color: var(--dark); margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
.rules-tips-header p { font-size: 13px; line-height: 1.7; color: #7f8c8d; margin: 0; }
.rules-tips-body { display: flex; flex-direction: column; gap: 14px; flex: 1; }
.tip-block { padding: 16px 16px 14px; border-radius: 14px; background: rgba(255, 255, 255, 0.82); border: 1px solid #f4dede; }
.tip-block-title { font-size: 15px; font-weight: 700; color: var(--dark); margin-bottom: 6px; }
.tip-block p { margin: 0; font-size: 13px; color: #666; line-height: 1.7; }
.rules-note { margin-top: 16px; padding: 14px 16px; border-radius: 14px; background: rgba(255, 107, 107, 0.08); color: #6b7280; font-size: 13px; line-height: 1.6; display: flex; flex-direction: column; gap: 4px; }
.rules-note-label { font-size: 12px; font-weight: 700; color: var(--primary); letter-spacing: 0.04em; }

.admin-map-overlay {
  position: fixed;
  inset: 0;
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(15, 23, 42, 0.48);
  backdrop-filter: blur(4px);
}
.admin-map-modal {
  width: min(100%, 760px);
  background: #fff;
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 30px 80px rgba(15, 23, 42, 0.22);
}
.admin-map-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 10px;
}
.admin-map-kicker {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--primary);
  margin-bottom: 6px;
}
.admin-map-header h3 {
  margin: 0;
  font-size: 24px;
  color: var(--dark);
}
.admin-map-close {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: #f3f6f9;
  color: #51606d;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
}
.admin-map-address {
  margin: 0 0 14px;
  font-size: 14px;
  line-height: 1.7;
  color: #64748b;
}
.admin-map-shell {
  position: relative;
  height: 380px;
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(44, 62, 80, 0.08);
  background: linear-gradient(180deg, #f7fafc 0%, #eef4f7 100%);
}
.admin-map-canvas {
  width: 100%;
  height: 100%;
}
.admin-map-canvas-hidden {
  visibility: hidden;
}
.admin-map-state {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 12px;
  padding: 24px;
  text-align: center;
  color: #64748b;
  font-size: 14px;
  line-height: 1.7;
}
.admin-map-state-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(247, 250, 252, 0.96) 0%, rgba(238, 244, 247, 0.96) 100%);
}
.admin-map-state-error {
  background: linear-gradient(180deg, #fff7f7 0%, #fff 100%);
}
.admin-map-state p {
  margin: 0;
}
.admin-map-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-top: 14px;
}
.admin-map-tip {
  flex: 1;
  font-size: 13px;
  color: #64748b;
  line-height: 1.7;
}
.admin-map-links {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}
.admin-map-link-btn,
.admin-map-link-text {
  color: #0f766e;
  font-weight: 700;
  text-decoration: none;
}
.admin-map-link-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 140px;
  padding: 10px 14px;
  border-radius: 10px;
  background: rgba(78, 205, 196, 0.16);
}

@media (max-width: 1200px) {
  .analysis-grid { grid-template-columns: 1fr; }
  .rules-container { grid-template-columns: 1fr; }
}

@media (max-width: 900px) {
  .rules-card,
  .rules-tips {
    padding: 24px 20px;
  }

  .admin-machine-map-header {
    flex-direction: column;
    align-items: stretch;
  }

  .rule-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
  }

  .rule-control {
    width: 100%;
    justify-content: space-between;
  }

  .admin-map-modal {
    padding: 18px;
  }

  .admin-map-shell {
    height: 320px;
  }

  .admin-map-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .admin-map-links {
    align-items: stretch;
  }
}
</style>
