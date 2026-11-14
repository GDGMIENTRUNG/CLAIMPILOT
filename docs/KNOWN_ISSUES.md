# Known issues — CURRENT và AI-first v4

Nguồn [requirements](AI_CUSTOMER_SUPPORT_REQUIREMENTS.md). Sau đợt docs, người dùng đã giao triển khai local: runtime v4/0006/20 bảng đã có, xem [implementation report](../IMPLEMENTATION_REPORT.md). Các bảng K01–K26 bên dưới ghi lịch sử/gap của đợt thiết kế, không phải trạng thái runtime mới nhất. 96 cases tài liệu cần đối chiếu từng ID, không suy từ tổng số automated tests.

## Gap hiện hành của bản local

| ID | Hiện trạng | Owner/gate |
|---|---|---|
| LOCAL-01 | Chưa kiểm live Gmail/Gemini/Groq; Gmail write mặc định tắt | B/C adapter và A credential wiring; kiểm live riêng |
| LOCAL-02 | Chưa hoàn thiện draft update/send/reconcile UI; draft đã lưu bị chặn bảo toàn nội dung remote | C FS-C3 |
| LOCAL-03 | Chưa nghiệm thu Cloud Run/SQL/GCS/Scheduler; ảnh hiện dùng private local adapter | A/B cloud gate, không ALL1 PASS |
| LOCAL-04 | Safety local kiểm luật/nguồn/version; chưa semantic quality hoặc confidence calibration/pilot. Có threshold nhưng không có confidence đã đo → review_required | B/C SC pilot |
| LOCAL-05 | Crash giữa provider/run chưa có recovery UI đầy đủ; run đang chạy có thể cần đối soát trước retry | A/B orchestration |
| LOCAL-06 | Chưa review độc lập A/B/C và chưa xác nhận toàn bộ96 test đặc tả | Reviewer theo TESTING_GUIDELINES |

## Lịch sử baseline và thiết kế trước triển khai local

| ID | Hiện trạng/rủi ro | Owner xử lý |
|---|---|---|
| K01 | BASE14/11:92 backend tests PASS local; 96 test FS/live/cloud hiện hành chưa nghiệm thu | từng domain chạy own regression và acceptance |
| K02 | Gemini timeout lịch sử, chưa probe lại | B text/ảnh FS-B2/FS-B3; C reply provider FS-C2 |
| K03 | Token readonly không draft/send | C FS-C3 OAuth compose; A factory/secrets mount |
| K04 | BASE đã thêm GMAIL_TOKEN_READ_ONLY=true: refresh giữ memory; chưa kiểm live mounted secret | A FS-A3/C FS-C3 kiểm OAuth cloud thực |
| K05 | threading.Lock chỉ1 process | A FS-A4 DB lock; C FS-C3 operation lock riêng |
| K06 | Project claimpilot-513010 ACTIVE nhưng billing chưa hoạt động; có infra scripts chưa provision/deploy | A FS-A3 xử lý billing/IAM; B bucket/model, C Gmail own |
| K07 | Chưa tính năng v3 trong code | Tất cả FS tasks vẫn TODO, không claim implemented |
| K08 | HEAD20ebb35 trước BASE; nhánh bàn giao feat/mvp-db-cloud-run-base, đích merge main; kiểm git log/status trước khi code tiếp | Nhóm review diff, không reset/commit hộ |
| K09 | Policy delivered guard sai not_received | B FS-B2 |
| K10 | Seed ngày/email cứng | BASE fixture manifests; A intake factories/B assessment/C resolution own test data |
| K11 | Keyword query bỏ follow-up không mã/từ khóa | A FS-A2/FS-A4 known-thread polling |
| K12 | Schema13 bảng đã có; pipeline cũ chưa ghi thread/messages/runs/version/audit cho email mới | A/B/C nối business lên schema0005, không thêm bảng/cột |
| K13 | Gmail không atomic với DB | C FS-C3 reserve/complete/unknown/reconcile qua shared UoW |
| K14 | Một staff account không phân biệt từng nhân viên | Giới hạn MVP, không hứa RBAC production |
| K15 | A/C đều có workload hạ tầng/tích hợp nặng | Cloud preflight sớm, contract harness/ghép08:45, B tự quản GCS/Gemini |
| K16 | Polling bounded có độ trễ/backlog | A UI last_success/deferred/cursor rõ |
| K17 | Code hiện tại monolithic main/App/models dễ conflict | BASE module shells/registries và file owner theo SHARED_CONTRACTS |
| K18 | Harness/interfaces chỉ là thiết kế chưa code | Chốt BASE trước phát triển; không nói B/C đã chạy độc lập khi chưa có artifact |
| K19 | DB0005 local và92 tests đạt; runtime gates nghiệp vụ/cloud chưa đủ | B/C review mapping; A hoàn thiện BASE harness/ports; không tự ALTER theo feature |

Đợt BASE đã giải quyết schema/container và thêm cấu hình; chưa giải quyết các feature/rủi ro còn lại bằng code. Thiếu Google/cloud là BLOCKED đúng phần, không mock production. Phân tầng owner cũ hết hiệu lực; tìm dòng “Mã cũ” trong ba bộ test fullstack nếu nhận bàn giao mã cũ.
## Gaps v4
| ID | Gap và ảnh hưởng | Owner/gate |
|---|---|---|
| K20 |0005 không có KB/settings/per-role run/safety history; không thể claim đủ v4 | CR-001 PENDING_REVIEW, A aggregate/B+C review |
| K21 | UI hiện list/detail cũ, chưa5 mục/search/progress/KB/settings | A shell; B KB; C quality/composer |
| K22 | Chưa KnowledgeService/eligibility/citations/source conflicts | B FS-B2/B4; C trước writer/send |
| K23 | Chưa settings immutable revisions và pin config cho reply | A FS-A3/C FS-C2 |
| K24 | Chưa coordinator/role history/check/preview-source invalidation | A FS-A4/B steps/C safety |
| K25 | SC pilot chưa dataset/rubric/manual baseline, số phần trăm chỉ đề xuất | Cả nhóm AC18/B4-T07 |
| K26 | Thêm KB/settings/safety tăng scope, timeline4h cũ hết là cam kết | Gate plan mới; không cắt P2 âm thầm rồi báo full done |
