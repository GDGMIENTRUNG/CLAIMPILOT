import { useState } from "react";
import { api } from "../../api";
import type { Knowledge, Page } from "./contracts";
import { useLoad, Badge, stamp, ErrorNotice, Empty } from "./ui";

interface ArticleHistory {
  revisions: Knowledge[];
  events: {
    event_id: string;
    action: string;
    actor: string;
    at: string;
    note: string;
  }[];
}
const historyLabels: Record<string,string> = {created:'Tạo bài viết',revision_created:'Tạo phiên bản',draft_edited:'Sửa bản nháp',submit:'Gửi duyệt',approve:'Duyệt & xuất bản',archive:'Lưu trữ',conflict:'Cập nhật mâu thuẫn'};
function localTime(value: string | null) {
  if (!value) return "";
  const d = new Date(value);
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 16);
}
function eligibility(r: Knowledge) {
  return r.has_conflict
    ? "⚠ Mâu thuẫn"
    : r.valid_until && new Date(r.valid_until) <= new Date()
      ? "⚠ Hết hiệu lực"
      : r.review_due_at && new Date(r.review_due_at) <= new Date()
        ? "⚠ Đến hạn rà soát"
        : "";
}

export default function KnowledgePanel() {
  const [q, setQ] = useState(""),
    [filter, setFilter] = useState(""),
    [chosen, setChosen] = useState<Knowledge | null>(null),
    [creating, setCreating] = useState(false),
    [title, setTitle] = useState(""),
    [body, setBody] = useState(""),
    [topic, setTopic] = useState(""),
    [source, setSource] = useState(""),
    [reference, setReference] = useState(""),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [success, setSuccess] = useState(""),
    [dirty, setDirty] = useState(false);
  const [validUntil, setValidUntil] = useState(""),
    [reviewDue, setReviewDue] = useState(""),
    [history, setHistory] = useState<ArticleHistory | null>(null),
    [topicFilter, setTopicFilter] = useState(""),
    [page, setPage] = useState(1);
  const list = useLoad<Page<Knowledge>>(
    `/knowledge?q=${encodeURIComponent(q)}&status=${filter}&topic=${encodeURIComponent(topicFilter)}&page=${page}`,
  );
  function open(r: Knowledge | null) {
    if (
      dirty &&
      !window.confirm("Bạn có muốn bỏ nội dung chưa lưu để mở bài khác?")
    )
      return;
    setChosen(r);
    setCreating(!r);
    setTitle(r?.title ?? "");
    setBody(r?.body ?? "");
    setTopic(r?.topic ?? "");
    setSource(r?.source_label ?? "");
    setReference(r?.source_reference ?? "");
    setValidUntil(localTime(r?.valid_until ?? null));
    setReviewDue(localTime(r?.review_due_at ?? null));
    setHistory(null);
    setError("");
    setSuccess("");
    setDirty(false);
  }
  async function save() {
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const data = {
        title,
        body,
        topic,
        source_label: source,
        source_reference: reference || null,
        valid_until: validUntil ? new Date(validUntil).toISOString() : null,
        review_due_at: reviewDue ? new Date(reviewDue).toISOString() : null,
      };
      let result: Knowledge;
      if (!chosen) {
        const v = await api<{ revision: Knowledge }>(
          "/knowledge",
          "POST",
          data,
        );
        result = v.revision;
      } else if (chosen.status === "draft")
        result = await api<Knowledge>(
          `/knowledge/${chosen.article_id}/revisions/${chosen.id}`,
          "PATCH",
          { ...data, expected_updated_at: chosen.updated_at },
        );
      else {
        const v = await api<{ revision: Knowledge }>(
          `/knowledge/${chosen.article_id}/revisions`,
          "POST",
          { ...data, expected_revision: chosen.revision },
        );
        result = v.revision;
      }
      setChosen(result);
      setCreating(false);
      setDirty(false);
      setHistory(null);
      setSuccess(
        "Đã lưu bản nháp. Bài viết chỉ được agent sử dụng sau khi được duyệt.",
      );
      list.reload();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function transition(action: string) {
    if (!chosen) return;
    setBusy(true);
    setError("");
    try {
      const note =
        action === "conflict"
          ? window.prompt("Lý do đánh dấu/bỏ đánh dấu mâu thuẫn?")
          : "Nhân viên kiểm tra nội dung";
      if (!note) {
        setBusy(false);
        return;
      }
      const result = await api<Knowledge>(
        `/knowledge/${chosen.article_id}/revisions/${chosen.id}/${action}`,
        "POST",
        {
          expected_updated_at: chosen.updated_at,
          note,
          ...(action === "conflict"
            ? { has_conflict: !chosen.has_conflict }
            : {}),
        },
      );
      setChosen(result);
      setHistory(null);
      setSuccess("Đã cập nhật trạng thái bài viết.");
      list.reload();
      window.dispatchEvent(new Event("claimpilot:settings-changed"));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function loadHistory() {
    if (!chosen) return;
    setBusy(true);
    setError("");
    try {
      setHistory(await api<ArticleHistory>(`/knowledge/${chosen.article_id}`));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <div className="cp-section-intro cp-between">
        <div>
          <span className="cp-eyebrow">APPROVED KNOWLEDGE</span>
          <h1>Tri thức doanh nghiệp</h1>
          <p>Để mỗi phản hồi đều có một nguồn đáng tin cậy.</p>
        </div>
        <button className="cp-primary" onClick={() => open(null)}>
          ＋ Tạo bài viết
        </button>
      </div>
      <div className="cp-knowledge-layout">
        <section className="cp-card">
          <div className="cp-toolbar">
            <input
              aria-label="Tìm tri thức"
              placeholder="Tìm trong tri thức…"
              value={q}
              onChange={(e) => {
                setQ(e.target.value);
                setPage(1);
              }}
            />
            <select
              aria-label="Trạng thái bài viết"
              value={filter}
              onChange={(e) => {
                setFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Tất cả trạng thái</option>
              {["draft", "pending_review", "approved", "archived"].map((x) => (
                <option value={x} key={x}>
                  {x === "draft"
                    ? "Bản nháp"
                    : x === "pending_review"
                      ? "Chờ duyệt"
                      : x === "approved"
                        ? "Đã duyệt"
                        : "Đã lưu trữ"}
                </option>
              ))}
            </select>
          </div>
          <label>
            Lọc chủ đề
            <input
              value={topicFilter}
              onChange={(e) => {
                setTopicFilter(e.target.value);
                setPage(1);
              }}
              placeholder="Ví dụ: giao hàng"
            />
          </label>
          <ErrorNotice message={list.error} />
          {list.loading ? (
            <p role="status">Đang tải…</p>
          ) : list.data?.items.length ? (
            list.data.items.map((r) => (
              <button
                className={`cp-article ${chosen?.id === r.id ? "selected" : ""}`}
                key={r.id}
                onClick={() => open(r)}
              >
                <Badge value={r.status} />
                <strong>{r.title}</strong>
                <span>
                  {r.topic} · v{r.revision}
                </span>
                <small>
                  {stamp(r.updated_at)}
                  {eligibility(r) ? " · " + eligibility(r) : ""}
                </small>
              </button>
            ))
          ) : (
            <Empty title="Chưa có bài viết phù hợp">
              <p>
                Thêm chính sách hoặc hướng dẫn đã kiểm chứng của doanh nghiệp.
              </p>
            </Empty>
          )}
          <div className="cp-pagination">
            <button
              aria-label="Trang tri thức trước"
              disabled={page === 1}
              onClick={() => setPage((p) => p - 1)}
            >
              ←
            </button>
            <span>
              Trang {page} · {list.data?.total ?? 0} phiên bản
            </span>
            <button
              aria-label="Trang tri thức sau"
              disabled={!list.data || page * 20 >= list.data.total}
              onClick={() => setPage((p) => p + 1)}
            >
              →
            </button>
          </div>
        </section>
        <section className="cp-card">
          {chosen || creating ? (
            <>
              <div className="cp-card-head">
                <h2>
                  {chosen ? "Phiên bản " + chosen.revision : "Bài viết mới"}
                </h2>
                {chosen && <Badge value={chosen.status} />}
              </div>
              <ErrorNotice message={error} />
              {success && (
                <div className="cp-notice" role="status">
                  {success}
                </div>
              )}
              {chosen && eligibility(chosen) && (
                <div className="cp-notice warning">
                  {eligibility(chosen)}
                  {chosen.conflict_note ? ": " + chosen.conflict_note : ""}.
                  Agent không dùng phiên bản này làm căn cứ mới.
                </div>
              )}
              <form
                className="cp-form"
                onSubmit={(e) => {
                  e.preventDefault();
                  save();
                }}
              >
                <label>
                  Tiêu đề
                  <input
                    value={title}
                    onChange={(e) => {
                      setTitle(e.target.value);
                      setDirty(true);
                    }}
                    maxLength={300}
                    required
                  />
                </label>
                <div className="cp-form-row">
                  <label>
                    Chủ đề
                    <input
                      value={topic}
                      onChange={(e) => {
                        setTopic(e.target.value);
                        setDirty(true);
                      }}
                      required
                    />
                  </label>
                  <label>
                    Nguồn nội dung
                    <input
                      value={source}
                      onChange={(e) => {
                        setSource(e.target.value);
                        setDirty(true);
                      }}
                      placeholder="Ví dụ: chính sách doanh nghiệp"
                      required
                    />
                  </label>
                </div>
                <label>
                  Tham chiếu nguồn
                  <input
                    value={reference}
                    onChange={(e) => {
                      setReference(e.target.value);
                      setDirty(true);
                    }}
                    placeholder="Tên tài liệu hoặc URL tham khảo; hệ thống không tự truy cập"
                  />
                </label>
                <div className="cp-form-row">
                  <label>
                    Hết hiệu lực lúc
                    <input
                      type="datetime-local"
                      value={validUntil}
                      onChange={(e) => {
                        setValidUntil(e.target.value);
                        setDirty(true);
                      }}
                    />
                  </label>
                  <label>
                    Hạn rà soát
                    <input
                      type="datetime-local"
                      value={reviewDue}
                      onChange={(e) => {
                        setReviewDue(e.target.value);
                        setDirty(true);
                      }}
                    />
                  </label>
                </div>
                <p className="cp-muted">
                  Thời gian theo múi giờ trình duyệt. Để trống nếu chưa có hạn;
                  nguồn hết hạn hoặc quá hạn rà soát sẽ bị loại khỏi tra cứu.
                </p>
                <label>
                  Nội dung
                  <textarea
                    rows={13}
                    value={body}
                    onChange={(e) => {
                      setBody(e.target.value);
                      setDirty(true);
                    }}
                    maxLength={50000}
                    required
                  />
                </label>
                <button className="cp-primary" disabled={busy}>
                  {busy
                    ? "Đang lưu…"
                    : chosen && chosen.status !== "draft"
                      ? "Tạo phiên bản nháp mới"
                      : "Lưu bản nháp"}
                </button>
              </form>
              {chosen && (
                <div className="cp-actions">
                  {chosen.status === "draft" && (
                    <button
                      className="cp-secondary"
                      disabled={busy || dirty}
                      onClick={() => transition("submit")}
                    >
                      Gửi duyệt
                    </button>
                  )}
                  {chosen.status === "pending_review" && (
                    <button
                      className="cp-primary"
                      disabled={busy || dirty}
                      onClick={() => transition("approve")}
                    >
                      Duyệt & xuất bản
                    </button>
                  )}
                  {chosen.status !== "archived" && (
                    <button
                      className="cp-secondary"
                      disabled={busy || dirty}
                      onClick={() => transition("archive")}
                    >
                      Lưu trữ
                    </button>
                  )}
                  <button
                    className="cp-text"
                    disabled={busy || dirty}
                    onClick={() => transition("conflict")}
                  >
                    {chosen.has_conflict
                      ? "Bỏ đánh dấu mâu thuẫn"
                      : "Đánh dấu mâu thuẫn"}
                  </button>
                  <button
                    className="cp-text"
                    disabled={busy}
                    onClick={loadHistory}
                  >
                    Xem lịch sử phiên bản
                  </button>
                </div>
              )}
              {history && (
                <section aria-label="Lịch sử tri thức">
                  <h3>Các phiên bản</h3>
                  <div className="cp-actions">
                    {history.revisions.map((r) => (
                      <button
                        className="cp-secondary"
                        key={r.id}
                        onClick={() => open(r)}
                      >
                        v{r.revision} · {r.title}
                      </button>
                    ))}
                  </div>
                  <h3>Lịch sử duyệt & thay đổi</h3>
                  {history.events.map((e) => (
                    <div className="cp-timeline-item" key={e.event_id}>
                      <strong>{historyLabels[e.action]??e.action}</strong>
                      <p>{e.note}</p>
                      <small>
                        {e.actor} · {stamp(e.at)}
                      </small>
                    </div>
                  ))}
                </section>
              )}
              <p className="cp-muted">
                Chỉnh bài đã duyệt sẽ tạo phiên bản mới. Các nguồn đã dùng trong
                lịch sử vẫn được giữ.
              </p>
            </>
          ) : (
            <Empty title="Không gian tri thức của bạn">
              <p>Chọn một bài viết hoặc tạo nội dung mới để bắt đầu.</p>
            </Empty>
          )}
        </section>
      </div>
    </>
  );
}
