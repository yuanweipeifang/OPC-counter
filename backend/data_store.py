"""
JSON 文件数据存储模块
用于替代 SQLite 数据库
"""

import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

DATA_FILE = "data.json"

class DataStore:
    """JSON 文件数据存储类"""
    
    def __init__(self, data_file: str = DATA_FILE):
        self.data_file = data_file
        self.data = self._load()
    
    def _load(self) -> Dict:
        """从文件加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception):
                pass
        return self._get_default_data()
    
    def _get_default_data(self) -> Dict:
        """获取默认数据结构"""
        return {
            "users": [],
            "machines": [],
            "donations": [],
            "pickups": [],
            "rules": [{"id": 1, "name": "default", "daily_limit": 3, "category_limits": {"food": 2, "drink": 2}, "is_active": True}],
            "notifications": [],
            "auth_tokens": []
        }
    
    def _save(self):
        """保存数据到文件"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2, default=str)
    
    def _get_next_id(self, collection: str) -> int:
        """获取下一个ID"""
        items = self.data.get(collection, [])
        if not items:
            return 1
        return max(item.get("id", 0) for item in items) + 1
    
    # ============= 用户操作 =============
    
    def get_users(self, role: Optional[str] = None, skip: int = 0, limit: int = 50) -> tuple:
        """获取用户列表"""
        users = self.data.get("users", [])
        if role:
            users = [u for u in users if u.get("role") == role]
        total = len(users)
        return users[skip:skip+limit], total
    
    def get_user_by_phone(self, phone: str) -> Optional[Dict]:
        """根据手机号获取用户"""
        users = self.data.get("users", [])
        for user in users:
            if user.get("phone") == phone:
                return user
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """根据ID获取用户"""
        users = self.data.get("users", [])
        for user in users:
            if user.get("id") == user_id:
                return user
        return None
    
    def create_user(self, user_data: Dict) -> Dict:
        """创建用户"""
        user_data["id"] = self._get_next_id("users")
        user_data["created_at"] = datetime.utcnow().isoformat()
        user_data["updated_at"] = datetime.utcnow().isoformat()
        if "daily_limit" not in user_data:
            user_data["daily_limit"] = 3
        if "used_today" not in user_data:
            user_data["used_today"] = 0
        if "is_active" not in user_data:
            user_data["is_active"] = True
        self.data["users"].append(user_data)
        self._save()
        return user_data
    
    def update_user(self, user_id: int, update_data: Dict) -> Optional[Dict]:
        """更新用户"""
        users = self.data.get("users", [])
        for i, user in enumerate(users):
            if user.get("id") == user_id:
                user.update(update_data)
                user["updated_at"] = datetime.utcnow().isoformat()
                self.data["users"][i] = user
                self._save()
                return user
        return None
    
    def import_users(self, users_data: List[Dict]) -> int:
        """批量导入用户"""
        count = 0
        for u in users_data:
            phone = u.get("phone")
            existing = self.get_user_by_phone(phone)
            if existing:
                self.update_user(existing["id"], u)
            else:
                self.create_user(u)
            count += 1
        return count
    
    # ============= 柜机操作 =============
    
    def get_machines(self) -> List[Dict]:
        """获取所有柜机"""
        return self.data.get("machines", [])
    
    def get_machine_by_id(self, machine_id: str) -> Optional[Dict]:
        """根据ID获取柜机"""
        machines = self.data.get("machines", [])
        for machine in machines:
            if machine.get("id") == machine_id:
                return machine
        return None
    
    def create_machine(self, machine_data: Dict) -> Dict:
        """创建柜机"""
        machine_data["created_at"] = datetime.utcnow().isoformat()
        self.data["machines"].append(machine_data)
        self._save()
        return machine_data
    
    def update_machine_status(self, machine_id: str, status: str):
        """更新柜机状态"""
        machines = self.data.get("machines", [])
        for i, m in enumerate(machines):
            if m.get("id") == machine_id:
                self.data["machines"][i]["status"] = status
                self.data["machines"][i]["last_communication"] = datetime.utcnow().isoformat()
                self._save()
                break
    
    # ============= 捐赠操作 =============
    
    def get_donations(self, status: Optional[str] = None) -> List[Dict]:
        """获取捐赠记录"""
        donations = self.data.get("donations", [])
        if status:
            donations = [d for d in donations if d.get("status") == status]
        return donations
    
    def get_donation_by_id(self, donation_id: int) -> Optional[Dict]:
        """根据ID获取捐赠"""
        donations = self.data.get("donations", [])
        for d in donations:
            if d.get("id") == donation_id:
                return d
        return None
    
    def create_donation(self, donation_data: Dict) -> Dict:
        """创建捐赠记录"""
        donation_data["id"] = self._get_next_id("donations")
        donation_data["created_at"] = datetime.utcnow().isoformat()
        donation_data["updated_at"] = datetime.utcnow().isoformat()
        if "status" not in donation_data:
            donation_data["status"] = "active"
        self.data["donations"].append(donation_data)
        self._save()
        return donation_data
    
    def update_donation(self, donation_id: int, update_data: Dict) -> Optional[Dict]:
        """更新捐赠记录"""
        donations = self.data.get("donations", [])
        for i, d in enumerate(donations):
            if d.get("id") == donation_id:
                d.update(update_data)
                d["updated_at"] = datetime.utcnow().isoformat()
                self.data["donations"][i] = d
                self._save()
                return d
        return None
    
    # ============= 领取操作 =============
    
    def get_pickups(self, skip: int = 0, limit: int = 50) -> List[Dict]:
        """获取领取记录"""
        pickups = self.data.get("pickups", [])
        return pickups[skip:skip+limit]
    
    def get_pickups_by_user(self, user_id: int, limit: int = 20) -> List[Dict]:
        """获取用户的领取记录"""
        pickups = self.data.get("pickups", [])
        user_pickups = [p for p in pickups if p.get("user_id") == user_id]
        return user_pickups[-limit:]
    
    def create_pickup(self, pickup_data: Dict) -> Dict:
        """创建领取记录"""
        pickup_data["id"] = self._get_next_id("pickups")
        pickup_data["pickup_time"] = datetime.utcnow().isoformat()
        if "is_compliant" not in pickup_data:
            pickup_data["is_compliant"] = True
        self.data["pickups"].append(pickup_data)
        self._save()
        return pickup_data
    
    # ============= 规则操作 =============
    
    def get_rules(self) -> List[Dict]:
        """获取规则"""
        return self.data.get("rules", [])
    
    def get_default_rule(self) -> Dict:
        """获取默认规则"""
        rules = self.data.get("rules", [])
        for rule in rules:
            if rule.get("name") == "default":
                return rule
        return {"daily_limit": 3, "category_limits": {}}
    
    def set_rule(self, rule_data: Dict) -> Dict:
        """设置规则"""
        rules = self.data.get("rules", [])
        for i, r in enumerate(rules):
            if r.get("name") == rule_data.get("name"):
                r.update(rule_data)
                self.data["rules"][i] = r
                self._save()
                return r
        rule_data["id"] = self._get_next_id("rules")
        self.data["rules"].append(rule_data)
        self._save()
        return rule_data
    
    # ============= 通知操作 =============
    
    def get_notifications(self, skip: int = 0, limit: int = 20) -> List[Dict]:
        """获取通知"""
        notifications = self.data.get("notifications", [])
        return notifications[skip:skip+limit]
    
    def create_notification(self, notification_data: Dict) -> Dict:
        """创建通知"""
        notification_data["id"] = self._get_next_id("notifications")
        notification_data["created_at"] = datetime.utcnow().isoformat()
        if "is_read" not in notification_data:
            notification_data["is_read"] = False
        self.data["notifications"].append(notification_data)
        self._save()
        return notification_data
    
    # ============= 认证操作 =============
    
    def create_auth_token(self, phone: str, otp: str = "123456") -> Dict:
        """创建认证令牌"""
        token = str(uuid.uuid4())
        auth_data = {
            "phone": phone,
            "token": token,
            "otp": otp,
            "verified": False,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        }
        self.data["auth_tokens"].append(auth_data)
        self._save()
        return auth_data
    
    def get_auth_token(self, token: str) -> Optional[Dict]:
        """获取认证令牌"""
        tokens = self.data.get("auth_tokens", [])
        for t in tokens:
            if t.get("token") == token:
                return t
        return None
    
    def verify_auth_token(self, token: str) -> bool:
        """验证令牌"""
        tokens = self.data.get("auth_tokens", [])
        for i, t in enumerate(tokens):
            if t.get("token") == token:
                self.data["auth_tokens"][i]["verified"] = True
                self.data["auth_tokens"][i]["verified_at"] = datetime.utcnow().isoformat()
                self._save()
                return True
        return False
    
    # ============= 统计操作 =============
    
    def get_dashboard_stats(self) -> Dict:
        """获取仪表盘统计"""
        users = self.data.get("users", [])
        machines = self.data.get("machines", [])
        donations = self.data.get("donations", [])
        pickups = self.data.get("pickups", [])
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        return {
            "users": {
                "total": len(users),
                "special_group": len([u for u in users if u.get("role") == "special_group"]),
                "merchant": len([u for u in users if u.get("role") == "merchant"]),
                "admin": len([u for u in users if u.get("role") == "admin"])
            },
            "machines": {
                "total": len(machines),
                "online": len([m for m in machines if m.get("status") == "online"]),
                "offline": len([m for m in machines if m.get("status") == "offline"])
            },
            "donations": {
                "active": len([d for d in donations if d.get("status") == "active"]),
                "expired": len([d for d in donations if d.get("status") == "expired"])
            },
            "pickups": {
                "total": len(pickups),
                "today": len([p for p in pickups if p.get("pickup_time") and datetime.fromisoformat(p["pickup_time"]) >= today_start]),
                "compliant": len([p for p in pickups if p.get("is_compliant") == True]),
                "violations": len([p for p in pickups if p.get("is_compliant") == False])
            }
        }
    
    def get_user_portrait(self) -> Dict:
        """获取用户画像数据"""
        users = self.data.get("users", [])
        pickups = self.data.get("pickups", [])
        
        # 角色分布
        role_distribution = {}
        for u in users:
            role = u.get("role", "unknown")
            role_distribution[role] = role_distribution.get(role, 0) + 1
        
        # 类别分布
        category_distribution = {}
        for u in users:
            cat = u.get("category")
            if cat:
                category_distribution[cat] = category_distribution.get(cat, 0) + 1
        
        # 社区分布
        community_distribution = {}
        for u in users:
            com = u.get("community")
            if com:
                community_distribution[com] = community_distribution.get(com, 0) + 1
        
        # 领取趋势
        pickup_trend = []
        for i in range(6, -1, -1):
            date = datetime.utcnow().date() - timedelta(days=i)
            count = 0
            for p in pickups:
                if p.get("pickup_time"):
                    pt = datetime.fromisoformat(p["pickup_time"]).date()
                    if pt == date:
                        count += 1
            pickup_trend.append({"date": date.isoformat(), "count": count})
        
        return {
            "role_distribution": role_distribution,
            "category_distribution": category_distribution,
            "community_distribution": community_distribution,
            "pickup_trend": pickup_trend
        }
    
    def get_demand_heatmap(self) -> Dict:
        """获取需求热力图数据"""
        pickups = self.data.get("pickups", [])
        machines = self.data.get("machines", [])
        
        # 按柜机统计
        machine_stats = {}
        for p in pickups:
            mid = p.get("machine_id")
            machine_stats[mid] = machine_stats.get(mid, 0) + 1
        
        by_machine = []
        for mid, count in machine_stats.items():
            machine = self.get_machine_by_id(mid)
            if machine:
                by_machine.append({
                    "machine_id": mid,
                    "machine_name": machine.get("name"),
                    "location": machine.get("location"),
                    "latitude": machine.get("latitude"),
                    "longitude": machine.get("longitude"),
                    "pickup_count": count
                })
        
        # 按商品统计
        item_stats = {}
        for p in pickups:
            item = p.get("item_name")
            if item:
                item_stats[item] = item_stats.get(item, 0) + 1
        
        by_item = [{"item_name": k, "count": v} for k, v in item_stats.items()]
        by_item.sort(key=lambda x: x["count"], reverse=True)
        
        return {"by_machine": by_machine, "by_item": by_item}
    
    def check_expired_donations(self):
        """检查过期捐赠"""
        now = datetime.utcnow()
        donations = self.data.get("donations", [])
        
        for d in donations:
            if d.get("status") == "active" and d.get("expiry_time"):
                expiry = datetime.fromisoformat(d["expiry_time"])
                if expiry < now:
                    d["status"] = "expired"
                    # 创建通知
                    self.create_notification({
                        "user_id": d.get("merchant_id"),
                        "title": "捐赠已过期",
                        "content": f"您在柜机 {d.get('machine_id')} 投放的 {d.get('item_name')} 已过期",
                        "type": "warning"
                    })
        
        self._save()
    
    def init_default_data(self):
        """初始化默认数据"""
        if not self.data.get("users"):
            # 创建默认管理员
            self.create_user({
                "phone": "13800000000",
                "name": "系统管理员",
                "role": "admin",
                "category": "管理员",
                "community": "总部"
            })
            
            # 创建测试用户
            test_users = [
                {"phone": "13900000001", "name": "张三", "role": "special_group", "category": "残疾人", "community": "朝阳区"},
                {"phone": "13900000002", "name": "李四", "role": "special_group", "category": "低保户", "community": "海淀区"},
                {"phone": "13900000003", "name": "王五", "role": "special_group", "category": "残疾人", "community": "东城区"},
                {"phone": "13900000004", "name": "赵六", "role": "special_group", "category": "老年人", "community": "西城区"},
                {"phone": "13900000005", "name": "钱七", "role": "special_group", "category": "低保户", "community": "朝阳区"},
                {"phone": "13700000001", "name": "志愿者小王", "role": "special_group", "category": "志愿者", "community": "朝阳区"},
                {"phone": "13600000001", "name": "爱心商户A", "role": "merchant", "category": "商户", "community": "朝阳区"},
                {"phone": "13600000002", "name": "爱心商户B", "role": "merchant", "category": "商户", "community": "海淀区"},
                {"phone": "13600000003", "name": "爱心商户C", "role": "merchant", "category": "商户", "community": "东城区"},
            ]
            for u in test_users:
                self.create_user(u)
        
        if not self.data.get("machines"):
            # 创建默认柜机
            machines = [
                {"id": "MC001", "name": "爱心柜-朝阳区政务中心", "location": "北京市朝阳区政务服务中心", "latitude": 39.9288, "longitude": 116.4569, "status": "online", "api_url": "http://localhost:8000/mock"},
                {"id": "MC002", "name": "爱心柜-海淀区社区中心", "location": "北京市海淀区中关村街道", "latitude": 39.9830, "longitude": 116.3120, "status": "online", "api_url": "http://localhost:8000/mock"},
                {"id": "MC003", "name": "爱心柜-东城区困难帮扶站", "location": "北京市东城区景山街道", "latitude": 39.9163, "longitude": 116.4100, "status": "offline", "api_url": "http://localhost:8000/mock"},
                {"id": "MC004", "name": "爱心柜-西城区民政局", "location": "北京市西城区二龙路街道", "latitude": 39.9120, "longitude": 116.3700, "status": "online", "api_url": "http://localhost:8000/mock"},
            ]
            for m in machines:
                self.create_machine(m)
        
        # 创建测试捐赠记录
        if not self.data.get("donations"):
            merchant = self.get_user_by_phone("13600000001")
            if merchant:
                self.create_donation({
                    "merchant_id": merchant["id"],
                    "machine_id": "MC001",
                    "item_name": "矿泉水",
                    "quantity": 10,
                    "expiry_time": (datetime.utcnow() + timedelta(days=5)).isoformat(),
                    "status": "active"
                })
                self.create_donation({
                    "merchant_id": merchant["id"],
                    "machine_id": "MC001",
                    "item_name": "方便面",
                    "quantity": 5,
                    "expiry_time": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                    "status": "active"
                })

# 导入 timedelta
from datetime import timedelta

# 全局数据存储实例
store = DataStore()
