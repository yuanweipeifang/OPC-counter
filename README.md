# 爱心柜公益管理系统 (LoveCabinet)

项目地点：江苏省无锡市梁溪区扬名街道。

为街道特殊群体提供免费物资领取，为爱心商户提供捐赠渠道，并为管理者提供数据决策支持。

## 项目简介

本系统基于 FastAPI + Vue 3 开发，包含两套前端入口：

- 用户端：特殊群体与商户登录、开门领取、商户投放、地图查看
- 管理端：用户管理、柜机管理、捐赠管理、领取记录、分析看板、规则配置、通知中心
- 本地联调测试端：无公网时模拟第三方平台回调与联调流程（`/tester/`）

## 当前功能状态

- 已支持用户管理 CRUD（增删改查）
- 已支持捐赠与领取记录分页
- 已支持登录日志与操作日志写入数据层

## 映翰通接口联调（pre.smartvm.cn）

后端已增加签名与联调能力，可直接对接你提供的测试平台。

### 1. 环境变量配置

在启动后端前设置：

```bash
export SMARTVM_ENABLED=true
export SMARTVM_BASE_URL="http://pre.smartvm.cn"
export SMARTVM_CLIENT_ID="你的clientId"
export SMARTVM_SIGN_KEY="你的签名key"
# 付款成功异步通知路径（若对方有明确路径请覆盖）
export SMARTVM_PAYMENT_NOTIFY_PATH="/api/pay/container/paySuccessNotify"
```

### 2. 已对接的联调入口（本系统 -> 映翰通）

- POST /integration/smartvm/get-cabinet-goods
	- 对应：/api/pay/container/getCabinetGoodsInfo
- POST /integration/smartvm/opendoor
	- 对应：/api/pay/container/opendoor
- POST /integration/smartvm/payment-success-notify
	- 对应：付款成功异步通知（路径由 SMARTVM_PAYMENT_NOTIFY_PATH 指定）
- POST /machine/open
	- 当 SMARTVM_ENABLED=true 时，会自动走映翰通开门接口并返回 orderNo

### 3. 已新增的回调验签入口（映翰通 -> 本系统）

- POST /callbacks/smartvm/door-status
- POST /callbacks/smartvm/settlement
- POST /callbacks/smartvm/retry-settlement
- POST /callbacks/smartvm/refund

以上回调均按文档规则做 clientId/nonceStr/sign 验签；签名错误返回：

```json
{
	"code": 400,
	"message": "签名错误"
}
```
- 已支持手机号脱敏展示
- 已支持志愿者绑定关系校验与异常数据清理

说明：当前为演示/开发形态，验证码固定为 123456，数据存储为本地 JSON。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI、Uvicorn、Pydantic、PyJWT |
| 前端 | Vue 3、Element Plus、Axios、ECharts |
| 地图 | 高德 Web JS API（可选） |
| 存储 | JSON 文件（backend/data.json） |
| 构建 | Vite |

## 项目结构

```text
OPC-counter/
├── backend/
│   ├── main.py
│   ├── data_store.py
│   └── data.json
├── frontend/
│   ├── index.html
│   ├── admin/
│   │   ├── index.html
│   │   └── AdminApp.vue
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── docs/
│   └── tasks.md
├── requirements.txt
└── README.md
```

## 环境要求

- Python 3.9+
- Node.js 18+
- npm 9+

## 快速开始

### 1. 安装依赖

```bash
# 在项目根目录执行
pip install -r requirements.txt

cd frontend
npm install
```

### 2. 配置地图 Key（可选）

```bash
cd frontend
cp .env.example .env
```

在 .env 中填写：

```env
VITE_AMAP_KEY=你的高德Web端Key
VITE_AMAP_SECURITY_CODE=你的高德安全密钥
```

如果不配置，页面会自动退化为提示/外链，不影响核心业务流程。

### 3. 启动后端

```bash
cd backend
python main.py
```

后端地址：http://localhost:8000

首次启动会自动初始化 backend/data.json。

### 4. 启动前端

```bash
cd frontend
npm run dev
```

前端地址：http://localhost:3000

- 用户端：http://localhost:3000/
- 管理端：http://localhost:3000/admin/
- 本地联调测试端：http://localhost:3000/tester/

## 无公网本地三端联调

当无法提供公网回调地址时，可在本机完成“用户端 + 管理端 + 测试端”三端联调：

1. 启动后端（建议开启联调签名配置）：

```bash
cd backend
export SMARTVM_CLIENT_ID="你的clientId"
export SMARTVM_SIGN_KEY="你的签名key"
python main.py
```

2. 启动前端：

```bash
cd frontend
npm run dev
```

3. 打开测试端：`http://localhost:3000/tester/`

- 在“测试配置”中确认 `callback_base_url`（本机通常为 `http://localhost:8000`）
- 复制并使用四个回调地址：
  - 门状态：`/callbacks/smartvm/door-status`
  - 订单完结：`/callbacks/smartvm/settlement`
  - 补扣推送：`/callbacks/smartvm/retry-settlement`
  - 退款：`/callbacks/smartvm/refund`
- 点击测试端按钮即可触发对应回调，管理端可实时查看状态与记录变化
- 测试设备已内置为 `91120149`（符合比赛文档要求）

## 测试账号

| 角色 | 手机号 | 验证码 | 社区 |
|------|--------|--------|------|
| 管理员 | 13800000000 | 123456 | 扬名街道办事处 |
| 特殊群体 | 18912340001 | 123456 | 扬名社区 |
| 特殊群体 | 18912340004 | 123456 | 五星社区 |
| 特殊群体 | 18912340007 | 123456 | 清名桥社区 |
| 志愿者 | 18912340020 | 123456 | 扬名社区 |
| 商户 | 18912340030 | 123456 | 家乐福超市(清名路店) |
| 商户 | 18912340031 | 123456 | 大润发超市(五星店) |

## 常用接口

后端文档地址：http://localhost:8000/docs

| 接口 | 方法 | 说明 |
|------|------|------|
| /auth/login | POST | 手机号+验证码登录 |
| /auth/request_otp | POST | 请求验证码（演示环境） |
| /machine/open | POST | 开门 |
| /merchant/donate | POST | 商户投放 |
| /admin/dashboard | GET | 管理看板 |
| /admin/users | GET/POST | 用户查询/新增 |
| /admin/users/{user_id} | PUT/DELETE | 用户编辑/删除 |
| /admin/donations | GET | 捐赠列表（分页） |
| /admin/pickups | GET | 领取记录（分页） |

## 数据文件说明

系统使用 backend/data.json 持久化数据。默认结构包含：

- users
- machines
- donations
- pickups
- rules
- notifications
- auth_tokens
- admin_logs
- login_logs

重置方式：

1. 停止后端
2. 删除 backend/data.json
3. 重新启动后端自动生成初始数据

## 常见问题

### 1. 管理后台全部 401

常见原因：后端未启动，或前端 token 过期/残留。

建议处理顺序：

1. 确认后端在 8000 端口运行
2. 确认前端从 frontend 目录启动而不是其他目录
3. 清理浏览器 LocalStorage 的 admin_token 和 admin_user 后重新登录

### 2. 柜机列表看不到数据

常见原因：

- 前端代理未生效（Vite 未在 frontend 目录启动）
- backend/data.json 被清空或初始化失败

### 3. 地图不显示

检查 VITE_AMAP_KEY 与 VITE_AMAP_SECURITY_CODE 是否配置正确。

## 开发建议

- 生产环境建议迁移 PostgreSQL/MySQL
- 生产环境建议接入真实短信网关替代固定验证码
- 建议补充单元测试与接口集成测试

## 构建

```bash
cd frontend
npm run build
```

构建产物位于 frontend/dist。

## 许可证

MIT License
