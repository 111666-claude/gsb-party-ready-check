"""队伍就绪检查：名额上限、队长挂机豁免、超时踢人与请求幂等。"""


class Check:
    """就绪台账。"""

    def __init__(self, max_members, wait_ms):
        self.max_members = max_members
        self.wait_ms = wait_ms
        self.members = {}
        self.ready = set()
        self.bypass_used = set()
        self.seen = set()
        self.kicked = []

    def join(self, player, at_ms):
        """加入队伍，满员时返回 False。"""
        if player not in self.members and len(self.members) >= self.max_members:
            return False
        self.members[player] = at_ms
        return True

    def set_ready(self, req_id, player):
        """把玩家标成就绪，同一个 req_id 只生效一次。"""
        if req_id in self.seen:
            return False
        if player not in self.members:
            return False
        self.ready.add(player)
        self.seen.add(req_id)
        return True

    def confirm(self, leader, now_ms):
        """踢掉超时未就绪成员，返回 (是否通过, 还差谁)。"""
        for name in list(self.members):
            if name not in self.ready and now_ms - self.members[name] > self.wait_ms:
                del self.members[name]
                self.kicked.append(name)
        missing = sorted(name for name in self.members if name not in self.ready)
        if (
            missing
            and leader in self.members
            and leader in self.ready
            and leader not in self.bypass_used
        ):
            self.bypass_used.add(leader)
            missing = missing[1:]
        return (not missing), missing

    def dump(self):
        """序列化成员、就绪、已用豁免与请求台账。"""
        return {
            "max_members": self.max_members,
            "wait_ms": self.wait_ms,
            "members": dict(self.members),
            "ready": sorted(self.ready),
            "bypass_used": sorted(self.bypass_used),
            "seen": sorted(self.seen),
            "kicked": list(self.kicked),
        }

    def load(self, data):
        self.max_members = data.get("max_members", self.max_members)
        self.wait_ms = data.get("wait_ms", self.wait_ms)
        members = data.get("members", {})
        if isinstance(members, dict):
            self.members.update(members)
        else:
            for name in members:
                self.members.setdefault(name, 0)
        self.ready = set(data.get("ready", []))
        self.bypass_used = set(data.get("bypass_used", []))
        self.seen = set(data.get("seen", []))
        self.kicked = list(data.get("kicked", []))
        return True
