"""Risk assessment and severity evaluation for ClaimPilot AI-first customer support."""
import re
from typing import Literal

SeverityLevel = Literal["critical", "high", "medium", "low"]

LEGAL_THREAT_REGEX = re.compile(
    r"(kiện|tòa án|pháp luật|luật sư|công an|quản lý thị trường|bảo vệ người tiêu dùng|tố cáo|bóc phốt|lừa đảo|scam|sue|court|lawyer|police|legal action)",
    re.IGNORECASE
)

HOSTILE_REGEX = re.compile(
    r"(khốn nạn|mất dạy|đồ tồi|đồ lừa đảo|chết tiệt|đồ rác rưởi|fuck|shit|bọn lừa|lũ lừa)",
    re.IGNORECASE
)

PROMPT_INJECTION_REGEX = re.compile(
    r"(ignore (all|previous|above)|system prompt|api[_-]?key|bỏ qua (mọi|tất cả) chỉ dẫn|tiết lộ prompt|jailbreak|pretend you are)",
    re.IGNORECASE
)


def assess_case_risk(complaint, order=None, inbound_messages=None, approved_kb_count: int = 0):
    """
    Evaluates the risk level and returns (severity, escalation_reasons, requires_immediate_takeover).
    
    Levels:
      - 'critical': Stop all automation, immediate alert, staff takeover required
      - 'high': Requires staff manual review, auto-send blocked, draft only
      - 'medium': Needs review, auto-draft created, staff verification recommended
      - 'low': Low risk, eligible for automated response / quick draft
    """
    reasons = []

    subject = str(complaint.email_subject or "")
    body = str(complaint.email_body or "")
    combined_text = f"{subject}\n{body}"

    # 1. CRITICAL checks
    if LEGAL_THREAT_REGEX.search(combined_text):
        reasons.append({
            "code": "legal_or_regulatory_threat",
            "severity": "critical",
            "message": "Khách hàng có dấu hiệu khiếu nại cơ quan chức năng, kiện tụng hoặc tố cáo lừa đảo."
        })

    if HOSTILE_REGEX.search(combined_text):
        reasons.append({
            "code": "hostile_or_toxic_sentiment",
            "severity": "critical",
            "message": "Email chứa ngôn từ xúc phạm hoặc thái độ gay gắt nghiêm trọng."
        })

    if PROMPT_INJECTION_REGEX.search(combined_text):
        reasons.append({
            "code": "prompt_injection_detected",
            "severity": "critical",
            "message": "Phát hiện dấu hiệu thao túng câu lệnh (Prompt Injection / Jailbreak)."
        })

    if complaint.ownership_status == "mismatch" and order is not None:
        reasons.append({
            "code": "ownership_mismatch",
            "severity": "critical",
            "message": "Email người gửi không khớp với thông tin người đặt đơn hàng (Nguy cơ giả mạo)."
        })

    if order and getattr(order, "total_amount", None) is not None and order.total_amount >= 2000000:
        reasons.append({
            "code": "high_value_order",
            "severity": "critical",
            "message": f"Đơn hàng giá trị cao ({int(order.total_amount):,} VND), vượt ngưỡng an toàn tự động."
        })

    if getattr(complaint, "processing_error", None) == "gmail_result_unknown":
        reasons.append({
            "code": "ambiguous_delivery_state",
            "severity": "critical",
            "message": "Trạng thái gửi thư trước đó chưa xác định được trên Gmail, chặn gửi tự động."
        })

    if any(r["severity"] == "critical" for r in reasons):
        return "critical", reasons, True

    # 2. HIGH checks
    inbound_count = len([m for m in (inbound_messages or []) if getattr(m, "direction", "") == "inbound"])
    if inbound_count >= 3:
        reasons.append({
            "code": "multi_round_escalation",
            "severity": "high",
            "message": f"Hồ sơ đã trao đổi qua {inbound_count} lượt thư nhưng chưa được giải quyết dứt điểm."
        })

    if getattr(complaint, "policy_result", None) == "not_eligible":
        reasons.append({
            "code": "policy_exception_required",
            "severity": "high",
            "message": "Không đủ điều kiện theo chính sách chuẩn (cần nhân viên xem xét ngoại lệ)."
        })

    if getattr(complaint, "complaint_type", None) in ("damaged_item", "wrong_item"):
        evidence_snapshot = (complaint.policy_snapshot or {}).get("evidence_snapshot") or {}
        consistency = evidence_snapshot.get("consistency")
        if consistency in ("inconsistent", "inconclusive"):
            reasons.append({
                "code": "evidence_inconclusive_or_mismatch",
                "severity": "high",
                "message": "Ảnh bằng chứng sản phẩm hư hỏng/sai hàng không rõ ràng hoặc có mâu thuẫn."
            })

    if approved_kb_count == 0 and getattr(complaint, "complaint_type", None) not in (None, "other"):
        reasons.append({
            "code": "no_approved_kb_source",
            "severity": "high",
            "message": "Chưa có bài viết chính sách đã duyệt phù hợp trong Knowledge Base."
        })

    if getattr(complaint, "needs_manual_review", False):
        reasons.append({
            "code": "manual_review_flagged",
            "severity": "high",
            "message": "Hồ sơ được hệ thống đánh dấu cần nhân viên xem xét đặc biệt."
        })

    if any(r["severity"] == "high" for r in reasons):
        return "high", reasons, False

    # 3. MEDIUM checks
    if getattr(complaint, "policy_result", None) == "order_not_found" or not getattr(complaint, "order_id", None):
        reasons.append({
            "code": "missing_order_information",
            "severity": "medium",
            "message": "Chưa tìm thấy hoặc thiếu mã đơn hàng hợp lệ."
        })

    if getattr(complaint, "complaint_type", None) in ("not_received", "late_delivery"):
        reasons.append({
            "code": "carrier_investigation_pending",
            "severity": "medium",
            "message": "Cần tra cứu lịch trình hoặc mở yêu cầu đối soát với đơn vị vận chuyển."
        })

    if getattr(complaint, "ownership_status", None) == "unverified":
        reasons.append({
            "code": "ownership_unverified",
            "severity": "medium",
            "message": "Chủ đơn hàng chưa được xác minh qua email hoặc đối chiếu thủ công."
        })

    if any(r["severity"] == "medium" for r in reasons):
        return "medium", reasons, False

    # 4. LOW checks
    return "low", [{
        "code": "safe_standard_inquiry",
        "severity": "low",
        "message": "Yêu cầu tiêu chuẩn, thông tin rõ ràng và an toàn."
    }], False
