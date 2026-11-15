# Security — AI-first v4

Nguồn REQ-008/019/021–027/031 tại [requirements](AI_CUSTOMER_SUPPORT_REQUIREMENTS.md). Quy tắc core dưới đây tiếp tục bắt buộc; bổ sung v4 không cấp agent quyền staff hoặc coding subagents.

Phân công hiện hành v3: A fullstack workspace/auth/platform và shared credentials; B fullstack assessment/private GCS/Gemini; C fullstack resolution/Gmail write. Mọi router domain dùng auth/CSRF thật khi release, không harness Principal giả trên Cloud Run. Quy tắc bảo mật nghiệp vụ bên dưới được giữ.

## Human-in-the-Loop và live tests

- Có API send nhưng chỉ gọi sau staff login, CSRF, version/revision checks và confirmed=true từ preview người dùng. Không send trong AI prepare/sync/Scheduler hoặc chỉ vì approve.
- Không payment/refund API. Văn bản không được khẳng định đã hoàn tiền/đổi hàng trước khi fulfillment được ghi nhận thật.
- Coding agent chỉ gửi live test tới địa chỉ nhóm kiểm soát khi task đã giao rõ; không dùng inbox khách thật để thử.

## Auth

Một staff username/password hash từ Secrets, dùng thư viện hash chuẩn (Argon2id), không plaintext/hardcode. Session token >=32 byte random, hash SHA256 trong DB, TTL 8h, logout revoke; CSRF theo API_SPECIFICATION. Cookie HttpOnly/Secure cloud/SameSite=Lax; Origin kiểm tra login và mutation. Không localStorage session.

Ngoại lệ demo local do người dùng yêu cầu: `LOCAL_DEMO_LOGIN=true` chấp nhận username/password bất kỳ không rỗng khi URL cấu hình và request đều là HTTP loopback trực tiếp. `GET /api/auth/config` trả `demo_login` để UI hiển thị đúng chế độ. Cloud Run, public URL, client không loopback hoặc forwarded/Cloudflare headers không bật demo. Flag mặc định false; session/CSRF/Origin/logout vẫn áp dụng. Không nhúng mật khẩu staff vào frontend hoặc tự login bằng credentials hardcode.

Login limit 5 failed/15 phút/IP trong single-instance MVP; dùng peer IP đáng tin từ hạ tầng, không tin X-Forwarded-For tùy ý; ghi rõ chưa distributed production limiter. Một staff account chỉ truy vết identity cấu hình, chưa phân biệt nhiều nhân viên.

## Gmail và quyền dữ liệu

Scopes readonly + compose cho read/draft/send; consent lại token cũ. Không xin full mail scope để tiện. OAuth Desktop local cho mailbox demo rồi token secret mount readonly; refresh memory cloud, không ghi mount. Credentials chỉ runtime SA được đọc.

Recipient khóa theo correspondent đã lưu từ From của email gốc, không lấy email AI đoán hoặc cho client đổi; không Cc/Bcc/Reply-To tùy ý. Nếu thread có người gửi khác, gắn manual review, không tự đổi correspondent. Chưa xác minh chỉ cho yêu cầu thông tin an toàn hoặc từ chối không lộ dữ liệu; approve bị chặn. Sender match là tín hiệu, không chứng minh tuyệt đối.

Khi ownership chưa xác minh, prepare AI chỉ nhận nội dung khách đã cung cấp và yêu cầu bổ sung, không nhận email chủ đơn/địa chỉ/thông tin sản phẩm hoặc tiền nội bộ tra được. Server template/manual guidance và preview đều nhắc không tiết lộ dữ liệu đơn cho người chưa xác minh. Reconcile thư gửi ngoài app ghi actor system:reconcile, không giả staff đã click trong ClaimPilot.

## Prompt và ảnh

Email/ảnh là dữ liệu không đáng tin; không tool execution/URL fetch, không đưa secrets vào prompt. Structured output và validation bắt buộc; original AI/manual override tách biệt. Preview nhân viên là điểm kiểm tra cuối nội dung gửi.

Storage private, uniform access và public access prevention. API auth proxy content private/no-store. Decode JPEG/PNG thật, <=5MB/ảnh, pixel cap 20 megapixel; không SVG/video/archive, filename không làm object path. object_key do server tạo; không URL từ email để tránh SSRF. Ảnh chỉ hỗ trợ, không kết luận gian lận.

## Cloud và audit

Runtime SA least privilege: SQL Client, từng Secret Accessor, bucket object access; secrets ngoài image/frontend/build args. SQL qua connector/Unix socket, không mở mọi IP. Public web route không có nghĩa internal route được public quyền: OIDC verify signature/issuer/audience/email_verified/allowlist, không decode-only.

Audit actor từ session/system job, ghi cùng business transaction; before/after được lọc, không log raw customer PII. Không có API sửa/xóa decisions/audit. Demo dùng dữ liệu giả, logs chỉ IDs/code/duration. Retention và RBAC production để sau, không tuyên bố sẵn sàng vận hành khách thật.

Database theo CLAIMPILOT_MVP_DB_V1: không token/key/password gốc trong SQL; request_snapshot chứa nội dung thư nội bộ nên chỉ staff/role runtime đúng quyền được đọc, không log snapshot. Runtime không DDL hoặc sửa/xóa decisions/audit; migration job quyền riêng. Schema metadata freeze không thay cho kiểm tra quyền thực tế trên Cloud SQL.
## KB, settings và agent trust
Chỉ staff authenticated thấy CMS/settings/progress/sources; mọi mutation Origin+CSRF. KB approved content là nguồn nghiệp vụ, không trusted system instruction/tool permission. Draft/email/file không thể thay prompt/role/guardrails. Agent chỉ nhận whitelisted task fields, không token/PII không cần thiết; raw prompts/output không trả browser hoặc log.
KB source_reference chỉ text reference được validate/display; không auto fetch, crawl hoặc render HTML. Citation ID/revision phải resolve server-side; excerpt escaped và hạn chế ownership theo case/order. KB/case API không public Help Center.
Chỉ evidence_analysis là optional toggle; auth, mandatory roles, safe recipients, ownership, staff decision/confirm send không cấu hình tắt. Numeric threshold không thay human confirmation. Không secret editor/payment trong Settings.
Quality checks pin sources/config/body/case/reply; preview challenge không vào URL/log/localStorage. Send cần revalidate, không dùng token cũ với intent khác. Unknown không retry; manual path không bypass deterministic safety. Runtime quyền DML mới chỉ sau review grants; immutable source/settings/terminal attempts không cho sửa tùy tiện.
