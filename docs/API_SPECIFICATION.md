# API specification — TARGET v3, nguồn duy nhất về wire contract

Base `/api`, JSON UTF-8, UTC ISO8601; case ID int (complaint cũ), ID bảng mới UUID string; tiền decimal string. Enum nghiệp vụ tại [WORKFLOW](WORKFLOW.md). Toàn bộ endpoint mới là TARGET chưa code. Giữ đường dẫn API hiện có; không phải giữ các giới hạn một email/một quyết định của docs v1.

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

**Decision**: `id,complaint_id,action,resolution,note,missing_fields:string[],actor,basis_case_version,assessment_snapshot,created_at`.

**Reply**: `id,complaint_id,decision_id,in_reply_to_message_id,recipient_email,subject,body,status,basis_case_version,revision,is_stale,gmail_draft_id?,gmail_sent_message_id?,error_code?,sent_at?,updated_at`. Không trả attempt token/internal RFC ID. Reply response envelope `{reply:Reply,case_version:int}`.

**AuditEvent**: `id,event_type,actor,note,before_data,after_data,created_at` đã lọc dữ liệu nhạy cảm. OrderOut thêm purchased_at/product_name/total_amount nullable.

## Case list và dashboard

- GET `/complaints` thêm `workflow_status?,queue?`; queue=work (mặc định, is_complaint=true) hoặc technical (is_complaint NULL/true và processing failed/pending, không chứa false). workflow filter chỉ lọc nghiệp vụ, không giấu lỗi phân tích đã xác nhận complaint.
- GET `/dashboard/stats` thêm `workflow_counts:{needs_review,waiting_customer,waiting_fulfillment,resolved,closed},technical_failed:int`. Legacy counters là projection theo DATABASE_DESIGN; UI mới dùng workflow_counts.
- GET `/integrations/status` thêm `last_attempt_at?,last_success_at?,last_error_code?,deferred_count`. Presence credentials không chứng minh connectivity.
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

- GET `/complaints/{id}/evidence` → `{assets:[{id,source,message_id?,content_type,size_bytes,content_url}],analysis:EvidenceAnalysis|null}`; content_url `/api/evidence/{id}/content`, có auth, private/no-store.
- POST `/complaints/{id}/evidence/analyze` `{expected_case_version}` → `{analysis,case_version}`. Một phía vẫn chạy mode single_side; không ảnh 422 evidence_missing; đang pending 409 evidence_busy.
- Analysis: `id,status,mode,consistency?,observations:string[],limitations:string[],missing_evidence:string[],model?,error_code?,created_at,completed_at?`. Single_side consistency phải inconclusive; không tuyên bố đã đối chiếu.
- Tối đa 2 ảnh/phía/request, JPEG/PNG <=5 MB/ảnh; source customer gắn inbound message. Không UI upload trong MVP, ảnh lấy Gmail và seed order.

## Internal và đồng bộ

POST `/internal/gmail/sync`: OIDC signature/issuer/audience=PUBLIC_BASE_URL/email_verified/email allowlist SCHEDULER_SERVICE_ACCOUNT. Không session/CSRF. Manual sync và Scheduler cùng DB advisory lock, busy 409 sync_busy. SyncResult giữ cũ, thêm `messages_added,cases_created,cases_reopened`; successful nghĩa phân tích thành công, không email gửi thành công.

Các mã lỗi còn lại tại [ERROR_HANDLING](ERROR_HANDLING.md). Không hứa exactly-once Gmail; unknown cần reconcile và xác nhận vận hành.

Closed từ chối review/decision/reply mutation với invalid_case_state cho tới reopen. Khi manual review/AI retry/reassess cập nhật projection phải tuân thủ rule không ghi đè sửa tay và context sent trong WORKFLOW. Recipient và headers luôn validate không CR/LF injection; subject cố định theo conversation.

## Owner API và composition fullstack v3

| Owner | API nghiệp vụ + frontend cùng owner |
|---|---|
| A Workspace | auth/health/integrations/stats/list/detail/messages/audit read/sync/internal; Login/queues/conversation/status |
| B Assessment | review/reassess/analyze/evidence/content; ManualReview/Assessment/Evidence UI, text/image providers |
| C Resolution | decisions/replies prepare-edit-review-draft-send/history/fulfillment/close/reopen; Decision/Composer/Fulfillment UI |

A compose CaseDetail projection bằng read ports B/C đã chốt trong BASE, không import business write của B/C hoặc viết các router đó thay họ. Wire shape/HTTP/enum ở trên giữ nguyên. B/C tự tests UI/API/model bằng CaseContext/Session/Principal doubles trước; release thay bằng real shared runtime. Nội bộ [SHARED_CONTRACTS](SHARED_CONTRACTS.md), không tạo API phân tầng khác hoặc đổi tên field vì chia role mới.
