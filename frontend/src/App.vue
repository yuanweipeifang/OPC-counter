<template>
  <div class="app-container">
    <!-- 登录页 -->
    <div v-if="!isLoggedIn" class="page-shell login-shell">
      <div class="header">
        <h1><span class="heart-icon">❤️</span> 爱心柜</h1>
        <p>为爱续航，让温暖传递</p>
      </div>

      <div class="page-body login-body">
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

        <div class="card card-scroll card-soft">
          <div class="section-header">
            <div class="section-title section-title-tight">📍 附近柜机</div>
            <div class="view-switch">
              <button :class="['view-switch-btn', nearbyView === 'list' ? 'active' : '']" @click="nearbyView = 'list'">列表</button>
              <button :class="['view-switch-btn', nearbyView === 'map' ? 'active' : '']" @click="nearbyView = 'map'">地图</button>
            </div>
          </div>

          <div v-if="nearbyView === 'list'" class="machine-list">
            <div v-for="m in machines" :key="m.id" class="machine-card machine-card-sm" @click="selectMachine(m)">
              <div class="machine-info">
                <h3>🏪 {{ m.name }}</h3>
                <p>{{ m.location }}</p>
                <div class="machine-meta" v-if="hasMachineCoordinates(m)">
                  <span class="location-pill">高德地图可查看</span>
                </div>
              </div>
              <div class="machine-side-panel">
                <button class="btn-ghost-action" @click.stop="viewMachineMap(m)">地图</button>
                <span class="machine-status" :class="m.status"></span>
                <span class="status-text">{{ m.status === 'online' ? '在线' : '离线' }}</span>
              </div>
            </div>
          </div>

          <div v-else class="nearby-map-panel">
            <div class="nearby-map-shell">
              <div ref="nearbyMapContainer" class="nearby-map-container" :class="{ 'map-container-hidden': !!nearbyMapError }"></div>
              <div v-if="nearbyMapLoading" class="map-state map-state-overlay">附近柜机地图加载中...</div>
              <div v-else-if="nearbyMapError" class="map-state map-state-error map-state-overlay">
                <p>{{ nearbyMapError }}</p>
              </div>
            </div>
            <div class="nearby-map-tip">点击地图标点可查看柜机信息，点击下方卡片可打开完整地图弹层。</div>
            <div class="nearby-machine-strip">
              <button
                v-for="m in mappableMachines"
                :key="m.id"
                class="nearby-machine-pill"
                @click="viewMachineMap(m)"
              >
                {{ m.id }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 用户首页 -->
    <div v-else class="page-shell auth-shell">
      <div class="header">
        <h1><span class="heart-icon">❤️</span> 爱心柜</h1>
        <p>欢迎回来, {{ userInfo.name }}</p>
        <div class="user-badge">
          <span>🎭</span>
          <span>{{ roleText }}</span>
        </div>
      </div>

      <div class="page-body auth-body">
      <!-- 特殊群体界面 -->
      <div v-if="userInfo.role === 'special_group'" class="content-stack">
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

        <div v-if="activeTab === 'pickups'" class="card card-scroll list-card">
          <div class="section-title">📋 领取记录</div>
          <div class="content-scroll-list">
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
        </div>

        <div v-if="activeTab === 'machines'" class="card card-scroll card-soft">
          <div class="section-title">🏪 选择柜机</div>
          <div class="search-box">
            <input
              v-model="machineSearch"
              type="text"
              placeholder="搜索柜机名称、位置或编号"
              class="search-input"
            >
          </div>
          <div class="machine-list">
            <div v-for="m in filteredMachines" :key="m.id" class="machine-card machine-card-sm">
              <div class="machine-info">
                <h3>{{ m.name }}</h3>
                <p>{{ m.location }}</p>
                <div class="machine-meta" v-if="hasMachineCoordinates(m)">
                  <span class="location-pill">{{ machineCoordinateText(m) }}</span>
                </div>
              </div>
              <div class="machine-actions">
                <button class="btn-map" @click="viewMachineMap(m)">🗺️ 地图</button>
                <button class="btn-open-door" @click="openMachine(m)">🚪 开门</button>
              </div>
            </div>
            <p v-if="filteredMachines.length === 0" class="empty-tip empty-tip-compact">未找到匹配的柜机</p>
          </div>
        </div>

        <div v-if="!isVolunteerUser" class="card compact-card">
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
            <p class="bind-info">
              <span class="bind-name">{{ userInfo.volunteer_name || '志愿者' }}</span>
              <span class="bind-phone">{{ userInfo.volunteer_phone }}</span>
            </p>
            <button class="btn btn-outline" @click="showUnbindConfirm">解除绑定</button>
          </div>
        </div>
      </div>

      <!-- 商户界面 -->
      <div v-else-if="userInfo.role === 'merchant'" class="content-stack">
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

        <div v-if="activeTab === 'donations'" class="card card-scroll list-card">
          <div class="section-title">🎁 投放记录</div>
          <div class="content-scroll-list">
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
        </div>

        <div v-if="activeTab === 'new'" class="card card-scroll form-card">
          <div class="section-title">➕ 新增投放</div>

          <div class="content-scroll-list">
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

            <div v-if="selectedDonationMachine" class="machine-preview-card">
              <div class="machine-preview-copy">
                <div class="machine-preview-label">当前柜机位置</div>
                <div class="machine-preview-name">{{ selectedDonationMachine.name }}</div>
                <div class="machine-preview-location">{{ selectedDonationMachine.location }}</div>
              </div>
              <button class="btn-map" @click="viewMachineMap(selectedDonationMachine)">🗺️ 查看地图</button>
            </div>

            <button class="btn btn-success" @click="createDonation">✨ 确认投放</button>
          </div>
        </div>
      </div>

      <div v-else class="content-stack">
        <div class="card">
          <div class="empty-state">
            <div class="empty-icon">🔒</div>
            <p>请联系管理员分配角色</p>
          </div>
        </div>
      </div>

      <div class="footer">
        <button class="btn btn-outline" @click="logout">🚪 退出登录</button>
      </div>
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

    <div v-if="showMapModal" class="modal-overlay modal-overlay-map" @click.self="closeMapModal">
      <div class="modal modal-map">
        <div class="map-modal-header">
          <div>
            <div class="map-modal-kicker">高德地图定位</div>
            <h3>{{ mapMachine?.name || '柜机位置' }}</h3>
          </div>
          <button class="modal-close" @click="closeMapModal">×</button>
        </div>

        <p class="map-address">{{ mapMachine?.location || '暂无地址信息' }}</p>

        <div class="map-shell">
          <div ref="mapContainer" class="map-container" :class="{ 'map-container-hidden': !!mapError }"></div>
          <div v-if="mapLoading" class="map-state map-state-overlay">地图加载中...</div>
          <div v-else-if="mapError" class="map-state map-state-error map-state-overlay">
            <p>{{ mapError }}</p>
            <a v-if="mapExternalUrl" :href="mapExternalUrl" target="_blank" rel="noopener noreferrer" class="map-link-btn">在高德地图打开</a>
          </div>
        </div>

        <div class="map-footer">
          <div class="map-footer-left">
            <div class="map-tip">{{ mapFooterText }}</div>
            <div class="map-copy-actions">
              <button class="map-copy-btn" @click="copyMachineAddress">复制地址</button>
              <button class="map-copy-btn" @click="copyMachineCoordinates">复制坐标</button>
            </div>
          </div>
          <div class="map-link-actions">
            <a v-if="mapNavigationUrl" :href="mapNavigationUrl" target="_blank" rel="noopener noreferrer" class="map-link-btn map-link-nav">
              🧭 导航到这里
            </a>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 解除绑定确认弹窗 -->
    <div v-if="showUnbindModal" class="modal-overlay" @click.self="showUnbindModal = false">
      <div class="modal">
        <div class="modal-icon">🤔</div>
        <h3>确认解除绑定</h3>
        <p class="modal-text">确定要解除与 <strong>{{ userInfo.volunteer_name || '志愿者' }}</strong> 的绑定关系吗？</p>
        <button class="btn btn-primary" @click="confirmUnbind">确定解除</button>
        <button class="btn btn-outline" @click="showUnbindModal = false">取消</button>
      </div>
    </div>
    
    <!-- 消息提示 -->
    <div v-if="message" class="message-toast">{{ message }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch, onBeforeUnmount } from 'vue'
import axios from 'axios'

const API_BASE = '/api'
const AMAP_KEY = import.meta.env.VITE_AMAP_KEY || ''
const AMAP_SECURITY_CODE = import.meta.env.VITE_AMAP_SECURITY_CODE || ''

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
const machineSearch = ref('')
const machines = ref([])
const myPickups = ref([])
const myDonations = ref([])
const nearbyView = ref('list')

// UI状态
const otpCountdown = ref(0)
const showOpenModal = ref(false)
const showUnbindModal = ref(false)
const selectedMachine = ref(null)
const opening = ref(false)
const showMapModal = ref(false)
const mapMachine = ref(null)
const mapLoading = ref(false)
const mapError = ref('')
const mapContainer = ref(null)
const nearbyMapContainer = ref(null)
const nearbyMapLoading = ref(false)
const nearbyMapError = ref('')

let amapLoaderPromise = null
let amapInstance = null
let nearbyMapInstance = null
let nearbyClusterInstance = null

const roleText = computed(() => {
  const map = { special_group: '特殊群体', merchant: '爱心商户' }
  return map[userInfo.value?.role] || '用户'
})

const isVolunteerUser = computed(() => {
  return userInfo.value?.role === 'special_group' && userInfo.value?.category === '志愿者'
})

const filteredMachines = computed(() => {
  const keyword = machineSearch.value.trim().toLowerCase()

  if (!keyword) {
    return machines.value
  }

  return machines.value.filter((machine) => {
    const fields = [machine.id, machine.name, machine.location]
    return fields.some((field) => String(field || '').toLowerCase().includes(keyword))
  })
})

const selectedDonationMachine = computed(() => {
  return machines.value.find((machine) => String(machine.id) === String(donationForm.value.machine_id)) || null
})

const mappableMachines = computed(() => machines.value.filter((machine) => hasMachineCoordinates(machine)))

const mapExternalUrl = computed(() => {
  const machine = mapMachine.value

  if (!hasMachineCoordinates(machine)) {
    return ''
  }

  const name = encodeURIComponent(machine.name || '爱心柜')
  const address = encodeURIComponent(machine.location || '')
  return `https://uri.amap.com/marker?position=${machine.longitude},${machine.latitude}&name=${name}&src=LoveCabinet&coordinate=gaode&callnative=0&address=${address}`
})

const mapNavigationUrl = computed(() => {
  const machine = mapMachine.value

  if (!hasMachineCoordinates(machine)) {
    return ''
  }

  const name = encodeURIComponent(machine.name || '爱心柜')
  return `https://uri.amap.com/navigation?to=${machine.longitude},${machine.latitude},${name}&mode=car&policy=1&src=LoveCabinet&coordinate=gaode&callnative=0`
})

const mapWalkingUrl = computed(() => {
  const machine = mapMachine.value

  if (!hasMachineCoordinates(machine)) {
    return ''
  }

  const name = encodeURIComponent(machine.name || '爱心柜')
  return `https://uri.amap.com/navigation?to=${machine.longitude},${machine.latitude},${name}&mode=walk&policy=1&src=LoveCabinet&coordinate=gaode&callnative=0`
})

const mapFooterText = computed(() => {
  if (mapError.value) {
    return '当前已切换到兜底模式，你仍然可以通过高德外链查看定位。'
  }

  return hasMachineCoordinates(mapMachine.value)
    ? `经纬度 ${machineCoordinateText(mapMachine.value)}`
    : '当前柜机缺少经纬度信息。'
})

const machineCoordinateCopyText = computed(() => {
  return hasMachineCoordinates(mapMachine.value)
    ? `${Number(mapMachine.value.latitude)},${Number(mapMachine.value.longitude)}`
    : ''
})

const donationStatusText = (status) => {
  const map = { active: '进行中', expired: '已过期', all_claimed: '已领完' }
  return map[status] || status
}

const hasMachineCoordinates = (machine) => {
  return Number.isFinite(Number(machine?.latitude)) && Number.isFinite(Number(machine?.longitude))
}

const machineCoordinateText = (machine) => {
  if (!hasMachineCoordinates(machine)) {
    return '暂无坐标'
  }

  return `${Number(machine.latitude).toFixed(4)}, ${Number(machine.longitude).toFixed(4)}`
}

const escapeHtml = (text) => {
  return String(text || '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

const destroyMapInstance = () => {
  if (amapInstance) {
    amapInstance.destroy()
    amapInstance = null
  }
}

const destroyNearbyMapInstance = () => {
  if (nearbyClusterInstance && typeof nearbyClusterInstance.setMap === 'function') {
    nearbyClusterInstance.setMap(null)
    nearbyClusterInstance = null
  }

  if (nearbyMapInstance) {
    nearbyMapInstance.destroy()
    nearbyMapInstance = null
  }
}

const ensureAmapPlugins = async (AMap, plugins) => {
  await new Promise((resolve) => {
    AMap.plugin(plugins, resolve)
  })
}

const copyText = async (text, successMessage) => {
  if (!text) {
    showMessage('暂无可复制内容')
    return
  }

  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
    } else {
      const textArea = document.createElement('textarea')
      textArea.value = text
      textArea.style.position = 'fixed'
      textArea.style.opacity = '0'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
    }
    showMessage(successMessage)
  } catch (error) {
    console.error(error)
    showMessage('复制失败，请手动复制')
  }
}

const copyMachineAddress = () => {
  copyText(mapMachine.value?.location || '', '地址已复制')
}

const copyMachineCoordinates = () => {
  copyText(machineCoordinateCopyText.value, '经纬度已复制')
}

const ensureAmapLoaded = async () => {
  if (window.AMap) {
    return window.AMap
  }

  if (!AMAP_KEY) {
    throw new Error('missing-amap-key')
  }

  if (AMAP_SECURITY_CODE && !window._AMapSecurityConfig) {
    window._AMapSecurityConfig = {
      securityJsCode: AMAP_SECURITY_CODE
    }
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

const renderMap = async (machine) => {
  mapError.value = ''

  if (!hasMachineCoordinates(machine)) {
    mapError.value = '当前柜机暂无坐标信息，无法渲染地图。'
    return
  }

  mapLoading.value = true

  try {
    const AMap = await ensureAmapLoaded()
    await ensureAmapPlugins(AMap, ['AMap.MarkerCluster'])
    await nextTick()

    if (!mapContainer.value) {
      mapError.value = '地图容器未就绪，请重试。'
      return
    }

    destroyMapInstance()

    const position = [Number(machine.longitude), Number(machine.latitude)]
    amapInstance = new AMap.Map(mapContainer.value, {
      zoom: 15,
      center: position,
      resizeEnable: true,
      viewMode: '2D',
      mapStyle: 'amap://styles/whitesmoke'
    })

    const marker = new AMap.Marker({
      position,
      title: machine.name,
      anchor: 'bottom-center'
    })

    amapInstance.add(marker)
    amapInstance.setFitView([marker], false, [48, 48, 48, 48])
  amapInstance.resize()

    const infoWindow = new AMap.InfoWindow({
      offset: new AMap.Pixel(0, -28),
      content: `
        <div style="min-width: 170px; padding: 4px 2px; color: #2c3e50;">
          <div style="font-weight: 700; margin-bottom: 6px;">${escapeHtml(machine.name)}</div>
          <div style="font-size: 12px; line-height: 1.6; color: #6b7280;">${escapeHtml(machine.location)}</div>
        </div>
      `
    })

    infoWindow.open(amapInstance, position)
  } catch (error) {
    console.error(error)
    destroyMapInstance()
    if (error.message === 'missing-amap-key') {
      mapError.value = '尚未配置高德地图 Key，当前无法加载内嵌地图。'
    } else {
      mapError.value = '高德地图加载失败，请稍后重试或改用外部地图打开。'
    }
  } finally {
    mapLoading.value = false
  }
}

const renderNearbyMap = async () => {
  nearbyMapError.value = ''

  if (!mappableMachines.value.length) {
    nearbyMapError.value = '当前没有可展示坐标的柜机。'
    destroyNearbyMapInstance()
    return
  }

  nearbyMapLoading.value = true

  try {
    const AMap = await ensureAmapLoaded()
    await nextTick()

    if (!nearbyMapContainer.value) {
      nearbyMapError.value = '附近柜机地图容器未就绪，请稍后再试。'
      return
    }

    destroyNearbyMapInstance()

    const firstMachine = mappableMachines.value[0]
    nearbyMapInstance = new AMap.Map(nearbyMapContainer.value, {
      zoom: 13,
      center: [Number(firstMachine.longitude), Number(firstMachine.latitude)],
      resizeEnable: true,
      viewMode: '2D',
      mapStyle: 'amap://styles/whitesmoke'
    })

    const infoWindow = new AMap.InfoWindow({
      offset: new AMap.Pixel(0, -28)
    })

    const markers = mappableMachines.value.map((machine) => {
      const marker = new AMap.Marker({
        position: [Number(machine.longitude), Number(machine.latitude)],
        title: machine.name,
        anchor: 'bottom-center'
      })

      marker.on('click', () => {
        infoWindow.setContent(`
          <div style="min-width: 170px; padding: 4px 2px; color: #2c3e50;">
            <div style="font-weight: 700; margin-bottom: 6px;">${escapeHtml(machine.name)}</div>
            <div style="font-size: 12px; line-height: 1.6; color: #6b7280; margin-bottom: 8px;">${escapeHtml(machine.location)}</div>
            <div style="font-size: 12px; color: #0f766e;">点击下方卡片查看详情地图</div>
          </div>
        `)
        infoWindow.open(nearbyMapInstance, marker.getPosition())
      })

      return marker
    })

    nearbyClusterInstance = new AMap.MarkerCluster(nearbyMapInstance, markers, {
      gridSize: 64,
      maxZoom: 16,
      averageCenter: true,
      renderClusterMarker(context) {
        const count = context.count
        const div = document.createElement('div')
        div.className = 'nearby-cluster-marker'
        div.innerHTML = `<span>${count}</span>`
        context.marker.setContent(div)
        context.marker.setOffset(new AMap.Pixel(-22, -22))
      }
    })

    nearbyMapInstance.setFitView(markers, false, [36, 36, 36, 36])
    nearbyMapInstance.resize()
  } catch (error) {
    console.error(error)
    destroyNearbyMapInstance()
    nearbyMapError.value = error.message === 'missing-amap-key'
      ? '尚未配置高德地图 Key，无法展示附近柜机地图。'
      : '附近柜机地图加载失败，请稍后重试。'
  } finally {
    nearbyMapLoading.value = false
  }
}

const viewMachineMap = async (machine) => {
  mapMachine.value = machine
  showMapModal.value = true
  await nextTick()
  await renderMap(machine)
}

const closeMapModal = () => {
  showMapModal.value = false
}

const selectMachine = (machine) => {
  viewMachineMap(machine)
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
  machineSearch.value = ''
  nearbyView.value = 'list'
  closeMapModal()
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
    const res = await axios.post(`${API_BASE}/special/bind-volunteer`, null, { params: { token: token.value, volunteer_phone: volunteerPhone.value } })
    showMessage('绑定成功')
    userInfo.value.volunteer_phone = volunteerPhone.value
    userInfo.value.volunteer_name = res.data.volunteer_name || '志愿者'
    volunteerPhone.value = ''
  } catch (e) {
    showMessage(e.response?.data?.detail || '绑定失败')
  }
}

const showUnbindConfirm = () => {
  showUnbindModal.value = true
}

const confirmUnbind = async () => {
  try {
    await axios.post(`${API_BASE}/special/unbind-volunteer`, null, { params: { token: token.value } })
    userInfo.value.volunteer_phone = null
    userInfo.value.volunteer_name = null
    volunteerPhone.value = ''
    showUnbindModal.value = false
    showMessage('已解除绑定')
  } catch (e) {
    showMessage(e.response?.data?.detail || '解绑失败')
  }
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

watch(showMapModal, (visible) => {
  if (!visible) {
    destroyMapInstance()
    mapMachine.value = null
    mapLoading.value = false
    mapError.value = ''
  }
})

watch([nearbyView, machines, isLoggedIn], async ([view, machineList, loggedIn]) => {
  if (view !== 'map' || loggedIn || !machineList.length) {
    if (view !== 'map' || loggedIn) {
      destroyNearbyMapInstance()
      nearbyMapLoading.value = false
      nearbyMapError.value = ''
    }
    return
  }

  await renderNearbyMap()
})

onBeforeUnmount(() => {
  destroyMapInstance()
  destroyNearbyMapInstance()
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

html, body, #app {
  height: 100%;
  overflow: hidden;
}

body { 
  font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif; 
  background: linear-gradient(180deg, #FFF5F5 0%, #F8F9FA 100%);
  min-height: 100vh;
}

.app-container { 
  max-width: 480px; 
  margin: 0 auto; 
  height: 100vh;
  max-height: 100vh;
  background: #fff;
  box-shadow: 0 0 40px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  overflow-x: hidden;
  position: relative;
}

@supports (height: 100dvh) {
  .app-container {
    height: 100dvh;
    max-height: 100dvh;
  }
}

.page-shell {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header { 
  background: var(--gradient); 
  color: #fff; 
  padding: 24px 20px 20px; 
  text-align: center;
  position: relative;
  flex-shrink: 0;
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

.header h1 { font-size: 26px; margin-bottom: 6px; font-weight: 700; position: relative; }
.header p { font-size: 14px; opacity: 0.95; position: relative; }

.heart-icon { display: inline-block; animation: heartbeat 1.5s ease-in-out infinite; }
@keyframes heartbeat { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }

.page-body {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px;
  overflow: hidden;
}

.login-body > .card,
.login-body > .card-scroll {
  min-height: 0;
}

.content-stack {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow: hidden;
}

.card { background: #fff; border-radius: 18px; padding: 14px; margin: 0; box-shadow: var(--shadow); }
.card-soft { background: linear-gradient(180deg, #ffffff 0%, #fffaf9 100%); border: 1px solid rgba(255, 107, 107, 0.08); }
.card-scroll { display: flex; flex-direction: column; flex: 1; min-height: 0; overflow: hidden; }
.list-card,
.form-card,
.login-body .card-scroll { flex: 1; }
.compact-card { padding: 12px 14px; }
.content-scroll-list { flex: 1; min-height: 0; overflow-y: auto; padding-right: 4px; }
.machine-list { flex: 1; overflow-y: auto; min-height: 0; padding-right: 4px; }
.content-scroll-list::-webkit-scrollbar,
.machine-list::-webkit-scrollbar { width: 4px; }
.content-scroll-list::-webkit-scrollbar-thumb,
.machine-list::-webkit-scrollbar-thumb { background: var(--primary-light); border-radius: 4px; }

.btn { width: 100%; padding: 14px; border: none; border-radius: 12px; font-size: 15px; font-weight: 600; cursor: pointer; transition: all 0.3s; }
.btn-primary { background: var(--gradient); color: #fff; box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3); }
.btn-primary:hover { box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4); }
.btn-success { background: var(--gradient-blue); color: #fff; box-shadow: 0 4px 15px rgba(78, 205, 196, 0.3); }
.btn-outline { background: transparent; color: var(--primary); border: 2px solid var(--primary); }
.btn-sm { width: auto; padding: 10px 20px; font-size: 14px; }
.btn:active { transform: scale(0.98); }

.input-group { margin-bottom: 14px; }
.input-group label { display: block; margin-bottom: 8px; color: var(--dark); font-weight: 600; font-size: 13px; }
.input-group input, .input-group select { width: 100%; padding: 12px 14px; border: 2px solid #FFE8E8; border-radius: 12px; font-size: 14px; background: #FFFCFC; }
.input-group input:focus, .input-group select:focus { outline: none; border-color: var(--primary); background: #fff; box-shadow: 0 0 0 4px rgba(255, 107, 107, 0.1); }

.search-box {
  margin-bottom: 12px;
  flex-shrink: 0;
}

.search-input {
  width: 100%;
  padding: 12px 14px;
  border: 2px solid #FFE8E8;
  border-radius: 12px;
  font-size: 14px;
  background: #FFFCFC;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary);
  background: #fff;
  box-shadow: 0 0 0 4px rgba(255, 107, 107, 0.1);
}

.otp-btn { 
  background: var(--primary-light); 
  color: var(--primary); 
  border: 2px solid var(--primary); 
  font-weight: 600; 
  width: 110px; 
  min-width: 110px; 
  max-width: 110px; 
  height: 46px;
  padding: 0; 
  white-space: nowrap; 
  flex-shrink: 0; 
  display: inline-flex; 
  align-items: center; 
  justify-content: center; 
  text-align: center;
  font-size: 14px;
}
.otp-row { display: flex; gap: 8px; align-items: center; }
.otp-input { flex: 1; min-width: 0; padding: 12px 14px; border: 2px solid #FFE8E8; border-radius: 12px; font-size: 14px; background: #FFFCFC; }
.otp-input:focus { outline: none; border-color: var(--primary); background: #fff; box-shadow: 0 0 0 4px rgba(255, 107, 107, 0.1); }

.list-item { padding: 14px 0; border-bottom: 2px dashed #FFE8E8; display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.list-item:last-child { border-bottom: none; }
.item-name { font-weight: 600; color: var(--dark); }
.item-time { font-size: 12px; color: #95A5A6; }

.status-tag { padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.status-active { background: #E8F8F5; color: #27AE60; }
.status-expired { background: #FDEDEC; color: #E74C3C; }
.status-pending { background: #FEF9E7; color: #F39C12; }

.tabs { display: flex; background: #F8F9FA; padding: 4px; border-radius: 12px; }
.tab { flex: 1; text-align: center; padding: 10px; border-radius: 9px; cursor: pointer; font-weight: 600; color: #7F8C8D; transition: all 0.3s; font-size: 14px; }
.tab.active { background: #fff; color: var(--primary); box-shadow: 0 2px 8px rgba(0,0,0,0.08); }

.machine-card { 
  background: #fff; 
  border-radius: 14px; 
  padding: 16px; 
  margin: 8px 0; 
  box-shadow: var(--shadow); 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  transition: all 0.3s; 
  border: 2px solid transparent;
  gap: 16px;
}
.machine-card-sm { 
  padding: 12px 14px; 
  margin: 6px 0; 
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.1);
}
.machine-card:hover { border-color: var(--primary); transform: translateX(4px); }
.machine-info { flex: 1; min-width: 0; }
.machine-info h3 { font-size: 14px; margin-bottom: 4px; color: var(--dark); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.machine-info p { font-size: 12px; color: #95A5A6; line-height: 1.4; }
.machine-meta { margin-top: 8px; }
.location-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 9px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  color: #0f766e;
  background: rgba(78, 205, 196, 0.14);
}
.machine-side-panel {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: center;
  gap: 8px;
  flex-shrink: 0;
}
.machine-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
}
.btn-ghost-action,
.btn-map {
  border: none;
  border-radius: 10px;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.25s ease;
  white-space: nowrap;
}
.btn-ghost-action {
  color: var(--primary);
  background: rgba(255, 107, 107, 0.1);
}
.btn-ghost-action:hover,
.btn-map:hover {
  transform: translateY(-1px);
}
.btn-map {
  color: #0f766e;
  background: rgba(78, 205, 196, 0.16);
}
.btn-open-door {
  background: var(--gradient);
  color: #fff;
  border: none;
  padding: 9px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
  transition: all 0.3s;
}
.btn-open-door:hover { transform: scale(1.05); box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3); }
.machine-status { width: 12px; height: 12px; border-radius: 50%; display: inline-block; margin-right: 6px; }
.machine-status.online { background: #27AE60; box-shadow: 0 0 8px #27AE60; }
.machine-status.offline { background: #E74C3C; }
.status-text { font-size: 12px; color: #95A5A6; }

.stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.stat-item { background: linear-gradient(135deg, #FFF5F5 0%, #FFF 100%); padding: 16px 12px; border-radius: 14px; text-align: center; border: 2px solid #FFE8E8; }
.stat-value { font-size: 28px; font-weight: 700; background: var(--gradient); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; color: transparent; }
.stat-label { font-size: 13px; color: #95A5A6; margin-top: 6px; font-weight: 500; }

.section-title { font-size: 17px; font-weight: 700; color: var(--dark); margin-bottom: 12px; padding-left: 10px; border-left: 4px solid var(--primary); }
.section-title-tight { margin-bottom: 0; }
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}
.view-switch {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px;
  border-radius: 999px;
  background: rgba(255, 107, 107, 0.08);
  flex-shrink: 0;
}
.view-switch-btn {
  border: none;
  background: transparent;
  color: #7f8c8d;
  font-size: 12px;
  font-weight: 700;
  padding: 8px 12px;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.25s ease;
}
.view-switch-btn.active {
  color: var(--primary);
  background: #fff;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.12);
}

.quick-actions { display: flex; gap: 10px; }
.quick-action { flex: 1; background: var(--gradient); color: #fff; padding: 12px 10px; border-radius: 12px; text-align: center; cursor: pointer; transition: all 0.3s; }
.quick-action:hover { transform: translateY(-3px); box-shadow: var(--shadow-hover); }
.quick-action-icon { font-size: 20px; margin-bottom: 3px; }
.quick-action-label { font-size: 12px; font-weight: 600; }

.user-badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.2); padding: 6px 14px; border-radius: 20px; font-size: 14px; margin-top: 12px; }

.bind-success { text-align: center; padding: 12px 8px; }
.bind-icon { font-size: 34px; margin-bottom: 10px; }
.bind-label { color: var(--dark); font-weight: 600; margin-bottom: 8px; }
.bind-info { display: flex; flex-direction: column; gap: 4px; margin-bottom: 12px; }
.bind-name { color: var(--dark); font-size: 16px; font-weight: 600; }
.bind-phone { color: #64748b; font-size: 14px; }

.machine-preview-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px;
  margin-bottom: 12px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(78, 205, 196, 0.12) 0%, rgba(255, 255, 255, 0.95) 100%);
  border: 1px solid rgba(78, 205, 196, 0.18);
}
.machine-preview-copy { min-width: 0; }
.machine-preview-label { font-size: 11px; font-weight: 700; letter-spacing: 0.04em; color: #0f766e; margin-bottom: 4px; }
.machine-preview-name { font-size: 14px; font-weight: 700; color: var(--dark); margin-bottom: 3px; }
.machine-preview-location { font-size: 12px; line-height: 1.5; color: #6b7280; }

.nearby-map-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
  min-height: 0;
}
.nearby-map-shell {
  position: relative;
  min-height: 220px;
  flex: 1;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(78, 205, 196, 0.2);
  background: linear-gradient(180deg, #f7fafc 0%, #eef4f7 100%);
}
.nearby-map-container {
  width: 100%;
  height: 100%;
}
.nearby-map-tip {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.6;
}
.nearby-machine-strip {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 2px;
}
.nearby-machine-strip::-webkit-scrollbar {
  height: 4px;
}
.nearby-machine-strip::-webkit-scrollbar-thumb {
  background: rgba(255, 107, 107, 0.18);
  border-radius: 999px;
}
.nearby-machine-pill {
  border: none;
  border-radius: 999px;
  padding: 8px 12px;
  background: #fff;
  color: var(--dark);
  box-shadow: 0 2px 10px rgba(44, 62, 80, 0.08);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
}

.empty-tip, .empty-state p { text-align: center; color: #95A5A6; padding: 24px; }
.empty-tip-compact { padding: 16px 8px; }
.empty-icon { font-size: 48px; margin-bottom: 16px; }
.empty-state { text-align: center; padding: 24px; }

.tip { margin-top: 14px; font-size: 12px; color: #95A5A6; text-align: center; }
.tip strong { color: var(--primary); }

.footer { padding-top: 4px; flex-shrink: 0; }

@media (max-width: 480px) {
  .header {
    padding: 18px 16px 14px;
  }

  .header h1 {
    font-size: 23px;
  }

  .header p,
  .user-badge {
    font-size: 13px;
  }

  .page-body,
  .content-stack {
    gap: 8px;
  }

  .page-body {
    padding: 8px;
  }

  .card {
    border-radius: 16px;
    padding: 12px;
  }

  .quick-actions {
    gap: 8px;
  }

  .stats-grid {
    gap: 10px;
  }
}

@media (max-height: 760px) {
  .header {
    padding: 18px 16px 14px;
  }

  .header h1 {
    font-size: 22px;
  }

  .page-body {
    gap: 8px;
    padding: 8px;
  }

  .card {
    padding: 12px;
  }

  .quick-action {
    padding: 10px 8px;
  }

  .btn {
    padding: 12px;
  }

  .section-title {
    margin-bottom: 10px;
  }

  .machine-card-sm {
    padding: 10px 12px;
  }

  .search-box {
    margin-bottom: 10px;
  }
}

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(44, 62, 80, 0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-overlay-map { z-index: 1100; padding: 16px; }
.modal { background: #fff; border-radius: 24px; padding: 28px; width: 90%; max-width: 360px; text-align: center; }
.modal-icon { font-size: 48px; margin-bottom: 12px; }
.modal h3 { color: var(--dark); margin-bottom: 8px; }
.modal-text { color: #7F8C8D; margin-bottom: 24px; }
.modal-text strong { color: var(--primary); }
.modal .btn { margin-top: 12px; }

.modal-map {
  width: min(100%, 440px);
  max-width: 440px;
  padding: 18px;
  text-align: left;
  border-radius: 24px;
}
.map-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}
.map-modal-kicker {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--primary);
  text-transform: uppercase;
  margin-bottom: 6px;
}
.modal-close {
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 50%;
  background: #f4f6f8;
  color: #51606d;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
}
.map-address {
  margin: 0 0 12px;
  font-size: 13px;
  line-height: 1.6;
  color: #6b7280;
}
.map-shell {
  position: relative;
  height: 320px;
  border-radius: 18px;
  overflow: hidden;
  background: linear-gradient(180deg, #f7fafc 0%, #eef4f7 100%);
  border: 1px solid rgba(44, 62, 80, 0.08);
}
.map-container {
  width: 100%;
  height: 100%;
}
.map-container-hidden {
  visibility: hidden;
}
.map-state {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  text-align: center;
  color: #64748b;
  font-size: 14px;
  line-height: 1.7;
}
.map-state-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(247, 250, 252, 0.96) 0%, rgba(238, 244, 247, 0.96) 100%);
}
.map-state-error {
  background: linear-gradient(180deg, #fff7f7 0%, #fff 100%);
}
.map-state p {
  margin: 0;
}
.map-link-btn,
.map-link-text {
  color: #0f766e;
  text-decoration: none;
  font-weight: 700;
}
.map-link-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 140px;
  padding: 10px 14px;
  border-radius: 10px;
  background: rgba(78, 205, 196, 0.16);
}
.map-footer {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-top: 14px;
}
.map-footer-left {
  flex: 1;
  min-width: 0;
}
.map-link-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex-shrink: 0;
}
.map-copy-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}
.map-copy-btn {
  border: none;
  border-radius: 8px;
  padding: 8px 14px;
  background: #f1f5f9;
  color: #475569;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.map-copy-btn:hover {
  background: #e2e8f0;
  color: var(--dark);
}
.map-tip {
  font-size: 12px;
  line-height: 1.5;
  color: #64748b;
  margin-bottom: 4px;
}
.map-link-nav {
  width: 100%;
  min-width: auto;
}
.nearby-cluster-marker {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
  color: #fff;
  font-size: 13px;
  font-weight: 800;
  box-shadow: 0 10px 24px rgba(255, 107, 107, 0.28);
  border: 3px solid rgba(255, 255, 255, 0.92);
}

.message-toast { position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: var(--dark); color: #fff; padding: 14px 28px; border-radius: 12px; z-index: 2000; font-weight: 500; }

@media (max-width: 480px) {
  .machine-actions {
    gap: 6px;
  }

  .section-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .btn-map,
  .btn-open-door {
    width: 100%;
  }

  .machine-preview-card,
  .map-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .map-link-actions {
    width: 100%;
  }

  .map-link-nav {
    text-align: center;
  }

  .map-copy-actions {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .map-copy-btn {
    flex: 1;
    min-width: 80px;
    text-align: center;
  }

  .map-shell {
    height: 280px;
  }
}
</style>
