# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Nhóm 2
- Repository URL: https://github.com/HoangTuBangGia/Day13-K4-Observability
- Commit SHA cuối: dd0e2b67af2056ea079fa2f99fc252b331cc18f8
- Thành viên và vai trò:
  - Nguyễn Huy Hưng - MSSV 2A202601204 - Logging/PII, Tracing và Prompt Versioning.
  - Lương Quỳnh Chi - MSSV 2A202601630 - Dashboard/SLO/Alerts, Incident Investigation, Audit Log và Report.
  - Cả hai thành viên cùng kiểm thử, review evidence và chuẩn bị demo cuối.

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100
- Tổng số traces: Tối thiểu 20 trace executions từ hai đợt baseline và candidate (10 request mỗi đợt).
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: `submission/evidence/dashboard-baseline.png` và `submission/evidence/dashboard-incident.png`; runtime local tại `http://127.0.0.1:8501`.

## 3. Logging và tracing

- Evidence correlation ID: Baseline có 10 correlation ID duy nhất trên 10 request.
- Evidence PII redaction: `validate_logs.py` báo `Potential PII leaks detected: 0`.
- Evidence trace waterfall: `submission/evidence/ver1.png` và `submission/evidence/ver2.png`.
- Giải thích một span đáng chú ý: Generation `run` liên kết managed prompt, metadata và usage/cost; baseline trace có latency 0.94 s, candidate trace có latency 0.15 s trong evidence đã lưu.

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: Version 1 — labels `baseline`, `production` sau rollback.
- Version/label candidate: Version 2 — label `candidate`.
- Trace ID của mỗi version: baseline `a371b1ebaf831ac327a3f0bb75a3c1dc`; candidate `b2158898e8d884a6d4be69d466bfde8c`.
- Bằng chứng đổi label hoặc rollback: `submission/evidence/prompt_ver2_prod.png` chứng minh production chuyển sang v2; `submission/evidence/prompt_ver1_rollback.png` chứng minh rollback production về v1. Hai version nằm trong `prompt_ver1.png` và `prompt_ver2.png`.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ — 6/6 panel.
- Evidence dashboard: `submission/evidence/dashboard-baseline.png`.
- SLO đã chọn và lý do: P95 <= 3000 ms, error rate <= 2%, daily cost <= $2.50 và quality trung bình >= 0.75; bao phủ tốc độ, độ tin cậy, chi phí và chất lượng mà người dùng cảm nhận.
- Alert rules và runbook: `config/alert_rules.yaml` và `docs/alerts.md` gồm high latency, high error rate và low answer quality.

## 6. Điều tra challenge

- Challenge ID: `day13-k4-observability-v1` — incident `rag_slow`, affected feature `monitoring`.
- Triệu chứng từ metrics: Dashboard P95 tăng từ 879 ms lên 2651 ms (+1772 ms, khoảng 202%); P99 tăng từ 923 ms lên 3254 ms. Error rate vẫn 0%, vì vậy đây là suy giảm latency chứ không phải availability.
- Trace ID liên quan: `c3abd44b04a07ea5a61538c9d1689efb`; tổng trace 2.65 s, span `rag.retrieve` chiếm 2.50 s (khoảng 94% tổng latency). Evidence: `submission/evidence/challenge-trace.png`.
- Log line/correlation ID liên quan: session `k4-challenge-s01`, correlation ID `req-b64e908b`, event `retrieval_completed`, `latency_ms=2500`, `incident=rag_slow`. Bốn request challenge còn lại cũng có retrieval latency 2500 ms. Evidence: `submission/evidence/challenge-logs.txt`.
- Root cause: Retrieval bị incident `rag_slow` chèn độ trễ cố định 2.5 giây. Metrics khoanh vùng thời gian, trace xác định span chậm, và log xác nhận trạng thái incident cùng latency cụ thể.
- Fix action: Tắt `rag_slow` để khôi phục ngay; trong hệ thống thật, đặt retrieval timeout và dùng fallback document/cache khi vector store vượt ngân sách latency.
- Preventive measure: Theo dõi riêng retrieval latency, cảnh báo khi P95 vượt 2000 ms theo challenge threshold, áp dụng timeout/circuit breaker, và giữ runbook Metrics → Traces → Logs để giảm thời gian xác định nguyên nhân.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Huy Hưng (2A202601204) | Hoàn thiện JSON logging, correlation ID, request metadata, PII redaction; cấu hình Langfuse; tạo prompt v1/v2, trace baseline/candidate và bằng chứng rollback; viết test cho logging/tracing. | [4417c0cf1b8aa8ac187b8ca438d863bcc7cda019](https://github.com/HoangTuBangGia/Day13-K4-Observability/commit/4417c0cf1b8aa8ac187b8ca438d863bcc7cda019) | Structured logging, context propagation, bảo vệ PII, trace/span và quản lý vòng đời prompt. |
| Lương Quỳnh Chi (2A202601630) | Hoàn thiện dashboard 6 panel, SLO, alert và runbook; chạy baseline/challenge, điều tra `rag_slow` theo Metrics → Traces → Logs; hoàn thiện audit log, evidence và báo cáo incident. | [4417c0cf1b8aa8ac187b8ca438d863bcc7cda019](https://github.com/HoangTuBangGia/Day13-K4-Observability/commit/4417c0cf1b8aa8ac187b8ca438d863bcc7cda019) | Percentile, SLO/alert, phân tích root cause, correlation evidence và auditability. |

Phân công được cân bằng theo hai luồng kỹ thuật chính: Hưng phụ trách khả năng thu thập và truy xuất tín hiệu; Chi phụ trách trực quan hóa, vận hành và điều tra sự cố. Hai thành viên cùng chịu trách nhiệm kiểm thử và demo end-to-end.

## 8. Bonus — Audit log

- Triển khai audit log append-only riêng tại `data/audit.jsonl` cho thao tác bật/tắt incident.
- Actor ID được hash trước khi ghi; mỗi event có timestamp, correlation ID, action, target và outcome.
- Source: `app/audit.py`; validator: `scripts/validate_audit.py`; hướng dẫn: `docs/AUDIT_LOG.md`.
- Evidence validator: `submission/evidence/audit-validation.txt`.