from __future__ import annotations

import json
import sys
from pathlib import Path

AUDIT_LOG_PATH = Path("data/audit.jsonl")
REQUIRED_FIELDS = {
    "ts", "event", "actor_id_hash", "correlation_id", "action", "target", "outcome"
}


def main() -> int:
    if not AUDIT_LOG_PATH.exists():
        print("KHÔNG HỢP LỆ: data/audit.jsonl chưa tồn tại")
        return 1
    records = []
    for line in AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            print("KHÔNG HỢP LỆ: audit log chứa dòng không phải JSON")
            return 1
    if len(records) < 2:
        print("KHÔNG HỢP LỆ: cần ít nhất hai audit event enable/disable")
        return 1
    if any(not REQUIRED_FIELDS.issubset(record) for record in records):
        print("KHÔNG HỢP LỆ: audit event thiếu trường bắt buộc")
        return 1
    actions = {record.get("action") for record in records}
    if not {"enable", "disable"}.issubset(actions):
        print("KHÔNG HỢP LỆ: thiếu cặp action enable/disable")
        return 1
    if any(record.get("event") != "incident_control" for record in records):
        print("KHÔNG HỢP LỆ: event phải là incident_control")
        return 1
    print(f"HỢP LỆ: {len(records)} audit event; có enable/disable và đủ trường bắt buộc.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
