# SmartVM 联调请求样例

本文档提供可直接复制的请求样例，便于你在 Postman 或命令行进行联调。

## Python 脚本一键联调（推荐）

仓库根目录新增 `smartvm_cli.py`，支持自动签名并直接请求测试平台。

先在当前终端设置：

```bash
export SMARTVM_BASE_URL="http://pre.smartvm.cn"
export SMARTVM_CLIENT_ID="你的clientId"
export SMARTVM_SIGN_KEY="你的签名key"
```

示例：

```bash
# 获取设备商品列表
python smartvm_cli.py goods --device-code 91120149 --door-num 1

# 开门
python smartvm_cli.py opendoor \
  --user-id u10001 \
  --device-code 91120149 \
  --phone 13800138000 \
  --pay-style 2 \
  --door-num 1

# 付款成功异步通知（路径可按平台实际调整）
python smartvm_cli.py payment-notify \
  --order-no ORD_001 \
  --event-id EVT_001 \
  --transaction-id TRA_001 \
  --device-code 91120149 \
  --amount 0

# 交互模式
python smartvm_cli.py interactive
```

## 1. 准备

假设本地后端地址：

- `LOCAL_API=http://localhost:8000`

启动前配置环境变量（后端进程需要）：

```bash
export SMARTVM_ENABLED=true
export SMARTVM_BASE_URL="http://pre.smartvm.cn"
export SMARTVM_CLIENT_ID="你的clientId"
export SMARTVM_SIGN_KEY="你的签名key"
export SMARTVM_PAYMENT_NOTIFY_PATH="/api/pay/container/paySuccessNotify"
```

## 2. 本系统 -> 映翰通（自动签名）

这些接口由本地后端自动完成 `clientId/nonceStr/sign`。

### 2.1 获取设备商品列表

```bash
curl -X POST "$LOCAL_API/integration/smartvm/get-cabinet-goods" \
  -H "Content-Type: application/json" \
  -d '{
    "deviceCode": "00000001",
    "doorNum": "1"
  }'
```

### 2.2 开门接口（直连版）

```bash
curl -X POST "$LOCAL_API/integration/smartvm/opendoor" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "10001",
    "eventId": "evt_20260326_0001",
    "deviceCode": "9100003",
    "payStyle": "2",
    "doorNum": "1",
    "phone": "1861198283"
  }'
```

### 2.3 付款成功异步通知（由本系统代发给映翰通）

```bash
curl -X POST "$LOCAL_API/integration/smartvm/payment-success-notify" \
  -H "Content-Type: application/json" \
  -d '{
    "orderNo": "98002323H3243424243234H22342344",
    "eventId": "0000000000001",
    "transactionId": "49938493843849343434",
    "deviceCode": "98002323",
    "amount": 0,
    "openId": ""
  }'
```

### 2.4 业务开门入口（你原系统入口）

当 `SMARTVM_ENABLED=true` 时，会自动走映翰通开门接口。

```bash
curl -X POST "$LOCAL_API/machine/open" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "YM001",
    "token": "你的登录token",
    "pay_style": "2",
    "door_num": "1"
  }'
```

## 3. 映翰通 -> 本系统回调（需要签名）

以下是你可以手工模拟的回调接口：

- `/callbacks/smartvm/door-status`
- `/callbacks/smartvm/settlement`
- `/callbacks/smartvm/retry-settlement`
- `/callbacks/smartvm/refund`

### 3.1 先生成签名（Python）

把下面脚本保存为临时文件 `sign.py`，执行后得到 `sign`：

```python
import json
import hashlib

SIGN_KEY = "你的签名key"

payload = {
    "eventId": "000000000000",
    "deviceCode": "90000001",
    "status": "SUCCESS",
    "clientId": "你的clientId",
    "nonceStr": "nonce_20260326_001"
}

items = []
for k in sorted(payload.keys()):
    v = payload[k]
    if v is None or v == "":
        continue
    if isinstance(v, (dict, list)):
        v = json.dumps(v, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    items.append(f"{k}={v}")

string1 = "&".join(items)
string_sign_temp = f"{string1}&key={SIGN_KEY}"
sign = hashlib.md5(string_sign_temp.encode("utf-8")).hexdigest().upper()
print(sign)
```

### 3.2 门状态推送（示例）

将下面 `sign` 替换为你算出来的值：

```bash
curl -X POST "$LOCAL_API/callbacks/smartvm/door-status" \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "000000000000",
    "deviceCode": "90000001",
    "status": "SUCCESS",
    "clientId": "你的clientId",
    "nonceStr": "nonce_20260326_001",
    "sign": "这里填计算后的签名"
  }'
```

### 3.3 结算商品推送（示例）

```bash
curl -X POST "$LOCAL_API/callbacks/smartvm/settlement" \
  -H "Content-Type: application/json" \
  -d '{
    "orderNo": "98002323H3243424243234H22342344",
    "eventId": "0000000000001",
    "phone": "1861197973",
    "deviceCode": "98002323",
    "amount": 0,
    "notifyUrl": "http://example.com/pay-notify",
    "detail": [
      {
        "goodsName": "百事可乐",
        "quantity": 2,
        "unitPrice": 0,
        "goodsId": "9932323"
      }
    ],
    "clientId": "你的clientId",
    "nonceStr": "nonce_20260326_002",
    "sign": "这里填计算后的签名"
  }'
```

### 3.4 补扣商品推送（示例）

```bash
curl -X POST "$LOCAL_API/callbacks/smartvm/retry-settlement" \
  -H "Content-Type: application/json" \
  -d '{
    "orgOrderNo": "98002323H3243424243234H22342344",
    "orderNo": "98002323H3243424243234H22342345",
    "eventId": "0000000000001",
    "phone": "1861197973",
    "deviceCode": "98002323",
    "amount": 100,
    "noticeUrl": "http://example.com/pay-notify",
    "detail": [
      {
        "goodsName": "百事可乐",
        "quantity": 1,
        "unitPrice": 100,
        "goodsId": "9932323"
      }
    ],
    "clientId": "你的clientId",
    "nonceStr": "nonce_20260326_003",
    "sign": "这里填计算后的签名"
  }'
```

### 3.5 退款接口（示例）

```bash
curl -X POST "$LOCAL_API/callbacks/smartvm/refund" \
  -H "Content-Type: application/json" \
  -d '{
    "orderNo": "98002323H3243424243234H22342344",
    "transactionId": "49938493843849343434",
    "refundNo": "234234234234243",
    "deviceCode": "98002323",
    "amount": 0,
    "clientId": "你的clientId",
    "nonceStr": "nonce_20260326_004",
    "sign": "这里填计算后的签名"
  }'
```

## 4. 返回判断

成功通常为：

```json
{
  "code": 200,
  "message": "请求成功"
}
```

签名错误通常为：

```json
{
  "code": 400,
  "message": "签名错误"
}
```
