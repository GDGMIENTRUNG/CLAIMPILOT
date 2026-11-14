# Release checklist — AI-first v4

Nguồn [requirements](AI_CUSTOMER_SUPPORT_REQUIREMENTS.md). Các mục core dưới đây vẫn bắt buộc; tổng hiện hành96 test và AC01–18, không78/AC01–12 riêng lẻ. Chưa phần nào của v4 được tick bởi lần sửa docs.

Đây là kiểm tra sản phẩm, không task chuẩn bị slide/thuyết trình. Tất cả checkbox chưa thực hiện, không bằng chứng PASS. Owner theo phần fullstack, ALL1 do cả nhóm review.

## Trước tích hợp

- [ ] BASE frozen schema/DTO/registry/harness đúng hợp đồng, ba worktree cùng baseline.
- [ ] A workspace UI/API/auth/intake; B assessment UI/API/models; C resolution UI/API/models có own tests MERGE và báo dependencies còn doubles.
- [ ] Shared schema/env/deps delta đã tổng hợp, Alembic một head và backfill trên dữ liệu cũ thử đạt.
- [ ] Không secrets/PII trong image/Git/frontend/log; fixtures tách môi trường thật.

## Trên Google Cloud Run

- [ ] Một URL HTTPS React/FastAPI cùng origin; health/readiness SQL; unknown API JSON404.
- [ ] Login/CSRF/auth router B/C hoạt động; internal Scheduler verify OIDC, không nhận cookie staff thay OIDC.
- [ ] DB/token/ảnh bền vững qua new revision; bucket private, runtime least privilege, token refresh không ghi mount.
- [ ] Scheduler run-now và một lượt5 phút thật; last_success/deferred đúng, follow-up không keyword vẫn nhập.
- [ ] Không mock adapters/auth bypass hoặc fixture fallback trong production; provider/model thực tế rõ.

## Toàn quy trình

- [ ] AC01: approve→preview/send→chờ thực hiện→ghi thực hiện ngoài app→resolved→close.
- [ ] AC02: request info→sent→khách bổ sung cùng thread→needs_review→ảnh/policy→decision/reply mới.
- [ ] AC03/04: mismatch/manual correction/AI lỗi xử lý tiếp, không mất nguyên bản/audit.
- [ ] AC05/06/08: draft/edit/confirmed send, stale/double click/timeout/unknown/reconcile; không auto-send/refund.
- [ ] AC07: inbound sau closed mở lại, outbound không reopen, dedupe/canonical thread đúng.
- [ ] AC09: Gemini ảnh thật một/hai phía/private content; thiếu ảnh không giả comparison.
- [ ] AC10/11/12: security, năm policy/boundary/fixture repeat, cloud/scheduler/restart và regression đủ.

Live chỉ mailbox nhóm được giao, không gửi lặp không cần thiết; cùng revision có thể dùng evidence cho nhiều quan sát. Ghi Test ID/AC/commit/revision/time/provider/mock-DB-browser-live-cloud/results/reviewer trong TASK/evidence, không tự tích PASS từ fixture.

## Freeze và phục hồi

- [ ] Revision tốt/digest/schema compatibility được ghi; task chưa đủ evidence giữ REVIEW/BLOCKED.
- [ ] Rollback trên môi trường thử: pause Scheduler/mutations, không hai writer schema khác, không drop/downgrade DB.
- [ ] Sau kiểm thử thống nhất việc giữ/pause tài nguyên có chi phí; không tự xóa DB/bucket.
## Gate v4 bổ sung
- [ ] Review CR-001 có record quyết định; schema extension/wire/owner đã duyệt, không sửa migration0005 hoặc JSON legacy.
- [ ]96 cases A38/B26/C32 có evidence từng variant; AC13–17 real integration; SC/AC18 chưa đo ghi NOT_RUN.
- [ ]5-tab nav/search/filter/mobile/keyboard/dirty-input và panel error isolation đạt.
- [ ]6 role status/time/source/attempt persisted qua restart; required failure không completed, stale không đè manual.
- [ ] KB draft/submit/approve/publish/archive/expiry/conflict đúng; source link mở đúng historical revision.
- [ ] Settings save/reload/version/new-content-only, guardrails không tắt, invalid/409 không fake success.
- [ ] AI/manual reply có safety; source/config/context/content đổi làm preview/check stale, send không dispatch; replay idempotency không resend.
- [ ] Sent/case history/KB settings snapshots giữ qua image revision; không log PII/secrets hoặc public KB nội bộ.
- [ ] Báo rõ scope P1/P2 chưa xong; không công bố SC-001–007 đạt từ test fixtures.
