# Prompt cho ba fullstack và reviewer — v3

Mỗi người một phiên/worktree, nhận một feature domain, không tự spawn agent. Mã hiện hành FS-A1..FS-A4/FS-B1..FS-B4/FS-C1..FS-C4; không dùng vai trò backend/frontend/integrations cũ.

## Mở đầu — copy và thay A/B/C

> Đọc AGENTS.md, docs/CONTEXT.md, WORKFLOW.md, SHARED_CONTRACTS.md, TASK.md và IMPLEMENTATION_PLAN.md. Tôi giao bạn vai trò fullstack [A Workspace / B Assessment / C Resolution] và các mã FS tương ứng. Đọc task cá nhân, DATABASE/API/UI_UX/features/security/errors và test cases đúng owner. Kiểm Git/code thực tế, giữ thay đổi sẵn có. Tự làm UI, API, persistence và tests trong domain của bạn, dùng BASE frozen contract/test harness khi implementation domain khác chưa có; không chờ người khác viết backend/frontend hộ. Thiếu contract thì đề xuất rõ, báo owner; không tự đổi wire/schema. Dùng mocks chỉ test/dev, Cloud Run release phải nối thật. Thực hiện phần được giao và bàn giao theo test IDs/evidence, không claim live bằng mock, không tự send/refund từ AI/scheduler.

## Task và tests

- [A Workspace + Cloud Run](tasks/A_WORKSPACE.md), [test A](test-cases/A_TEST_CASES.md).
- [B Assessment + Evidence](tasks/B_ASSESSMENT.md), [test B](test-cases/B_TEST_CASES.md).
- [C Resolution + Communication](tasks/C_RESOLUTION.md), [test C](test-cases/C_TEST_CASES.md).

## BASE — cả ba chuẩn bị, A tổng hợp

Schema đọc từ DATABASE_DESIGN, version CLAIMPILOT_MVP_DB_V1, 13 bảng. Không tự thiết kế lại hoặc bổ sung bảng/cột vì riêng task; ánh xạ đủ model/FK/default/index trong BASE, kiểm DB01–DB12, một Alembic head. Các gate còn NOT_RUN thì chưa báo baseline DB hoàn thành. Key/provider/model API cấu hình bên ngoài SQL.

> Review dirty Git/baseline, chốt schema và module metadata/DTO/exports/config manifests. A chuẩn bị CaseStore/Principal/GoogleClientFactory Protocols, registry và migration outline. B/C tự chuẩn bị own module models/DTO/factories, dùng test doubles để bắt đầu fullstack. Không để dependency vào A business runtime chặn B/C. Worktree cùng baseline, không reset/commit hộ. Google project/billing/OAuth/quota do owner phần tương ứng kiểm tra trước release, không thêm nhiệm vụ thuyết trình.

## Tiếp tục phiên

> Đọc task FS mới; nếu nhận bàn giao mã cũ, tìm dòng “Mã cũ” trong ba bộ test để xác định FS-ID hiện hành. Bàn giao: [commit/file/tests/blocker]. Kiểm hiện trạng thay vì tin báo xong. Tiếp tục domain UI/API/tests của bạn; thiếu dependency runtime dùng contract double ở test harness, real integration còn thiếu ghi BLOCKED/REVIEW. Unknown side effect phải đối soát, không retry gửi mù.

## Ghép sản phẩm — A tích hợp, B/C xác minh domain

> Ghép BASE + Workspace + Assessment + Resolution theo registry/ports, không theo thứ tự backend→frontend. Review migration một head/deps/env/wire/CaseStore quyền patch, thay dev doubles bằng implementation thật. B/C tự giải conflict trong domain; A tích hợp shared. Chạy MERGE tests rồi RELEASE/AC01–AC12 trên Cloud Run, kiểm không fake adapters/auth bypass trong production. Không chọn ours/theirs toàn bộ để né conflict.

## Reviewer độc lập

> Review task [FS-ID] trên đúng commit/revision: đọc source contracts, own test IDs và evidence, không mặc định tin tác giả nói done. Đối chiếu mọi biến thể và đúng loại mock/DB/browser/live/cloud; chạy lại kiểm tra liên quan khi có thay đổi, lỗi hoặc evidence thiếu. Không tự sửa kỳ vọng/code/merge/deploy/send ngoài phạm vi review. Báo PASS/FAIL/NOT_RUN/BLOCKED theo test, lỗi/file/ảnh hưởng/owner sửa; chỉ đề nghị VERIFIED khi đủ gate. Một feature dùng mock chưa chứng minh ALL1/Cloud Run release.

## Bàn giao

```text
Task FS / owner / domain:
Branch + commit / Cloud Run revision:
UI/API/models/tests đã làm:
Shared schema/env/deps/interface delta cần tích hợp:
Test IDs/biến thể + thực tế + MERGE/RELEASE + reviewer:
Loại mock/DB/browser/Google-live/cloud + link evidence sanitized:
Blocker, phần còn mock và việc cần nối thật:
```
