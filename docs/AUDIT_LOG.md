# Audit log cho control plane

Các thao tác bật/tắt incident được ghi riêng vào `data/audit.jsonl`, không trộn
với application log. Mỗi event có timestamp, actor đã hash, correlation ID,
action, target và outcome. Thiết kế này hỗ trợ truy trách nhiệm mà không lưu
định danh người vận hành dưới dạng nguyên văn.

Tạo evidence bằng cách bật rồi tắt một practice incident:

```bash
python scripts/inject_incident.py --scenario cost_spike
python scripts/inject_incident.py --scenario cost_spike --disable
python scripts/validate_audit.py
```

Không sửa hoặc xóa audit event sau khi đã ghi. `data/audit.jsonl` là runtime data
và không cần commit; bài nộp lưu output validator đã scrub trong
`submission/evidence/audit-validation.txt`.
