"""
爱心柜公益管理系统 (LoveCabinet) - 后端API
技术栈: FastAPI + JSON 文件存储
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from threading import Thread
import jwt
import uuid
import json
import random
import os
import hashlib
from urllib.request import Request as UrlRequest, urlopen
from urllib.error import HTTPError, URLError

from data_store import store

# ============= 配置 =============
SECRET_KEY = "lovecabinet-secret-key-2024"
ALGORITHM = "HS256"
SMARTVM_BASE_URL = os.getenv("SMARTVM_BASE_URL", "http://pre.smartvm.cn")
SMARTVM_CLIENT_ID = os.getenv("SMARTVM_CLIENT_ID", "")
SMARTVM_SIGN_KEY = os.getenv("SMARTVM_SIGN_KEY", "")
SMARTVM_ENABLED = os.getenv("SMARTVM_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
SMARTVM_DEFAULT_DEVICE_CODE = os.getenv("SMARTVM_DEFAULT_DEVICE_CODE", "91120149").strip()
# 文档未给出付款成功异步通知的固定路径，默认使用常见命名，可通过环境变量覆盖。
SMARTVM_PAYMENT_NOTIFY_PATH = os.getenv("SMARTVM_PAYMENT_NOTIFY_PATH", "/api/pay/container/paySuccessNotify")

# ============= Lifespan =============
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化默认数据
    store.init_default_data()
    yield

app = FastAPI(
    title="爱心柜公益管理系统 API", 
    version="1.0.0", 
    lifespan=lifespan,
    docs_url=None,  # 禁用默认 docs
    redoc_url=None   # 禁用默认 redoc
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= 自定义API文档页面 =============
@app.get("/docs", response_class=HTMLResponse)
async def custom_docs():
    """自定义API文档页面（不依赖外部CDN）"""
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>爱心柜 API 文档</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #FF6B6B; margin-bottom: 10px; }
        .subtitle { color: #666; margin-bottom: 20px; }
        
        .endpoint { background: #fff; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden; }
        .endpoint-header { padding: 15px 20px; cursor: pointer; display: flex; align-items: center; gap: 15px; }
        .method { padding: 4px 12px; border-radius: 4px; font-weight: bold; font-size: 12px; min-width: 60px; text-align: center; }
        .method.get { background: #e8f5e9; color: #2e7d32; }
        .method.post { background: #e3f2fd; color: #1565c0; }
        .method.put { background: #fff3e0; color: #ef6c00; }
        .method.delete { background: #ffebee; color: #c62828; }
        .path { font-family: monospace; font-size: 14px; color: #333; flex: 1; }
        .desc { color: #666; font-size: 13px; }
        
        .endpoint-body { padding: 0 20px 20px; display: none; border-top: 1px solid #eee; background: #fafafa; }
        .endpoint.open .endpoint-body { display: block; }
        
        .section { margin-top: 15px; }
        .section-title { font-weight: 600; color: #333; margin-bottom: 8px; font-size: 14px; }
        
        .try-section { margin-top: 15px; padding: 15px; background: #fff; border-radius: 6px; border: 1px solid #ddd; }
        .try-section input, .try-section textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-family: monospace; font-size: 13px; margin-bottom: 10px; }
        .try-section textarea { min-height: 100px; }
        .try-btn { background: #FF6B6B; color: #fff; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-weight: 600; }
        .try-btn:hover { background: #ff5252; }
        
        .response { margin-top: 15px; padding: 15px; background: #263238; border-radius: 6px; color: #aed581; font-family: monospace; font-size: 13px; white-space: pre-wrap; max-height: 300px; overflow: auto; }
        .error { color: #ef5350; }
        
        .tag { display: inline-block; padding: 2px 8px; background: #f0f0f0; border-radius: 4px; font-size: 11px; color: #666; margin-left: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>❤️ 爱心柜 API 文档</h1>
        <p class="subtitle">公益售货机管理系统接口文档</p>
        
        <div id="endpoints"></div>
    </div>
    
    <script>
        const endpoints = [
            { method: 'POST', path: '/auth/login', desc: '手机号+验证码登录', body: '{"phone": "13900000001", "otp": "123456"}' },
            { method: 'POST', path: '/auth/request_otp', desc: '请求验证码', params: [{ name: 'phone', value: '13900000001' }] },
            { method: 'POST', path: '/auth/identify', desc: '识别用户身份', body: '{"phone": "13900000001"}' },
            { method: 'POST', path: '/machine/open', desc: '开门接口', body: '{"machine_id": "MC001", "token": "your_token"}' },
            { method: 'POST', path: '/machine/callback/结算接口', desc: '结算回调', body: '{"machine_id": "MC001", "operator": "13900000001", "items": [{"name": "矿泉水", "quantity": 1}]}' },
            { method: 'GET', path: '/admin/dashboard', desc: '仪表盘数据' },
            { method: 'GET', path: '/admin/machines', desc: '柜机列表' },
            { method: 'GET', path: '/admin/users', desc: '用户列表', params: [{ name: 'role', value: '' }, { name: 'skip', value: '0' }, { name: 'limit', value: '20' }] },
            { method: 'POST', path: '/admin/users/import', desc: '导入用户', body: '{"users": [{"phone": "13800000001", "name": "张三", "role": "special_group"}]}' },
            { method: 'GET', path: '/admin/donations', desc: '捐赠列表', params: [{ name: 'status', value: 'active' }] },
            { method: 'GET', path: '/admin/pickups', desc: '领取记录' },
            { method: 'GET', path: '/admin/rules', desc: '规则配置' },
            { method: 'POST', path: '/admin/rules', desc: '设置规则', body: '{"name": "default", "daily_limit": 3}' },
            { method: 'GET', path: '/admin/notifications', desc: '通知列表' },
            { method: 'GET', path: '/admin/analysis/user-portrait', desc: '用户画像分析' },
            { method: 'GET', path: '/admin/analysis/demand-heatmap', desc: '需求热力图' },
            { method: 'POST', path: '/merchant/donate', desc: '商户投放', params: [{ name: 'token', value: '' }], body: '{"machine_id": "MC001", "item_name": "矿泉水", "quantity": 10}' },
            { method: 'GET', path: '/merchant/donations', desc: '商户投放列表', params: [{ name: 'token', value: '' }] },
            { method: 'GET', path: '/special/my-pickups', desc: '我的领取记录', params: [{ name: 'token', value: '' }] },
            { method: 'POST', path: '/special/bind-volunteer', desc: '绑定志愿者', params: [{ name: 'token', value: '' }, { name: 'volunteer_phone', value: '' }] },
            { method: 'POST', path: '/mock/device/open', desc: '模拟开门', body: '{"device_id": "MC001"}' },
            { method: 'POST', path: '/mock/device/callback/pickup', desc: '模拟取货回调', body: '{"machine_id": "MC001", "operator": "13900000001"}' },
        ];
        
        function renderEndpoints() {
            const container = document.getElementById('endpoints');
            container.innerHTML = endpoints.map((ep, i) => `
                <div class="endpoint" id="ep-${i}">
                    <div class="endpoint-header" onclick="toggleEndpoint(${i})">
                        <span class="method ${ep.method.toLowerCase()}">${ep.method}</span>
                        <span class="path">${ep.path}</span>
                        <span class="desc">${ep.desc}</span>
                    </div>
                    <div class="endpoint-body">
                        ${ep.params ? `
                            <div class="section">
                                <div class="section-title">Query Parameters</div>
                                ${ep.params.map(p => `<input type="text" id="param-${i}-${p.name}" placeholder="${p.name}" value="${p.value}">`).join('')}
                            </div>
                        ` : ''}
                        ${ep.body ? `
                            <div class="section">
                                <div class="section-title">Request Body</div>
                                <textarea id="body-${i}">${ep.body}</textarea>
                            </div>
                        ` : ''}
                        <div class="try-section">
                            <button class="try-btn" onclick="tryEndpoint(${i}, '${ep.method}', '${ep.path}', ${ep.params ? 1 : 0}, ${ep.body ? 1 : 0})">发送请求</button>
                        </div>
                        <div class="response" id="response-${i}">点击"发送请求"查看响应</div>
                    </div>
                </div>
            `).join('');
        }
        
        function toggleEndpoint(i) {
            document.getElementById('ep-' + i).classList.toggle('open');
        }
        
        async function tryEndpoint(i, method, path, hasParams, hasBody) {
            let url = path;
            if (hasParams) {
                const endpoint = endpoints[i];
                const params = endpoint.params.map(p => {
                    const val = document.getElementById('param-' + i + '-' + p.name).value;
                    return val ? p.name + '=' + encodeURIComponent(val) : '';
                }).filter(x => x).join('&');
                if (params) url += '?' + params;
            }
            
            const options = { method };
            if (hasBody) {
                const body = document.getElementById('body-' + i).value;
                options.body = body;
                options.headers = { 'Content-Type': 'application/json' };
            }
            
            try {
                const res = await fetch(url, options);
                const data = await res.json();
                document.getElementById('response-' + i).textContent = JSON.stringify(data, null, 2);
            } catch (e) {
                document.getElementById('response-' + i).innerHTML = '<span class="error">Error: ' + e.message + '</span>';
            }
        }
        
        renderEndpoints();
    </script>
</body>
</html>
    """

# ============= Pydantic模型 =============

class UserCreate(BaseModel):
    phone: str
    name: str
    role: str
    category: Optional[str] = None
    community: Optional[str] = None

class UserUpdate(BaseModel):
    phone: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None
    category: Optional[str] = None
    community: Optional[str] = None
    daily_limit: Optional[int] = None
    used_today: Optional[int] = None
    volunteer_phone: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    phone: str
    name: str
    role: str
    category: Optional[str]
    community: Optional[str]
    volunteer_phone: Optional[str]
    daily_limit: int
    used_today: int

class MachineCreate(BaseModel):
    id: str
    name: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    api_url: str

class DonationCreate(BaseModel):
    machine_id: str
    item_name: str
    quantity: int
    expiry_days: int = 1

class RuleCreate(BaseModel):
    name: str
    daily_limit: int = 3
    category_limits: str = "{}"

class LoginRequest(BaseModel):
    phone: str
    otp: Optional[str] = None

class OpenRequest(BaseModel):
    machine_id: str
    token: str
    pay_style: str = "2"
    door_num: Optional[str] = None


class SmartvmGoodsRequest(BaseModel):
    deviceCode: str
    doorNum: Optional[str] = None


class SmartvmOpenDoorRequest(BaseModel):
    userId: str
    eventId: str
    deviceCode: str
    payStyle: str
    doorNum: Optional[str] = None
    phone: str


class SmartvmPaymentNotifyRequest(BaseModel):
    orderNo: str
    eventId: str
    transactionId: str
    deviceCode: str
    amount: int
    openId: Optional[str] = None

class LocalTestConfig(BaseModel):
    callback_base_url: str = "http://localhost:8000"
    device_code: str = "91120149"
    user_id: str = "u_local_001"
    phone: str = "13800138000"


class LocalTestTriggerRequest(BaseModel):
    payload: Optional[dict] = None
    callback_base_url: Optional[str] = None


class LocalTestSignRequest(BaseModel):
    payload: dict

class CallbackPickup(BaseModel):
    machine_id: str
    operator: str
    items: List[dict]


class SignedPushBase(BaseModel):
    clientId: str
    nonceStr: str
    sign: str


class DoorStatusPush(SignedPushBase):
    eventId: str
    deviceCode: str
    status: str
    doorIsOpen: Optional[str] = None


class SettlementDetail(BaseModel):
    goodsName: str
    quantity: int
    unitPrice: int
    goodsId: str


class SettlementPush(SignedPushBase):
    orderNo: str
    eventId: str
    phone: str
    deviceCode: str
    amount: int
    notifyUrl: str
    detail: Optional[List[SettlementDetail]] = None


class RetrySettlementPush(SignedPushBase):
    orgOrderNo: Optional[str] = None
    orOrderNo: Optional[str] = None
    orderNo: str
    eventId: str
    phone: str
    deviceCode: str
    amount: int
    noticeUrl: str
    detail: Optional[List[SettlementDetail]] = None


class RefundPush(SignedPushBase):
    orderNo: str
    transactionId: str
    refundNo: str
    deviceCode: str
    amount: int


LOCAL_TEST_STATE = {
    "config": LocalTestConfig().model_dump(),
    "logs": [],
}

MAX_LOCAL_TEST_LOGS = 200

# ============= 辅助函数 =============

def create_token(phone: str) -> str:
    """生成JWT token"""
    payload = {
        "phone": phone,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    """验证JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        return None

def _reset_daily_if_needed(user: dict):
    """重置每日使用次数"""
    now = datetime.utcnow()
    last_reset = user.get("last_reset")
    if last_reset:
        if isinstance(last_reset, str):
            last_reset = datetime.fromisoformat(last_reset)
    
    if last_reset is None or last_reset.date() < now.date():
        store.update_user(user["id"], {"used_today": 0, "last_reset": now.isoformat()})

def _is_bindable_special_group(user: Optional[dict]) -> bool:
    """可绑定志愿者的对象必须是非志愿者的特殊群体。"""
    if not user:
        return False
    return user.get("role") == "special_group" and not store._is_volunteer_user(user)


def _random_nonce() -> str:
    return uuid.uuid4().hex


def _to_sign_value(value):
    if value is None:
        return None
    if isinstance(value, str) and value == "":
        return None
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return str(value)


def _build_sign(params: dict, sign_key: str) -> str:
    sign_items = []
    for key in sorted(params.keys()):
        if key == "sign":
            continue
        sign_value = _to_sign_value(params.get(key))
        if sign_value is None:
            continue
        sign_items.append(f"{key}={sign_value}")
    string1 = "&".join(sign_items)
    string_sign_temp = f"{string1}&key={sign_key}"
    return hashlib.md5(string_sign_temp.encode("utf-8")).hexdigest().upper()


def _local_test_log(action: str, request_payload: dict, response_payload: dict):
    logs = LOCAL_TEST_STATE["logs"]
    logs.append(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "request": request_payload,
            "response": response_payload,
        }
    )
    if len(logs) > MAX_LOCAL_TEST_LOGS:
        del logs[0 : len(logs) - MAX_LOCAL_TEST_LOGS]


def _local_test_config() -> dict:
    return dict(LOCAL_TEST_STATE["config"])


def _local_signed_payload(payload: dict) -> dict:
    _require_smartvm_configured()
    out = dict(payload)
    out["clientId"] = SMARTVM_CLIENT_ID
    out["nonceStr"] = out.get("nonceStr") or _random_nonce()
    out["sign"] = _build_sign(out, SMARTVM_SIGN_KEY)
    return out


def _post_json_url(url: str, payload: dict, timeout: int = 10) -> dict:
    req = UrlRequest(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return {
                "ok": True,
                "status": resp.status,
                "data": json.loads(raw) if raw else {},
                "raw": raw,
            }
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
        parsed = body
        try:
            parsed = json.loads(body) if body else {}
        except json.JSONDecodeError:
            pass
        return {"ok": False, "status": exc.code, "data": parsed, "raw": body}
    except URLError as exc:
        return {"ok": False, "status": 0, "data": {"error": str(exc.reason)}, "raw": str(exc.reason)}


def _trigger_callback_in_background(url: str, payload: dict):
    def _runner():
        result = _post_json_url(url, payload, timeout=10)
        _local_test_log("async-callback", {"url": url, "payload": payload}, result)
    Thread(target=_runner, daemon=True).start()


def _verify_signature(payload: dict) -> bool:
    client_id = payload.get("clientId")
    provided_sign = str(payload.get("sign", "")).upper()
    if client_id != SMARTVM_CLIENT_ID or not provided_sign:
        return False

    data = dict(payload)
    data.pop("sign", None)
    expected = _build_sign(data, SMARTVM_SIGN_KEY)
    return expected == provided_sign


def _require_smartvm_configured():
    if not SMARTVM_CLIENT_ID or not SMARTVM_SIGN_KEY:
        raise HTTPException(
            status_code=500,
            detail="未配置 SMARTVM_CLIENT_ID 或 SMARTVM_SIGN_KEY，无法进行联调"
        )


def _smartvm_post(path: str, biz_payload: dict, timeout: int = 10) -> dict:
    _require_smartvm_configured()
    nonce = _random_nonce()
    payload = {
        **biz_payload,
        "clientId": SMARTVM_CLIENT_ID,
        "nonceStr": nonce,
    }
    payload["sign"] = _build_sign(payload, SMARTVM_SIGN_KEY)

    base = SMARTVM_BASE_URL.rstrip("/")
    endpoint = path if path.startswith("/") else f"/{path}"
    url = f"{base}{endpoint}"

    req = UrlRequest(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {"code": 500, "message": "空响应"}
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
        try:
            parsed = json.loads(body) if body else {}
            return {
                "code": parsed.get("code", exc.code),
                "message": parsed.get("message", f"HTTP {exc.code}"),
                "raw": parsed,
            }
        except json.JSONDecodeError:
            return {"code": exc.code, "message": body or f"HTTP {exc.code}"}
    except URLError as exc:
        return {"code": 503, "message": f"调用失败: {exc.reason}"}


def _local_default_payload(kind: str) -> dict:
    cfg = _local_test_config()
    ts = int(datetime.utcnow().timestamp())
    if kind == "door-status":
        return {
            "eventId": f"evt_local_{ts}",
            "deviceCode": cfg["device_code"],
            "status": "SUCCESS",
            "doorIsOpen": "Y",
        }
    if kind == "settlement":
        return {
            "orderNo": f"ORD_LOCAL_{ts}",
            "eventId": f"evt_local_{ts}",
            "phone": cfg["phone"],
            "deviceCode": cfg["device_code"],
            "amount": 0,
            "notifyUrl": "http://localhost:8000/mock-notify",
            "detail": [{"goodsName": "测试商品", "quantity": 1, "unitPrice": 0, "goodsId": "G_LOCAL_001"}],
        }
    if kind == "retry-settlement":
        return {
            "orgOrderNo": f"ORD_LOCAL_{ts}",
            "orderNo": f"ORD_LOCAL_RETRY_{ts}",
            "eventId": f"evt_local_{ts}",
            "phone": cfg["phone"],
            "deviceCode": cfg["device_code"],
            "amount": 100,
            "noticeUrl": "http://localhost:8000/mock-notify",
            "detail": [{"goodsName": "测试商品", "quantity": 1, "unitPrice": 100, "goodsId": "G_LOCAL_001"}],
        }
    if kind == "refund":
        return {
            "orderNo": f"ORD_LOCAL_{ts}",
            "transactionId": f"TRA_LOCAL_{ts}",
            "refundNo": f"REF_LOCAL_{ts}",
            "deviceCode": cfg["device_code"],
            "amount": 0,
        }
    raise HTTPException(status_code=400, detail=f"不支持的回调类型: {kind}")


def _local_callback_path(kind: str) -> str:
    mapping = {
        "door-status": "/callbacks/smartvm/door-status",
        "settlement": "/callbacks/smartvm/settlement",
        "retry-settlement": "/callbacks/smartvm/retry-settlement",
        "refund": "/callbacks/smartvm/refund",
    }
    path = mapping.get(kind)
    if not path:
        raise HTTPException(status_code=400, detail=f"不支持的回调类型: {kind}")
    return path


def _mock_smartvm_error(message: str, code: int = 400) -> dict:
    return {"code": code, "message": message}


def _resolve_smartvm_device_code(machine: dict) -> str:
    # 优先使用柜机上配置的第三方设备号。
    explicit = machine.get("smartvm_device_code")
    if explicit:
        return str(explicit)

    machine_id = str(machine.get("id", ""))
    if machine_id == "91120149":
        return machine_id

    # 本地联调默认映射到比赛测试设备号，避免 YM001 等本地编号导致“设备不存在”。
    if SMARTVM_DEFAULT_DEVICE_CODE:
        return SMARTVM_DEFAULT_DEVICE_CODE
    return machine_id

# ============= 认证接口 =============

@app.post("/auth/login")
def login(request: LoginRequest, req: Request):
    """
    手机号+验证码登录
    测试验证码: 123456
    """
    phone = request.phone
    
    # 查找用户
    user = store.get_user_by_phone(phone)
    if not user or not user.get("is_active", True):
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 验证码验证（测试用：123456）
    if request.otp and request.otp != "123456":
        raise HTTPException(status_code=400, detail="验证码错误")
    
    # 生成token
    token = create_token(phone)
    
    # 记录登录日志
    store.create_login_log(phone, req.client.host if req.client else "")
    
    # 更新用户每日使用次数（如果是特殊群体）
    if user.get("role") == "special_group":
        _reset_daily_if_needed(user)
        user = store.get_user_by_phone(phone)  # 重新获取
    
    # 获取志愿者信息
    volunteer_name = None
    if user.get("volunteer_phone"):
        volunteer = store.get_user_by_phone(user["volunteer_phone"])
        if volunteer:
            volunteer_name = volunteer.get("name")
    
    return {
        "token": token,
        "phone": user["phone"],
        "name": user["name"],
        "role": user["role"],
        "daily_limit": user.get("daily_limit", 3),
        "used_today": user.get("used_today", 0),
        "volunteer_phone": user.get("volunteer_phone"),
        "volunteer_name": volunteer_name
    }

@app.post("/auth/request_otp")
def request_otp(phone: str):
    """请求验证码（模拟发送）"""
    otp = "123456"
    auth = store.create_auth_token(phone, otp)
    return {
        "message": "验证码已发送（测试用：123456）",
        "token": auth["token"],
        "otp": otp
    }

@app.post("/auth/identify")
def identify(request: LoginRequest):
    """根据手机号识别用户身份"""
    user = store.get_user_by_phone(request.phone)
    if not user:
        return {"role": "guest", "exists": False}
    
    return {
        "role": user["role"],
        "name": user["name"],
        "exists": True
    }

# ============= 柜机接口 =============

@app.post("/machine/open")
def open_machine(request: OpenRequest):
    """开门接口"""
    # 验证token
    payload = verify_token(request.token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效的token")
    
    phone = payload.get("phone")
    user = store.get_user_by_phone(phone)
    if not user or not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="用户不存在或已禁用")
    
    # 检查柜机
    machine = store.get_machine_by_id(request.machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="柜机不存在")
    
    # 检查权限
    if user.get("role") not in ["special_group", "merchant"]:
        raise HTTPException(status_code=403, detail="无权限开门")
    
    # 特殊群体：检查每日限制
    if user.get("role") == "special_group":
        _reset_daily_if_needed(user)
        user = store.get_user_by_phone(phone)
        if user.get("used_today", 0) >= user.get("daily_limit", 3):
            raise HTTPException(status_code=403, detail="今日领取次数已用完")
    
    order_no = None
    smartvm_device_code = None
    # 联调模式：按第三方文档请求映翰通平台开门
    if SMARTVM_ENABLED:
        smartvm_device_code = _resolve_smartvm_device_code(machine)
        event_id = uuid.uuid4().hex
        result = _smartvm_post(
            "/api/pay/container/opendoor",
            {
                "userId": str(user.get("id")),
                "eventId": event_id,
                "deviceCode": smartvm_device_code,
                "payStyle": str(request.pay_style),
                "doorNum": request.door_num,
                "phone": str(user.get("phone")),
            },
        )
        if result.get("code") != 200:
            raise HTTPException(status_code=502, detail=f"映翰通开门失败: {result.get('message', '未知错误')}")
        order_no = (result.get("data") or {}).get("orderNo")
    else:
        # 本地演示模式：使用模拟开门
        result = _mock_open_door(machine["id"], machine.get("api_url", ""))
        if not result.get("success"):
            raise HTTPException(status_code=500, detail="开门失败")
    
    # 更新用户使用次数
    if user.get("role") == "special_group":
        store.update_user(user["id"], {"used_today": user.get("used_today", 0) + 1})
    
    return {
        "message": "开门成功",
        "machine_id": machine["id"],
        "machine_name": machine["name"],
        "mode": user["role"],
        "orderNo": order_no,
        "deviceCode": smartvm_device_code or str(machine["id"]),
    }


@app.post("/integration/smartvm/get-cabinet-goods")
def integration_get_cabinet_goods(request: SmartvmGoodsRequest):
    """调用映翰通 获取设备商品列表接口。"""
    result = _smartvm_post(
        "/api/pay/container/getCabinetGoodsInfo",
        request.model_dump(exclude_none=True),
    )
    return result


@app.post("/integration/smartvm/opendoor")
def integration_open_door(request: SmartvmOpenDoorRequest):
    """按文档字段直连映翰通开门接口，便于接口联调。"""
    result = _smartvm_post(
        "/api/pay/container/opendoor",
        request.model_dump(exclude_none=True),
    )
    return result


@app.post("/integration/smartvm/payment-success-notify")
def integration_payment_success_notify(request: SmartvmPaymentNotifyRequest):
    """调用映翰通付款成功异步通知接口（路径可通过环境变量配置）。"""
    result = _smartvm_post(
        SMARTVM_PAYMENT_NOTIFY_PATH,
        request.model_dump(exclude_none=True),
    )
    return result


@app.post("/mock-smartvm/api/pay/container/getCabinetGoodsInfo")
def mock_smartvm_get_cabinet_goods(payload: dict):
    if not _verify_signature(payload):
        return _mock_smartvm_error("签名错误")
    if str(payload.get("deviceCode")) != "91120149":
        return _mock_smartvm_error("设备不存在")
    return {
        "code": 200,
        "message": "请求成功",
        "data": [
            {
                "goodsCode": "LOCAL_GOODS_001",
                "goodsId": "LOCAL_001",
                "name": "本地联调矿泉水",
                "price": 0,
                "imageUrl": "",
            },
            {
                "goodsCode": "LOCAL_GOODS_002",
                "goodsId": "LOCAL_002",
                "name": "本地联调饼干",
                "price": 0,
                "imageUrl": "",
            },
        ],
    }


@app.post("/mock-smartvm/api/pay/container/opendoor")
def mock_smartvm_opendoor(payload: dict):
    if not _verify_signature(payload):
        return _mock_smartvm_error("签名错误")
    if str(payload.get("deviceCode")) != "91120149":
        return _mock_smartvm_error("设备不存在")

    event_id = str(payload.get("eventId", ""))
    phone = str(payload.get("phone", ""))
    if not event_id or not phone:
        return _mock_smartvm_error("参数缺失")

    order_no = f"ORD_LOCAL_{int(datetime.utcnow().timestamp())}"
    cfg = _local_test_config()
    base = cfg["callback_base_url"].rstrip("/")
    door_url = f"{base}/callbacks/smartvm/door-status"
    settlement_url = f"{base}/callbacks/smartvm/settlement"

    door_payload = _local_signed_payload(
        {
            "eventId": event_id,
            "deviceCode": "91120149",
            "status": "SUCCESS",
            "doorIsOpen": "Y",
        }
    )
    settlement_payload = _local_signed_payload(
        {
            "orderNo": order_no,
            "eventId": event_id,
            "phone": phone,
            "deviceCode": "91120149",
            "amount": 0,
            "notifyUrl": "http://localhost:8000/mock-notify",
            "detail": [{"goodsName": "本地联调矿泉水", "quantity": 1, "unitPrice": 0, "goodsId": "LOCAL_001"}],
        }
    )
    _trigger_callback_in_background(door_url, door_payload)
    _trigger_callback_in_background(settlement_url, settlement_payload)

    return {"code": 200, "message": "请求成功", "data": {"orderNo": order_no}}


@app.post("/mock-smartvm/api/pay/container/paySuccessNotify")
def mock_smartvm_payment_notify(payload: dict):
    if not _verify_signature(payload):
        return _mock_smartvm_error("签名错误")
    return {"code": 200, "message": "请求成功", "data": {"accepted": True}}


@app.get("/local-test/status")
def local_test_status():
    cfg = _local_test_config()
    base = cfg["callback_base_url"].rstrip("/")
    return {
        "smartvm_configured": bool(SMARTVM_CLIENT_ID and SMARTVM_SIGN_KEY),
        "smartvm_enabled": SMARTVM_ENABLED,
        "smartvm_base_url": SMARTVM_BASE_URL,
        "client_id": SMARTVM_CLIENT_ID,
        "device_code": cfg["device_code"],
        "callback_base_url": cfg["callback_base_url"],
        "callbacks": {
            "door_status": f"{base}/callbacks/smartvm/door-status",
            "settlement": f"{base}/callbacks/smartvm/settlement",
            "retry_settlement": f"{base}/callbacks/smartvm/retry-settlement",
            "refund": f"{base}/callbacks/smartvm/refund",
        },
    }


@app.post("/local-test/config")
def local_test_set_config(config: LocalTestConfig):
    current = _local_test_config()
    current.update(config.model_dump())
    LOCAL_TEST_STATE["config"] = current
    return {"message": "配置已更新", "config": current}


@app.get("/local-test/logs")
def local_test_logs():
    return {"logs": LOCAL_TEST_STATE["logs"]}


@app.delete("/local-test/logs")
def local_test_clear_logs():
    LOCAL_TEST_STATE["logs"] = []
    return {"message": "日志已清空"}


@app.post("/local-test/sign")
def local_test_sign(request: LocalTestSignRequest):
    payload = _local_signed_payload(request.payload)
    return {"payload": payload}


@app.post("/local-test/trigger/{kind}")
def local_test_trigger(kind: str, request: LocalTestTriggerRequest):
    payload = _local_default_payload(kind)
    if request.payload:
        payload.update(request.payload)

    signed = _local_signed_payload(payload)
    base_url = (request.callback_base_url or _local_test_config()["callback_base_url"]).rstrip("/")
    callback_url = f"{base_url}{_local_callback_path(kind)}"

    result = _post_json_url(callback_url, signed, timeout=10)
    _local_test_log(kind, {"url": callback_url, "payload": signed}, result)
    return {"kind": kind, "target": callback_url, "result": result}


@app.post("/local-test/simulate-open-flow")
def local_test_simulate_open_flow():
    cfg = _local_test_config()
    event_id = f"evt_local_{int(datetime.utcnow().timestamp())}"
    signed_open_payload = _local_signed_payload(
        {
            "userId": cfg["user_id"],
            "eventId": event_id,
            "deviceCode": cfg["device_code"],
            "payStyle": "2",
            "doorNum": "1",
            "phone": cfg["phone"],
        }
    )
    open_result = _post_json_url(
        f"{cfg['callback_base_url'].rstrip('/')}/mock-smartvm/api/pay/container/opendoor",
        signed_open_payload,
        timeout=10,
    )

    result = {"open_result": open_result}
    _local_test_log("simulate-open-flow", {"eventId": event_id}, result)
    return result


@app.post("/callbacks/smartvm/door-status")
def callback_smartvm_door_status(request: DoorStatusPush):
    payload = request.model_dump(exclude_none=True)
    if not _verify_signature(payload):
        return {"code": 400, "message": "签名错误"}

    # 仅做联调透传与状态落库
    machine = store.get_machine_by_id(request.deviceCode)
    if machine:
        if request.status == "SUCCESS":
            store.update_machine_status(request.deviceCode, "online")
        elif request.status == "FAIL":
            store.update_machine_status(request.deviceCode, "offline")

    return {
        "code": 200,
        "message": "请求成功",
        "result": {"eventId": request.eventId},
    }


@app.post("/callbacks/smartvm/settlement")
def callback_smartvm_settlement(request: SettlementPush):
    payload = request.model_dump(exclude_none=True)
    if not _verify_signature(payload):
        return {"code": 400, "message": "签名错误"}

    # 尝试复用既有领取记录逻辑，若用户不存在也保持接口可测。
    user = store.get_user_by_phone(request.phone)
    machine = store.get_machine_by_id(request.deviceCode)
    if user and machine:
        items = []
        for d in request.detail or []:
            items.append({"name": d.goodsName, "quantity": d.quantity})
        if items:
            callback_settlement(CallbackPickup(machine_id=request.deviceCode, operator=request.phone, items=items))

    return {"code": 200, "message": "请求成功"}


@app.post("/callbacks/smartvm/retry-settlement")
def callback_smartvm_retry_settlement(request: RetrySettlementPush):
    payload = request.model_dump(exclude_none=True)
    if not _verify_signature(payload):
        return {"code": 400, "message": "签名错误"}

    if request.amount <= 0:
        return {"code": 500, "message": "等待用户付款"}
    return {"code": 200, "message": "付款成功"}


@app.post("/callbacks/smartvm/refund")
def callback_smartvm_refund(request: RefundPush):
    payload = request.model_dump(exclude_none=True)
    if not _verify_signature(payload):
        return {"code": 400, "message": "签名错误"}
    return {"code": 200, "message": "请求成功"}

@app.post("/machine/callback/结算接口")
def callback_settlement(request: CallbackPickup):
    """结算回调接口"""
    # 查找操作者
    user = store.get_user_by_phone(request.operator)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查柜机
    machine = store.get_machine_by_id(request.machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="柜机不存在")
    
    pickups_created = []
    
    for item in request.items:
        item_name = item.get("name")
        quantity = item.get("quantity", 1)
        
        # 检查是否有对应的捐赠记录
        donations = store.get_donations("active")
        donation = None
        for d in donations:
            if d.get("machine_id") == request.machine_id and d.get("item_name") == item_name:
                donation = d
                break
        
        # 检查领取是否合规
        is_compliant = True
        violation_reason = None
        
        if user.get("role") == "special_group":
            _reset_daily_if_needed(user)
            if user.get("used_today", 0) > user.get("daily_limit", 3):
                is_compliant = False
                violation_reason = "超过每日领取限制"
        
        # 创建领取记录
        pickup = store.create_pickup({
            "user_id": user["id"],
            "machine_id": request.machine_id,
            "donation_id": donation["id"] if donation else None,
            "item_name": item_name,
            "quantity": quantity,
            "is_compliant": is_compliant,
            "violation_reason": violation_reason
        })
        pickups_created.append(pickup)
        
        # 更新捐赠记录数量
        if donation:
            new_qty = donation.get("quantity", 1) - quantity
            if new_qty <= 0:
                store.update_donation(donation["id"], {"quantity": 0, "status": "all_claimed"})
            else:
                store.update_donation(donation["id"], {"quantity": new_qty})
    
    # 生成告警（如果有不合规记录）
    if any(not p.get("is_compliant") for p in pickups_created):
        store.create_notification({
            "user_id": None,
            "title": "违规领取告警",
            "content": f"用户 {user['phone']} ({user['name']}) 发生违规领取",
            "type": "alert"
        })
    
    return {
        "message": "结算成功",
        "pickups_count": len(pickups_created),
        "violations": [p.get("violation_reason") for p in pickups_created if not p.get("is_compliant")]
    }

# ============= 管理后台接口 =============

@app.get("/admin/dashboard")
def dashboard():
    """管理后台首页数据"""
    return store.get_dashboard_stats()

@app.post("/admin/users/import")
def import_users(data: dict):
    """导入用户"""
    users = data.get("users", [])
    imported = store.import_users(users)
    store.create_admin_log("import_users", "admin", f"导入 {imported} 个用户")
    return {"message": f"成功导入 {imported} 个用户"}

@app.get("/admin/users")
def list_users(
    role: Optional[str] = None,
    category: Optional[str] = None,
    phone: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """用户列表"""
    users, total = store.get_users(role=role, category=category, phone=phone, skip=skip, limit=limit)
    return {"total": total, "users": users}

@app.post("/admin/users")
def create_user(request: UserCreate):
    """创建用户"""
    if store.get_user_by_phone(request.phone):
        raise HTTPException(status_code=400, detail="手机号已存在")

    user = store.create_user(request.model_dump())
    store.create_admin_log("create_user", "admin", f"创建用户 {user.get('phone')}")
    return {"message": "创建成功", "user": user}

@app.put("/admin/users/{user_id}")
def update_user(user_id: int, request: UserUpdate):
    """更新用户"""
    existing = store.get_user_by_id(user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="用户不存在")

    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    if not update_data:
        return {"message": "无更新内容", "user": existing}

    new_phone = update_data.get("phone")
    if new_phone and new_phone != existing.get("phone"):
        conflict = store.get_user_by_phone(new_phone)
        if conflict and conflict.get("id") != user_id:
            raise HTTPException(status_code=400, detail="手机号已存在")

    user = store.update_user(user_id, update_data)
    store.create_admin_log("update_user", "admin", f"更新用户 {user.get('phone')}")
    return {"message": "更新成功", "user": user}

@app.delete("/admin/users/{user_id}")
def delete_user(user_id: int):
    """删除用户"""
    existing = store.get_user_by_id(user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="用户不存在")

    if existing.get("role") == "admin":
        admin_count = len([u for u in store.get_users(role="admin", skip=0, limit=10000)[0] if u.get("is_active", True)])
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="至少保留一个管理员账号")

    ok = store.delete_user(user_id)
    if not ok:
        raise HTTPException(status_code=500, detail="删除失败")

    store.create_admin_log("delete_user", "admin", f"删除用户 {existing.get('phone')}")
    return {"message": "删除成功"}

@app.get("/admin/machines")
def list_machines():
    """柜机列表"""
    return {"machines": store.get_machines()}

@app.get("/admin/analysis/user-portrait")
def user_portrait_analysis():
    """用户画像分析"""
    return store.get_user_portrait()

@app.get("/admin/analysis/demand-heatmap")
def demand_heatmap():
    """需求热力图"""
    return store.get_demand_heatmap()

@app.get("/admin/donations")
def list_donations(status: Optional[str] = None, skip: int = 0, limit: int = 50):
    """捐赠列表"""
    donations, total = store.get_donations(status=status, skip=skip, limit=limit)
    return {"total": total, "donations": donations}

@app.get("/admin/pickups")
def list_pickups(skip: int = 0, limit: int = 50):
    """领取记录列表"""
    pickups, total = store.get_pickups(skip=skip, limit=limit)
    return {"total": total, "pickups": pickups}

@app.get("/admin/rules")
def get_rules():
    """获取规则"""
    return {"rules": store.get_rules()}

@app.post("/admin/rules")
def set_rule(request: RuleCreate):
    """设置规则"""
    rule = store.set_rule({
        "name": request.name,
        "daily_limit": request.daily_limit,
        "category_limits": request.category_limits
    })
    store.create_admin_log("set_rule", "admin", f"设置规则 {request.name}")
    return {"message": "规则设置成功", "rule": rule}

@app.get("/admin/notifications")
def list_notifications(skip: int = 0, limit: int = 20):
    """通知列表"""
    return {"notifications": store.get_notifications(skip=skip, limit=limit)}

@app.get("/admin/volunteer-binds")
def list_volunteer_binds():
    """志愿者绑定关系列表"""
    all_users = store.get_users(role=None, skip=0, limit=10000)[0]
    
    # 获取志愿者列表（category为"志愿者"的用户）
    volunteers = [u for u in all_users if store._is_volunteer_user(u)]
    
    # 获取真正需要绑定的特殊群体用户列表（排除志愿者本人）
    special_groups = [u for u in all_users if _is_bindable_special_group(u)]
    
    # 构建绑定关系
    bindings = []
    for sg in special_groups:
        if sg.get("volunteer_phone"):
            # 找到对应的志愿者
            volunteer = next((v for v in volunteers if v.get("phone") == sg["volunteer_phone"]), None)
            bindings.append({
                "special_group": {
                    "id": sg.get("id"),
                    "phone": sg.get("phone"),
                    "name": sg.get("name"),
                    "category": sg.get("category"),
                    "community": sg.get("community")
                },
                "volunteer": {
                    "id": volunteer.get("id") if volunteer else None,
                    "phone": sg.get("volunteer_phone"),
                    "name": volunteer.get("name") if volunteer else "未知",
                    "community": volunteer.get("community") if volunteer else ""
                } if sg.get("volunteer_phone") else None
            })
    
    # 未绑定的特殊群体
    unbinded = [sg for sg in special_groups if not sg.get("volunteer_phone")]
    
    return {
        "total_binded": len(bindings),
        "total_unbinded": len(unbinded),
        "bindings": bindings,
        "volunteers": volunteers
    }

# ============= 商户接口 =============

@app.post("/merchant/donate")
def create_donation(request: DonationCreate, token: str):
    """商户投放商品"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效的token")
    
    phone = payload.get("phone")
    user = store.get_user_by_phone(phone)
    if not user or user.get("role") != "merchant":
        raise HTTPException(status_code=403, detail="只有商户才能投放商品")
    
    machine = store.get_machine_by_id(request.machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="柜机不存在")
    
    expiry_time = datetime.utcnow() + timedelta(days=request.expiry_days)
    donation = store.create_donation({
        "merchant_id": user["id"],
        "machine_id": request.machine_id,
        "item_name": request.item_name,
        "quantity": request.quantity,
        "expiry_time": expiry_time.isoformat(),
        "status": "active"
    })
    
    return {"message": "投放成功", "donation": donation}

@app.get("/merchant/donations")
def my_donations(token: str):
    """商户查看投放列表"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效的token")
    
    phone = payload.get("phone")
    user = store.get_user_by_phone(phone)
    if not user or user.get("role") != "merchant":
        raise HTTPException(status_code=403, detail="只有商户才能查看")
    
    donations = store.get_donations()
    my = [d for d in donations if d.get("merchant_id") == user["id"]]
    return {"donations": my}

# ============= 特殊群体接口 =============

@app.get("/special/my-pickups")
def my_pickups(token: str):
    """特殊群体领取记录"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效的token")
    
    phone = payload.get("phone")
    user = store.get_user_by_phone(phone)
    if not user or user.get("role") != "special_group":
        raise HTTPException(status_code=403, detail="无权限")
    
    _reset_daily_if_needed(user)
    user = store.get_user_by_phone(phone)
    
    pickups = store.get_pickups_by_user(user["id"])
    return {
        "pickups": pickups,
        "remaining_today": user.get("daily_limit", 3) - user.get("used_today", 0)
    }

@app.post("/special/bind-volunteer")
def bind_volunteer(volunteer_phone: str, token: str):
    """绑定志愿者"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效的token")
    
    phone = payload.get("phone")
    user = store.get_user_by_phone(phone)
    if not _is_bindable_special_group(user):
        raise HTTPException(status_code=403, detail="无权限")
    
    volunteer = store.get_user_by_phone(volunteer_phone)
    if not volunteer:
        raise HTTPException(status_code=404, detail="志愿者用户不存在")
    
    # 被绑定对象必须是真正的志愿者，且不能绑自己
    if not store._is_volunteer_user(volunteer):
        raise HTTPException(status_code=400, detail="只能绑定志愿者用户")
    if volunteer.get("phone") == user.get("phone"):
        raise HTTPException(status_code=400, detail="不能绑定自己为志愿者")
    
    store.update_user(user["id"], {"volunteer_phone": volunteer_phone})
    return {
        "message": "绑定成功",
        "volunteer_phone": volunteer_phone,
        "volunteer_name": volunteer.get("name")
    }


@app.post("/special/unbind-volunteer")
def unbind_volunteer(token: str):
    """解除志愿者绑定"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效的token")

    phone = payload.get("phone")
    user = store.get_user_by_phone(phone)
    if not _is_bindable_special_group(user):
        raise HTTPException(status_code=403, detail="无权限")

    store.update_user(user["id"], {"volunteer_phone": None})
    return {"message": "解绑成功"}

# ============= 模拟硬件接口 =============

@app.post("/mock/device/open")
def mock_device_open(data: dict):
    """模拟厂家开门接口"""
    import time
    time.sleep(0.5)
    success = random.random() < 0.9
    return {
        "success": success,
        "message": "开门成功" if success else "开门失败",
        "device_id": data.get("device_id"),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/mock/device/callback/pickup")
def mock_callback_pickup(data: dict):
    """模拟厂家推送结算数据"""
    machine_id = data.get("machine_id")
    operator = data.get("operator")
    
    items = [
        {"slot": "A1", "name": "矿泉水", "quantity": 1},
        {"slot": "A2", "name": "方便面", "quantity": 1},
        {"slot": "B1", "name": "饼干", "quantity": 1},
    ]
    taken_items = random.sample(items, k=random.randint(1, 2))
    
    callback_request = CallbackPickup(
        machine_id=machine_id,
        operator=operator,
        items=taken_items
    )
    
    return callback_settlement(callback_request)

# ============= 辅助函数 =============

def _mock_open_door(machine_id: str, api_url: str) -> dict:
    """模拟开门"""
    return {
        "success": random.random() < 0.9,
        "machine_id": machine_id
    }

# ============= 启动 =============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
