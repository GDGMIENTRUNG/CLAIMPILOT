# Checklist phát hành sản phẩm — Cloud Run

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
