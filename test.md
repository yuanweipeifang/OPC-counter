**快速开始**
- 在项目根目录打开两个终端。
- 终端1启动后端：

```bash
cd /home/kali/OPC-counter/backend
export SMARTVM_ENABLED=true
export SMARTVM_BASE_URL="http://localhost:8000/mock-smartvm"
export SMARTVM_CLIENT_ID="2066260320115214"
export SMARTVM_SIGN_KEY="vS4bzyH0kiAqwQ4kTXxAzapIVK6EiOjV"
python main.py
```

- 终端2启动前端：

```bash
cd /home/kali/OPC-counter/frontend
npm install
npm run dev -- --host 0.0.0.0 --port 3000
```

- 打开三个页面：
- 用户端：`http://localhost:3000/`
- 管理端：`http://localhost:3000/admin/`
- 测试端：`http://localhost:3000/tester/`

**先测联调链路（推荐第一步）**
- 在测试端 `http://localhost:3000/tester/`：
- 确认 `回调基础地址 = http://localhost:8000`
- 确认 `测试设备编号 = 91120149`
- 点击“模拟开门全流程”
- 预期结果：
- 测试端日志出现 `simulate-open-flow`、`door-status`、`settlement` 成功记录
- 管理端“柜机管理”里 `91120149` 有通信更新
- 管理端“领取记录”出现新增记录（如有匹配用户）

**用户端功能测试**
- 登录（验证码固定 `123456`）：
- 特殊群体：`18912340001`
- 商户：`18912340030`
- 重点测试：
- 特殊群体：开门、查看领取记录、绑定/解绑志愿者
- 商户：新增投放、查看投放记录
- 预期：
- 操作成功会有页面提示
- 对应数据会在管理端同步可见

**管理端功能测试**
- 管理员登录：
- 手机号：`13800000000`
- 验证码：`123456`
- 重点检查：
- 用户管理：增删改查
- 柜机管理：能看到 `91120149`
- 捐赠管理、领取记录：有分页数据
- 志愿者绑定：关系展示正常
- 规则配置：保存后生效
- 通知中心：可查看通知

**比赛文档四个回调地址（本地）**
- 门状态推送：`http://localhost:8000/callbacks/smartvm/door-status`
- 订单完结：`http://localhost:8000/callbacks/smartvm/settlement`
- 补扣推送：`http://localhost:8000/callbacks/smartvm/retry-settlement`
- 退款地址：`http://localhost:8000/callbacks/smartvm/refund`

**测试完成后清理**
- 在测试端点击“清空日志”
- 如需重置业务数据：停止后端，删除 `backend/data.json`，再启动后端自动初始化

**代码入口参考**
- 本地联调与测试接口：[main.py](file:///home/kali/OPC-counter/backend/main.py)
- 测试端页面：[TesterApp.vue](file:///home/kali/OPC-counter/frontend/tester/TesterApp.vue)
- 启动与说明文档：[README.md](file:///home/kali/OPC-counter/README.md)

如果你愿意，我可以下一步按“比赛验收顺序”给你一份逐条勾选清单（每一步点哪里、看哪里、什么算通过）。