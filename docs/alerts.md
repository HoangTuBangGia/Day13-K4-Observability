# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: High API latency
- Severity: Critical
- SLI/SLO liên quan: P95 latency <= 3000 ms
- Điều kiện và thời gian duy trì: P95 latency > 3000 ms trong 5 phút.
- Ảnh hưởng tới người dùng: Người dùng phải chờ lâu hoặc request timeout.
- Ba bước kiểm tra đầu tiên: Xác nhận P95 trên dashboard; mở các trace chậm; tìm log cùng correlation ID để xác định span gây nghẽn.
- Mitigation tạm thời: Giảm concurrency, vô hiệu hóa incident/feature lỗi hoặc chuyển sang fallback đã kiểm chứng.
- Owner: Nguyễn Huy Hưng

## Alert 2

- Tên: High API error rate
- Severity: Critical
- SLI/SLO liên quan: Error rate <= 2%
- Điều kiện và thời gian duy trì: Error rate > 2% trong 5 phút.
- Ảnh hưởng tới người dùng: Request thất bại và không nhận được câu trả lời.
- Ba bước kiểm tra đầu tiên: Xem error breakdown; mở trace lỗi; đối chiếu `error_type` và correlation ID trong log.
- Mitigation tạm thời: Rollback thay đổi gần nhất hoặc tắt dependency/feature đang gây lỗi.
- Owner: Nguyễn Huy Hưng

## Alert 3

- Tên: Low answer quality
- Severity: Warning
- SLI/SLO liên quan: Average quality score >= 0.75
- Điều kiện và thời gian duy trì: Quality score trung bình < 0.75 trong 15 phút.
- Ảnh hưởng tới người dùng: Câu trả lời kém liên quan hoặc thiếu căn cứ.
- Ba bước kiểm tra đầu tiên: Kiểm tra panel quality; so sánh prompt version trong trace; kiểm tra retrieval input/output của trace bất thường.
- Mitigation tạm thời: Rollback label `production` về prompt baseline đã kiểm chứng.
- Owner: Nguyễn Huy Hưng
