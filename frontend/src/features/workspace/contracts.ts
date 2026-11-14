export interface Session { username: string; csrf_token: string; expires_at: string }
export interface Page<T> { items: T[]; total: number; page: number; page_size: number }
export interface Settings { id: string; settings_version_id: string; revision: number; display_name: string; language: string; tone: string; optional_roles: string[]; review_threshold: string | null }
export interface EscalationReason { code: string; severity: string; message: string }
export interface Case { 
  id: number; 
  email_subject: string; 
  email_body: string; 
  sender_email: string; 
  order_id: string|null; 
  complaint_type: string|null; 
  requested_action: string|null; 
  workflow_status: string; 
  processing_status: string; 
  processing_error: string|null; 
  priority: string|null; 
  case_version: number; 
  current_decision_id: string|null; 
  ownership_status: string; 
  ai_summary: string|null; 
  policy_reason: string|null; 
  is_complaint: boolean|null; 
  severity?: 'critical' | 'high' | 'medium' | 'low';
  escalation_reasons?: EscalationReason[];
  taken_over_by?: string | null;
  requires_immediate_takeover?: boolean;
  case_report?: { resolved_by: string; generated_at: string; decision_action: string; decision_resolution: string; severity: string; sources_used: any[]; summary: string } | null;
  policy_snapshot: { missing_fields?: string[]; next_action?: string; severity?: string; escalation_reasons?: EscalationReason[]; taken_over_by?: string | null; case_report?: any }; 
  verified_order: Order|null; 
  messages: Message[]; 
  decisions: Decision[]; 
  replies: Reply[]; 
  audit_events: Audit[]; 
  agent_run: Run|null; 
  fulfillment_status: string; 
  needs_manual_review: boolean; 
  received_at: string;
}
export interface Order { id: number; order_id: string; customer_email: string; order_status: string; product_name: string|null; shipping_fee: string; total_amount: string|null; currency: string; expected_delivery_date: string|null; actual_delivery_date: string|null }
export interface Message { id: string; direction: string; subject: string; body: string; sender_email: string; recipient_email: string|null; occurred_at: string; processing_status: string }
export interface Decision { id: string; action: string; resolution: string; note: string; actor: string; created_at: string; proposed_amount: string|null }
export interface Reply { id: string; decision_id: string; body: string; subject: string; recipient_email: string; status: string; revision: number; is_stale: boolean; error_code: string|null; has_draft?: boolean; gmail_draft_id?: string|null; gmail_draft_content_hash?: string|null; accepted_external_hash?: string|null }
export interface Audit { id: string; event_type: string; actor: string; note: string; created_at: string }
export interface Source { id: string; article_id: string; kind: string; version: string; title?: string; excerpt: string|null; eligible?: boolean }
export interface Check { id: string; status: string; source_refs: Source[]; findings: {code:string;severity:string;message:string}[] }
export interface Envelope { reply: Reply; case_version: number; sources: Source[]; quality_check: Check|null; preview_token: string|null }
export interface Step { id: string; role: string; status: string; source_refs: Source[]; output: {reply_id?:string;reason?: string; missing_fields?: string[];findings?:{message:string}[]} | null; error_code: string|null; skip_reason: string|null; finished_at: string|null }
export interface Run { id: string; status: string; trigger:string; created_at: string; steps: Step[] }
export interface Knowledge { id: string; article_id: string; revision: number; title: string; body: string; topic: string; source_label: string; source_reference: string|null; status: string; has_conflict: boolean; conflict_note: string|null; valid_until: string|null; review_due_at: string|null; updated_at: string }
export interface Stats { total: number; workflow_counts: Record<string,number>; technical_failed: number; agent_counts: Record<string,number>; severity_counts?: Record<string,number>; urgent_count?: number }
export interface Integrations { gmail_configured: boolean; ai_configured: boolean; ai_provider: string; ai_model: string; gmail_write_enabled: boolean; last_attempt_at: string|null; last_success_at: string|null; last_error_code: string|null; deferred_count: number; intake_failed_count: number }
export interface ReportsSummary {
  total_cases: number;
  workflow_counts: Record<string, number>;
  severity_counts: Record<string, number>;
  urgent_count: number;
  escalation_rate: number;
  automation_rate: number;
  taken_over_count: number;
  top_escalation_triggers: { code: string; count: number }[];
}
