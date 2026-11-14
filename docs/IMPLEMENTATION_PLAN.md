# Implementation plan — AI-first v4

Đích [PRD](PRD.md), nguồn [requirements](AI_CUSTOMER_SUPPORT_REQUIREMENTS.md). Kế hoạch này thay timeline bốn giờ v3: yêu cầu mới có KB/settings/orchestration và schema review nên chưa cam kết hoàn tất trong khung thời gian cũ.

## Gate0 — Review trước code extension
A/B/C đối chiếu REQ-001–032, chốt CR-001 (schema+wire), vai trò/nguồn dữ liệu/escalation, người duyệt KB và bộ pilot synthetic hoặc đã được phép/ẩn danh. Một staff account MVP có thể submit và approve nhưng hai hành động phải tách, audit identity thực; không giả người duyệt độc lập. Các quyết định mặc định trong docs là đề xuất, reviewer xác nhận trước triển khai.

## Gate1 — BASE và phần độc lập
Giữ DB0005, legacy data và image hiện có. A chuẩn bị DTO/Principal/CaseStore/UoW, registry/feature slots, shell5 mục và auth. B/C làm domain UI/API và test harness từ cùng baseline bằng doubles test/dev. A tổng hợp extension chain chỉ sau gate0; thử fresh+old-data+rerun/drift, giữ mọi ID/body/audit cũ, không tạo KB approved/run/check giả từ legacy.

## Gate2 — Ba phần fullstack
| Đợt ghép | A | B | C |
|---|---|---|---|
| 1 | Auth/intake/queues/data + contracts | Lookup/policy/manual | Decisions/manual composer/lifecycle |
| 2 sau CR | Settings persistence/orchestrator/progress | KB revisions/review/search/retrieval/evidence steps | Reply writer/sources/safety checks |
| 3 | Nối real ports/Cloud/SQL/secrets/Scheduler | Probe text/image/private storage, source staleness | Controlled Gmail send/draft/reconcile |

Không chờ A xong toàn nghiệp vụ mới code B/C; contract và test doubles giúp bắt đầu độc lập. Không dùng doubles cho production.

## Gate3 — Release/pilot
Chạy96 test đặc tả và regression phù hợp; AC01–18 trên revision tích hợp; Cloud thật sau billing/IAM/OAuth/quota checks. SC-001–007 có dataset ID/cỡ mẫu/rubric và manual baseline; thiếu pilot ghi NOT_RUN. Có UI v4 chưa đủ release khi KB/runtime/check còn fake. Rollout pause Scheduler/mutations → backup → migration Job → grant runtime → deploy compatible image → smoke → resume; rollback compatible revision, không drop/downgrade DB.
