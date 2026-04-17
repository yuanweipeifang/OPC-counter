#!/usr/bin/env python3
"""SmartVM API CLI 工具。

功能：
- 按文档规则自动追加 clientId/nonceStr/sign
- 直接调用 pre.smartvm.cn 的开门业务接口
- 支持交互模式，便于比赛现场联调

环境变量：
- SMARTVM_BASE_URL (默认: http://pre.smartvm.cn)
- SMARTVM_CLIENT_ID
- SMARTVM_SIGN_KEY
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import uuid
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "http://pre.smartvm.cn"


def _compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _normalize_sign_value(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str) and value == "":
        return None
    if isinstance(value, (dict, list)):
        return _compact_json(value)
    return str(value)


def build_sign(payload: Dict[str, Any], sign_key: str) -> str:
    items = []
    for key in sorted(payload.keys()):
        if key == "sign":
            continue
        normalized = _normalize_sign_value(payload.get(key))
        if normalized is None:
            continue
        items.append(f"{key}={normalized}")
    string1 = "&".join(items)
    raw = f"{string1}&key={sign_key}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest().upper()


def enrich_payload(
    payload: Dict[str, Any],
    client_id: str,
    sign_key: str,
    nonce: Optional[str] = None,
) -> Dict[str, Any]:
    if not client_id or not sign_key:
        raise ValueError("缺少 SMARTVM_CLIENT_ID 或 SMARTVM_SIGN_KEY")

    out = dict(payload)
    out["clientId"] = client_id
    out["nonceStr"] = nonce or out.get("nonceStr") or uuid.uuid4().hex
    out["sign"] = build_sign(out, sign_key)
    return out


def post_json(url: str, payload: Dict[str, Any], timeout: int = 20) -> Dict[str, Any]:
    req = Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode("utf-8", errors="ignore")
            return {
                "ok": True,
                "status": resp.status,
                "response": json.loads(text) if text else {},
                "raw": text,
            }
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
        parsed: Any = body
        try:
            parsed = json.loads(body) if body else {}
        except json.JSONDecodeError:
            pass
        return {
            "ok": False,
            "status": exc.code,
            "response": parsed,
            "raw": body,
        }
    except URLError as exc:
        return {
            "ok": False,
            "status": 0,
            "response": {"error": str(exc.reason)},
            "raw": str(exc.reason),
        }


def output_result(url: str, req_payload: Dict[str, Any], result: Dict[str, Any]) -> None:
    print("\n=== REQUEST URL ===")
    print(url)
    print("\n=== REQUEST BODY ===")
    print(json.dumps(req_payload, ensure_ascii=False, indent=2))
    print("\n=== RESPONSE STATUS ===")
    print(result.get("status"))
    print("\n=== RESPONSE BODY ===")
    print(json.dumps(result.get("response"), ensure_ascii=False, indent=2))


def require_env() -> tuple[str, str, str]:
    base_url = os.getenv("SMARTVM_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    client_id = os.getenv("SMARTVM_CLIENT_ID", "").strip()
    sign_key = os.getenv("SMARTVM_SIGN_KEY", "").strip()
    if not client_id or not sign_key:
        raise SystemExit(
            "请先设置环境变量 SMARTVM_CLIENT_ID 和 SMARTVM_SIGN_KEY。"
        )
    return base_url, client_id, sign_key


def call_endpoint(
    path: str,
    payload: Dict[str, Any],
    base_url: str,
    client_id: str,
    sign_key: str,
    timeout: int,
) -> int:
    url = f"{base_url}{path if path.startswith('/') else '/' + path}"
    body = enrich_payload(payload, client_id=client_id, sign_key=sign_key)
    result = post_json(url, body, timeout=timeout)
    output_result(url, body, result)
    return 0 if result.get("ok") else 1


def cmd_goods(args: argparse.Namespace) -> int:
    base_url, client_id, sign_key = require_env()
    payload = {"deviceCode": args.device_code, "doorNum": args.door_num}
    return call_endpoint(
        "/api/pay/container/getCabinetGoodsInfo",
        payload,
        base_url,
        client_id,
        sign_key,
        args.timeout,
    )


def cmd_opendoor(args: argparse.Namespace) -> int:
    base_url, client_id, sign_key = require_env()
    payload = {
        "userId": args.user_id,
        "eventId": args.event_id or f"evt_{int(time.time())}",
        "deviceCode": args.device_code,
        "payStyle": args.pay_style,
        "doorNum": args.door_num,
        "phone": args.phone,
    }
    return call_endpoint(
        "/api/pay/container/opendoor",
        payload,
        base_url,
        client_id,
        sign_key,
        args.timeout,
    )


def cmd_payment_notify(args: argparse.Namespace) -> int:
    base_url, client_id, sign_key = require_env()
    payload = {
        "orderNo": args.order_no,
        "eventId": args.event_id,
        "transactionId": args.transaction_id,
        "deviceCode": args.device_code,
        "amount": args.amount,
        "openId": args.open_id,
    }
    return call_endpoint(
        args.path,
        payload,
        base_url,
        client_id,
        sign_key,
        args.timeout,
    )


def cmd_raw(args: argparse.Namespace) -> int:
    base_url, client_id, sign_key = require_env()
    try:
        payload = json.loads(args.payload)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"payload 不是合法 JSON: {exc}")

    if not isinstance(payload, dict):
        raise SystemExit("payload 必须是 JSON 对象")

    return call_endpoint(
        args.path,
        payload,
        base_url,
        client_id,
        sign_key,
        args.timeout,
    )


def _prompt(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or default


def cmd_interactive(args: argparse.Namespace) -> int:
    base_url, client_id, sign_key = require_env()
    timeout = args.timeout

    while True:
        print("\nSmartVM 交互菜单")
        print("1) 获取设备商品列表")
        print("2) 开门接口")
        print("3) 付款成功异步通知")
        print("4) 自定义路径请求")
        print("0) 退出")
        choice = input("请选择: ").strip()

        if choice == "0":
            return 0
        if choice == "1":
            device = _prompt("deviceCode", "91120149")
            door = _prompt("doorNum", "1")
            code = call_endpoint(
                "/api/pay/container/getCabinetGoodsInfo",
                {"deviceCode": device, "doorNum": door},
                base_url,
                client_id,
                sign_key,
                timeout,
            )
            print(f"执行结果: {'成功' if code == 0 else '失败'}")
        elif choice == "2":
            payload = {
                "userId": _prompt("userId", "u10001"),
                "eventId": _prompt("eventId", f"evt_{int(time.time())}"),
                "deviceCode": _prompt("deviceCode", "91120149"),
                "payStyle": _prompt("payStyle", "2"),
                "doorNum": _prompt("doorNum", "1"),
                "phone": _prompt("phone", "13800138000"),
            }
            code = call_endpoint(
                "/api/pay/container/opendoor",
                payload,
                base_url,
                client_id,
                sign_key,
                timeout,
            )
            print(f"执行结果: {'成功' if code == 0 else '失败'}")
        elif choice == "3":
            payload = {
                "orderNo": _prompt("orderNo", f"ORD_{int(time.time())}"),
                "eventId": _prompt("eventId", f"evt_{int(time.time())}"),
                "transactionId": _prompt("transactionId", f"TRA_{int(time.time())}"),
                "deviceCode": _prompt("deviceCode", "91120149"),
                "amount": int(_prompt("amount(分)", "0")),
                "openId": _prompt("openId", ""),
            }
            path = _prompt("通知路径", "/api/pay/container/paySuccessNotify")
            code = call_endpoint(path, payload, base_url, client_id, sign_key, timeout)
            print(f"执行结果: {'成功' if code == 0 else '失败'}")
        elif choice == "4":
            path = _prompt("path", "/api/pay/container/getCabinetGoodsInfo")
            raw_json = _prompt("JSON payload", '{"deviceCode":"91120149"}')
            try:
                payload = json.loads(raw_json)
            except json.JSONDecodeError as exc:
                print(f"JSON 解析失败: {exc}")
                continue
            if not isinstance(payload, dict):
                print("payload 必须是对象")
                continue
            code = call_endpoint(path, payload, base_url, client_id, sign_key, timeout)
            print(f"执行结果: {'成功' if code == 0 else '失败'}")
        else:
            print("无效选项，请重试")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SmartVM 第三方 APP 开门业务接口 CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_goods = sub.add_parser("goods", help="获取设备商品列表")
    p_goods.add_argument("--device-code", required=True, help="设备编码")
    p_goods.add_argument("--door-num", default="1", help="门编码，双门柜必填")
    p_goods.add_argument("--timeout", type=int, default=20)
    p_goods.set_defaults(func=cmd_goods)

    p_open = sub.add_parser("opendoor", help="调用开门接口")
    p_open.add_argument("--user-id", required=True)
    p_open.add_argument("--event-id", default="", help="事件ID，可空自动生成")
    p_open.add_argument("--device-code", required=True)
    p_open.add_argument("--pay-style", default="2", help="2=微信，3=支付宝")
    p_open.add_argument("--door-num", default="1")
    p_open.add_argument("--phone", required=True)
    p_open.add_argument("--timeout", type=int, default=20)
    p_open.set_defaults(func=cmd_opendoor)

    p_notify = sub.add_parser("payment-notify", help="付款成功异步通知")
    p_notify.add_argument("--path", default="/api/pay/container/paySuccessNotify", help="文档路径待定，可覆盖")
    p_notify.add_argument("--order-no", required=True)
    p_notify.add_argument("--event-id", required=True)
    p_notify.add_argument("--transaction-id", required=True)
    p_notify.add_argument("--device-code", required=True)
    p_notify.add_argument("--amount", required=True, type=int)
    p_notify.add_argument("--open-id", default="")
    p_notify.add_argument("--timeout", type=int, default=20)
    p_notify.set_defaults(func=cmd_payment_notify)

    p_raw = sub.add_parser("raw", help="自定义路径 + payload 调用")
    p_raw.add_argument("--path", required=True)
    p_raw.add_argument("--payload", required=True, help="JSON 对象字符串")
    p_raw.add_argument("--timeout", type=int, default=20)
    p_raw.set_defaults(func=cmd_raw)

    p_interactive = sub.add_parser("interactive", help="交互模式")
    p_interactive.add_argument("--timeout", type=int, default=20)
    p_interactive.set_defaults(func=cmd_interactive)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        print("\n已取消")
        return 130


if __name__ == "__main__":
    sys.exit(main())
