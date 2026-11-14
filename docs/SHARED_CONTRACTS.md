# Shared contracts — fullstack AI-first v4

Nguồn [requirements](AI_CUSTOMER_SUPPORT_REQUIREMENTS.md). Core ports v3 dưới đây được kế thừa. Owner mới bổ sung: A settings/coordinator, B KB/retrieval, C quality/source-aware reply. Các extension DTO/API/storage là PROPOSED CR-001 cần review; domain không tự thêm JSON hoặc sửa snapshot0005.

BASE DB/models/migration0005 và container đã triển khai local ngày14/11; code harness/module shells/Principal/CaseStore mới vẫn chưa có. Không viết lại models domain hoặc tạo migration riêng: dùng mappings trong backend/app/models.py và frozen snapshot schema_v1.py; phát triển DTO/services trong domain của mình. Schema đã chốt là CLAIMPILOT_MVP_DB_V1 trong DATABASE_DESIGN (13 bảng); workflow v2/wire v3 được giữ, các field projection đọc thêm phải đồng bộ API. Contract-first không có nghĩa không có phụ thuộc: ba phần phát triển độc lập, sau đó ghép implementation thật.

## Tổ chức module và file owner

| Phần | Backend TARGET | Frontend TARGET | Trách nhiệm |
|---|---|---|---|
| A Workspace | app/modules/workspace: router, schemas, services, models, gmail_read | src/features/workspace: WorkspaceShell, LoginPage, CaseList, ConversationPanel, SyncStatus | auth/intake/conversation/core store; Cloud Run/SQL/Secrets/Scheduler |
| B Assessment | app/modules/assessment: router, schemas, services, models, text_ai, evidence, storage | src/features/assessment: AssessmentPanel, ManualReviewForm, EvidencePanel | order verification/manual/text/policy/ảnh/GCS; auth tại router dùng dependency chung |
| C Resolution | app/modules/resolution: router, schemas, services, models, gmail_write, reconcile | src/features/resolution: ResolutionPanel, DecisionPanel, ReplyComposer, FulfillmentPanel, HistoryPanel | quyết định/nháp/gửi/lifecycle; reserve-complete do C implement |
| Shared, A tích hợp | app/shared: contracts, case_store, auth dependency, google_credentials; main/config/database/models compatibility facade | src/shared: api client, contract types; App/main/style tokens là composition root | primitives và registration ổn định, không gom business B/C vào shared |

Python paths tương đối backend; TS paths tương đối frontend. Mỗi domain xuất `router` FastAPI và UI root nhận `{caseId,onCaseChanged}`; A đăng ký ba router, App render WorkspaceShell + AssessmentPanel + ResolutionPanel theo manifest ngay BASE. Domain fetch API own data; onCaseChanged invalidates detail, không truyền ORM/schema riêng qua UI props.

Legacy files không bị xóa: A quản read/sync entrypoint, B tiếp nhận policy/text adapters đang có qua facade, C Gmail write mới riêng. B/C không cùng sửa gmail.py chỉ để thêm read/send; google credential factory chung cấp client. Không circular import model module: FK/relationship string và tập trung import metadata ở registry.

## BASE: artifact chung trước code song song

Nhóm review hiện trạng Git và chốt một baseline có: toàn schema đích, enum/wire examples, domain directories/exports, DTO Protocols, test harness và dependency manifest. DB/models/migration aggregate đã có; A còn composition/primitives outline. B/C review mappings sẵn có, chuẩn bị DTO/service signatures và fixture phần mình. Khi A đang triển khai runtime thật, B/C dùng test doubles đúng Protocol để làm UI→API→DB của phần mình.

Harness chạy riêng từng domain với Session fixture, stub Principal/CaseStore/Google client có call counters; chỉ enable trong test app hoặc explicit development mode. Schema tạo bằng metadata chỉ trong test DB/schema tách biệt; production chỉ Alembic. Không coi harness là phần feature đã chạy thật. Migration cloud aggregate không cần hoàn thành trước khi B/C viết domain logic; field schema vẫn đã chốt.

## Interface nội bộ (không thay wire API)

| Interface | Owner thực thi | Dùng bởi / hành vi |
|---|---|---|
| `CaseStore.get_context(db,case_id) -> CaseContext` | A | B/C đọc projection chuẩn: case_version, tri-state, ownership, order, latest inbound ID, current decision ID, policy snapshot, workflow, fulfillment |
| `CaseStore.mutate(db,case_id,expected_case_version,actor,note) -> UnitOfWork` | A | B/C join transaction: lock/validate case, ghi own rows + core patch/audit nguyên tử; commit/rollback một lần; không network trong callback |
| `CaseStore.append_message(db,parsed,direction) -> IngestResult` | A | A inbound và C sent completion; unique Gmail ID, canonical thread, inbound bump/reopen; outbound không reopen |
| `CurrentStaff` dependency và `GoogleClientFactory.get_client()` | A | B/C dùng identity/client, không tự làm login/OAuth token riêng |
| `AssessmentService.analyze_message(case_id,message_id,basis_version)` | B | A sync gọi sau persist; đọc thread context, raw output lưu message; publish patch qua CaseStore nếu context không mới hơn |
| `EvidenceService.ingest_message(case_id,message_id,raw_bytes)` | B | A gọi sau saved inbound; MIME validation/storage/metadata do B; lỗi ảnh không hủy saved text |
| `AssessmentService.get_projection(db,case_id)` | B | Pure DB read trả verified_order/policy_snapshot/ownership và dữ liệu assessment theo CaseDetail, không gọi Gemini ở GET |
| `ResolutionService.get_history(db,case_id)` | C | Pure DB read trả decisions/replies/lifecycle projection theo CaseDetail, không gọi Gmail write ở GET |
| `AssessmentPanel`/`ResolutionPanel` UI contract | B/C | A chỉ compose và refresh theo onCaseChanged; mỗi người quản UI state/API own |
| `ResolutionService.reserve_reply(...)` và `complete_reply(...)` | C | Router C gọi để validate version/decision, persist operation; network Gmail write nằm giữa hai transaction; giữ needs_review khi inbound mới |

ParsedMessage giữ Gmail/thread/RFC headers/From/To/text/time theo API message fields; raw bytes chỉ truyền nội bộ trong lượt ingest, không DTO trả browser. IngestResult có case_id/message_id/created/became_needs_review/case_version. CaseContext là snapshot immutable, không SQLAlchemy entity mutable truyền qua module. C đọc sent history qua own model trong cùng UoW; B đọc evidence own models. DTO field wire chính xác theo API_SPECIFICATION.

UnitOfWork cho phép patch core theo quyền: A intake/auth/status; B extraction/verified order/ownership/policy/manual flag và invalidation current_decision khi dữ liệu trọng yếu đổi; C current decision/workflow/fulfillment/closed_at. Audit writer dùng cùng session. Nested commit bị cấm; network result completion dùng UoW mới. B/C không cần đợi A runtime để test UoW: fake đúng contract trước, DB thật joint contract tests ở BASE/ghép.

CaseStore.append_message khi được gọi bên trong UoW của C phải join cùng Session/transaction, không tự commit: sent reply + outbound message + audit cần atomic trong DB. Khi A intake dùng riêng thì A mở UoW quanh append trước khi gọi AI/network. CaseContext/GET projections không giữ lock qua request UI và không side effect Google. A compose reads từ B/C theo hai ports trên, không import write service/domain ORM để sửa hộ.

Version tăng chỉ cho event ngữ cảnh trong WORKFLOW; reply save/reserve/status-only completion không tăng case_version. Completion send chuyển workflow khi basis vẫn khớp, nếu inbound mới giữ needs_review. Business event làm version tăng đúng một lần; projection cũ cập nhật cùng transaction. Primitive này không tự chọn policy/decision thay domain owner.

## Schema, dependencies và thay đổi shared

- A quản orders/complaints/core audit/messages/sessions/integration_state/gmail_intake_failures; B quản text_analysis_runs/evidence_assets/evidence_analyses; C quản complaint_decisions/case_replies/reply_operations. Mọi field/type/default/FK đã có ở DATABASE_DESIGN, cả ba dùng mappings đã có trong app/models.py (domain models.py chỉ re-export); không tạo metadata mới hoặc thêm field theo từng màn hình.
- Migration aggregate0005 một head đã có từ snapshot metadata chung, gồm FK vòng; A giữ registry Base.metadata/models.py, B/C dùng lại trong test domain. Không tách lại thành ba metadata modules hoặc tạo migration mới để chia việc; không phải chờ A viết routes/services.
- B khai báo AI/Storage/image dependencies/env, C khai báo Gmail write/reconcile dependencies/env; A tổng hợp lock/settings/Secret bindings trước merge. Không pip/npm upgrade chéo hoặc tạo requirements/lock cạnh tranh.
- Shared change ghi DECISIONS + ảnh hưởng wire/schema/fixtures, owner tích hợp và báo cả ba; không tự đổi Protocol khiến feature khác không chạy.

Schema gate core v3: BASE có13 bảng; v4 cần review extension CR-001 trước feature mới, B/C review model mapping, A aggregate migration đúng head thực tế; DB01/DB02/DB04 có evidence local; DB gates còn lại chưa đủ và DB12 cloud NOT_RUN. Xem IMPLEMENTATION_REPORT. Sau BASE không tự ALTER hoặc gửi schema delta bất ngờ. Chỉ có change request được nhóm thống nhất mới thay database. Text run lưu raw output từng lần, message.analysis là cache; intake fail trước parse nằm riêng, không tạo complaint giả. CaseStore xác thực mailbox/canonical alias và join transaction để sent/outbound/audit atomic. Các pointer cùng case/reply dùng composite FK, không chỉ service check.

## Ghép và chống production giả

Mỗi owner giao UI/API/models/tests cùng nhau. Hợp nhất BASE + cả ba domain qua shared contracts, không theo thứ tự backend→frontend. Mock adapters chỉ tests/dev; Cloud Run release khởi động thất bại rõ nếu config fake/bypass auth. Nếu real service chưa sẵn thì trả lỗi/BLOCKED đúng, không gọi mock fallback. Không gọi send từ event hook sync/AI.

CaseStore chịu trách nhiệm clear resolved_at/closed_at/closed_by/close_note khi một event hợp lệ đưa workflow về needs_review; B chỉ yêu cầu mutation theo quyền, không cần tự sửa closure của C để vượt CHECK. Fulfillment completion cũ được giữ tới decision mới rồi reset theo WORKFLOW, audit giữ kết quả trước. Không dùng cache projection thay lịch sử text runs.
## Ports bổ sung v4
| Interface/owner | I/O và hành vi |
|---|---|
| SettingsService.get_snapshot(db) / A | immutable SettingsSnapshot={version_id,revision,display_name,language,tone,optional_roles,review_threshold}; config thiếu lỗi rõ |
| AgentCoordinator.start(db,case_id,basis,trigger,settings_snapshot) / A | AgentRun persisted; không network trong reserve; dispatch registered role ports theo dependencies, không Gmail write |
| AgentStepPort.execute(context,settings,source_refs) / B hoặc C | StepResult={role,status,output,confidence?,source_refs,missing_fields,review_reasons,error_code?}; coordinator persist, owner validate role payload |
| KnowledgeService.retrieve(db,query,as_of,limit=5) / B | SourceRef[] eligible approved only; query là nội bộ có giới hạn, không arbitrary URL |
| KnowledgeService.resolve(db,ref,as_of) / B | content/version/digest/eligible/stale_reason; exact revision, không tự thay sang latest |
| QualityService.check(db,case_context,reply,settings,refs) / C | persisted ReplyCheck, input fingerprint; network nếu có nằm ngoài lock; deterministic manual path giữ được |
| SourceValidator.revalidate(db,refs,settings_version_id) / B + A | kiểm nguồn/settings dưới transaction reserve của C; không commit hoặc gọi provider |

SourceRef và DTO public tại API/DATABASE. Business context thêm settings snapshot/agent run refs trong DTO mới; không sửa các cột/JSONschema1 tương ứng. Actor agent:<role> không được qua CurrentStaff dependency hoặc gọi staff mutation.
Feature exports: A WorkspaceShell/SettingsPanel/DataPanel/AgentProgress; B KnowledgePanel/AssessmentPanel/EvidencePanel/SourceList; C ResolutionPanel/QualityPanel. Root domain nhận caseId/onCaseChanged, SettingsPanel change phát config revision event, không replay mutation. A quản navigation5 mục và composition, B/C gửi integration manifest; mỗi người vẫn UI/API/DB/tests.

CR-001 là shared change request hiện hành. B review KB/source schema, C checks/reserve schema, A settings/coordinator và aggregate. Chưa duyệt thì tests dùng explicit contract fixtures; production không fake save/publish/agent status.
