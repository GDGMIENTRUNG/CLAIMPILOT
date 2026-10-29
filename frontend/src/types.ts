export interface Complaint {
  id: number;
  gmail_message_id: string;
  sender_email: string;
  email_subject: string;
  received_at: string;
  complaint_type: string | null;
  order_id: string | null;
  requested_action: string | null;
  priority: string | null;
  policy_result: string | null;
  case_status: string;
  processing_error: string | null;
}
export interface Order {
  order_id: string;
  customer_email: string;
  order_status: string;
  expected_delivery_date: string | null;
  actual_delivery_date: string | null;
  shipping_fee: string;
}
export interface Detail extends Complaint {
  email_body: string;
  ai_summary: string | null;
  missing_information: string[];
  verification_status: string;
  sender_matches_order: boolean | null;
  verified_order: Order | null;
  policy_reason: string | null;
}
export interface Stats {
  total: number;
  pending_review: number;
  insufficient_information: number;
  processed: number;
}
export interface Page {
  items: Complaint[];
  total: number;
  page: number;
  page_size: number;
}
export interface Integrations {
  gmail_configured: boolean;
  gemini_configured: boolean;
  ai_provider?: "groq" | "gemini";
  ai_model?: string;
  ai_configured?: boolean;
  note: string;
}
export interface SyncResult {
  successful: number;
  skipped: number;
  failed: number;
  deferred: number;
  errors: { message_id: string; error: string }[];
}
