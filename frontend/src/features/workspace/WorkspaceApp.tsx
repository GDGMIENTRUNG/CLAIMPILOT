import {useEffect,useState} from 'react';
import {LayoutDashboard,Inbox,BookOpen,Database,Settings as SettingsIcon,Sparkles,LogOut,RefreshCw,ArrowUpRight,ShieldCheck} from 'lucide-react';
import {api,setCsrfToken} from '../../api';
import type {Session,Settings,Stats,Integrations,Order,Page,ReportsSummary} from './contracts';
import {useLoad,stamp,label,Badge,ErrorNotice} from './ui';
import InboxPanel from './InboxPanel';
import KnowledgePanel from './KnowledgePanel';
import SettingsPanel from './SettingsPanel';
import './workspace.css';

const nav=[['overview','Tổng quan',LayoutDashboard],['inbox','Hộp thư',Inbox],['knowledge','Knowledge Base',BookOpen],['data','Dữ liệu & Tích hợp',Database],['settings','Cài đặt',SettingsIcon]] as const;
export default function WorkspaceApp(){
 const [session,setSession]=useState<Session|null>(null),[checking,setChecking]=useState(true),[ever,setEver]=useState(false),[epoch,setEpoch]=useState(0);
 useEffect(()=>{api<Session>('/auth/me').then(s=>{setCsrfToken(s.csrf_token);setSession(s);setEver(true);}).catch(()=>{}).finally(()=>setChecking(false));const expired=()=>{setSession(null);setCsrfToken('');};window.addEventListener('claimpilot:expired',expired);return()=>window.removeEventListener('claimpilot:expired',expired);},[]);
 function authenticated(s:Session){setCsrfToken(s.csrf_token);setSession(s);setEver(true);}
 async function logout(){await api<void>('/auth/logout','POST');setSession(null);setCsrfToken('');setEver(false);setEpoch(x=>x+1);}
 if(checking)return <div className="cp-start"><Sparkles/><p>Đang mở workspace của bạn…</p></div>;
 return <>{ever&&<div hidden={!session}><Workspace key={epoch} username={session?.username||''} logout={logout}/></div>}{!session&&<Login onLogin={authenticated} expired={ever}/>}</>;
}
function Login({onLogin,expired}:{onLogin:(s:Session)=>void;expired:boolean}){
 const [user,setUser]=useState(''),[password,setPassword]=useState(''),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 const [demo,setDemo]=useState(false);
 useEffect(()=>{let active=true;api<{demo_login:boolean}>('/auth/config').then(c=>{if(active)setDemo(c.demo_login);}).catch(()=>{});return()=>{active=false;};},[]);
 async function submit(e:React.FormEvent){e.preventDefault();setBusy(true);setError('');try{const s=await api<Session>('/auth/login','POST',{username:user,password});setPassword('');onLogin(s);}catch(e){setError((e as Error).message);}finally{setBusy(false);}}
 return <div className="cp-login"><section className="cp-login-story"><a className="cp-brand" href="/"><span><Sparkles size={22}/></span>ClaimPilot</a><div><span className="cp-eyebrow">YOUR CUSTOMER SUPPORT COPILOT</span><h1>Chăm sóc tốt hơn.<br/><em>Từ mỗi cuộc trao đổi.</em></h1><p>Một workspace kết nối hội thoại, dữ liệu và tri thức — để bạn tập trung vào những quyết định cần con người.</p><div className="cp-login-points"><span>✧ AI có nguồn căn cứ</span><span>✓ Nhân viên kiểm soát</span><span>↗ Lịch sử minh bạch</span></div></div><small>ClaimPilot · AI-first Customer Support</small></section><section className="cp-login-form"><span className="cp-eyebrow">STAFF WORKSPACE</span><h2>{expired?'Đăng nhập lại':'Chào mừng trở lại'}</h2><p>{expired?'Phiên đã hết hạn. Đăng nhập để tiếp tục; hệ thống không tự gửi lại thao tác.':'Đăng nhập để tiếp tục xử lý và hỗ trợ khách hàng.'}</p><ErrorNotice message={error}/>{demo&&<div className="cp-notice" role="status">Đăng nhập demo local: nhập tài khoản và mật khẩu bất kỳ để vào workspace.</div>}<form onSubmit={submit} className="cp-form"><label>Tên đăng nhập<input autoComplete="username" autoFocus maxLength={100} placeholder={demo?"Tên bất kỳ, ví dụ: demo":"Tên đăng nhập"} value={user} onChange={e=>setUser(e.target.value)} required/></label><label>Mật khẩu<input type="password" autoComplete="current-password" maxLength={256} placeholder={demo?"Nhập bất kỳ":"Mật khẩu"} value={password} onChange={e=>setPassword(e.target.value)} required/></label><button className="cp-primary" disabled={busy}>{busy?'Đang đăng nhập…':'Vào workspace →'}</button></form><div className="cp-login-safe"><ShieldCheck size={18}/> Dữ liệu khách hàng chỉ dành cho nhân viên đã đăng nhập.</div></section></div>;
}
function Workspace({username,logout}:{username:string;logout:()=>Promise<void>}){
 const first=new URLSearchParams(location.search).get('tab')||'overview';
 const [tab,setTab]=useState(nav.some(([id])=>id===first)?first:'overview'),[revision,setRevision]=useState(0),[busy,setBusy]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState('');
 const status=useLoad<Integrations>('/integrations/status',revision),config=useLoad<Settings>('/settings/business',revision),stats=useLoad<Stats>('/dashboard/stats',revision);
 function changed(){setRevision(v=>v+1);}
 function navigate(id:string){setTab(id);const url=new URL(location.href);url.searchParams.set('tab',id);if(id!=='inbox')url.searchParams.delete('case');history.replaceState(null,'',url);}
 async function sync(){setBusy(true);setError('');setNotice('');try{const result=await api<{messages_added:number;failed:number;deferred:number}>('/gmail/sync','POST');setNotice(`Đã nhập ${result.messages_added} email · ${result.failed} cần kiểm tra · ${result.deferred} chờ lượt tiếp theo.`);}catch(e){setError((e as Error).message);}finally{setBusy(false);changed();}}
 return <div className="cp-app"><aside className="cp-sidebar"><a className="cp-brand" href="/?tab=overview"><span><Sparkles size={21}/></span>ClaimPilot<span className="cp-beta">AI</span></a><div className="cp-business"><span className="cp-business-icon">{(config.data?.display_name||'W').slice(0,1)}</span><div><strong>{config.data?.display_name||'Workspace của bạn'}</strong><small>Một đội ngũ · Một hộp thư</small></div></div><p className="cp-nav-caption">KHÔNG GIAN LÀM VIỆC</p><nav aria-label="Điều hướng chính">{nav.map(([id,title,Icon])=><button key={id} aria-label={title} aria-current={tab===id?'page':undefined} className={tab===id?'active':''} onClick={()=>navigate(id)}><Icon size={19}/><span>{title}</span>{id==='inbox'?(<span style={{display:'inline-flex',alignItems:'center',gap:4,marginLeft:'auto'}}>{!!stats.data?.urgent_count&&<span className="cp-badge-urgent" title="Ca cần can thiệp khẩn">🚨 {stats.data.urgent_count}</span>}{!!stats.data?.total&&<small>{stats.data.total}</small>}</span>):null}</button>)}</nav><div className="cp-sidebar-bottom"><div className="cp-sidebar-note"><ShieldCheck size={20}/><strong>AI hỗ trợ. Bạn quyết định.</strong><p>Mọi phản hồi đều cần nhân viên kiểm tra trước khi gửi.</p></div><div className="cp-profile"><span className="cp-avatar">{username.slice(0,1).toUpperCase()}</span><div><strong>{username}</strong><small>Nhân viên hỗ trợ</small></div><button aria-label="Đăng xuất" onClick={()=>logout().catch(e=>setError(e.message))}><LogOut size={18}/></button></div></div></aside>
 <div className="cp-main"><header className="cp-topbar"><div><span className="cp-dot"/>Workspace <span className="cp-breadcrumb">/</span><strong>{nav.find(([id])=>id===tab)?.[1]}</strong></div><div className="cp-topbar-right"><span className="cp-env">LOCAL WORKSPACE</span><button className="cp-secondary" disabled={busy} onClick={sync}><RefreshCw size={15} className={busy?'cp-spin':''}/>{busy?'Đang đồng bộ…':'Đồng bộ Gmail'}</button></div></header><main className="cp-content"><ErrorNotice message={error}/>{notice&&<div className="cp-notice" role="status">{notice}</div>}
 {!config.data&&!config.loading&&<div className="cp-setup-banner"><span>✧ Thiết lập thông tin doanh nghiệp để các agent sử dụng đúng ngữ cảnh.</span><button onClick={()=>navigate('settings')}>Thiết lập ngay →</button></div>}
 <div hidden={tab!=='overview'}><Overview stats={stats.data} error={stats.error} status={status.data} navigate={navigate}/></div>
 <div hidden={tab!=='inbox'}><InboxPanel revision={revision} onChanged={changed} integrations={status.data}/></div>
 <div hidden={tab!=='knowledge'}><KnowledgePanel/></div>
 <div hidden={tab!=='data'}><DataPanel revision={revision} status={status.data} statusError={status.error}/></div>
 <div hidden={tab!=='settings'}><SettingsPanel onChanged={changed}/></div>
 </main><footer className="cp-footer">ClaimPilot <span>AI-first Customer Support · Nhân viên xác nhận mọi email gửi đi</span></footer></div></div>;
}
function Overview({stats,error,status,navigate}:{stats:Stats|null;error:string;status:Integrations|null;navigate:(s:string)=>void}){
 const reports = useLoad<ReportsSummary>('/reports/summary');
 return <><div className="cp-welcome"><span className="cp-eyebrow">MỘT NGÀY HỖ TRỢ HIỆU QUẢ HƠN</span><div className="cp-between"><div><h1>Mọi cuộc trao đổi.<br/><em>Một góc nhìn rõ ràng.</em></h1><p>Nhìn thấy điều cần làm, hiểu rõ căn cứ và chủ động bước tiếp theo.</p></div><div className="cp-welcome-art"><div className="cp-orbit"><Sparkles size={35}/></div><div className="cp-art-label">Human + AI</div></div></div></div><ErrorNotice message={error}/><div className="cp-metrics">{[['Tổng hồ sơ',stats?.total,'Tất cả khiếu nại'],['Cần xem xét',stats?.workflow_counts.needs_review,'Ưu tiên bước tiếp theo'],['Chờ khách',stats?.workflow_counts.waiting_customer,'Đang chờ thông tin'],['Đã giải quyết',stats?.workflow_counts.resolved,'Chờ đóng hồ sơ']].map(([title,value,hint])=><div className="cp-metric" key={String(title)}><span>{title}</span><strong>{value??'—'}</strong><small>{hint}</small></div>)}</div>

<section className="cp-card" style={{marginTop:16}}>
  <div className="cp-card-head">
    <h2>Phân cấp Cảnh báo & Rủi ro (Human Escalation)</h2>
    <button className="cp-text" onClick={()=>{
      const url=new URL(location.href);
      url.searchParams.set('tab','inbox');
      url.searchParams.set('queue','urgent');
      history.replaceState(null,'',url);
      navigate('inbox');
    }}>Xem ca khẩn cấp 🚨 <ArrowUpRight size={15}/></button>
  </div>
  <div className="cp-reports-grid">
    <div className="cp-reports-card" style={{borderLeft:'4px solid #ef4444'}}>
      <span>🔴 Khẩn cấp (Critical)</span>
      <strong>{reports.data?.severity_counts?.critical ?? stats?.severity_counts?.critical ?? 0}</strong>
      <small>Dừng tự động, báo động khẩn</small>
    </div>
    <div className="cp-reports-card" style={{borderLeft:'4px solid #f97316'}}>
      <span>🟠 Rủi ro cao (High)</span>
      <strong>{reports.data?.severity_counts?.high ?? stats?.severity_counts?.high ?? 0}</strong>
      <small>Khóa auto-send, chỉ tạo Draft</small>
    </div>
    <div className="cp-reports-card" style={{borderLeft:'4px solid #eab308'}}>
      <span>🟡 Cần xem xét (Medium)</span>
      <strong>{reports.data?.severity_counts?.medium ?? stats?.severity_counts?.medium ?? 0}</strong>
      <small>Soạn draft, chờ xác nhận</small>
    </div>
    <div className="cp-reports-card" style={{borderLeft:'4px solid #22c55e'}}>
      <span>🟢 An toàn (Low)</span>
      <strong>{reports.data?.severity_counts?.low ?? stats?.severity_counts?.low ?? 0}</strong>
      <small>Đủ điều kiện Auto-Reply</small>
    </div>
  </div>
  <div style={{display:'flex',gap:16,marginTop:14,flexWrap:'wrap',fontSize:12,color:'#475569'}}>
    <div>Tỷ lệ cần can thiệp: <strong>{reports.data?.escalation_rate ?? 0}%</strong></div>
    <div>Tỷ lệ giải quyết tự động: <strong>{reports.data?.automation_rate ?? 0}%</strong></div>
    <div>Đã tiếp quản bởi nhân viên: <strong>{reports.data?.taken_over_count ?? 0} ca</strong></div>
  </div>
  {reports.data?.top_escalation_triggers && reports.data.top_escalation_triggers.length > 0 && (
    <div style={{marginTop:12,paddingTop:10,borderTop:'1px dashed #e2e8f0',fontSize:12}}>
      <strong>Nguyên nhân cảnh báo hàng đầu: </strong>
      {reports.data.top_escalation_triggers.map(t=>(
        <span key={t.code} style={{marginRight:10,display:'inline-block',background:'#f1f5f9',padding:'2px 8px',borderRadius:4}}>
          {label(t.code)} ({t.count})
        </span>
      ))}
    </div>
  )}
</section>

<div className="cp-overview-grid"><section className="cp-card"><div className="cp-card-head"><h2>Công việc cần chú ý</h2><button className="cp-text" onClick={()=>navigate('inbox')}>Mở hộp thư <ArrowUpRight size={15}/></button></div>{[['needs_review','Hồ sơ chờ quyết định'],['waiting_customer','Khách cần bổ sung thông tin'],['waiting_fulfillment','Phương án chờ thực hiện'],['closed','Hồ sơ đã đóng']].map(([s,text])=><button className="cp-queue-row" key={s} onClick={()=>navigate('inbox')}><span className="cp-queue-icon"><Inbox size={17}/></span><span>{text}</span><strong>{stats?.workflow_counts[s]??'—'}</strong><ArrowUpRight size={16}/></button>)}</section><section className="cp-card"><div className="cp-card-head"><h2>Trạng thái xử lý</h2><span className="cp-tag">Agent workspace</span></div><div className="cp-agent-summary"><div><strong>{stats?.agent_counts.running??'—'}</strong><span>Đang chạy</span></div><div><strong>{stats?.agent_counts.waiting_data??'—'}</strong><span>Chờ dữ liệu</span></div><div><strong>{stats?.agent_counts.failed??'—'}</strong><span>Cần kiểm tra</span></div></div><p className="cp-muted">Agent giúp phân tích và chuẩn bị nội dung. Hồ sơ có lỗi vẫn có thể được kiểm tra thủ công.</p><div className="cp-sync-summary"><span className="cp-dot"/><div><strong>Đồng bộ Gmail</strong><small>Thành công gần nhất: {stamp(status?.last_success_at)}</small><small>{status?.deferred_count??'—'} mục chờ lượt tiếp theo</small></div></div></section></div><section className="cp-bottom-card"><BookOpen size={28}/><div><h3>Phản hồi tốt bắt đầu từ tri thức tốt.</h3><p>Thêm chính sách đã duyệt để agent đưa ra câu trả lời có nguồn căn cứ.</p></div><button className="cp-secondary" onClick={()=>navigate('knowledge')}>Mở Knowledge Base →</button></section></>;
}
function DataPanel({revision,status,statusError}:{revision:number;status:Integrations|null;statusError:string}){
 const orders=useLoad<Page<Order>>('/orders',revision),policies=useLoad<{items:{version:string;label:string;rules_summary:string[];source_status:string}[]}>('/policies',revision);
 const failures=useLoad<Page<{gmail_message_id:string;error_code:string;status:string}>>('/integrations/intake-failures?status=pending',revision);
 return <><div className="cp-section-intro"><span className="cp-eyebrow">YOUR CONNECTED CONTEXT</span><h1>Dữ liệu & Tích hợp</h1><p>Hiểu rõ dữ liệu agent dựa vào và tình trạng kết nối hiện tại.</p></div><ErrorNotice message={statusError}/><section className="cp-card"><div className="cp-card-head"><h2>Gmail & AI</h2><span className="cp-tag">Cấu hình ≠ kết nối đã kiểm</span></div><div className="cp-integration-grid"><div><h3>Gmail</h3><p>{status?.gmail_configured?'Đã có token OAuth':'Cần cấp quyền đọc Gmail'}</p><small>Thử gần nhất: {stamp(status?.last_attempt_at)}</small><small>Thành công: {stamp(status?.last_success_at)}</small>{status?.last_error_code&&<p className="cp-error-text">{label(status.last_error_code)}</p>}</div><div><h3>AI text</h3><p>{status?.ai_configured?'Đã có cấu hình key':'Chưa có API key khả dụng'}</p><small>Provider: {status?.ai_provider??'Chưa biết'}</small><small>Model: {status?.ai_model??'Chưa biết'}</small></div><div><h3>Gửi phản hồi</h3><p>{status?.gmail_write_enabled?'Đã bật tính năng gửi có xác nhận':'Đang tắt trên local'}</p><small>Cần OAuth compose và nhân viên xác nhận nội dung cuối.</small></div></div></section><section className="cp-card"><div className="cp-card-head"><h2>Dữ liệu đơn hàng</h2><span>{orders.data?.total??'—'} bản ghi</span></div><ErrorNotice message={orders.error}/><div className="cp-table-scroll"><table><thead><tr><th>Mã đơn</th><th>Sản phẩm</th><th>Trạng thái</th><th>Giao dự kiến</th><th>Tổng tiền</th></tr></thead><tbody>{orders.data?.items.map(o=><tr key={o.id}><td><strong>{o.order_id}</strong></td><td>{o.product_name||'Chưa có dữ liệu'}</td><td>{o.order_status}</td><td>{o.expected_delivery_date||'Chưa biết'}</td><td>{o.total_amount?Number(o.total_amount).toLocaleString('vi-VN')+' đ':'Chưa biết'}</td></tr>)}</tbody></table></div></section><section className="cp-card"><h2>Chính sách đang áp dụng</h2><ErrorNotice message={policies.error}/>{policies.data?.items.map(p=><div key={p.version}><Badge value={p.source_status}/><h3>{p.label} · {p.version}</h3><ul>{p.rules_summary.map(r=><li key={r}>{r}</li>)}</ul></div>)}</section><section className="cp-card"><h2>Lỗi tiếp nhận email</h2><ErrorNotice message={failures.error}/>{failures.data?.items.length?failures.data.items.map(f=><p key={f.gmail_message_id}><code>{f.gmail_message_id}</code> · {label(f.error_code)}</p>):<p className="cp-muted">Chưa có lỗi tiếp nhận được ghi nhận.</p>}</section></>;
}
