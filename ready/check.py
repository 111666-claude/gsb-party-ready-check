"""队伍就绪检查：名额上限、队长挂机豁免、超时踢人与请求幂等。

缺陷：名额上限不生效、队长豁免能反复用、超时成员不踢、同一个 req_id 重复生效、
状态往返丢掉已用豁免与请求台账。
"""


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
        """加入队伍。缺陷：不看名额上限。"""
        self.members[player] = at_ms
        return True

    def set_ready(self, req_id, player):
        """把玩家标成就绪。缺陷：不查 req_id。"""
        if player not in self.members:
            return False
        self.ready.add(player)
        self.seen.add(req_id)
        return True

    def confirm(self, leader, now_ms):
        """返回 (是否通过, 还差谁)。缺陷：队长豁免不限次用、超时不踢。"""
        missing = [name for name in self.members if name not in self.ready]
        if leader in self.members and leader in self.ready:
            for name in missing:
                self.bypass_used.add(leader)
            missing = []
        return (not missing), missing

    def dump(self):
        """序列化。缺陷：只写成员与就绪，豁免与请求台账都丢。"""
        return {"max_members": self.max_members, "members": sorted(self.members), "ready": sorted(self.ready)}

    def load(self, data):
        self.max_members = data.get("max_members", self.max_members)
        for name in data.get("members", []):
            self.members.setdefault(name, 0)
        self.ready = set(data.get("ready", []))
        return True
