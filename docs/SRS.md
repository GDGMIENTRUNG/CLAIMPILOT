# SRS — TARGET v3 và traceability fullstack

| ID | Yêu cầu | Task fullstack | Nghiệm thu |
|---|---|---|---|
| FR01 | Login/logout/me, CSRF và phiên hết hạn | FS-A1; router B/C dùng dependency BASE | AC10 |
| FR02 | Một hồ sơ nhiều email, bổ sung/mở lại, intake không trùng | FS-A2 + FS-C4 | AC02/AC07 |
| FR03 | Nhiều quyết định, phương án, audit/version | FS-C1 + shared CaseStore | AC01/AC02/AC06 |
| FR04 | Năm policy, missing fields/next action/version | FS-B1/FS-B2/FS-B4 | AC03/AC04/AC11 |
| FR05 | Prepare/edit/review/draft/send có xác nhận | FS-C2/FS-C3 | AC01/AC05/AC06/AC08 |
| FR06 | Ảnh private, một/hai phía, Gemini nhận xét | FS-B3 | AC02/AC09 |
| FR07 | Cloud Run/SQL/Secrets/Storage bền vững | FS-A3 + B private GCS manifests | AC12 |
| FR08 | Scheduler5 phút/OIDC/DB lock/last sync | FS-A4 | AC12 |
| FR09 | Fixture/seed đủ 5 nhóm, relative dates, lỗi và full-loop release | BASE + FS-A2/FS-B4/FS-C4; không task thuyết trình | AC11/AC12 |
| FR10 | Đính chính/xác minh/manual khi AI lỗi | FS-B1/FS-B4 + manual composer FS-C2 | AC03/AC04 |
| FR11 | Ghi thực hiện ngoài app/resolved/close/reopen | FS-C4 + A inbound primitive | AC01/AC07 |

## Phi chức năng

- NFR01: Không key/token/stacktrace/ảnh public; session/CSRF/OIDC đúng ranh giới.
- NFR02: AI/Gmail lỗi giữ dữ liệu/decision/body, không báo thành công giả.
- NFR03: Gmail unique/DB lock/persistent reservation, không hứa exactly-once khi provider timeout.
- NFR04: loading/empty/error/stale/unknown rõ, keyboard/mobile390px dùng được.
- NFR05: timeout/budget bounded, last_success/deferred rõ, không claim realtime.
- NFR06: UTC timestamps/ngày nghiệp vụ Asia/Ho_Chi_Minh, Decimal/string tiền.
- NFR07: frozen schema/backfill/additive migration một head, không xóa dữ liệu cũ.
- NFR08: isolated domain harness để ba fullstack bắt đầu song song; release Cloud Run cấm fake adapters/auth bypass.
- NFR09: schema CLAIMPILOT_MVP_DB_V1 đủ13 bảng/203 cột trong BASE, FK cùng case/reply và gates DB01–DB12; không thay DDL trong FS task nếu chưa có change request thống nhất nhóm. FROZEN_SPEC không thay runtime migration checks.

Enum [WORKFLOW](WORKFLOW.md), internal [SHARED_CONTRACTS](SHARED_CONTRACTS.md), wire/schema tại API/DATABASE, evidence [AC matrix](ACCEPTANCE_MATRIX.md). CURRENT chỉ phần được nêu ở CONTEXT; requirements mới chưa thành code vì docs đã xong. Không có requirement làm slide/thuyết trình.
