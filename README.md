# 爱心柜公益管理系统 (LoveCabinet)

**项目地点**：江苏省无锡市梁溪区扬名街道

为街道特殊群体提供免费物资领取，为爱心商户提供捐赠渠道，并为管理者提供数据决策支持。

## 项目主程

- 项目负责人：Peiyuan Xue(NPU)
- 欢迎您向本项目commit

## 项目简介

本系统是一个基于 **FastAPI** + **Vue3** 开发的公益售货机管理系统，支持：

- 用户端（特殊群体/商户）：扫码开门、领取物资、投放捐赠
- 管理后台：用户管理、柜机管理、数据分析、规则配置

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI + JSON 文件存储 |
| 前端 | Vue3 + Element Plus + ECharts |
| 认证 | JWT Token |
| 构建工具 | Vite |

## 项目结构

```
OPC-counter/
├── backend/               # 后端代码
│   ├── main.py           # FastAPI主程序
│   └── data_store.py     # JSON数据存储模块
├── frontend/             # 前端代码
│   ├── index.html        # 用户端入口
│   ├── admin/            # 管理后台
│   └── src/              # 用户端
├── requirements.txt      # Python依赖
└── README.md             # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
# 后端依赖
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
```

### 1.1 配置高德地图 Key

用户端现在支持在 APP 中直接查看柜机的高德地图位置。

1. 进入 frontend 目录
2. 复制 frontend/.env.example 为 frontend/.env
3. 填入你自己的高德 Web JS API Key 和安全密钥

```bash
cd frontend
cp .env.example .env
```

```env
VITE_AMAP_KEY=你的高德Web端Key
VITE_AMAP_SECURITY_CODE=你的高德安全密钥
```

如果没有配置这两个变量，APP 不会报错，但内嵌地图会自动退化为提示信息和高德外链打开方式。

### 2. 启动后端服务

```bash
cd backend
python main.py
```

后端服务启动在：http://localhost:8000

首次启动会自动创建 `data.json` 文件并初始化测试数据。

### 3. 启动前端服务

```bash
cd frontend
npm run dev
```

前端服务启动在：http://localhost:3000

- **用户端**: http://localhost:3000/
- **管理后台**: http://localhost:3000/admin/

### 用户端地图能力

- 登录前“附近柜机”支持直接查看柜机地图位置
- 特殊群体“选择柜机”支持地图弹层查看具体位置
- 商户“新增投放”在选中柜机后可直接查看该柜机地图位置

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

## 数据存储

系统使用 JSON 文件存储所有数据，数据文件位于 `backend/data.json`。

### 数据结构

```json
{
  "users": [],           // 用户数据
  "machines": [],        // 柜机数据
  "donations": [],       // 捐赠记录
  "pickups": [],         // 领取记录
  "rules": [],           // 规则配置
  "notifications": [],   // 通知消息
  "auth_tokens": []      // 认证令牌
}
```

### 重置数据

删除 `backend/data.json` 文件，重启服务即可重新初始化数据。

## API接口文档

启动后端后访问：http://localhost:8000/docs

### 核心接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/auth/login` | POST | 手机号+验证码登录 |
| `/auth/request_otp` | POST | 请求验证码 |
| `/machine/open` | POST | 开门（需鉴权） |
| `/admin/dashboard` | GET | 仪表盘数据 |
| `/admin/users` | GET/POST | 用户管理 |
| `/admin/analysis/user-portrait` | GET | 用户画像分析 |

## 构建生产版本

```bash
cd frontend
npm run build
```

构建产物在 `frontend/dist/` 目录。

## 许可证

MIT License
