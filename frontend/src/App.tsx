import { useEffect, useState, useRef } from "react";
import {
  Activity,
  ArrowDownLeft,
  ArrowRight,
  CheckCheck,
  ChevronLeft,
  ChevronRight,
  CircleHelp,
  Inbox,
  LayoutDashboard,
  Mail,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  X,
  AlertCircle,
  Clock3,
  CheckCircle2,
  Cable,
} from "lucide-react";
import { api } from "./api";
import type { Detail, Integrations, Page, Stats, SyncResult } from "./types";

const label = (v: string | null) =>
  v
    ? v.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase())
    : "Awaiting analysis";
const date = (v: string) =>
  new Date(v).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
function Badge({ value }: { value: string | null }) {
  return <span className={`badge ${value || ""}`}>{label(value)}</span>;
}
function Field({ name, value }: { name: string; value: string | null }) {
  return (
    <div className="field">
      <dt>{name}</dt>
      <dd>{value || "Not available"}</dd>
    </div>
  );
}

export default function App() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [list, setList] = useState<Page | null>(null);
  const [integrations, setIntegrations] = useState<Integrations | null>(null);
  const [status, setStatus] = useState("");
  const [type, setType] = useState("");
  const [page, setPage] = useState(1);
  const [version, setVersion] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<SyncResult | null>(null);
  const [syncError, setSyncError] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [detail, setDetail] = useState<Detail | null>(null);
  const [detailError, setDetailError] = useState("");
  const [detailLoading, setDetailLoading] = useState(false);
  const [analyzingId, setAnalyzingId] = useState<number | null>(null);
  const [analysisError, setAnalysisError] = useState<{
    id: number;
    message: string;
  } | null>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const opener = useRef<HTMLElement | null>(null);
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    const params = new URLSearchParams({ page: String(page), page_size: "10" });
    if (status) params.set("case_status", status);
    if (type) params.set("complaint_type", type);
    Promise.all([
      api<Stats>("/dashboard/stats"),
      api<Page>(`/complaints?${params}`),
      api<Integrations>("/integrations/status"),
    ])
      .then(([s, l, i]) => {
        if (active) {
          setStats(s);
          setList(l);
          setIntegrations(i);
        }
      })
      .catch((e) => {
        if (active) setError(e.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [page, status, type, version]);
  useEffect(() => {
    if (selectedId === null) return;
    let active = true;
    setDetail(null);
    setDetailError("");
    setDetailLoading(true);
    api<Detail>(`/complaints/${selectedId}`)
      .then((d) => {
        if (active) setDetail(d);
      })
      .catch((e) => {
        if (active) setDetailError(e.message);
      })
      .finally(() => {
        if (active) setDetailLoading(false);
      });
    return () => {
      active = false;
    };
  }, [selectedId, version]);
  useEffect(() => {
    if (selectedId === null) return;
    opener.current = document.activeElement as HTMLElement;
    closeRef.current?.focus();
    const old = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    function keys(event: KeyboardEvent) {
      if (event.key === "Escape") setSelectedId(null);
      if (event.key === "Tab") {
        const dialog = closeRef.current?.closest('[role="dialog"]');
        const buttons = Array.from(
          dialog?.querySelectorAll<HTMLElement>(
            'button:not([disabled]), a[href], select, textarea, [tabindex="0"]',
          ) || [],
        );
        const first = buttons[0];
        const last = buttons[buttons.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last?.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first?.focus();
        }
      }
    }
    document.addEventListener("keydown", keys);
    return () => {
      document.body.style.overflow = old;
      document.removeEventListener("keydown", keys);
      opener.current?.focus();
    };
  }, [selectedId]);
  async function sync() {
    setSyncing(true);
    setSyncError("");
    setSyncResult(null);
    try {
      setSyncResult(await api<SyncResult>("/gmail/sync", "POST"));
    } catch (e) {
      setSyncError((e as Error).message);
    } finally {
      setSyncing(false);
      setVersion((v) => v + 1);
    }
  }
  async function retryAnalysis(id: number) {
    if (analyzingId !== null || syncing) return;
    setAnalyzingId(id);
    setAnalysisError(null);
    try {
      await api<Detail>(`/complaints/${id}/analyze`, "POST");
    } catch (e) {
      setAnalysisError({ id, message: (e as Error).message });
    } finally {
      setAnalyzingId(null);
      setVersion((v) => v + 1);
    }
  }
  const providerConfigured =
    integrations?.ai_configured ?? integrations?.gemini_configured;
  const cards = [
    {
      name: "Total complaints",
      key: "total",
      icon: Inbox,
      hint: "All emails in your workspace",
    },
    {
      name: "Pending review",
      key: "pending_review",
      icon: Clock3,
      hint: "Ready for a human decision",
    },
    {
      name: "Needs information",
      key: "insufficient_information",
      icon: CircleHelp,
      hint: "More details are required",
    },
    {
      name: "Processed",
      key: "processed",
      icon: CheckCheck,
      hint: "Cases marked as completed",
    },
  ] as const;
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="/">
          <span className="brand-icon">
            <ArrowDownLeft size={25} />
          </span>
          ClaimPilot<span className="brand-dot">●</span>
        </a>
        <div className="workspace-label">SUPPORT WORKSPACE</div>
        <a href="#overview" className="nav-item active">
          <LayoutDashboard size={18} /> Overview <span className="nav-dot" />
        </a>
        <a href="#complaints" className="nav-item">
          <Inbox size={18} /> Complaints{" "}
          <span className="nav-count">{stats?.total ?? "—"}</span>
        </a>
        <a href="#connections" className="nav-item">
          <Cable size={18} /> Connections
        </a>
        <div className="sidebar-note">
          <ShieldCheck size={24} />
          <strong>AI assists. You decide.</strong>
          <p>Every policy assessment is a recommendation for staff review.</p>
          <span>30% MVP · Local workspace</span>
        </div>
        <div className="profile">
          <div className="avatar">CS</div>
          <div>
            <strong>Support team</strong>
            <small>Staff workspace</small>
          </div>
          <span className="online-dot" />
        </div>
      </aside>
      <div className="main-wrap">
        <header className="topbar">
          <span>
            Workspace <ChevronRight size={14} /> <strong>Overview</strong>
          </span>
          <span className="local-label">
            <span className="online-dot" /> Local environment
          </span>
        </header>
        <main id="overview">
          <div className="page-heading">
            <div>
              <div className="eyebrow">YOUR SUPPORT COMMAND CENTER</div>
              <h1>A clearer view of every complaint.</h1>
              <p>
                From inbox to insight. Review the facts and take the next step.
              </p>
            </div>
            <button className="primary" onClick={sync} disabled={syncing}>
              <RefreshCw size={17} className={syncing ? "spin" : ""} />
              {syncing ? "Processing emails…" : "Sync Emails"}
            </button>
          </div>
          <section
            id="connections"
            className="connection-bar"
            aria-label="Integration configuration"
          >
            <div>
              <span className="integration-icon">
                <Mail size={20} />
              </span>
              <strong>Gmail intake</strong>
              <span
                className={`connection-state ${integrations?.gmail_configured ? "configured" : ""}`}
              >
                {integrations
                  ? integrations.gmail_configured
                    ? "Token configured"
                    : "Authorization needed"
                  : "Checking configuration"}
              </span>
              <span className="divider" />
              <Sparkles size={16} />
              <span>
                AI provider {providerConfigured ? "configured" : "setup needed"}
              </span>
            </div>
            <small>
              Manual sync · Configuration does not confirm connectivity
            </small>
          </section>
          <div aria-live="polite">
            {syncError && (
              <div className="notice error" role="alert">
                <AlertCircle size={18} />
                <div>
                  <strong>Sync could not finish</strong>
                  <p>
                    {syncError}. Run the authorization command or check your
                    backend configuration.
                  </p>
                </div>
              </div>
            )}
            {syncResult && (
              <div
                className={`notice ${syncResult.failed ? "warning" : "success"}`}
              >
                <CheckCircle2 size={19} />
                <div>
                  <strong>Sync finished</strong>
                  <p>
                    {syncResult.successful} successful · {syncResult.skipped}{" "}
                    skipped · {syncResult.failed} failed
                    {!!syncResult.deferred &&
                      ` · ${syncResult.deferred} deferred (not attempted)`}
                  </p>
                  {syncResult.errors.map((e) => (
                    <p key={e.message_id}>
                      {e.message_id}: {label(e.error)}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </div>
          <section className="stats-grid" aria-label="Complaint overview">
            {cards.map(({ name, key, icon: Icon, hint }) => (
              <div className={`stat-card stat-${key}`} key={key}>
                <div className="stat-top">
                  <span>{name}</span>
                  <Icon size={19} />
                </div>
                <strong>
                  {loading || error ? "—" : (stats?.[key] ?? "—")}
                </strong>
                <small>{hint}</small>
              </div>
            ))}
          </section>
          <section className="complaints-panel" id="complaints">
            <div className="panel-heading">
              <div>
                <h2>
                  Complaint inbox{" "}
                  <span>{error || loading ? "—" : (list?.total ?? 0)}</span>
                </h2>
                <p>
                  Email complaints, with the context you need to review them.
                </p>
              </div>
              <button
                className="text-button"
                onClick={() => setVersion((v) => v + 1)}
                disabled={loading || syncing}
              >
                <RefreshCw size={15} /> Refresh
              </button>
            </div>
            <div className="filter-bar">
              <div className="filter-group">
                <label>
                  Status
                  <select
                    aria-label="Status"
                    value={status}
                    onChange={(e) => {
                      setStatus(e.target.value);
                      setPage(1);
                    }}
                  >
                    <option value="">All statuses</option>
                    {[
                      "pending_review",
                      "insufficient_information",
                      "processing_failed",
                      "processing",
                      "processed",
                    ].map((v) => (
                      <option key={v} value={v}>
                        {label(v)}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Complaint type
                  <select
                    aria-label="Complaint type"
                    value={type}
                    onChange={(e) => {
                      setType(e.target.value);
                      setPage(1);
                    }}
                  >
                    <option value="">All types</option>
                    {[
                      "late_delivery",
                      "not_received",
                      "damaged_item",
                      "wrong_item",
                      "refund_request",
                      "other",
                    ].map((v) => (
                      <option key={v} value={v}>
                        {label(v)}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
              <span className="table-caption">
                <Activity size={14} /> Live database records
              </span>
            </div>
            {loading ? (
              <div className="empty-state" role="status">
                <RefreshCw className="spin" />
                <h3>Loading your workspace</h3>
                <p>Retrieving complaint records…</p>
              </div>
            ) : error ? (
              <div className="empty-state">
                <AlertCircle size={30} />
                <h3>Workspace unavailable</h3>
                <p role="alert">{error}</p>
                <button
                  className="secondary"
                  onClick={() => setVersion((v) => v + 1)}
                >
                  Try again
                </button>
              </div>
            ) : !list?.items.length ? (
              <div className="empty-state">
                <span className="empty-icon">
                  <Inbox size={29} />
                </span>
                <h3>
                  {status || type
                    ? "No matching complaints"
                    : "Your inbox starts here"}
                </h3>
                <p>
                  {status || type
                    ? "Try another status or complaint type."
                    : "Connect your Gmail test account, then sync emails to bring complaints into your workspace."}
                </p>
                {!status && !type && (
                  <button
                    className="secondary"
                    disabled={syncing}
                    onClick={sync}
                  >
                    <RefreshCw size={15} /> Sync Emails
                  </button>
                )}
              </div>
            ) : (
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Complaint / sender</th>
                      <th>Type / order</th>
                      <th>Priority</th>
                      <th>Policy assessment</th>
                      <th>Case status</th>
                      <th>Received</th>
                      <th>
                        <span className="sr-only">Open</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {list.items.map((c) => (
                      <tr key={c.id}>
                        <td>
                          <button
                            className="subject-link"
                            onClick={() => setSelectedId(c.id)}
                          >
                            {c.email_subject || "(no subject)"}
                          </button>
                          <small>
                            #{String(c.id).padStart(4, "0")} · {c.sender_email}
                          </small>
                        </td>
                        <td>
                          {label(c.complaint_type)}
                          <small>{c.order_id || "Order not extracted"}</small>
                        </td>
                        <td>
                          <Badge value={c.priority} />
                        </td>
                        <td>
                          <Badge value={c.policy_result} />
                        </td>
                        <td>
                          <Badge value={c.case_status} />
                        </td>
                        <td className="date-cell">{date(c.received_at)}</td>
                        <td>
                          <button
                            className="icon-button"
                            aria-label={`Open complaint ${c.id}`}
                            onClick={() => setSelectedId(c.id)}
                          >
                            <ArrowRight size={17} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <div className="table-footer">
              <span>
                {loading || error
                  ? "Awaiting database response"
                  : `${list?.total ?? 0} complaint${list?.total === 1 ? "" : "s"} · Page ${page}`}
              </span>
              <div>
                <button
                  aria-label="Previous page"
                  className="icon-button"
                  disabled={page === 1 || loading}
                  onClick={() => setPage((p) => p - 1)}
                >
                  <ChevronLeft size={17} />
                </button>
                <button
                  aria-label="Next page"
                  className="icon-button"
                  disabled={loading || !list || page * 10 >= list.total}
                  onClick={() => setPage((p) => p + 1)}
                >
                  <ChevronRight size={17} />
                </button>
              </div>
            </div>
          </section>
          <div className="workflow-note">
            <span>
              <Sparkles size={16} /> How ClaimPilot works
            </span>
            <p>
              Gmail intake <ArrowRight /> AI analysis <ArrowRight /> Order
              verification <ArrowRight /> Policy assessment <ArrowRight /> Your
              review
            </p>
          </div>
          <footer>
            <span>
              ClaimPilot <span> / </span> A little more clarity. A lot less
              manual work.
            </span>
            <span>No refunds or customer emails are sent automatically.</span>
          </footer>
        </main>
      </div>
      {selectedId !== null && (
        <div className="modal-backdrop" onClick={() => setSelectedId(null)}>
          <section
            className="detail-panel"
            role="dialog"
            aria-modal="true"
            aria-labelledby="detail-title"
            onClick={(e) => e.stopPropagation()}
          >
            <header className="detail-header">
              <div>
                <div className="eyebrow">COMPLAINT #{selectedId}</div>
                <h2 id="detail-title">Case details</h2>
              </div>
              <button
                ref={closeRef}
                className="icon-button"
                onClick={() => setSelectedId(null)}
                aria-label="Close details"
              >
                <X />
              </button>
            </header>
            {detailLoading ? (
              <p className="detail-section" role="status">
                Loading complaint…
              </p>
            ) : detailError ? (
              <p className="notice error" role="alert">
                {detailError}
              </p>
            ) : (
              detail && (
                <>
                  <section className="detail-section">
                    <h3>
                      <Mail size={17} /> Original email
                    </h3>
                    <h2>{detail.email_subject}</h2>
                    <p className="muted">
                      {detail.sender_email} · {date(detail.received_at)}
                    </p>
                    <pre className="email-body">{detail.email_body}</pre>
                  </section>
                  <section className="detail-section ai-section">
                    <h3>
                      <Sparkles size={17} /> AI-generated analysis{" "}
                      <span className="section-tag">Unverified extraction</span>
                    </h3>
                    {detail.processing_error && (
                      <p className="notice error">
                        {[
                          "gemini_timeout_retry_sync",
                          "groq_timeout_retry_sync",
                        ].includes(detail.processing_error)
                          ? "The AI provider did not respond before the time limit. Your email is saved."
                          : `Analysis failed: ${label(detail.processing_error)}.`}
                      </p>
                    )}
                    {analysisError?.id === detail.id && (
                      <p className="notice error" role="alert">
                        {analysisError.message}
                      </p>
                    )}
                    {["processing_failed", "processing"].includes(
                      detail.case_status,
                    ) && (
                      <div className="analysis-control">
                        <button
                          className="primary"
                          disabled={analyzingId !== null || syncing}
                          onClick={() => retryAnalysis(detail.id)}
                        >
                          {analyzingId === detail.id ? (
                            <RefreshCw size={16} className="spin" />
                          ) : (
                            <Sparkles size={16} />
                          )}
                          {analyzingId === detail.id
                            ? "AI is analyzing…"
                            : "Retry AI analysis"}
                        </button>
                        <p className="muted" aria-live="polite">
                          {analyzingId === detail.id
                            ? "Analyzing this saved email. Gmail is not being scanned."
                            : "Runs only this saved email through the configured AI provider, order verification, and the sample policy."}
                        </p>
                      </div>
                    )}
                    <p>
                      {detail.ai_summary || "Analysis is not available yet."}
                    </p>
                    <dl className="detail-grid">
                      <Field
                        name="Complaint type"
                        value={label(detail.complaint_type)}
                      />
                      <Field
                        name="Extracted order ID"
                        value={detail.order_id}
                      />
                      <Field
                        name="Requested action"
                        value={label(detail.requested_action)}
                      />
                      <Field name="Priority" value={label(detail.priority)} />
                    </dl>
                    <div className="field">
                      <dt>Missing information reported by AI</dt>
                      <dd>
                        {detail.ai_summary
                          ? detail.missing_information.join(", ") ||
                            "None reported"
                          : "Not analyzed"}
                      </dd>
                    </div>
                  </section>
                  <section className="detail-section">
                    <h3>
                      <ShieldCheck size={17} /> Verified database information
                    </h3>
                    <p className="muted">
                      Verification: {label(detail.verification_status)}
                    </p>
                    {detail.verified_order ? (
                      <>
                        <dl className="detail-grid">
                          <Field
                            name="Order"
                            value={detail.verified_order.order_id}
                          />
                          <Field
                            name="Status"
                            value={detail.verified_order.order_status}
                          />
                          <Field
                            name="Expected delivery"
                            value={detail.verified_order.expected_delivery_date}
                          />
                          <Field
                            name="Actual delivery"
                            value={detail.verified_order.actual_delivery_date}
                          />
                          <Field
                            name="Shipping fee"
                            value={`${Number(detail.verified_order.shipping_fee).toLocaleString()} VND`}
                          />
                          <Field
                            name="Customer email"
                            value={detail.verified_order.customer_email}
                          />
                        </dl>
                        <p
                          className={
                            detail.sender_matches_order ? "muted" : "mismatch"
                          }
                        >
                          {detail.sender_matches_order
                            ? "Sender matches the order customer email."
                            : "Sender does not match the order customer email. Verify ownership before proceeding."}
                        </p>
                      </>
                    ) : (
                      <p>No verified order is linked to this complaint.</p>
                    )}
                  </section>
                  <section className="detail-section policy-section">
                    <h3>
                      <CheckCircle2 size={17} /> Backend policy assessment
                    </h3>
                    <Badge value={detail.policy_result} />
                    <p>
                      {detail.policy_reason ||
                        "Policy assessment awaits successful analysis."}
                    </p>
                    <small>
                      Sample policy only. Staff review is required. No refund
                      has been issued.
                    </small>
                  </section>
                  <section className="detail-section">
                    <h3>Current case status</h3>
                    <Badge
                      value={
                        analyzingId === detail.id
                          ? "processing"
                          : detail.case_status
                      }
                    />
                  </section>
                </>
              )
            )}
          </section>
        </div>
      )}
    </div>
  );
}
