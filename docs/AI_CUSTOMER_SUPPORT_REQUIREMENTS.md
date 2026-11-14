# Đặc tả yêu cầu: ClaimPilot AI-first Customer Support

**Trạng thái:** Đề xuất, chờ review sản phẩm  
**Ngày:** 2026-11-14  
**Nguồn đầu vào:** yêu cầu người dùng và [Chatwoot](https://www.chatwoot.com/) làm tham khảo về cách tổ chức inbox, hội thoại và Help Center; không sao chép giao diện, nội dung hay thương hiệu.  
**Quan hệ với đặc tả hiện hành:** tài liệu mới, không thay thế [FEATURE_SPECIFICATION](./FEATURE_SPECIFICATION.md), [WORKFLOW](./WORKFLOW.md), [API_SPECIFICATION](./API_SPECIFICATION.md) hoặc schema đóng băng trong [DATABASE_DESIGN](./DATABASE_DESIGN.md).

## 1. Mục tiêu và phạm vi

ClaimPilot cung cấp một workspace hỗ trợ khách hàng, trong đó các AI agent đảm nhiệm phần lớn công việc thường lệ: tiếp nhận, phân loại, tra cứu dữ liệu, kiểm tra chính sách, tổng hợp bằng chứng và soạn phản hồi. Nhân viên không phải tự đọc và điều phối từng bước; họ tập trung vào ngoại lệ, quyết định nghiệp vụ và xác nhận nội dung trước khi gửi.

Đặc tả này giữ phạm vi MVP hiện hành của ClaimPilot: một doanh nghiệp, một hộp thư Gmail, xử lý hồ sơ/khiếu nại liên quan đơn hàng, một tài khoản nhân viên và một ứng dụng cùng origin. Bố cục Chatwoot chỉ là tham khảo cho workspace hội thoại. Các kênh live chat, WhatsApp, mạng xã hội, voice, nhiều doanh nghiệp và tự động gửi email không thuộc phạm vi được phê duyệt ở đây.

**Ranh giới tự động hóa:** “AI-first” nghĩa là các agent là người xử lý chính cho phân tích và chuẩn bị phản hồi. Không có nghĩa là AI tự phê duyệt hoàn tiền/thay thế hàng, tự thực hiện fulfillment, hoặc tự gửi email. Theo chính sách hiện hành, nhân viên phải duyệt quyết định và xác nhận gửi.

## 2. Người dùng và thuật ngữ

- **Nhân viên:** tài khoản doanh nghiệp sử dụng workspace, xem kết quả, sửa dữ liệu, duyệt quyết định và xác nhận gửi.
- **AI agent:** năng lực phần mềm có một vai trò, phạm vi dữ liệu và đầu ra xác định; không phải tài khoản người dùng và không được giả danh nhân viên.
- **Điều phối agent:** xếp các vai trò AI theo thứ tự phụ thuộc, theo dõi trạng thái và chuyển hồ sơ cần xem xét sang hàng đợi phù hợp.
- **Hồ sơ:** một chuỗi trao đổi/email và ngữ cảnh xử lý khiếu nại hiện hữu của ClaimPilot.
- **Knowledge Base (KB):** nội dung doanh nghiệp đã duyệt, có nguồn gốc và phiên bản, dùng để hỗ trợ trả lời.
- **Dữ liệu doanh nghiệp:** hồ sơ đơn hàng, chính sách, hướng dẫn, cấu hình thương hiệu và trạng thái tích hợp được phép sử dụng.

## 3. Cơ sở và giả định

- Phạm vi được xác nhận là **mở rộng ClaimPilot hiện tại**, không khởi tạo một sản phẩm đa kênh mới.
- Duyệt quyết định và xác nhận gửi bởi nhân viên vẫn bắt buộc.
- Một workspace doanh nghiệp và một Gmail mailbox là mặc định MVP; không tạo multi-tenant.
- Các thay đổi yêu cầu bảng/cột/index/enum mới không tự động được phép. Trước khi triển khai, nhóm phải đối chiếu schema đóng băng và thống nhất change request theo quy tắc hiện hành.
- Mục tiêu số liệu dưới đây là ngưỡng nghiệm thu đề xuất trên bộ kiểm thử đại diện; cần hiệu chỉnh bằng dữ liệu pilot đã được ẩn danh trước khi dùng làm cam kết thương mại.
- Từ “tab” chỉ các mục điều hướng cấp workspace. Trên desktop chúng có thể trình bày thành sidebar hoặc tab bar; không bắt buộc sao chép pixel/layout của Chatwoot.

## 4. Phạm vi chức năng và điều hướng

### 4.1 Điều hướng cấp doanh nghiệp

Workspace phải có vùng nhận diện doanh nghiệp hiện hành và các mục điều hướng rõ ràng:

1. **Tổng quan** — tình trạng hộp thư, số hồ sơ theo trạng thái, agent đang chạy và lỗi cần chú ý.
2. **Hộp thư** — hàng đợi hồ sơ và chi tiết hội thoại.
3. **Knowledge Base** — bài viết, chính sách và nguồn tri thức được duyệt.
4. **Dữ liệu & Tích hợp** — trạng thái Gmail, dữ liệu đơn hàng, nguồn dữ liệu và lần đồng bộ gần nhất.
5. **Cài đặt** — thông tin doanh nghiệp, ngôn ngữ/giọng điệu, cấu hình agent, chính sách an toàn và tùy chọn dữ liệu.

MVP chỉ có một doanh nghiệp nên vùng doanh nghiệp hiển thị doanh nghiệp hiện tại, không giả lập chức năng chuyển đổi giữa nhiều tenant.

### 4.2 Bố cục Hộp thư

Màn hình desktop ưu tiên ba vùng:

- **Danh sách hồ sơ:** hàng đợi, chủ đề, người gửi, mã đơn nếu có, lần cập nhật gần nhất, trạng thái nghiệp vụ và trạng thái phân tích.
- **Hội thoại:** email inbound/outbound theo thứ tự thời gian, tệp đính kèm và các phản hồi đã gửi/nháp.
- **Ngữ cảnh xử lý:** kết quả từng agent, đơn hàng, xác minh chủ đơn, policy, bằng chứng, phương án đề xuất và bước tiếp theo.

Màn hình hồ sơ phải có đường dẫn sâu và không làm mất bộ lọc khi quay lại danh sách. Trên màn hình hẹp, ba vùng chuyển thành luồng một cột với các tab “Hội thoại”, “Đánh giá” và “Lịch sử”; nút hành động không che nội dung đang sửa.

### 4.3 Trạng thái hiển thị riêng biệt

UI phải phân biệt trạng thái công việc với trạng thái xử lý AI. Ví dụ: hồ sơ có thể đang “Cần xử lý” trong khi một agent báo “Thất bại”; lỗi AI không được biểu diễn như quyết định từ chối, còn trạng thái “Đã gửi” không được diễn giải là khách đã đọc.

## 5. Kịch bản người dùng và kiểm thử

### Kịch bản 1 — Tiếp nhận và theo dõi nhiều agent (P1)

**Lý do ưu tiên:** nếu không thể tin cậy việc tiếp nhận, phân loại và hiển thị tiến độ, các tính năng AI khác không tạo được hàng đợi làm việc đáng tin cậy.

**Kiểm thử độc lập:** nạp một email kiểm thử, mở workspace và xác nhận hồ sơ cùng trạng thái từng agent xuất hiện mà không cần chuyển màn hình.

1. **Given** email mới trong Gmail, **When** ClaimPilot đồng bộ, **Then** email được gắn vào hồ sơ đúng một lần và xuất hiện trong hàng đợi.
2. **Given** các agent đang xử lý, **When** nhân viên mở hồ sơ, **Then** UI cho biết vai trò nào đang chạy, hoàn tất, thất bại hoặc chờ dữ liệu.
3. **Given** email bổ sung trong cùng thread, **When** hệ thống tiếp nhận, **Then** hồ sơ hiện hữu được cập nhật và ngữ cảnh cũ không bị xóa.
4. **Given** một lỗi phân tích, **When** nhân viên mở hàng đợi, **Then** lỗi có thể tìm thấy và không bị nhầm là hồ sơ đã giải quyết.

### Kịch bản 2 — Xem hội thoại và quyết định có căn cứ (P1)

**Kiểm thử độc lập:** mở một hồ sơ có email và đơn hàng mẫu; xác nhận hội thoại, nguồn dữ liệu, policy và khác biệt giữa dữ liệu gốc với đề xuất AI.

1. **Given** hồ sơ có nhiều email, **When** nhân viên mở hội thoại, **Then** nội dung hiển thị theo thời gian và phân biệt rõ khách hàng với thư do ClaimPilot gửi.
2. **Given** agent đưa ra kết quả, **When** nhân viên xem ngữ cảnh xử lý, **Then** đề xuất có nguồn dữ liệu và mức độ chắc chắn/thiếu thông tin tương ứng.
3. **Given** nhân viên sửa dữ liệu, **When** thay đổi được lưu, **Then** hệ thống giữ kết quả gốc, ghi nhận nội dung sửa và yêu cầu tính lại quyết định liên quan.

### Kịch bản 3 — Duyệt quyết định và phản hồi (P1)

**Kiểm thử độc lập:** dùng hồ sơ mẫu để tạo đề xuất, sửa nội dung phản hồi, lưu nháp và kiểm tra điều kiện xác nhận gửi.

1. **Given** agent đã phân tích xong, **When** nhân viên xem phương án, **Then** nhân viên có thể chấp thuận, sửa hoặc yêu cầu xử lý thủ công mà không mất lịch sử.
2. **Given** nội dung phản hồi đã tạo, **When** nhân viên chỉnh sửa, **Then** bản cuối được xem trước trước khi gửi và thay đổi của nhân viên được giữ.
3. **Given** chưa có xác nhận gửi của nhân viên, **When** agent hoặc đồng bộ nền tiếp tục chạy, **Then** không có email outbound nào được gửi.
4. **Given** ngữ cảnh hồ sơ thay đổi sau khi soạn, **When** nhân viên định gửi, **Then** UI cảnh báo nội dung cũ và yêu cầu xem lại.

### Kịch bản 4 — Quản lý tri thức doanh nghiệp (P1)

**Kiểm thử độc lập:** tạo hoặc cập nhật một bài viết thử nghiệm, duyệt/publish, rồi kiểm tra agent có trích dẫn đúng phiên bản đã duyệt khi trả lời.

1. **Given** bài viết ở trạng thái nháp, **When** agent tra cứu, **Then** bài viết không được coi là nguồn đã duyệt.
2. **Given** có bài viết đã duyệt phù hợp, **When** agent tạo đề xuất, **Then** nhân viên xem được nguồn bài viết và đoạn thông tin làm căn cứ.
3. **Given** nguồn tri thức hết hạn hoặc mâu thuẫn, **When** agent phát hiện, **Then** hệ thống hiển thị cảnh báo và không trình bày nội dung đó như sự thật đã xác nhận.

### Kịch bản 5 — Quản lý doanh nghiệp, dữ liệu và agent (P2)

**Kiểm thử độc lập:** mở từng mục cài đặt, thay đổi giá trị thử nghiệm hợp lệ, lưu, tải lại và kiểm tra giá trị có hiệu lực.

1. **Given** kết nối Gmail không khả dụng, **When** nhân viên mở Dữ liệu & Tích hợp, **Then** trạng thái lỗi và lần đồng bộ thành công gần nhất được hiển thị rõ.
2. **Given** cấu hình giọng điệu hoặc ngôn ngữ doanh nghiệp được cập nhật, **When** nhân viên tạo phản hồi mới, **Then** đề xuất mới áp dụng cấu hình đó và không sửa ngược phản hồi cũ.
3. **Given** agent không thể hoàn tất vì thiếu dữ liệu hoặc bất đồng, **When** quy trình dừng, **Then** hồ sơ được đưa vào hàng đợi cần xem xét với lý do và dữ liệu còn thiếu.

### Trường hợp biên

- Đồng bộ lặp hoặc email được nhận lại không tạo hồ sơ/message trùng.
- Agent hoàn tất trên phiên bản ngữ cảnh cũ không ghi đè sửa đổi hoặc email mới.
- Một agent lỗi/quá thời gian không ngăn nhân viên xem hồ sơ và tiếp tục quy trình thủ công.
- Kết quả agent bất đồng phải được hiển thị; điều phối không được âm thầm chọn kết quả có rủi ro cao hơn.
- KB không có kết quả, có nhiều kết quả mâu thuẫn hoặc chỉ có bài viết nháp: phản hồi phải nêu thiếu căn cứ và chuyển xử lý phù hợp.
- Email có chỉ dẫn yêu cầu agent bỏ quy tắc, tiết lộ dữ liệu hoặc thực hiện hành động ngoài phạm vi phải được coi là nội dung không đáng tin.
- Nếu Gmail timeout sau khi gửi có thể đã xảy ra, giao diện phải hiển thị trạng thái chưa xác định và không cho gửi lại mù.
- Nếu khách trả lời khi nhân viên đang duyệt/gửi, nội dung cũ phải được đánh dấu cần xem lại; lịch sử không bị xóa.

## 6. Yêu cầu chức năng

### Điều hướng và hộp thư

- **REQ-001:** Workspace MUST hiển thị các mục Tổng quan, Hộp thư, Knowledge Base, Dữ liệu & Tích hợp và Cài đặt trong vùng điều hướng nhất quán; mục hiện hành phải được nhận biết mà không chỉ dựa vào màu sắc.
- **REQ-002:** Hộp thư MUST cung cấp hàng đợi có thể lọc theo trạng thái nghiệp vụ, trạng thái xử lý, loại vấn đề và từ khóa; bộ lọc được giữ khi mở rồi quay lại hồ sơ.
- **REQ-003:** Chi tiết hồ sơ MUST trình bày toàn bộ chuỗi email, trạng thái hồ sơ, thông tin đơn hàng, lịch sử quyết định và hành động tiếp theo trong một ngữ cảnh thống nhất.
- **REQ-004:** Hệ thống MUST phân biệt email inbound, nháp, email đã gửi, lỗi gửi và trạng thái chưa xác định; không mô tả nháp là email đã gửi hoặc email đã gửi là đã được khách đọc.
- **REQ-005:** Hệ thống MUST hỗ trợ bố cục desktop ba vùng và bố cục mobile một cột với chuyển đổi Hội thoại/Đánh giá/Lịch sử; nội dung nhập chưa lưu không được mất khi chuyển vùng.

### Điều phối và vai trò AI

- **REQ-006:** Hệ thống MUST điều phối các vai trò agent chuyên biệt: tiếp nhận/phân loại; tra cứu hồ sơ và đơn hàng; đánh giá policy; phân tích bằng chứng; soạn phản hồi; và kiểm tra an toàn/chất lượng trước khi trình nhân viên.
- **REQ-007:** Mỗi kết quả agent MUST ghi rõ vai trò, trạng thái, thời điểm, nguồn dữ liệu được dùng, đầu ra và lỗi hoặc dữ liệu còn thiếu; UI MUST phân biệt nội dung do AI đề xuất với dữ liệu gốc và nội dung nhân viên sửa.
- **REQ-008:** Agent MUST chỉ nhận các trường dữ liệu cần cho nhiệm vụ của mình; kết quả không đủ căn cứ, quá hạn hoặc dựa trên phiên bản cũ MUST bị đánh dấu cần đánh giá lại.
- **REQ-009:** Agent MUST không được thực hiện hành động của vai trò khác bằng cách giả danh nhân viên; điều phối MUST lưu trạng thái từng bước và không được báo hoàn tất khi bước bắt buộc thất bại.
- **REQ-010:** Khi agent lỗi, bất đồng, thiếu nguồn hoặc không đạt ngưỡng an toàn, hệ thống MUST dừng hành động có ảnh hưởng tới khách, nêu lý do và chuyển hồ sơ tới hàng đợi cần xem xét.
- **REQ-011:** Nhân viên MUST có thể yêu cầu chạy lại phân tích hoặc tiếp tục thủ công; kết quả cũ và dữ liệu sửa tay vẫn phải được giữ để đối chiếu.

### Knowledge Base

- **REQ-012:** Nhân viên MUST có thể tạo, xem, sửa, tìm kiếm, publish và lưu trữ bài viết tri thức với tiêu đề, nội dung, chủ đề, nguồn, trạng thái duyệt và ngày cập nhật.
- **REQ-013:** Hệ thống MUST phân biệt tối thiểu trạng thái nháp, chờ duyệt, đã duyệt và lưu trữ; chỉ nội dung đã duyệt, còn hiệu lực mới được dùng làm căn cứ trả lời khách.
- **REQ-014:** Đề xuất của agent dựa trên KB MUST cho phép nhân viên mở tới bài viết/phiên bản nguồn; nếu không tìm được nguồn phù hợp, phản hồi phải nói rõ thiếu căn cứ thay vì bịa nội dung.
- **REQ-015:** Nhân viên MUST có thể tìm và lọc KB theo từ khóa, chủ đề và trạng thái; bài viết mâu thuẫn hoặc đến hạn rà soát MUST được đánh dấu để xử lý.

### Dữ liệu, cài đặt doanh nghiệp và tích hợp

- **REQ-016:** Mục Dữ liệu & Tích hợp MUST hiển thị trạng thái kết nối Gmail, lần thử gần nhất, lần đồng bộ thành công gần nhất và lỗi/deferred hiện tại.
- **REQ-017:** Workspace MUST cho phép nhân viên xem dữ liệu doanh nghiệp mà agent dựa vào, gồm hồ sơ đơn hàng, chính sách đang áp dụng và nguồn tri thức liên quan; trạng thái thiếu hoặc không nhất quán phải được chỉ rõ.
- **REQ-018:** Cài đặt MUST cho phép cập nhật thông tin doanh nghiệp cần cho phản hồi như tên hiển thị, ngôn ngữ và giọng điệu; thay đổi chỉ áp dụng cho nội dung mới và có xác nhận lưu thành công.
- **REQ-019:** Cài đặt agent MUST cho phép bật/tắt từng vai trò không thiết yếu và đặt ngưỡng chuyển xem xét; các rào chắn gửi thư, quyền truy cập và hành động cấm không được tắt từ cài đặt thông thường.
- **REQ-020:** Mọi thiết lập dữ liệu hoặc agent không hợp lệ MUST bị từ chối với thông báo dễ hiểu; giao diện không được báo đã lưu nếu thay đổi không được xác nhận.

### Quyết định, phản hồi và an toàn

- **REQ-021:** AI MUST chỉ đề xuất quyết định và phương án; quyết định nghiệp vụ cuối cùng phải do nhân viên xác nhận theo workflow hiện hành.
- **REQ-022:** Mọi email outbound MUST yêu cầu nhân viên xem phiên bản cuối và xác nhận gửi tường minh; agent, đồng bộ Gmail và tác vụ nền MUST NOT tự gửi.
- **REQ-023:** Nhân viên MUST có thể sửa phản hồi do AI soạn, lưu nháp và xem người nhận/nội dung trước gửi; thay đổi ngữ cảnh hoặc nội dung sau lần xem trước phải làm mất hiệu lực xác nhận cũ.
- **REQ-024:** Hệ thống MUST ngăn gửi trùng do nhấp lặp hoặc retry tự động; trạng thái gửi chưa xác định phải được đối soát, không được tự gửi lại.
- **REQ-025:** AI MUST NOT gọi API thanh toán/hoàn tiền, tự xác nhận đã hoàn tiền/đổi hàng, tự đóng hồ sơ hoặc biến một đề xuất thành fulfillment đã thực hiện.
- **REQ-026:** Nội dung email, tệp đính kèm và tài liệu chưa duyệt MUST được coi là dữ liệu không đáng tin; chúng không thể thay đổi chỉ dẫn an toàn, quyền hạn hoặc cấu hình hệ thống.
- **REQ-027:** Lịch sử hồ sơ MUST cho phép phân biệt hành động của nhân viên, agent và tác vụ hệ thống; thông tin nhạy cảm không được hiển thị trong log chẩn đoán hoặc nội dung frontend không liên quan.

### NFR — khả dụng, khả năng tiếp cận và quyền riêng tư

- **REQ-028:** Workspace MUST dùng chung một URL ứng dụng cùng origin như đích triển khai hiện hành; lỗi của một panel hoặc agent không được làm mất khả năng đọc lịch sử hồ sơ.
- **REQ-029:** Các hành động lưu, quyết định và gửi MUST phản hồi bằng trạng thái đang xử lý/thành công/thất bại rõ ràng; lỗi phải giữ lại nội dung người dùng đã nhập khi an toàn.
- **REQ-030:** Mọi thao tác chính MUST dùng được bằng bàn phím, có nhãn cho trường nhập, thông báo trạng thái không chỉ dựa vào màu và bố cục không tràn ở chiều rộng 390 px.
- **REQ-031:** Chỉ nhân viên đã đăng nhập mới được xem dữ liệu khách hàng, KB nội bộ và kết quả agent; nội dung khách hàng, token và bí mật MUST NOT xuất hiện trong URL, log frontend hoặc thông báo lỗi công khai.
- **REQ-032:** Hệ thống MUST chỉ hiển thị dữ liệu đã tồn tại hoặc được cấu hình; trường không biết phải được biểu diễn là chưa biết/thiếu, không tự suy diễn thành giá trị mặc định có vẻ hợp lệ.

## 7. Thực thể nghiệp vụ chính

- **Doanh nghiệp:** tên hiển thị, ngôn ngữ, giọng điệu và các thiết lập workspace. Trong MVP chỉ có một doanh nghiệp.
- **Hồ sơ/hội thoại:** email, người gửi, đơn hàng liên quan, trạng thái nghiệp vụ, trạng thái xử lý và lịch sử hành động.
- **Lượt chạy agent:** vai trò, trạng thái, thời điểm, căn cứ được phép hiển thị, đầu ra, lỗi và phiên bản ngữ cảnh liên quan.
- **Bài viết tri thức:** nội dung, chủ đề, nguồn gốc, trạng thái duyệt, hiệu lực và lịch sử cập nhật.
- **Nguồn dữ liệu/tích hợp:** loại nguồn, trạng thái kết nối, thời điểm đồng bộ và lỗi đã làm sạch thông tin nhạy cảm.
- **Quyết định và phản hồi:** quyết định được nhân viên duyệt, nội dung phản hồi, phiên bản đã xem, trạng thái nháp/gửi và người thực hiện.

Việc bổ sung khả năng lưu trữ thực thể mới phải được đối chiếu với schema đã đóng băng và quy trình change-control trước khi lập kế hoạch triển khai.

## 8. Tiêu chí thành công đề xuất

- **SC-001:** Trong bộ kiểm thử đại diện, ít nhất 95% email hợp lệ được gắn vào đúng hồ sơ/thread một lần; email lỗi vẫn có trạng thái truy vết được.
- **SC-002:** Ít nhất 90% ca kiểm thử chuẩn có trạng thái agent và bước tiếp theo hiển thị chính xác sau khi xử lý hoặc thất bại.
- **SC-003:** 100% nội dung outbound trong kiểm thử đều có xác nhận tường minh của nhân viên cho đúng phiên bản nội dung; không có lượt chạy AI/đồng bộ nền nào tự gửi.
- **SC-004:** Ít nhất 95% câu trả lời AI được chấm trên bộ đánh giá có căn cứ từ nguồn dữ liệu/KB được phép hoặc được đánh dấu rõ là cần người xem xét.
- **SC-005:** Nhân viên kiểm thử hoàn thành việc tìm hồ sơ, xem nguồn căn cứ và tạo phản hồi đã duyệt mà không phải rời workspace trong ít nhất 90% lượt thử.
- **SC-006:** Thời gian trung vị để nhân viên hoàn thành một hồ sơ chuẩn giảm ít nhất 30% so với baseline xử lý thủ công được đo trước pilot, không tính thời gian chờ khách hoặc nhà vận chuyển.
- **SC-007:** 100% trường hợp agent lỗi, nguồn tri thức mâu thuẫn, context stale hoặc Gmail chưa xác định được kết quả được hiển thị như ngoại lệ, không bị báo thành hoàn tất thành công.

## 9. Ngoài phạm vi

- Tự gửi email hoặc tự quyết định hoàn tiền/thay thế/ngoại lệ chính sách.
- API thanh toán, refund, kho vận hoặc thực hiện fulfillment.
- Live chat, WhatsApp, Facebook/Instagram, voice, SMS và omnichannel.
- Nhiều doanh nghiệp/tenant, nhiều mailbox, RBAC nhiều cấp hoặc onboarding OAuth self-service.
- Nhân viên ảo tự hành động không có audit hoặc tự thay đổi policy/guardrail.
- Tự động crawl URL tùy ý hoặc coi email/tệp đính kèm là nguồn chính sách đáng tin.
- Sao chép thương hiệu, văn bản, tài sản thiết kế hoặc mã nguồn của Chatwoot.
- Thay đổi schema, migration, API wire contract hay phân công FS-A/B/C khi chưa qua review và change-control hiện hành.

## 10. Cổng trước khi lập kế hoạch triển khai

Đây là đề xuất yêu cầu, không phải cho phép bắt đầu các FS task hoặc mở rộng schema. Trước khi tạo plan/task, reviewer cần xác nhận:

1. Tác vụ nào của các agent được phép chạy tự động và ngưỡng nào bắt buộc chuyển xem xét.
2. Danh mục nội dung được phép đưa vào KB và chủ sở hữu/quy trình duyệt nội dung.
3. Những mục điều hướng và cài đặt nào có thể triển khai trên schema, API và file owner hiện hành; phần nào cần change request.
4. Bộ dữ liệu pilot an toàn để đo SC-001–SC-007, với mọi email/đơn hàng dùng dữ liệu được phép.

