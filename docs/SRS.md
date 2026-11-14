# SRS — Traceability AI-first v4

Nguồn chuẩn sản phẩm: [AI_CUSTOMER_SUPPORT_REQUIREMENTS](AI_CUSTOMER_SUPPORT_REQUIREMENTS.md). ID REQ/SC giữ nguyên; FR01–11 là nhóm chức năng legacy để đọc78 test cũ, không thay REQ mới.

| REQ | Hành vi bắt buộc | Owner/task | Acceptance |
|---|---|---|---|
| 001–005 | 5 mục điều hướng, search/filter, toàn hội thoại, trạng thái mail và mobile giữ input | A FS-A2/A3; B/C panel riêng | AC02/07/13 |
| 006–011 | Điều phối6 vai trò, nguồn/version/timing, lỗi/bất đồng chuyển review và manual/retry | A FS-A4; B FS-B2/B4; C FS-C2 | AC04/14/17 |
| 012–015 | KB CRUD/search/review/publish/archive, effective approved revisions và citation | B FS-B2/B4; C đọc nguồn | AC15/17 |
| 016–017 | Trạng thái Gmail/deferred, dữ liệu đơn/policy/KB có nguồn rõ | A FS-A2/A4; B FS-B1/B2 | AC03/12/16 |
| 018–020 | Business settings, optional agent toggles và escalation settings, validation/persistence | A FS-A3; B/C dùng snapshot | AC16/17 |
| 021–025 | Quyết định nhân viên, xác nhận đúng final revision, idempotency, fulfillment thủ công | C FS-C1..C4; A core UoW | AC01/05/06/08/17 |
| 026–027 | Input không đáng tin; actor staff/agent/system phân biệt; không secrets/log PII | A+B+C | AC10/17 |
| 028–032 | Cùng origin, panel isolation, lỗi giữ input, keyboard390px, auth và unknown=null | A+B+C | AC10/12/13 |

## Yêu cầu kế thừa
FR01 auth; FR02 hội thoại; FR03 quyết định/audit; FR04 policy; FR05 replies/send; FR06 ảnh; FR07 Cloud; FR08 polling; FR09 fixtures; FR10 manual; FR11 lifecycle. AC01–12 và78 test FS cũ tiếp tục bắt buộc; AC13–18 và18 tests mới bổ sung v4.

## Ràng buộc triển khai
- Schema0005 là CURRENT. CR-001 và API v4 là PROPOSED; review schema/wire/owner trước feature cần storage mới.
- Một chain Alembic additive, giữ dữ liệu cũ; không sửa schema_v1/backfill_v1/migrations đã chạy hoặc nhét KB/settings vào JSON legacy.
- AI role có thể dùng code deterministic hoặc provider; không buộc6 SDK calls/6 services. Phải có kết quả nguồn/trạng thái thật, không progress giả.
- Không network khi giữ row lock; kiểm context/source/config dependencies trước apply/check/send.
- Token/keys ở Secrets, binary ảnh private Storage; business data chỉ nhân viên đã đăng nhập.
- SC-001–007 cần pilot có dataset/rubric/baseline; ngưỡng không tự chứng minh bằng unit tests.
