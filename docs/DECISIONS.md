# Decisions — kế thừa v3 và đề xuất v4

D01–D23 dưới đây ghi lịch sử v3, không tự cấp quyền triển khai extension. Người dùng giao đồng bộ docs theo [requirements](AI_CUSTOMER_SUPPORT_REQUIREMENTS.md); giữ file nguồn đề xuất. D24–D29 mô tả mặc định thiết kế v4, PENDING_REVIEW trước code phần CR.

Các quyết định hiện hành giữ workflow v2, thay phân công phân tầng bằng ba phần fullstack; giới hạn draft-only/một quyết định/modal cũ không có hiệu lực. Đây là thiết kế TARGET, chưa code.

| ID | Quyết định | Lý do/hệ quả |
|---|---|---|
| D01 | Yêu cầu sản phẩm là đích; code được mở rộng/refactor | Bảo toàn công việc không có nghĩa khóa thiết kế thiếu |
| D02 | Một thread/canonical case, nhiều messages | Bổ sung không thành hồ sơ rời; không auto gộp theo order |
| D03 | Nhiều decisions append-only + resolution cụ thể | Request info không ngõ cụt; không mơ hồ approve gì |
| D04 | Workflow/processing/decision/reply/fulfillment tách biệt | Không coi AI xong/đã gửi là đã giải quyết |
| D05 | Nhân viên preview/confirm send trong app, draft phụ | Quy trình liền mạch vẫn Human-in-the-Loop |
| D06 | case_version và reply revision riêng; stale cần review | Context đổi không gửi nội dung cũ âm thầm |
| D07 | Persistent reservation/idempotency + unknown/reconcile | Gmail và DB không atomic, không claim exactly-once |
| D08 | Manual correction/verification/reply có audit | AI lỗi không khóa công việc; mismatch không auto reject |
| D09 | Frozen schema ba domain, A aggregate Alembic | B/C tự model/schema own, test qua harness không chờ A business; một head release |
| D10 | UI conversation/assessment/composer/timeline | Được đổi detail cũ nếu workflow cần |
| D11 | Same-origin image Run + SQL/Storage/Secrets | Cookie và dữ liệu bền vững, không local token cloud |
| D12 | Scheduler OIDC + DB lock, polling known threads | Không bỏ follow-up vì keyword; không auto-send |
| D13 | Policy demo-v2 và snapshot; loại vấn đề khác yêu cầu | Không giả policy chung mọi doanh nghiệp |
| D14 | Ảnh một/hai phía, không phán gian lận | Thiếu ảnh gốc vẫn hữu ích, limitations rõ |
| D15 | Một staff account và scope demo | Audit không quảng bá danh tính nhiều nhân viên |
| D16 | Đợt hiện tại chỉ docs | Không sửa code/migration/cloud trong lần chuẩn bị |
| D17 | Ba fullstack theo Workspace/Assessment/Resolution | Mỗi owner UI/API/DB/tests, không A backend/B frontend/C toàn Google |
| D18 | BASE ports/registry/harness trước feature | B/C bắt đầu độc lập với doubles test/dev; production không fake |
| D19 | Một URL Google Cloud Run, A platform/B GCS-AI/C Gmail write | Giữ đơn giản deploy, không ba microservice/DB |
| D20 | Không task thuyết trình, gate RELEASE | Giữ fixtures và acceptance như kiểm tra sản phẩm; mapping78 test giữ traceability |
| D21 | Khóa CLAIMPILOT_MVP_DB_V1 gồm13 bảng | Một dictionary cho các mốc; BASE dựng đủ trước FS tasks, không tự thêm bảng/cột |
| D22 | Tách text_analysis_runs và gmail_intake_failures | Giữ retries/failed/stale và lỗi trước parse, không bịa case hoặc ghi đè AI history |
| D23 | FK composite + operation snapshots + immutable GCS refs | Chặn gắn sai hồ sơ, lưu đúng nội dung đã xác nhận, đọc đúng ảnh đã đánh giá; Gmail vẫn không exactly-once |

Thay đổi sau: ghi ID/người quyết/thời điểm/lý do/docs-fixture ảnh hưởng, thông báo A/B/C trước merge. API/schema không đổi âm thầm, nhưng phát hiện thiếu thực tế phải được sửa có kiểm soát.
## Quyết định dẫn xuất v4 — PENDING_REVIEW

Cập nhật local14/11: yêu cầu tiếp theo của người dùng giao chạy mini hackathon local đúng requirements. CR-001 đã được hiện thực trong0006 sau thử clone/migration/data preservation. Quyết định này áp dụng LOCAL; review độc lập/liên thông v4 và quyền triển khai cloud vẫn chưa hoàn tất. D24–D29 giữ rationale thiết kế, không phải kết quả acceptance.
| ID | Thiết kế đề xuất | Hệ quả/reviewer cần chốt |
|---|---|---|
| D24 |5 mục workspace,6 role capabilities; một doanh nghiệp/Gmail/staff | A/B/C vẫn fullstack, không6 services/coding subagents |
| D25 | KB versioned submit/approve/archive, approved effective sources only | B owner nội dung/C source consumer; cùng account approve riêng, không giả review độc lập |
| D26 | Business/settings immutable snapshots; mandatory guards không toggle | A owner; optional evidence only, confidence threshold default null |
| D27 | Persist per-role attempts + citations/checks; freeze13 bảng chỉ corev3 | CR-001 đề xuất7 bảng; A aggregate, B KB/source review, C checks review; chưa authorize migration |
| D28 | Check/preview pin case/reply/source/settings/content; send revalidate | C owns quality/reserve, B resolves sources, A settings/core; old send wire cần review version transition |
| D29 |96 test đặc tả, AC01–18, SC pilot đo riêng | Không suy success/accuracy từ92 tests hoặc hứa khung4h đủ scope mới |

Trước triển khai CR: ghi approved/rejected/revised, người dùng/owner/reviewer, ngày, revision docs và lý do; chưa có record thì PENDING_REVIEW. Docs sync không phải reviewer VERIFIED sản phẩm hoặc quyền provision/send.
