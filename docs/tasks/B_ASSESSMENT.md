# B — fullstack Assessment, Knowledge Base và Evidence v4

Nguồn [requirements](../AI_CUSTOMER_SUPPORT_REQUIREMENTS.md), [TASK](../TASK.md), [contracts](../SHARED_CONTRACTS.md). Đọc AGENTS/CONTEXT/WORKFLOW/DATABASE/API/UI/security/testing trước code. Lần này đồng bộ docs, chưa code tính năng.

## Bốn task
- FS-B1: Lookup đơn, ownership/manual correction có căn cứ/audit/version, reset decision khi dữ liệu trọng yếu đổi; Assessment/ManualReview và sources UI/API.
- FS-B2: Text/policy agents và5 nhóm policy; Knowledge Base fullstack list/search/editor/revisions/submit/approve/publish/archive. Retrieval chỉ eligible approved KB, citation đúng version/digest/excerpt và no-match/manual path.
- FS-B3: MIME image decode/private GCS/Gemini evidence agent một/hai phía, source metadata/current case+order, EvidencePanel/content auth; upload immutable generation và giới hạn byte/pixel.
- FS-B4: Failed/stale/raw attempt history, manual protection, conflict/expiry/source freshness, KB version tests, representative synthetic dataset/rubric cho pilot. Không công bố accuracy khi chưa đo.

## Ownership và ports
B assessment/knowledge modules và frontend features tương ứng; A owns shell/settings/orchestrator/shared, C owns reply/check/send. Export KnowledgePanel/SourceList/AssessmentPanel/EvidencePanel, KnowledgeService retrieve/resolve và AgentStepPorts. Core patches qua CaseStore, không sửa trực tiếp C tables hoặc commit lồng.
Existing TextAnalysisRun/EvidenceAsset/EvidenceAnalysis mappings giữ nguyên. KB/steps extension theo CR-001 PENDING_REVIEW, không tạo metadata/migration riêng. Không dùng text_analysis_runs.output để lưu output6roles ngoài Analysis schema. B đề xuất delta/env/deps cho A aggregate sau review.

## Bắt đầu và nghiệm thu
Dùng exact DTO doubles cho A services chưa có trong test/dev, không chờ A làm toàn backend. Kiểm sources từ server, model không tự đặt citation IDs. Không fetch URL tài liệu/email, publish từ AI hoặc public ảnh. Mọi input/body render text.
[26 tests B](../test-cases/B_TEST_CASES.md); MERGE/RELEASE và provider/Storage live evidence khác fixtures. Deliver ports/files/env/deps/test variants/blockers/reviewer; không tự spawn/commit/push/reset, không báo PASS từ thiếu key hoặc CR chưa duyệt.
