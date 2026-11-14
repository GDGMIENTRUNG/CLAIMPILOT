# Task board — AI-first v4, ba fullstack

## Cập nhật LOCAL sau yêu cầu chạy mini hackathon
Đã có implementation chung local (auth/workspace/KB/settings/assessment/composer/checks/preview và adapters), schema0006/20 bảng.111 automated tests và Chrome desktop/mobile smoke đạt; xem IMPLEMENTATION_REPORT. Chưa review độc lập từng FS/96 cases hoặc live Google/cloud, nên các task phía dưới không tự chuyển VERIFIED. CR-001 đã migrate LOCAL theo yêu cầu mới; BLOCKED_CR ở bảng là trạng thái kế hoạch trước đó, cloud/release gates vẫn chưa hoàn tất.

Nguồn [REQ-001–032](AI_CUSTOMER_SUPPORT_REQUIREMENTS.md). Đây là phân rã docs để review; không tự cho phép code/migration/cloud.12 FS IDs được giữ; nội dung mở rộng có nhãn CR-001. Feature chưa được thực hiện bởi lần sửa docs này.

| ID | Owner | Đầu ra UI + API + persistence + tests | Gate/phụ thuộc | Status |
|---|---|---|---|---|
| BASE | A tổng hợp, B/C review | Core DTO/CaseStore/Principal/registry/harness; review CR-001/API v4/settings/source refs | DB0005/container đã có; extension chưa duyệt | IN_PROGRESS |
| FS-A1 | A | Login/session/CSRF/rate-limit/shared API client bảo vệ cả KB/settings/agents | BASE identity contract | TODO |
| FS-A2 | A | 5-tab shell, queues/search/filter/conversation, Gmail intake/dedupe/technical queue, data read/fixtures | B/C ports doubles lúc đầu | TODO |
| FS-A3 | A | CaseStore/composition/Cloud Run; business+agent settings UI/API/storage; aggregate migration sau CR review | Settings storage BLOCKED_CR; cloud billing/IAM kiểm lại | TODO |
| FS-A4 | A | OIDC/Scheduler/DB lock/cursor/deferred; orchestration coordinator, agent progress/status API/UI | Agent persistence BLOCKED_CR; B/C step ports | TODO |
| FS-B1 | B | Lookup/ownership/manual correction + order/policy/source context UI/API | Shared CaseContext/UoW | TODO |
| FS-B2 | B | Text/policy agent; KB CRUD/search/submit/approve/archive UI/API; approved-source retrieval | KB storage BLOCKED_CR | TODO |
| FS-B3 | B | MIME/private GCS/Gemini evidence agent + EvidencePanel | Existing asset schema; run refs sau CR | TODO |
| FS-B4 | B | Version/manual/stale protection; citation freshness/conflicts, KB revision tests and datasets | Source/settings snapshot contract | TODO |
| FS-C1 | C | Staff decisions/resolution/history/snapshot/version, cảnh báo từ AI | BASE; không agent approve | TODO |
| FS-C2 | C | AI/manual composer + pinned KB/settings sources, safety/quality evaluation UI/API | Checks storage BLOCKED_CR; B retrieval/A config | TODO |
| FS-C3 | C | Confirmed send/draft/idempotency/unknown/reconcile; kiểm lại check/source/revision tại reserve | Auth/UoW + CR checks | TODO |
| FS-C4 | C | Manual fulfillment/close/reopen/history; full-loop + pilot timing observations | Không payment; A inbound | TODO |
| ALL1 | A+B+C | AC01–18/96 test cases/MERGE+RELEASE, SC pilot có dataset/baseline | Real Cloud/Google, extension được duyệt | TODO |

BLOCKED_CR là trạng thái dependency/biến thể, không thay trạng thái toàn task khi phần độc lập còn làm được. Trước khi bắt đầu phần extension, ghi reviewer, quyết định CR, migration/wire version vào DECISIONS; chỉ sau đó A được tổng hợp chain mới.

## Evidence và bàn giao
Baseline trước đây: commit fad5fe1, merge main74d0936;13 bảng/203 cột/revision0005,92 backend tests local/image và container/browser smoke lịch sử. Không có bằng chứng live v4.
Mỗi owner bàn giao task/branch/commit/files/DTO/env/deps delta/test ID và từng biến thể/type(mock,DB,browser,live,cloud)/timestamp/blocker/reviewer. Owner đề nghị REVIEW; người khác xác nhận VERIFIED. A tổng hợp board chung, B/C sửa module/test docs phần mình để tránh conflict.
