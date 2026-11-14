import { useEffect, useState } from "react";
import { api } from "../../api";
import type {
  Case,
  Page,
  Envelope,
  Run,
  Knowledge,
  Source,
  Integrations,
} from "./contracts";
import { useLoad, label, stamp, Badge, ErrorNotice, Empty } from "./ui";

export default function InboxPanel({
  revision,
  onChanged,
  integrations,
}: {
  revision: number;
  onChanged: () => void;
  integrations: Integrations | null;
}) {
  const initial =
    Number(new URLSearchParams(location.search).get("case")) || null;
  const initialQueue = new URLSearchParams(location.search).get("queue") || "work";
  const [selected, setSelected] = useState<number | null>(initial),
    [q, setQ] = useState(""),
    [queue, setQueue] = useState(initialQueue),
    [workflow, setWorkflow] = useState(""),
    [processing, setProcessing] = useState(""),
    [type, setType] = useState(""),
    [severity, setSeverity] = useState(""),
    [page, setPage] = useState(1),
    [mobile, setMobile] = useState("conversation");
  const list = useLoad<Page<Case>>(
    `/complaints?queue=${queue}&q=${encodeURIComponent(q)}&workflow_status=${workflow}&processing_status=${processing}&complaint_type=${type}&severity=${severity}&page=${page}&page_size=15`,
    revision,
  );
  function choose(id: number | null) {
    setSelected(id);
    const url = new URL(location.href);
    url.searchParams.set("tab", "inbox");
    if (id) url.searchParams.set("case", String(id));
    else url.searchParams.delete("case");
    history.replaceState(null, "", url);
  }
  return (
    <>
      <div className="cp-section-intro cp-between">
        <div>
          <span className="cp-eyebrow">CUSTOMER INBOX</span>
          <h1>Hộp thư khách hàng</h1>
          <p>Mỗi cuộc trao đổi, đầy đủ ngữ cảnh và bước tiếp theo.</p>
        </div>
        <button
          className="cp-secondary"
          onClick={() => {
            list.reload();
            onChanged();
          }}
        >
          ↻ Làm mới
        </button>
      </div>
      <div className="cp-inbox-filters">
        <input
          aria-label="Tìm hồ sơ"
          value={q}
          placeholder="Tìm chủ đề, nội dung hoặc mã đơn…"
          onChange={(e) => {
            setQ(e.target.value);
            setPage(1);
          }}
        />
        <select
          aria-label="Hàng đợi"
          value={queue}
          onChange={(e) => {
            setQueue(e.target.value);
            setPage(1);
          }}
        >
          <option value="work">Hồ sơ khiếu nại</option>
          <option value="urgent">🚨 Cần can thiệp khẩn</option>
          <option value="technical">Lỗi & chờ phân loại</option>
        </select>
        <select
          aria-label="Mức độ rủi ro"
          value={severity}
          onChange={(e) => {
            setSeverity(e.target.value);
            setPage(1);
          }}
        >
          <option value="">Mọi mức độ</option>
          <option value="critical">🔴 Khẩn cấp (Critical)</option>
          <option value="high">🟠 Rủi ro cao (High)</option>
          <option value="medium">🟡 Cần xem xét (Medium)</option>
          <option value="low">🟢 An toàn (Low)</option>
        </select>
        <select
          aria-label="Trạng thái hồ sơ"
          value={workflow}
          onChange={(e) => {
            setWorkflow(e.target.value);
            setPage(1);
          }}
        >
          <option value="">Mọi trạng thái</option>
          {[
            "needs_review",
            "waiting_customer",
            "waiting_fulfillment",
            "resolved",
            "closed",
          ].map((x) => (
            <option key={x} value={x}>
              {label(x)}
            </option>
          ))}
        </select>
        <select
          aria-label="Trạng thái phân tích"
          value={processing}
          onChange={(e) => setProcessing(e.target.value)}
        >
          <option value="">Mọi xử lý AI</option>
          {["pending", "processing", "completed", "failed"].map((x) => (
            <option key={x} value={x}>
              {label(x)}
            </option>
          ))}
        </select>
        <select
          aria-label="Loại khiếu nại"
          value={type}
          onChange={(e) => setType(e.target.value)}
        >
          <option value="">Mọi vấn đề</option>
          {[
            "late_delivery",
            "not_received",
            "damaged_item",
            "wrong_item",
            "refund_request",
            "other",
          ].map((x) => (
            <option key={x} value={x}>
              {label(x)}
            </option>
          ))}
        </select>
      </div>
      <div className={`cp-inbox ${selected ? "has-detail" : ""}`}>
        <aside className="cp-case-list">
          <div className="cp-list-caption">
            {list.data?.total ?? "—"} hồ sơ{" "}
            <span>
              {queue === "technical"
                ? "Hàng đợi kỹ thuật"
                : "Hàng đợi công việc"}
            </span>
          </div>
          <ErrorNotice message={list.error} />
          {list.loading ? (
            <p className="cp-padding" role="status">
              Đang tải hồ sơ…
            </p>
          ) : list.data?.items.length ? (
            list.data.items.map((c) => (
              <button
                className={`cp-case ${selected === c.id ? "selected" : ""}`}
                key={c.id}
                onClick={() => choose(c.id)}
              >
                <div className="cp-between">
                  <span className="cp-avatar">
                    {c.sender_email.slice(0, 1).toUpperCase()}
                  </span>
                  <div style={{display:'flex',gap:4,alignItems:'center',flexWrap:'wrap',justifyContent:'flex-end'}}>
                    {c.severity && (
                      <span className={`cp-severity-pill ${c.severity}`} title={label(c.severity)}>
                        {c.severity === 'critical' ? '🔴 Khẩn cấp' : c.severity === 'high' ? '🟠 Rủi ro cao' : c.severity === 'medium' ? '🟡 Xem xét' : '🟢 An toàn'}
                      </span>
                    )}
                    {c.taken_over_by && (
                      <span className="cp-taken-over-pill" title={`Tiếp quản bởi ${c.taken_over_by}`}>
                        👤 {c.taken_over_by}
                      </span>
                    )}
                    <small>#{c.id}</small>
                  </div>
                </div>
                <strong>{c.email_subject}</strong>
                <span className="cp-truncate">{c.sender_email}</span>
                <p>
                  {c.ai_summary ||
                    c.email_body?.slice(0, 100) ||
                    "Chưa có bản tóm tắt"}
                </p>
                <div className="cp-between">
                  <Badge value={c.workflow_status} />
                  <span
                    className={`cp-dot ${c.processing_status === "failed" ? "warning" : ""}`}
                    title={label(c.processing_status)}
                  />
                </div>
              </button>
            ))
          ) : (
            <Empty
              title={q ? "Không có kết quả phù hợp" : "Hàng đợi đang trống"}
            >
              <p>
                {queue === "work"
                  ? "Đồng bộ Gmail hoặc kiểm tra hàng đợi lỗi/chờ phân loại."
                  : "Không có hồ sơ chờ xử lý kỹ thuật."}
              </p>
            </Empty>
          )}
          <div className="cp-pagination">
            <button disabled={page === 1} onClick={() => setPage((p) => p - 1)}>
              ←
            </button>
            <span>Trang {page}</span>
            <button
              disabled={!list.data || page * 15 >= list.data.total}
              onClick={() => setPage((p) => p + 1)}
            >
              →
            </button>
          </div>
        </aside>
        {selected ? (
          <CaseDetail
            key={selected}
            id={selected}
            revision={revision}
            onChanged={onChanged}
            onBack={() => choose(null)}
            mobile={mobile}
            setMobile={setMobile}
            integrations={integrations}
          />
        ) : (
          <section className="cp-no-selection">
            <Empty title="Một góc nhìn rõ ràng hơn">
              <p>
                Chọn hồ sơ để xem hội thoại, nguồn dữ liệu và phương án xử lý.
              </p>
              <span className="cp-safety">
                AI hỗ trợ phân tích. Nhân viên giữ quyền quyết định.
              </span>
            </Empty>
          </section>
        )}
      </div>
    </>
  );
}

function CaseDetail({
  id,
  revision,
  onChanged,
  onBack,
  mobile,
  setMobile,
  integrations,
}: {
  id: number;
  revision: number;
  onChanged: () => void;
  onBack: () => void;
  mobile: string;
  setMobile: (x: string) => void;
  integrations: Integrations | null;
}) {
  const request = useLoad<Case>(`/complaints/${id}`, revision),
    runs = useLoad<{ items: Run[] }>(`/complaints/${id}/agent-runs`, revision);
  const [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [notice, setNotice] = useState(""),
    [source, setSource] = useState<Knowledge | null>(null);
  const c = request.data;
  async function execute(path: string, data: unknown, method = "POST") {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const result = await api<unknown>(path, method, data);
      request.reload();
      runs.reload();
      onChanged();
      setNotice("Thao tác đã được lưu.");
      return result;
    } catch (e) {
      setError((e as Error).message);
      return null;
    } finally {
      setBusy(false);
    }
  }
  async function showSource(s: Source) {
    if (s.kind === "asset") {
      window.open(
        `/api/evidence/${s.id}/content`,
        "_blank",
        "noopener,noreferrer",
      );
      return;
    }
    try {
      setSource(
        await api<Knowledge>(`/knowledge/${s.article_id}/revisions/${s.id}`),
      );
    } catch (e) {
      setError((e as Error).message);
    }
  }
  if (!c)
    return (
      <section className="cp-case-detail">
        <button className="cp-text" onClick={onBack}>
          ← Quay lại
        </button>
        <ErrorNotice message={request.error} />
        {request.loading ? "Đang tải hội thoại…" : null}
      </section>
    );
  const roles = [
    "intake_classification",
    "order_lookup",
    "policy_assessment",
    "evidence_analysis",
    "reply_writer",
    "safety_quality",
  ];
  return (
    <div className="cp-detail-layout">
      <section className="cp-conversation">
        <div className="cp-detail-heading">
          <button className="cp-text" onClick={onBack}>
            ← Danh sách
          </button>
          <span>
            HỒ SƠ #{c.id} · v{c.case_version}
          </span>
          <h2>{c.email_subject}</h2>
          <div className="cp-badges">
            <Badge value={c.workflow_status} />
            <Badge value={c.processing_status} />
            {c.severity && (
              <span className={`cp-severity-pill ${c.severity}`}>
                {c.severity === "critical"
                  ? "🔴 Khẩn cấp (P0)"
                  : c.severity === "high"
                    ? "🟠 Rủi ro cao (P1)"
                    : c.severity === "medium"
                      ? "🟡 Cần xem xét (P2)"
                      : "🟢 An toàn (P3)"}
              </span>
            )}
            {c.taken_over_by && (
              <span className="cp-taken-over-pill">
                👤 Đang tiếp quản: {c.taken_over_by}
              </span>
            )}
            {(c.severity === "low" || c.severity === "medium") &&
              c.workflow_status === "needs_review" &&
              !c.replies.some((r) => r.status === "sent") && (
                <button
                  className="cp-auto-reply-btn"
                  disabled={busy}
                  onClick={() =>
                    execute(`/complaints/${c.id}/auto-reply`, {
                      expected_case_version: c.case_version,
                    })
                  }
                  title="AI tự động duyệt quyết định, soạn phản hồi và kiểm tra an toàn theo chính sách"
                >
                  ⚡ AI Auto-Reply (Tự động rep)
                </button>
              )}
          </div>
          <div className="cp-mobile-tabs">
            {[
              ["conversation", "Hội thoại"],
              ["assessment", "Đánh giá"],
              ["history", "Lịch sử"],
            ].map(([k, v]) => (
              <button
                className={mobile === k ? "active" : ""}
                key={k}
                onClick={() => setMobile(k)}
              >
                {v}
              </button>
            ))}
          </div>
        </div>
        {(c.severity === "critical" ||
          c.severity === "high" ||
          c.requires_immediate_takeover) && (
          <div className={`cp-escalation-banner ${c.severity || "high"}`}>
            <div className="cp-escalation-header">
              <strong>
                {c.severity === "critical"
                  ? "🔴 BÁO ĐỘNG ĐỎ: CẦN CON NGƯỜI CAN THIỆP KHẨN CẤP"
                  : "🟠 CẢNH BÁO RỦI RO CAO (HIGH RISK)"}
              </strong>
              <small>
                Hệ thống đã dừng tất cả hành vi tự động để bảo đảm an toàn.
              </small>
            </div>
            {c.escalation_reasons && c.escalation_reasons.length > 0 && (
              <ul className="cp-escalation-reasons">
                {c.escalation_reasons.map((r, idx) => (
                  <li key={idx}>
                    ⚠️ <strong>{label(r.code)}:</strong> {r.message}
                  </li>
                ))}
              </ul>
            )}
            <div className="cp-takeover-action">
              {c.taken_over_by ? (
                <div className="cp-taken-over-status">
                  <span>
                    👤 Đang được tiếp quản bởi chuyên viên:{" "}
                    <strong>{c.taken_over_by}</strong>
                  </span>
                  <button
                    className="cp-secondary cp-btn-sm"
                    disabled={busy}
                    onClick={() =>
                      execute(`/complaints/${c.id}/release-takeover`, {
                        expected_case_version: c.case_version,
                        note: "Bàn giao lại hệ thống",
                      })
                    }
                  >
                    Bỏ tiếp quản
                  </button>
                </div>
              ) : (
                <button
                  className="cp-primary cp-btn-sm"
                  disabled={busy}
                  onClick={() =>
                    execute(`/complaints/${c.id}/takeover`, {
                      expected_case_version: c.case_version,
                      note: "Chuyên viên tiếp quản xử lý hồ sơ",
                    })
                  }
                >
                  ✋ Tiếp quản ca này (Staff Takeover)
                </button>
              )}
            </div>
          </div>
        )}
        {c.case_report && (
          <div className="cp-case-report-box">
            <h4>📊 Báo cáo kết quả xử lý (Case Summary Report)</h4>
            <p>{c.case_report.summary}</p>
            <small>
              Người giải quyết:{" "}
              <strong>
                {c.case_report.resolved_by === "ai_automation"
                  ? "AI Tự động"
                  : "Nhân viên"}
              </strong>{" "}
              · Phương án:{" "}
              <strong>
                {label(
                  c.case_report.decision_resolution ||
                    c.case_report.decision_action,
                )}
              </strong>{" "}
              · Thời điểm: {stamp(c.case_report.generated_at)}
            </small>
          </div>
        )}
        <ErrorNotice message={error || request.error} />
        {notice && (
          <div className="cp-notice" role="status">
            {notice}
          </div>
        )}
        <div
          className={`cp-mobile-content ${mobile === "conversation" ? "mobile-active" : ""}`}
        >
          <div className="cp-thread">
            {c.messages.length ? (
              c.messages.map((m) => (
                <article key={m.id} className={`cp-message ${m.direction}`}>
                  <div className="cp-between">
                    <strong>
                      {m.direction === "inbound"
                        ? "Khách hàng"
                        : "Doanh nghiệp"}
                    </strong>
                    <small>{stamp(m.occurred_at)}</small>
                  </div>
                  <small>
                    {m.sender_email}
                    {m.recipient_email ? ` → ${m.recipient_email}` : ""}
                  </small>
                  <h3>{m.subject}</h3>
                  <p>{m.body}</p>
                  <Badge value={m.processing_status} />
                </article>
              ))
            ) : (
              <article className="cp-message inbound">
                <strong>Email gốc</strong>
                <p>{c.email_body}</p>
              </article>
            )}
          </div>
          <Composer
            key={c.current_decision_id ?? "no-decision"}
            c={c}
            execute={execute}
            busy={busy}
            integrations={integrations}
            onSource={showSource}
          />
        </div>
        <section
          className={`cp-history cp-mobile-content ${mobile === "history" ? "mobile-active" : ""}`}
        >
          <h3>Lịch sử xử lý</h3>
          {[
            ...c.audit_events.map((a) => ({
              id: a.id,
              title: label(a.event_type),
              note: a.note,
              actor: a.actor,
              at: a.created_at,
            })),
            ...c.decisions.map((d) => ({
              id: d.id,
              title: `${label(d.action)} · ${label(d.resolution)}`,
              note: d.note,
              actor: d.actor,
              at: d.created_at,
            })),
          ]
            .sort(
              (a, b) => a.at.localeCompare(b.at) || a.id.localeCompare(b.id),
            )
            .map((a) => (
              <div className="cp-timeline-item" key={a.id}>
                <span className="cp-timeline-dot" />
                <strong>{a.title}</strong>
                <p>{a.note}</p>
                <small>
                  {a.actor} · {stamp(a.at)}
                </small>
              </div>
            ))}
          {!c.audit_events.length && !c.decisions.length && (
            <p className="cp-muted">Chưa có hành động được ghi nhận.</p>
          )}
        </section>
      </section>
      <aside
        className={`cp-context cp-mobile-content ${mobile === "assessment" ? "mobile-active" : ""}`}
      >
        <section className="cp-context-section">
          <div className="cp-between">
            <h3>Đội ngũ agent</h3>
            <button
              className="cp-text"
              disabled={busy || c.workflow_status === "closed"}
              onClick={() =>
                execute(`/complaints/${id}/agent-runs`, {
                  expected_case_version: c.case_version,
                })
              }
            >
              Chạy phân tích
            </button>
          </div>
          <p className="cp-muted">Tiến độ thực tế · không tự gửi email</p>
          {roles.map((role) => {
            const currentReply=c.replies.find(r=>r.decision_id===c.current_decision_id);
            const replyRole=role==='reply_writer'||role==='safety_quality';
            const roleRun=runs.data?.items.find(run=>replyRole
              ? run.trigger==='prepare'&&run.steps.some(s=>s.role==='reply_writer'&&s.output?.reply_id===currentReply?.id)
              : run.trigger!=='prepare'&&run.steps.some(s=>s.role===role));
            const st=roleRun?[...roleRun.steps].reverse().find(s=>s.role===role):undefined;
            return (
              <div className="cp-agent" key={role}>
                <div>
                  <span
                    className={`cp-agent-dot status-${st?.status ?? "idle"}`}
                  />
                  <strong>{label(role)}</strong>
                </div>
                {st ? (
                  <>
                    <Badge value={st.status} />
                    {(st.error_code || st.skip_reason) && (
                      <small>
                        {st.error_code ? label(st.error_code) : st.skip_reason}
                      </small>
                    )}
                    {st.source_refs.map((s) => (
                      <button
                        className="cp-source-link"
                        key={s.id}
                        onClick={() => showSource(s)}
                      >
                        ↗ {s.title || "Nguồn KB"} · v{s.version}
                      </button>
                    ))}
                  </>
                ) : (
                  <small>Chưa có lượt chạy</small>
                )}
              </div>
            );
          })}
          <ErrorNotice message={runs.error} />
        </section>
        <section className="cp-context-section">
          <h3>Đánh giá & dữ liệu gốc</h3>
          <p>
            {c.ai_summary ||
              "Chưa có tóm tắt AI. Bạn có thể kiểm tra email gốc và tiếp tục thủ công."}
          </p>
          <Badge value={c.ownership_status} />
          {c.verified_order ? (
            <dl className="cp-facts">
              <dt>Mã đơn</dt>
              <dd>{c.verified_order.order_id}</dd>
              <dt>Trạng thái</dt>
              <dd>{c.verified_order.order_status}</dd>
              <dt>Ngày dự kiến</dt>
              <dd>{c.verified_order.expected_delivery_date || "Chưa biết"}</dd>
              <dt>Ngày thực tế</dt>
              <dd>{c.verified_order.actual_delivery_date || "Chưa biết"}</dd>
              <dt>Phí vận chuyển</dt>
              <dd>
                {Number(c.verified_order.shipping_fee).toLocaleString("vi-VN")}{" "}
                đ
              </dd>
              <dt>Tổng tiền</dt>
              <dd>
                {c.verified_order.total_amount
                  ? Number(c.verified_order.total_amount).toLocaleString(
                      "vi-VN",
                    ) + " đ"
                  : "Chưa biết"}
              </dd>
            </dl>
          ) : (
            <p className="cp-muted">Chưa xác minh được đơn hàng.</p>
          )}
          <div className="cp-policy">
            <small>CHÍNH SÁCH MẪU · demo-v2</small>
            <p>
              {c.policy_reason ||
                "Cần đánh giá dữ liệu để xác định chính sách."}
            </p>
            {c.policy_snapshot?.missing_fields?.map((x) => (
              <span className="cp-tag" key={x}>
                {label(x)}
              </span>
            ))}
          </div>
        </section>
        <EvidencePanel c={c} execute={execute} busy={busy} />
        <ManualReview c={c} execute={execute} busy={busy} />
        <DecisionPanel c={c} execute={execute} busy={busy} />
        <Lifecycle c={c} execute={execute} busy={busy} />
      </aside>
      {source && (
        <div className="cp-modal-backdrop">
          <section
            role="dialog"
            aria-modal="true"
            aria-label="Nguồn tri thức"
            className="cp-source-modal"
          >
            <button
              autoFocus
              className="cp-text"
              onClick={() => setSource(null)}
            >
              ✕ Đóng
            </button>
            <Badge value={source.status} />
            <h2>{source.title}</h2>
            <p className="cp-muted">
              Phiên bản {source.revision} · {source.source_label} ·{" "}
              {stamp(source.updated_at)}
            </p>
            <div className="cp-prose">{source.body}</div>
            {source.has_conflict && (
              <div className="cp-notice warning">
                Nguồn đang có mâu thuẫn, không dùng để tạo phản hồi mới.
              </div>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
type Execute = (
  path: string,
  data: unknown,
  method?: string,
) => Promise<unknown>;
function EvidencePanel({
  c,
  execute,
  busy,
}: {
  c: Case;
  execute: Execute;
  busy: boolean;
}) {
  const data = useLoad<{
    assets: {
      id: string;
      source: string;
      evidence_kind: string;
      content_url: string;
    }[];
    analysis: {
      status: string;
      consistency: string | null;
      observations: string[];
      limitations: string[];
      error_code: string | null;
    } | null;
  }>(`/complaints/${c.id}/evidence`, c.case_version);
  return (
    <section className="cp-context-section">
      <h3>Bằng chứng hình ảnh</h3>
      <ErrorNotice message={data.error} />
      {data.data?.assets.length ? (
        <>
          <div className="cp-evidence-grid">
            {data.data.assets.map((a) => (
              <a
                key={a.id}
                href={a.content_url}
                target="_blank"
                rel="noreferrer"
              >
                <img
                  src={a.content_url}
                  alt={
                    a.source === "customer"
                      ? "Ảnh khách gửi"
                      : a.evidence_kind === "packing"
                        ? "Ảnh đóng gói"
                        : "Ảnh giao hàng"
                  }
                />
                <small>
                  {a.source === "customer"
                    ? "Khách hàng"
                    : a.evidence_kind === "packing"
                      ? "Đóng gói"
                      : "Giao hàng"}
                </small>
              </a>
            ))}
          </div>
          <button
            className="cp-secondary"
            disabled={busy}
            onClick={async () => {
              await execute(`/complaints/${c.id}/evidence/analyze`, {
                expected_case_version: c.case_version,
              });
              data.reload();
            }}
          >
            Phân tích ảnh bằng Gemini
          </button>
        </>
      ) : (
        <p className="cp-muted">
          Chưa có ảnh hợp lệ từ cuộc trao đổi. Bạn vẫn có thể kiểm tra và yêu
          cầu khách bổ sung.
        </p>
      )}
      {data.data?.analysis && (
        <div className="cp-policy">
          <Badge value={data.data.analysis.status} />
          <p>
            {data.data.analysis.consistency === "inconclusive"
              ? "Chưa đủ căn cứ kết luận"
              : data.data.analysis.consistency === "consistent"
                ? "Các quan sát có điểm phù hợp"
                : data.data.analysis.consistency === "inconsistent"
                  ? "Có điểm cần nhân viên kiểm tra thêm"
                  : ""}
          </p>
          {data.data.analysis.observations.map((o, i) => (
            <p key={i}>{o}</p>
          ))}
          {data.data.analysis.limitations.map((o, i) => (
            <p className="cp-muted" key={i}>
              Giới hạn: {o}
            </p>
          ))}
          {data.data.analysis.error_code && (
            <p>{label(data.data.analysis.error_code)}</p>
          )}
        </div>
      )}
    </section>
  );
}
function ManualReview({
  c,
  execute,
  busy,
}: {
  c: Case;
  execute: Execute;
  busy: boolean;
}) {
  const [order, setOrder] = useState(c.order_id || ""),
    [type, setType] = useState(c.complaint_type || "other"),
    [action, setAction] = useState(c.requested_action || "request_information"),
    [note, setNote] = useState(""),
    [proof, setProof] = useState(""),
    [ack, setAck] = useState(false);
  return (
    <section className="cp-context-section">
      <details>
        <summary>Kiểm tra & chỉnh sửa thủ công</summary>
        <form
          className="cp-form"
          onSubmit={async (e) => {
            e.preventDefault();
            const result = await execute(
              `/complaints/${c.id}/review`,
              {
                expected_case_version: c.case_version,
                is_complaint: true,
                order_id: order || null,
                complaint_type: type,
                requested_action: action,
                note,
                acknowledge_manual_review: ack,
                ownership_confirmation: proof
                  ? { verified: true, reason: proof }
                  : null,
              },
              "PATCH",
            );
            if (result) setNote("");
          }}
        >
          <label>
            Mã đơn
            <input value={order} onChange={(e) => setOrder(e.target.value)} />
          </label>
          <label>
            Loại vấn đề
            <select value={type} onChange={(e) => setType(e.target.value)}>
              {[
                "late_delivery",
                "not_received",
                "damaged_item",
                "wrong_item",
                "refund_request",
                "other",
              ].map((x) => (
                <option value={x} key={x}>
                  {label(x)}
                </option>
              ))}
            </select>
          </label>
          <label>
            Yêu cầu của khách
            <select value={action} onChange={(e) => setAction(e.target.value)}>
              {[
                "shipping_fee_refund",
                "order_refund",
                "replacement",
                "request_information",
                "other",
              ].map((x) => (
                <option value={x} key={x}>
                  {label(x)}
                </option>
              ))}
            </select>
          </label>
          <label>
            Căn cứ xác minh chủ đơn (nếu có)
            <input
              value={proof}
              onChange={(e) => setProof(e.target.value)}
              placeholder="Chỉ nhập sau khi thực sự xác minh"
            />
          </label>
          <label>
            Ghi chú kiểm tra
            <textarea
              required
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={2}
            />
          </label>
          {c.needs_manual_review && (
            <label className="cp-checkbox">
              <input
                type="checkbox"
                checked={ack}
                onChange={(e) => setAck(e.target.checked)}
              />
              Tôi đã xem ngoại lệ người gửi/đơn hàng
            </label>
          )}
          <button
            className="cp-secondary"
            disabled={busy || c.workflow_status === "closed"}
          >
            Lưu kết quả kiểm tra
          </button>
        </form>
      </details>
    </section>
  );
}
function DecisionPanel({
  c,
  execute,
  busy,
}: {
  c: Case;
  execute: Execute;
  busy: boolean;
}) {
  const [action, setAction] = useState("request_information"),
    [resolution, setResolution] = useState("replacement"),
    [note, setNote] = useState(""),
    [missing, setMissing] = useState("");
  return (
    <section className="cp-context-section">
      <h3>Quyết định của nhân viên</h3>
      <p className="cp-muted">
        Đề xuất AI cần bạn xác nhận. Lưu quyết định chưa gửi email.
      </p>
      <form
        className="cp-form"
        onSubmit={async (e) => {
          e.preventDefault();
          const result = await execute(`/complaints/${c.id}/decisions`, {
            expected_case_version: c.case_version,
            action,
            resolution:
              action === "approve"
                ? resolution
                : action === "reject"
                  ? "decline"
                  : "request_information",
            note,
            missing_fields:
              action === "request_information"
                ? missing
                    .split(",")
                    .map((x) => x.trim())
                    .filter(Boolean)
                : [],
          });
          if (result) setNote("");
        }}
      >
        <label>
          Phương án
          <select value={action} onChange={(e) => setAction(e.target.value)}>
            {["request_information", "approve", "reject"].map((x) => (
              <option key={x} value={x}>
                {label(x)}
              </option>
            ))}
          </select>
        </label>
        {action === "approve" && (
          <label>
            Cách giải quyết
            <select
              value={resolution}
              onChange={(e) => setResolution(e.target.value)}
            >
              {[
                "replacement",
                "shipping_fee_refund",
                "order_refund",
                "reshipment",
                "carrier_investigation",
                "other",
              ].map((x) => (
                <option key={x} value={x}>
                  {label(x)}
                </option>
              ))}
            </select>
          </label>
        )}
        {action === "request_information" && (
          <label>
            Thông tin cần bổ sung
            <input
              required
              value={missing}
              onChange={(e) => setMissing(e.target.value)}
              placeholder="Ví dụ: mã đơn, ảnh sản phẩm"
            />
          </label>
        )}
        <label>
          Lý do quyết định
          <textarea
            rows={2}
            required
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
        </label>
        <button
          className="cp-primary"
          disabled={busy || !c.is_complaint || c.workflow_status === "closed"}
        >
          Ghi nhận quyết định
        </button>
      </form>
    </section>
  );
}
function Lifecycle({
  c,
  execute,
  busy,
}: {
  c: Case;
  execute: Execute;
  busy: boolean;
}) {
  const [note, setNote] = useState(""),
    [reference, setReference] = useState("");
  const action =
    c.workflow_status === "waiting_fulfillment"
      ? "fulfillment"
      : c.workflow_status === "resolved"
        ? "close"
        : c.workflow_status === "closed"
          ? "reopen"
          : null;
  if (!action) return null;
  return (
    <section className="cp-context-section">
      <h3>
        {action === "fulfillment"
          ? "Ghi nhận thực hiện ngoài ứng dụng"
          : action === "close"
            ? "Đóng hồ sơ"
            : "Mở lại hồ sơ"}
      </h3>
      <form
        className="cp-form"
        onSubmit={(e) => {
          e.preventDefault();
          execute(`/complaints/${c.id}/${action}`, {
            expected_case_version: c.case_version,
            note,
            reference: reference || null,
          });
        }}
      >
        {action === "fulfillment" && (
          <label>
            Mã tham chiếu
            <input
              value={reference}
              onChange={(e) => setReference(e.target.value)}
            />
          </label>
        )}
        <label>
          Ghi chú
          <textarea
            required
            value={note}
            onChange={(e) => setNote(e.target.value)}
            rows={2}
          />
        </label>
        <button className="cp-secondary" disabled={busy}>
          {action === "fulfillment"
            ? "Đã thực hiện ngoài ứng dụng"
            : action === "close"
              ? "Đóng hồ sơ"
              : "Mở lại"}
        </button>
      </form>
    </section>
  );
}
function Composer({
  c,
  execute,
  busy,
  integrations,

  onSource,
}: {
  c: Case;
  execute: Execute;
  busy: boolean;
  integrations: Integrations | null;
  onSource: (s: Source) => void;
}) {
  const active = c.replies.find((r) => r.decision_id === c.current_decision_id),
    [env, setEnv] = useState<Envelope | null>(null),
    [draft, setDraft] = useState<string | null>(null),
    [preview, setPreview] = useState(false),
    [confirmed, setConfirmed] = useState(false),
    [localError, setLocalError] = useState(""),
    [reviewing, setReviewing] = useState(false),
    [reviewNote, setReviewNote] = useState("");
  useEffect(() => {
    let cancelled = false;
    if (active)
      api<Envelope>(`/complaints/${c.id}/replies/${active.id}`)
        .then((e) => {
          if (!cancelled)
            setEnv((old) => ({
              ...e,
              preview_token:
                old?.quality_check?.id === e.quality_check?.id
                  ? (old?.preview_token ?? null)
                  : null,
            }));
        })
        .catch((e) => {
          if (!cancelled) setLocalError(e.message);
        });
    else setEnv(null);
    return () => {
      cancelled = true;
    };
  }, [active?.id, active?.revision, c.case_version]);
  const candidate =
    env?.reply && (!active || env.reply.revision >= active.revision)
      ? env.reply
      : active;
  const r = candidate
    ? { ...candidate, is_stale: active?.is_stale || candidate.is_stale }
    : undefined;
  const body = draft ?? r?.body ?? "",
    dirty = draft !== null && draft !== r?.body;
  useEffect(() => {
    setPreview(false);
    setConfirmed(false);
  }, [c.case_version, active?.id, active?.revision]);
  useEffect(() => {
    const changed = () => {
      setPreview(false);
      setConfirmed(false);
      setEnv((e) =>
        e?.quality_check
          ? {
              ...e,
              preview_token: null,
              quality_check: { ...e.quality_check, status: "stale" },
            }
          : e,
      );
    };
    window.addEventListener("claimpilot:settings-changed", changed);
    return () =>
      window.removeEventListener("claimpilot:settings-changed", changed);
  }, []);
  async function prepare(mode: string) {
    const result = (await execute(`/complaints/${c.id}/replies/prepare`, {
      expected_case_version: c.case_version,
      decision_id: c.current_decision_id,
      mode,
    })) as Envelope | null;
    if (result) {
      setEnv(result);
      setDraft(null);
    }
  }
  async function save() {
    if (!r) return;
    const result = (await execute(
      `/complaints/${c.id}/replies/${r.id}`,
      { expected_reply_revision: r.revision, body },
      "PATCH",
    )) as Envelope | null;
    if (result) {
      setEnv(result);
      setDraft(null);
      setPreview(false);
      setConfirmed(false);
    }
  }
  async function review() {
    if (!r) return;
    const result = (await execute(
      `/complaints/${c.id}/replies/${r.id}/review-context`,
      {
        expected_case_version: c.case_version,
        expected_reply_revision: r.revision,
        note: reviewNote,
      },
    )) as Envelope | null;
    if (result) {
      setEnv(result);
      setReviewing(false);
      setReviewNote("");
      setPreview(false);
      setConfirmed(false);
    }
  }
  async function check() {
    if (!r) return;
    const result = (await execute(
      `/complaints/${c.id}/replies/${r.id}/preview`,
      { expected_case_version: c.case_version, expected_revision: r.revision },
    )) as Envelope | null;
    if (result) {
      setEnv(result);
      setPreview(true);
      setConfirmed(false);
    }
  }
  async function send(operation: string) {
    if (!r || !env) return;
    const result = (await execute(
      `/complaints/${c.id}/replies/${r.id}/${operation}`,
      {
        expected_case_version: c.case_version,
        expected_reply_revision: r.revision,
        idempotency_key: crypto.randomUUID(),
        confirmed,
        preview_token: env.preview_token,
      },
    )) as Envelope | null;
    if (result) {
      setEnv(result);
      setPreview(false);
    }
  }
  async function sendWithOverride() {
    if (!r) return;
    const result = (await execute(
      `/complaints/${c.id}/replies/${r.id}/send`,
      {
        expected_case_version: c.case_version,
        expected_reply_revision: r.revision,
        idempotency_key: crypto.randomUUID(),
        confirmed: true,
        preview_token: env?.preview_token,
        accept_local_over_external: true,
      },
    )) as Envelope | null;
    if (result) {
      setEnv(result);
      setPreview(false);
      setLocalError("");
    }
  }
  if (!c.current_decision_id)
    return (
      <section className="cp-composer">
        <div className="cp-safety">
          ✧ Phản hồi sẽ được chuẩn bị sau khi bạn ghi nhận quyết định.
        </div>
      </section>
    );
  return (
    <section className="cp-composer">
      <div className="cp-card-head">
        <h3>Phản hồi khách hàng</h3>
        {r && <Badge value={r.status} />}
      </div>
      <ErrorNotice message={localError} />
      {!r ? (
        <>
          <p>Chọn cách chuẩn bị phản hồi. Các thao tác này không gửi email.</p>
          <div className="cp-actions">
            <button
              className="cp-primary"
              disabled={busy}
              onClick={() => prepare("ai")}
            >
              ✧ Soạn bằng AI
            </button>
            <button
              className="cp-secondary"
              disabled={busy}
              onClick={() => prepare("manual")}
            >
              Viết thủ công
            </button>
          </div>
        </>
      ) : (
        <>
          <div className="cp-recipient">
            <span>Đến</span>
            <strong>{r.recipient_email}</strong>
            <span>Chủ đề</span>
            <strong>{r.subject}</strong>
          </div>
          {r.has_draft && (
            <div className="cp-notice" style={{background:'#eff6ff',borderColor:'#93c5fd',color:'#1e40af'}}>
              ✉️ <strong>Đã liên kết Gmail Draft:</strong> Thư nháp đã được đồng bộ với tài khoản Gmail.
            </div>
          )}
          {(localError.includes("external_draft_changed") || localError.includes("draft_requires_reconciliation")) && (
            <div className="cp-reconciliation-box">
              <strong>⚠️ Phát hiện thay đổi trên Gmail:</strong>
              <p style={{margin:"4px 0 8px 0"}}>
                Bản nháp trên Gmail đã bị thay đổi ngoài hệ thống hoặc cần đối soát trước khi gửi.
              </p>
              <button
                className="cp-primary cp-btn-sm"
                disabled={busy}
                onClick={sendWithOverride}
              >
                Dùng nội dung ClaimPilot (Ghi đè Gmail & Gửi)
              </button>
            </div>
          )}
          {r.is_stale && (
            <div className="cp-notice warning">
              Hồ sơ đã thay đổi. Đối chiếu lại nội dung với ngữ cảnh và nguồn
              hiện hành trước khi gửi.
            </div>
          )}
          <label>
            Nội dung phản hồi
            <textarea
              aria-label="Nội dung phản hồi"
              rows={8}
              value={body}
              disabled={busy}
              readOnly={r.status === "sent" || r.status === "unknown"}
              onChange={(e) => {
                setDraft(e.target.value);
                setPreview(false);
                setConfirmed(false);
              }}
              placeholder="Nhập nội dung bạn muốn gửi cho khách hàng…"
            />
          </label>
          {r.status === "sent" ? (
            <p className="cp-safety">
              ✓ Đã gửi qua Gmail. Điều này không xác nhận khách đã nhận hoặc đã
              đọc.
            </p>
          ) : r.status === "unknown" ? (
            <div className="cp-notice warning">
              Chưa xác định Gmail đã gửi hay chưa. Cần đối soát trước khi thử
              lại.
            </div>
          ) : (
            <>
              <div className="cp-actions">
                <button
                  className="cp-secondary"
                  disabled={busy || !dirty || r.is_stale || !body.trim()}
                  onClick={save}
                >
                  Lưu nội dung
                </button>
                <button
                  className="cp-primary"
                  disabled={busy || dirty || !body.trim() || r.is_stale}
                  onClick={check}
                >
                  Kiểm tra & xem trước
                </button>
                <button
                  className="cp-text"
                  disabled={busy}
                  onClick={() => setReviewing(!reviewing)}
                >
                  Đối chiếu ngữ cảnh & nguồn
                </button>
              </div>
              {reviewing && (
                <form
                  className="cp-form cp-notice"
                  onSubmit={(e) => {
                    e.preventDefault();
                    review();
                  }}
                >
                  <p>
                    Đọc lại hội thoại, quyết định, cài đặt doanh nghiệp và các
                    bài KB đã duyệt. Xác nhận dưới đây giữ nguyên nội dung, gắn
                    nguồn hiện hành và yêu cầu kiểm tra/xem trước lại. Phần đang
                    nhập vẫn được giữ để bạn lưu tiếp.
                  </p>
                  <label>
                    Ghi chú đối chiếu
                    <textarea
                      required
                      maxLength={2000}
                      value={reviewNote}
                      onChange={(e) => setReviewNote(e.target.value)}
                      rows={2}
                    />
                  </label>
                  <button
                    className="cp-secondary"
                    disabled={busy || !reviewNote.trim()}
                  >
                    Xác nhận đã đối chiếu
                  </button>
                </form>
              )}
            </>
          )}
          {env?.quality_check && (
            <div className="cp-quality">
              <div className="cp-between">
                <strong>Kiểm tra an toàn & chất lượng</strong>
                <Badge value={env.quality_check.status} />
              </div>
              {env.quality_check.findings.map((f, i) => (
                <p
                  className={
                    f.severity === "blocker" ? "cp-error-text" : "cp-muted"
                  }
                  key={i}
                >
                  {f.severity === "blocker" ? "⚠" : "ⓘ"} {f.message}
                </p>
              ))}
              {env.sources.map((s) => (
                <button
                  className="cp-source-link"
                  key={s.id}
                  onClick={() => onSource(s)}
                >
                  ↗ {s.title || "Nguồn tri thức"} · v{s.version}
                </button>
              ))}
            </div>
          )}
          {preview && (
            <div className="cp-preview">
              <span className="cp-eyebrow">NỘI DUNG CUỐI</span>
              <p>
                <strong>{r.recipient_email}</strong>
              </p>
              <h4>{r.subject}</h4>
              <div className="cp-prose">{body}</div>
              {env?.preview_token ? (
                <>
                  <label className="cp-checkbox">
                    <input
                      type="checkbox"
                      checked={confirmed}
                      onChange={(e) => setConfirmed(e.target.checked)}
                    />
                    Tôi đã kiểm tra người nhận, nội dung và nguồn; xác nhận gửi
                    phiên bản này.
                  </label>
                  {!integrations?.gmail_write_enabled && (
                    <p className="cp-muted">
                      Gửi Gmail đang tắt trên bản local. Cần cấp quyền compose
                      và bật cấu hình gửi trước khi sử dụng.
                    </p>
                  )}
                  <div className="cp-actions">
                    <button
                      className="cp-primary"
                      disabled={
                        !confirmed || busy || !integrations?.gmail_write_enabled
                      }
                      onClick={() => send("send")}
                    >
                      Gửi phản hồi
                    </button>
                    <button
                      className="cp-secondary"
                      disabled={busy || !integrations?.gmail_write_enabled}
                      onClick={() => send("draft")}
                    >
                      Lưu Gmail Draft
                    </button>
                    <button
                      className="cp-text"
                      onClick={() => setPreview(false)}
                    >
                      Tiếp tục chỉnh sửa
                    </button>
                  </div>
                </>
              ) : (
                <p className="cp-error-text">
                  Hãy xử lý các điểm cần sửa rồi kiểm tra lại.
                </p>
              )}
            </div>
          )}
        </>
      )}
    </section>
  );
}
