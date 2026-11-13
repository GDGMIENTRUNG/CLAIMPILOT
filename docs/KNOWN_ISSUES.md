# Known issues — CURRENT và rủi ro fullstack v3

| ID | Hiện trạng/rủi ro | Owner xử lý |
|---|---|---|
| K01 | Khảo sát backend31pass/31DB setup errors, chưa full pass | FS-A3 baseline DB; từng domain chạy own regression |
| K02 | Gemini timeout lịch sử, chưa probe lại | B text/ảnh FS-B2/FS-B3; C reply provider FS-C2 |
| K03 | Token readonly không draft/send | C FS-C3 OAuth compose; A factory/secrets mount |
| K04 | Refresh ghi token local, cloud mount readonly | A FS-A3 shared credentials, C dùng factory |
| K05 | threading.Lock chỉ1 process | A FS-A4 DB lock; C FS-C3 operation lock riêng |
| K06 | Chưa cloud artifacts/project/billing/IAM xác minh | A FS-A3, B bucket/model, C Gmail prerequisites own |
| K07 | Chưa tính năng v3 trong code | Tất cả FS tasks vẫn TODO, không claim implemented |
| K08 | Dirty Git/0004 chưa commit | BASE review, không reset/commit hộ |
| K09 | Policy delivered guard sai not_received | B FS-B2 |
| K10 | Seed ngày/email cứng | BASE fixture manifests; A intake factories/B assessment/C resolution own test data |
| K11 | Keyword query bỏ follow-up không mã/từ khóa | A FS-A2/FS-A4 known-thread polling |
| K12 | Schema cũ một email/không thread/ảnh | BASE frozen schema, A migration/backfill+metadata read, B evidence schema |
| K13 | Gmail không atomic với DB | C FS-C3 reserve/complete/unknown/reconcile qua shared UoW |
| K14 | Một staff account không phân biệt từng nhân viên | Giới hạn MVP, không hứa RBAC production |
| K15 | A/C đều có workload hạ tầng/tích hợp nặng | Cloud preflight sớm, contract harness/ghép08:45, B tự quản GCS/Gemini |
| K16 | Polling bounded có độ trễ/backlog | A UI last_success/deferred/cursor rõ |
| K17 | Code hiện tại monolithic main/App/models dễ conflict | BASE module shells/registries và file owner theo SHARED_CONTRACTS |
| K18 | Harness/interfaces chỉ là thiết kế chưa code | Chốt BASE trước phát triển; không nói B/C đã chạy độc lập khi chưa có artifact |

Docs không giải quyết các lỗi bằng code. Thiếu Google/cloud là BLOCKED đúng phần, không mock production. Phân tầng owner cũ hết hiệu lực; tìm dòng “Mã cũ” trong ba bộ test fullstack nếu nhận bàn giao mã cũ.
