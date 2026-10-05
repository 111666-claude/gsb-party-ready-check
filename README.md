# party-ready-check

队伍就绪检查：名额上限、队长挂机豁免、超时踢人与请求幂等，状态存 JSON，只用 Python 标准库。

```
python3 main.py --sample=cap
python3 main.py --sample=bypass
python3 main.py --sample=timeout
python3 main.py --sample=dup
python3 main.py --sample=round
python3 main.py confirm lead --state state.json
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **名额**：队伍成员数不超过 `max_members`，超出时 `join` 返回 False。
- **就绪**：全员就绪才算通过，没就绪的进 `missing`。
- **队长豁免**：队长已就绪时可以豁免一名未就绪成员（按名字升序取第一个），但每队只能用一次。
- **超时踢人**：加入后超过 `wait_ms` 还没就绪的成员移出队伍并记进 `kicked`，不再算 missing。
- **幂等**：同一个 `req_id` 只生效一次，重复提交返回 False。
- **往返一致**：状态存 JSON 再读回来，成员、就绪集合、已用豁免与请求台账都要一致。
- **规模**：就绪查询按名字索引，摊还 O(1)；10 万玩家每秒 10 万次查询。

## 输出契约（不改格式）

```
third=..
first=.. second=..
ok=.. missing=..
second=.. again=..
bypass=.. reqs=..
```

## 目录

```
ready/check.py      名额、豁免、超时与幂等
main.py             子命令入口与 JSON 状态
tests/test_check.py unittest 用例
```
