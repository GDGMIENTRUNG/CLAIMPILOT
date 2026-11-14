# Coding conventions — AI-first v4

Nguồn [requirements](AI_CUSTOMER_SUPPORT_REQUIREMENTS.md), core conventions bên dưới giữ nguyên. Baseline13 bảng frozen chỉ phạm vi v3; CR-001 extension cần review, không codegen/migrate trong đợt docs.

- Giữ FastAPI/SQLAlchemy 2/Pydantic 2 và React/TypeScript/Vite; cho phép refactor/component/router/model mới khi đáp ứng workflow, không dựng lại bằng stack khác.
- Router: HTTP/auth/validation; service: rule/state; ORM: persistence. Không network trong row-lock transaction. State machine theo WORKFLOW, wire API, schema DATABASE_DESIGN.
- Pydantic input/output, enums/nullability explicit; extra fields không được dùng lách validation. Client không đặt actor, recipient, workflow_status hay policy_result trực tiếp.
- Mỗi fullstack quản router/models/schemas/services/frontend/tests trong domain; A quản aggregate requirements/lock/migration/composition, B/C gửi dependency/env/schema manifests để tích hợp (không đợi A viết backend). Không tạo hai migration heads hoặc rewrite migration đã áp dụng.
- UTC aware timestamps; ngày nghiệp vụ Asia/Ho_Chi_Minh; tiền Decimal ↔ JSON string. Không random mock thành dữ liệu app.
- Frontend api helper hỗ trợ method/body/CSRF/204/status/code, cùng origin; 401 giữ route và không replay POST. Không localStorage session.
- React components theo UI_UX: Conversation/Assessment/Decision/Reply/Evidence/Fulfillment/Timeline. Cho phép thay bố cục detail cũ để đủ workflow; không format/redesign toàn repo không liên quan.
- Case version là business context, reply revision là nội dung; không dùng updated_at thay optimistic lock. Không đổi hai cơ chế thành một mà không sửa contract.
- original extraction được giữ, manual override có audit; AI completion không ghi đè sửa tay mới.
- Email render text, ảnh qua auth endpoint, không dangerouslySetInnerHTML hoặc URL fetch tùy ý.
- Config mới có env example an toàn, không secrets trong VITE/image/log. Naming Python snake_case, TS camelCase/components PascalCase.
- Comment giải thích constraint/side-effect; báo cáo ghi kết quả test thực, không “100% done” khi chưa live.

- Tách domain theo SHARED_CONTRACTS: workspace/assessment/resolution exports cố định trong BASE, legacy facades giữ tương thích; không cùng chỉnh App/main/models/config monolithic.
- CaseStore UoW shared được join bởi domain write; B/C sở hữu rule/reserve-complete tương ứng, không lấy ORM domain khác thay CaseContext snapshot.
- Mocks/Principal stub chỉ test/dev; release startup cấm fake adapter/auth bypass, không return fake success khi dịch vụ chưa cấu hình. Một image/URL Cloud Run, không chia microservice theo developer.
- Schema khóa CLAIMPILOT_MVP_DB_V1: ORM phải đúng type/null/default/composite ForeignKeyConstraint/partial indexes trong DATABASE_DESIGN. BASE dựng đủ13 bảng một lần, mốc 50%/80% không tự thêm cột. JSON có schema cố định; key/model/provider thay config, không thêm field SQL theo nhà cung cấp.
## Quy ước bổ sung
A owns settings/coordinator/shared, B knowledge/retrieval/assessment, C quality/replies. SourceRef/SettingsSnapshot/StepResult có typed DTO chung, nullable confidence explicit, role status enum tách lifecycle. Không dùng any/random hoặc timer UI để giả trạng thái.
SQL queries parameterized; search escape wildcard, limit refs/snippets/results; không fetch source URL. Approved KB body và settings version immutable, new revisions thay inplace update. LLM output phải validate rồi resolve references server-side.
Case mutation join UoW; progress persistence không tự bump business version. Hash canonical JSON gồm nội dung và dependency versions; dữ liệu private không log/hash input thô ra frontend. Check/send validation không provider network trong row lock.
Không thêm keys vào Analysis/policy_snapshot/request_snapshot schema1 để chứa extension. Khi review CR approved phải cập nhật DTO/DB/API/tests đồng bộ trong migration chain mới; không rewrite snapshot đã áp dụng.
