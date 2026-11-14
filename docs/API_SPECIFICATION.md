# API specification — core v3 và extension AI-first v4

Nguồn REQ-001–032: [requirements](AI_CUSTOMER_SUPPORT_REQUIREMENTS.md). Sau đợt docs, người dùng đã giao triển khai local; auth/KB/settings/agent/check/preview và core workflow đã có runtime, xem [implementation report](../IMPLEMENTATION_REPORT.md). Các đoạn TARGET/PROPOSED bên dưới giữ đích hợp đồng, không chứng minh mọi endpoint/live/cloud đã hoàn tất. Auth/Origin/CSRF áp dụng cả KB/settings/agents.

Base `/api`, JSON UTF-8, UTC ISO8601; case ID int (complaint cũ), ID bảng mới UUID string; tiền decimal string. Enum nghiệp vụ tại [WORKFLOW](WORKFLOW.md). Giữ đường dẫn API hiện có; không phải giữ các giới hạn một email/một quyết định của docs v1.

Runtime local: `review-context` hiện hỗ trợ `{expected_case_version,expected_reply_revision,note}` cho reply chưa gửi cùng quyết định; giữ body, tăng revision, ghim lại nguồn đủ điều kiện/settings qua một lượt staff_context_review có audit. Preview cũ bị vô hiệu; phải check/preview/xác nhận lại. Chưa hỗ trợ các fields chấp thuận ghi đè remote draft (`accept_local_over_external`/`expected_external_hash`) hoặc reconcile đầy đủ ở phần thiết kế bên dưới. Preview trả `check` và envelope chung `quality_check`, cùng một check. Không suy quyền live-send từ endpoint có sẵn.

## CURRENT giữ đường dẫn

| Method/path | Input | Output cũ giữ lại |
|---|---|---|
| GET /health | — | status, public, DB readiness |
| GET /integrations/status | — | gmail_configured,gemini_configured,ai_provider,ai_model,ai_configured,note |
| GET /dashboard/stats | — | total,pending_review,insufficient_information,processed |
| GET /complaints | page>=1,page_size 1..100,case_status?,complaint_type? | items,total,page,page_size |
| GET /complaints/{id} | — | ComplaintDetail |
| POST /gmail/sync | — | successful,skipped,failed,deferred,errors |
| POST /complaints/{id}/analyze | — | Detail; TARGET retry latest failed inbound, không overwrite manual correction |

## Auth và lỗi

- POST `/auth/login` `{username,password}` → 200 `{username,csrf_token,expires_at}` + cookie cp_session HttpOnly/SameSite=Lax/Secure cloud/Path=/, TTL 28800s. Login kiểm tra Origin, lỗi 401 invalid_credentials.
- GET `/auth/me` → cùng shape; POST `/auth/logout` → 204 và revoke session.
- Session token random >=32 byte; DB lưu SHA256. CSRF token = SHA256(`csrf:` + raw session token), DB lưu hash token CSRF; me tính lại từ cookie. Không trả session token trong JSON.
- Tất cả API nghiệp vụ cần phiên. POST/PATCH/DELETE dùng cookie phải kiểm tra Origin đúng PUBLIC_BASE_URL và `X-CSRF-Token` (login chỉ kiểm Origin). Internal Scheduler dùng OIDC riêng; health public.
- Lỗi `{detail:string,code:string}`; 401/403/404/409/422/503. Validation Pydantic 422 có thể detail array; frontend xử lý được. API lạ JSON 404, không SPA HTML.

## Shapes TARGET

**CaseSummary** bổ sung vào ComplaintOut: `workflow_status,processing_status,ownership_status,case_version,current_decision_id?,decision_status,fulfillment_status,needs_manual_review,last_message_at,reply_status?`. Các field cũ giữ để tương thích.

**CaseDetail** thêm `messages:Message[],decisions:Decision[],replies:Reply[],audit_events:AuditEvent[],policy_version?,policy_snapshot,closed_at?`; original email cũ giữ nguyên, không thay bằng thư mới nhất. MVP detail trả toàn bộ lịch sử của dataset nhỏ, không phân trang lịch sử.

**Message**: `id,gmail_message_id,gmail_thread_id?,direction,sender_email,recipient_email,subject,body,occurred_at,processing_status,processing_error?,analysis`. Raw OAuth/MIME không xuất ra client.

**Decision**: `id,complaint_id,action,resolution,note,missing_fields:string[],actor,basis_case_version,assessment_snapshot,proposed_amount?,currency,created_at`. proposed_amount decimal string hoặc null, currency VND; server derive từ order, không nhận số tiền tùy ý từ client.

**Reply**: `id,complaint_id,decision_id,in_reply_to_message_id,recipient_email,subject,body,status,basis_case_version,revision,is_stale,gmail_draft_id?,gmail_sent_message_id?,error_code?,sent_at?,updated_at`. Không trả attempt token/internal RFC ID. Reply response envelope `{reply:Reply,case_version:int}`.

**AuditEvent**: `id,event_type,actor,note,before_data,after_data,created_at` đã lọc dữ liệu nhạy cảm. OrderOut thêm purchased_at/product_name/total_amount nullable và currency VND. CaseDetail thêm resolved_at/closed_by/close_note nullable và `fulfillment_details:{completed_at,completed_by,reference,note}` với từng field nullable; lấy từ các cột đã chốt, không tạo bảng payment hoặc fulfillment mới.

## Case list và dashboard

- GET `/complaints` thêm `workflow_status?,queue?`; queue=work (mặc định, is_complaint=true) hoặc technical (is_complaint NULL/true và processing failed/pending, không chứa false). workflow filter chỉ lọc nghiệp vụ, không giấu lỗi phân tích đã xác nhận complaint.
- Cả hai queue và counters chỉ tính canonical_case_id NULL. GET detail theo alias legacy resolve về canonical và trả ID/version canonical; các mutation resolve/lock/check version trên canonical. Staff được đọc candidate NULL trong technical queue để manual review; false không hiển thị như complaint. Không sửa cột is_complaint thành false chỉ để giấu legacy alias.
- GET `/dashboard/stats` thêm `workflow_counts:{needs_review,waiting_customer,waiting_fulfillment,resolved,closed},technical_failed:int`. Legacy counters là projection theo DATABASE_DESIGN; UI mới dùng workflow_counts.
- GET `/integrations/status` thêm `last_attempt_at?,last_success_at?,last_error_code?,deferred_count`. Presence credentials không chứng minh connectivity.
- GET `/integrations/status` thêm intake_failed_count integer>=0. GET `/integrations/intake-failures` (staff auth) nhận page/page_size/status? và trả `{items:[{gmail_message_id,gmail_thread_id?,complaint_id?,error_code,status,attempt_count,first_seen_at,last_attempt_at,resolved_at?}],total,page,page_size}` từ gmail_intake_failures; chỉ metadata sanitized, không raw MIME. Technical UI có thể xem lỗi chưa tạo được case mà không dựng complaint giả; không public API reset/ignore trong MVP.
- GET `/complaints/{id}/messages` → `{items:Message[]}`; GET `/complaints/{id}/decisions` → `{items:Decision[]}`; GET `/complaints/{id}/audit` → `{items:AuditEvent[]}`. Timeline dùng occurred_at/created_at, stable tie-break ID.

## Manual và reassessment

PATCH `/complaints/{id}/review`:
```json
{"expected_case_version":3,"note":"Đã kiểm tra dữ liệu khách bổ sung","is_complaint":true,"order_id":"CPDEMO003","complaint_type":"damaged_item","requested_action":"replacement","ownership_confirmation":null}
```
Fields ngoài version/note đều optional; ownership_confirmation nếu xác minh thủ công là `{verified:true,reason:"Căn cứ xác minh..."}`. order_id thay đổi reset ownership dựa email/đơn mới, không giữ xác minh cũ. Không cho client sửa trạng thái nghiệp vụ/actor/policy_result trực tiếp. Server tra DB và đánh giá lại, tăng version, append audit; 200 CaseDetail. Không tìm thấy mã là kết quả order_not_found, không giả verified. Candidate lỗi được nhân viên xác nhận/sửa đủ dữ liệu có projection processing_status completed với source manual; original message analysis/error vẫn giữ.

Có thể gửi `acknowledge_manual_review:true` kèm note và đơn đã chọn để xác nhận đã xem tình huống nhiều đơn/người gửi; server clear needs_manual_review, không tự merge/split hoặc tự thay correspondent. Nếu đổi order/type/requested_action/ownership thì current_decision_id trở về null, cần quyết định mới; quyết định/reply/fulfillment cũ giữ trong lịch sử. Chỉ acknowledge banner hoặc ghi note không thay dữ liệu không hủy quyết định.

POST `/complaints/{id}/reassess` `{expected_case_version,note}` → CaseDetail, đánh giá deterministic từ DB/manual data hiện có; không cần gọi AI. AI retry lưu analysis gốc mới nhưng không ghi đè manual override đã audit. Snapshot ghi rõ nguồn dữ liệu AI/manual.

## Decisions và vòng xử lý

POST `/complaints/{id}/decisions`:
```json
{"expected_case_version":4,"action":"approve","resolution":"replacement","note":"Đổi sản phẩm sau khi kiểm tra ảnh","missing_fields":[]}
```
Note trim 1..2000; action/resolution theo WORKFLOW. request_information cần missing_fields 1..20 strings (1..200 ký tự/mục). Chỉ approve cần ownership email_matched/manually_verified và có order; thiếu thông tin vẫn được request_information. 201 `{decision:Decision,case_version:int}`. Mỗi lần append, không PATCH/xóa decision. Sau quyết định cũ đã gửi vẫn được quyết định mới, có note nêu thay đổi và audit; không đảo giao dịch ngoài app. Chặn khi reply operation đang network (409 reply_busy).

Quyết định mới đặt fulfillment_status pending nếu approve, not_required nếu reject/request_information; kết quả thực hiện trước đó vẫn ở audit/snapshot, không bị xóa. Không cho đổi quyết định trên closed cho tới reopen. Một decision chưa gửi có thể được thay bởi decision mới; reply cũ giữ lịch sử nhưng không còn được gửi.

POST `/complaints/{id}/fulfillment` `{expected_case_version,note,reference?}` → CaseDetail; chỉ latest approve có sent reply còn hiện hành, ghi nhận completed bên ngoài và resolved. reference text tối đa 200, không tự fetch URL.

POST `/complaints/{id}/close` `{expected_case_version,note}` → CaseDetail; chỉ resolved, latest decision đã gửi, không unknown/busy/stale context. POST `/complaints/{id}/reopen` cùng input → needs_review, audit. Inbound mới cũng tự mở lại theo WORKFLOW.

## Replies: chuẩn bị → sửa → xác nhận → draft/send

1. POST `/complaints/{id}/replies/prepare` `{expected_case_version,decision_id,mode:"ai"}` hoặc mode manual → Reply envelope. Một reply/decision; nếu đã có trả row hiện có. AI lỗi không tạo nội dung giả; nhân viên có thể prepare manual với template rỗng an toàn, subject cố định rồi nhập body. Content generation không gửi mail.
2. PATCH `/complaints/{id}/replies/{reply_id}` `{expected_reply_revision,body}` → envelope; body 1..10000, chỉ prepared/draft_saved/failed và không stale. Tăng revision. Subject/recipient readonly, derived server từ original correspondent và latest inbound; không Cc/Bcc/custom headers. Sửa sau draft_saved lưu local trước, Gmail draft đồng bộ lại khi save/send.
3. POST `.../{reply_id}/review-context` `{expected_case_version,expected_reply_revision,note}` → envelope; nhân viên đã xem context mới và nội dung. Chỉ cập nhật basis/latest inbound cho reply chưa gửi cùng current decision, revision+1. Decision đổi thì prepare reply mới.
4. POST `.../{reply_id}/draft` và POST `.../{reply_id}/send` body:
```json
{"expected_case_version":5,"expected_reply_revision":2,"idempotency_key":"UUID","confirmed":true}
```
Draft không cần confirmed; send bắt buộc true, UI xác nhận trên nội dung đã lưu đúng revision. Cả hai kiểm tra version/current decision/latest inbound, không stale; send approve cần ownership đã xác minh. 200 envelope sau hoàn tất; 409 khi busy/stale/unknown. Cùng key và payload trả kết quả đã lưu, không gọi Gmail lại; key khác nhưng reply sent cũng trả trạng thái sent. Key dùng khác operation/payload → 409 idempotency_conflict.
5. GET `/complaints/{id}/replies/{reply_id}` → envelope cho reload/poll trạng thái. UI poll mỗi 3s khi pending, dừng sau 60s và cho người dùng refresh, không tự gửi lại.

Send dùng Gmail messages.send từ MIME local cuối nếu chưa có draft; nếu đã có draft, kiểm tra nội dung Gmail hiện tại rồi cập nhật bằng bản local đã xác nhận trước drafts.send. So hash remote với gmail_draft_content_hash của lần đồng bộ trước (không so local đã sửa), theo DATABASE_DESIGN. Remote khác → 409 external_draft_changed, GET reply bổ sung `external_content:{subject,body,content_hash}?` sau fetch, không tự ghi đè. Nhân viên chọn giữ local qua review-context `{...,accept_local_over_external:true,expected_external_hash:"SHA256"}`; server đọc lại/so hash, lưu accepted_external_hash và audit, revision+1. Lần save/send chỉ được ghi đè remote đúng hash đã chấp thuận; remote đổi tiếp → conflict lại. Nếu draft bị xóa/đã gửi ngoài app → unknown, đối soát, không tạo/gửi bản mới mù. Gmail không cung cấp transaction với DB; kiểm tra này giảm rủi ro, không bảo đảm khóa sửa Gmail bên ngoài trong khoảng check/send.

Gmail trả message ID → sent (không đồng nghĩa đã đọc/giao chắc chắn). Lưu outbound case_message cùng Gmail ID, không nhân đôi lúc sync. Không đổi workflow nếu có inbound/context mới trong lúc network; giữ needs_review và audit concurrent_inbound.

## Evidence

- GET `/complaints/{id}/evidence` → `{assets:[{id,source,evidence_kind,message_id?,content_type,size_bytes,content_url}],analysis:EvidenceAnalysis|null}`; content_url `/api/evidence/{id}/content`, có auth, private/no-store.
- POST `/complaints/{id}/evidence/analyze` `{expected_case_version}` → `{analysis,case_version}`. Một phía vẫn chạy mode single_side; không ảnh 422 evidence_missing; đang pending 409 evidence_busy.
- Analysis: `id,status,mode,consistency?,observations:string[],limitations:string[],missing_evidence:string[],model?,error_code?,created_at,completed_at?`. Single_side consistency phải inconclusive; không tuyên bố đã đối chiếu.
- Tối đa 2 ảnh/phía/request, JPEG/PNG <=5 MB/ảnh; source customer gắn inbound message. Không UI upload trong MVP, ảnh lấy Gmail và seed order.

## Internal và đồng bộ

POST `/internal/gmail/sync`: OIDC signature/issuer/audience=PUBLIC_BASE_URL/email_verified/email allowlist SCHEDULER_SERVICE_ACCOUNT. Không session/CSRF. Manual sync và Scheduler cùng DB advisory lock, busy 409 sync_busy. SyncResult giữ cũ, thêm `messages_added,cases_created,cases_reopened`; successful nghĩa phân tích thành công, không email gửi thành công.

Các mã lỗi còn lại tại [ERROR_HANDLING](ERROR_HANDLING.md). Không hứa exactly-once Gmail; unknown cần reconcile và xác nhận vận hành.

Closed từ chối review/decision/reply mutation với invalid_case_state cho tới reopen. Khi manual review/AI retry/reassess cập nhật projection phải tuân thủ rule không ghi đè sửa tay và context sent trong WORKFLOW. Recipient và headers luôn validate không CR/LF injection; subject cố định theo conversation.

## Storage contract đã khóa

Schema CLAIMPILOT_MVP_DB_V1 trong DATABASE_DESIGN là nguồn cột/type/default/FK. text_analysis_runs/gmail_intake_failures là lưu trữ nội bộ, không bắt thêm CRUD endpoint. Message.analysis vẫn projection raw đã apply; failed/stale attempts giữ ở runs, không overwrite manual values. case_replies.sent_message_id/attempt_token là pointer nội bộ, không xuất browser; gửi thành công cần sent ID/time/outbound trong cùng transaction.

Phân tích ảnh vẫn trả shape ở trên; bucket/key/generation/dimensions là storage metadata nội bộ, proxy content đọc đúng generation đã lưu. Key/model/provider mới thay config/Secrets, không thay wire hoặc SQL. UI chưa triển khai phải cập nhật types cho những field đọc thêm, không dùng field chưa có trong schema khóa.

## Owner API và composition fullstack v3

| Owner | API nghiệp vụ + frontend cùng owner |
|---|---|
| A Workspace | auth/health/integrations/stats/list/detail/messages/audit read/sync/internal; Login/queues/conversation/status |
| B Assessment | review/reassess/analyze/evidence/content; ManualReview/Assessment/Evidence UI, text/image providers |
| C Resolution | decisions/replies prepare-edit-review-draft-send/history/fulfillment/close/reopen; Decision/Composer/Fulfillment UI |

A compose CaseDetail projection bằng read ports B/C đã chốt trong BASE, không import business write của B/C hoặc viết các router đó thay họ. Wire shape/HTTP/enum ở trên giữ nguyên. B/C tự tests UI/API/model bằng CaseContext/Session/Principal doubles trước; release thay bằng real shared runtime. Nội bộ [SHARED_CONTRACTS](SHARED_CONTRACTS.md), không tạo API phân tầng khác hoặc đổi tên field vì chia role mới.

Evidence asset.evidence_kind đọc ra là packing/delivery/customer theo schema freeze; source order chỉ packing/delivery, source customer chỉ customer. Các field này phục vụ gắn nhãn bằng chứng, không là kết luận AI về việc giao hàng.
## Extension v4 — PROPOSED / CR-001
Base /api, mọi business route cần staff; write kiểm CSRF/Origin. Không truyền actor/system flags từ client, unknown field422. page>=1,page_size1..100; q<=200; UUID parse422, timestamp UTC, nullable explicit. Endpoint search không log query/body. Các mutation v4 có response domain chứa revision/version đã lưu; không optimistic success.

| Route / owner | Request | Response / rule |
|---|---|---|
| GET /complaints / A | thêm processing_status?,q? | Envelope cũ; q tìm subject/body/order_id bằng parameterized escaped contains, không email/token search URL của UI; queue/filter canonical kế thừa |
| GET /orders / A | page/page_size/q? | {items:OrderOut[],total,page,page_size}; staff only, read dữ liệu nguồn |
| GET /policies / B | — | {items:[{version,label,rules_summary,source_status}]}; deterministic config đã nạp, không tưởng tượng policy thật |
| GET /settings/business / A | — | Settings; thiếu config503 config_unavailable |
| PATCH /settings/business / A | {expected_revision,display_name?,language?,tone?,note} | Settings; validate limits/enum theo DB; lock current pointer, append immutable version, conflict409 |
| GET /settings/agents / A | — | {revision,settings_version_id,optional_roles,review_threshold,mandatory_roles,guardrails}; guardrails read-only |
| PATCH /settings/agents / A | {expected_revision,optional_roles,review_threshold,note} | Cùng shape GET; optional_roles chỉ evidence_analysis, threshold null hoặc0..1; sửa mandatory/guardrails422 |
| GET /knowledge / B | page/page_size/q?/topic?/status? | {items:KnowledgeRevision[],total,page,page_size}; staff CMS có thể thấy draft, retrieval không dùng route này |
| POST /knowledge / B | {title,body,topic,source_label,source_reference?,valid_until?,review_due_at?} | 201 {article_id,revision:KnowledgeRevision}; draft revision1 |
| GET /knowledge/{article_id} / B | — | {article_id,current_published_revision_id,revisions:KnowledgeRevision[]} |
| GET /knowledge/{article_id}/revisions/{revision_id} / B | — | KnowledgeRevision đúng history, không redirect sang bản mới |
| POST /knowledge/{article_id}/revisions / B | {expected_revision,title,body,topic,source_label,source_reference?,valid_until?,review_due_at?} | 201 draft mới,409 khi article latest revision không khớp |
| PATCH /knowledge/{article_id}/revisions/{revision_id} / B | {expected_updated_at,title?,body?,topic?,source_label?,source_reference?,valid_until?,review_due_at?} | KnowledgeRevision; chỉ draft, row lock/time compare409; không sửa approved body |
| POST .../revisions/{revision_id}/submit / B | {expected_updated_at} | pending_review; không tự publish |
| POST .../revisions/{revision_id}/approve / B | {expected_updated_at,note} | approved + current published pointer; staff actor/time; cùng staff account vẫn là hành động riêng |
| POST .../revisions/{revision_id}/archive / B | {expected_updated_at,note} | archived; giữ citation history, clear pointer nếu đang published |
| POST .../revisions/{revision_id}/conflict / B | {expected_updated_at,has_conflict,note} | flag/review history; bỏ flag phải có staff căn cứ, không sửa content cũ |
| GET /complaints/{id}/agent-runs / A | — | {items:AgentRun[]}; newest run trước; steps có stable role/attempt order |
| POST /complaints/{id}/agent-runs / A | {expected_case_version} | 202 {run:AgentRun,case_version}; reserve persisted trước dispatch, busy409; chỉ analysis/preparation |
| GET /complaints/{id}/sources / B | — | {items:SourceRef[],warnings:string[]}; refs từ run/projection persisted, auth/history sources |
| GET /complaints/{id}/replies/{reply_id}/checks / C | — | {items:ReplyCheck[]}; latest check tính freshness lại, stale khi dependency đổi |
| POST /complaints/{id}/replies/{reply_id}/checks / C | {expected_case_version,expected_revision} | {check:ReplyCheck,case_version}; kiểm cả manual reply; không send |

Dấu ... trong route KB là /knowledge/{article_id}. Chưa có public Help Center, URL crawler, upload tài liệu hoặc DELETE history endpoint.

Settings={revision,settings_version_id,display_name,language,tone,updated_at}. Hai settings PATCH dùng chung revision sequence; ghi mới không đổi body cũ. Khởi tạo lần đầu bằng PATCH business expected_revision=0, bắt buộc display_name/language/tone/note từ staff; atomic tạo version1+singleton, race409. Agents PATCH cần settings đã khởi tạo; không tự tạo brand mặc định. KnowledgeRevision={id,article_id,revision,title,body,topic,source_label,source_reference,status,valid_until,review_due_at,has_conflict,conflict_note,author,approved_by,approved_at,created_at,updated_at}. GET article bổ sung events domain audit đã lọc. Title1..300/body1..50000/topic1..100/source_label1..200; server sanitize text, note1..2000. valid_until phải ở tương lai khi approve; review_due quá hạn không eligible retrieval. Không thể sửa metadata approval qua input.

AgentRun={id,complaint_id,basis_case_version,settings_version_id,status,required_roles,created_at,finished_at,steps:AgentStep[]}. AgentStep={id,role,attempt,status,started_at,finished_at,source_refs,output,confidence,error_code,skip_reason}; không expose raw prompt/input_snapshot. SourceRef schema tại DB, GET thêm eligible:boolean và stale_reason|null, không đổi persisted refs. Confidence có thể null, không tự hiển thị100%.
ReplyCheck={id,reply_id,reply_revision,basis_case_version,settings_version_id,status,source_refs,findings,created_at}; hashes ở server. CaseDetail thêm agent_run|null,source_refs[]; dashboard thêm agent_counts:{running,failed,waiting_data} (đếm steps của latest run mỗi canonical case). Thêm field là TARGET, không frontend đọc trước wiring.

### Extension vào composer/send
Reply envelope thêm sources:SourceRef[],settings_version_id|null,quality_check:ReplyCheck|null,preview_token|null. Prepare AI pin settings và approved sources; manual reply cũng chạy deterministic safety. Không dùng draft KB, nguồn expired/conflict hoặc facts của đơn chưa xác minh để trả lời.
POST /complaints/{id}/replies/{reply_id}/preview body {expected_case_version,expected_revision} → {reply,check,preview_token,case_version}; token là opaque HMAC-signed acknowledgement challenge với server PREVIEW_SIGNING_KEY, pin check/content/dependency/case/reply và hết hạn10 phút; không session token, giữ trong memory, không log/URL. Có thể render draft trước đó nhưng chỉ preview endpoint với passed check phát token.
Send core body thêm preview_token bắt buộc cho writer v4; reserve kiểm case/reply/content/decision/latest inbound và dependency hash, token chưa dùng với intent khác. Replay idempotency key cũ trả kết quả đã persist trước khi kiểm freshness lại; không dispatch lại. Edit/context/source/config đổi →409 source_context_changed hoặc stale_preview (kể cả token hết hạn), chưa đủ safety→409 quality_blocked, provider check lỗi→503 quality_unavailable. Không âm thầm fallback về send v3 thiếu preview; có transition contract test.
Đã sent giữ nguyên nguồn/check history; nguồn bị archive sau đó không đổi sent thành stale hoặc gửi lại.
