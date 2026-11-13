# B — fullstack Assessment và Evidence

## Prompt copy cho AI

> Đọc AGENTS → CONTEXT → WORKFLOW → SHARED_CONTRACTS → TASK → task này; đọc DATABASE/API/UI_UX/FEATURE/SECURITY/TESTING và B_TEST_CASES. Bạn làm FS-B1..FS-B4, tự làm backend, model/DTO, API, AssessmentPanel/ManualReview/EvidencePanel và tests. Bạn không là người làm toàn frontend. Dùng frozen CaseContext/CaseStore/Principal doubles từ BASE, không chờ A hoàn thiện backend/cloud hoặc C làm quyết định. Triển khai xác minh/sửa dữ liệu, text AI/năm policy, ảnh MIME/GCS/Gemini một-hai phía và snapshot/version/manual protection. Cung cấp ports cho A intake, publish core patches qua UoW chuẩn; không sửa trực tiếp C decisions/replies. Tự probe Gemini/Storage của phần mình, gửi env/deps/schema delta cho A tổng hợp release. Không payment/gửi mail/ảnh public, không fake production. Kiểm MERGE/RELEASE theo ID, báo đúng live/mocked/BLOCKED.

## Việc được giao

- **FS-B1:** order verification/manual correction/ownership reset khi đổi đơn; schemas/router + own data service + AssessmentPanel/ManualReviewForm; original AI và sửa tay phân biệt, note/audit bắt buộc.
- **FS-B2:** Gemini/Groq text explicit provider, classification/extraction, policy demo-v2 đủ năm nhóm và result/missing_fields/next_action UI/API; không đồng nhất vấn đề với mong muốn refund.
- **FS-B3:** EvidenceService.ingest_message(case,message,raw_bytes), decoder/MIME/byte/pixel/dedupe/private GCS metadata, Gemini one/two-side, evidence router/content auth + EvidencePanel. A chỉ cung cấp saved message/raw MIME qua port; bạn tự test raw fixtures không chờ Gmail intake chạy thật.
- **FS-B4:** snapshots/assessment date/manual override/late AI and evidence completion safety, cảnh báo UI và tests domain. Review fixture matrix đủ policy/boundary/missing/unknown/one-side, không task chuẩn bị demo.

## Schema, file và start độc lập

Assessment/evidence module backend và feature frontend thuộc B; evidence tables B khai báo theo frozen DB; field core/order bổ sung gửi manifest BASE để A dựng một lần. B không tự mở migration head hoặc chỉnh main/App/shared config/lock cạnh tranh. Dependencies text/Storage/image decoder + env gửi A, A tích hợp common runtime.

Domain harness: own model metadata/Session test, CaseStore fake đúng version/audit, Principal test, raw email/order/image factories, provider doubles. Thực hiện UI→router→DB phần mình trước; khi ghép đổi CaseStore/Google credentials thật. Không production auth bypass/mock fallback.

Dữ liệu trọng yếu đổi cần invalidate current_decision_id qua core patch quyền B, không sửa/xóa C decision row. AI finish chỉ publish khi basis còn hợp lệ, raw analysis vẫn giữ; ảnh không tự phán gian lận, không nguyên cớ tự từ chối.

## DoD

[Tests B](../test-cases/B_TEST_CASES.md) đủ MERGE/RELEASE, năm policy/missing/snapshot/manual và ảnh UI/API đúng. Có Gemini ảnh live/private bucket trong bản Cloud Run tích hợp, không claim fixture là live. Giao UI/model/router/ports/env/deps/tests/evidence + reviewer, không chờ A viết backend cho mình.
