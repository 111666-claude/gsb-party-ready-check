"""就绪检查入口：子命令 add/ready/confirm/dump 配 JSON 状态。"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ready.check import Check  # noqa: E402


def build_parser():
    parser = argparse.ArgumentParser(prog="party-ready-check", description="队伍就绪检查")
    parser.add_argument("--state", default="state.json", help="状态文件")
    parser.add_argument("--sample", default=None, help="cap / bypass / timeout / dup / round")
    parser.add_argument("command", nargs="*", help="add/ready/confirm/dump")
    return parser


def load(path, max_members, wait_ms):
    book = Check(max_members, wait_ms)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            book.load(json.load(handle))
    return book


def save(path, book):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(book.dump(), handle)


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "cap":
        book = Check(2, 10000)
        book.join("a", 0)
        book.join("b", 0)
        print("third=%s" % str(book.join("c", 0)).lower())
    elif args.sample == "bypass":
        book = Check(4, 10000)
        for name in ("lead", "x"):
            book.join(name, 0)
        book.set_ready("r1", "lead")
        first = book.confirm("lead", 0)[0]
        book.join("y", 0)
        print("first=%s second=%s" % (first, book.confirm("lead", 0)[0]))
    elif args.sample == "timeout":
        book = Check(4, 1000)
        book.join("slow", 0)
        book.join("fast", 0)
        book.set_ready("r1", "fast")
        ok, _ = book.confirm("fast", 5000)
        print("ok=%s kicked=%d" % (str(ok).lower(), len(book.kicked)))
    elif args.sample == "dup":
        book = Check(4, 10000)
        book.join("a", 0)
        print("second=%s" % str(book.set_ready("r1", "a")).lower())
        book.ready.discard("a")
        print("again=%s" % str(book.set_ready("r1", "a")).lower())
    elif args.sample == "round":
        book = Check(4, 10000)
        book.join("lead", 0)
        book.join("afk", 0)
        book.set_ready("r1", "lead")
        book.confirm("lead", 0)
        restored = Check(4, 10000)
        restored.load(book.dump())
        print("bypass=%s reqs=%d" % (sorted(restored.bypass_used), len(restored.seen)))
    elif args.command and args.command[0] == "confirm":
        book = load(args.state, 4, 10000)
        print("ok=%s" % str(book.confirm(args.command[1], 0)[0]).lower())
    else:
        raise SystemExit("需要 --sample cap|bypass|timeout|dup|round，或 confirm 子命令")
    book = locals().get("book")
    if book is not None and not args.sample:
        save(args.state, book)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
