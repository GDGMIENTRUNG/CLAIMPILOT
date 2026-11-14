import { useEffect,useState } from 'react';
import { api,ApiError } from '../../api';
import type { Settings } from './contracts';
import { ErrorNotice } from './ui';

export default function SettingsPanel({onChanged}:{onChanged:()=>void}){
 const [config,setConfig]=useState<Settings|null>(null),[name,setName]=useState(''),[language,setLanguage]=useState('vi'),[tone,setTone]=useState('neutral'),[optional,setOptional]=useState(true),[threshold,setThreshold]=useState(''),[note,setNote]=useState(''),[error,setError]=useState(''),[notice,setNotice]=useState(''),[saving,setSaving]=useState(false),[loading,setLoading]=useState(true);
 useEffect(()=>{api<Settings>('/settings/business').then(c=>{setConfig(c);setName(c.display_name);setLanguage(c.language);setTone(c.tone);setOptional(c.optional_roles.includes('evidence_analysis'));setThreshold(c.review_threshold??'');}).catch(e=>{if(!(e instanceof ApiError&&e.code==='config_unavailable'))setError(e.message);}).finally(()=>setLoading(false));},[]);
 async function save(kind:'business'|'agents'){
  setSaving(true);setError('');setNotice('');try{
   const data=kind==='business'?{expected_revision:config?.revision??0,display_name:name,language,tone,note}:{expected_revision:config?.revision??0,optional_roles:optional?['evidence_analysis']:[],review_threshold:threshold===''?null:Number(threshold),note};
   const c=await api<Settings>(`/settings/${kind}`,'PATCH',data);setConfig(c);setNotice(`Đã lưu cấu hình phiên bản ${c.revision}. Nội dung cũ được giữ nguyên.`);setNote('');window.dispatchEvent(new Event('claimpilot:settings-changed'));onChanged();
  }catch(e){setError((e as Error).message);}finally{setSaving(false);}
 }
 if(loading)return <p role="status">Đang tải cài đặt…</p>;
 return <div className="cp-settings"><div className="cp-section-intro"><span className="cp-eyebrow">WORKSPACE SETTINGS</span><h1>Cài đặt doanh nghiệp</h1><p>Cá nhân hóa phản hồi và cách các agent hỗ trợ đội ngũ của bạn.</p></div><ErrorNotice message={error}/>{notice&&<div className="cp-notice" role="status">{notice}</div>}
 <section className="cp-card"><div className="cp-card-head"><h2>Thông tin doanh nghiệp</h2><span>Phiên bản {config?.revision??'chưa thiết lập'}</span></div>
 {!config&&<div className="cp-notice">Thiết lập doanh nghiệp để bắt đầu các lượt phân tích và soạn phản hồi có ngữ cảnh.</div>}
 <form onSubmit={e=>{e.preventDefault();save('business');}} className="cp-form"><label>Tên doanh nghiệp<input value={name} onChange={e=>setName(e.target.value)} required maxLength={200} placeholder="Nhập tên doanh nghiệp của bạn"/></label><div className="cp-form-row"><label>Ngôn ngữ<select value={language} onChange={e=>setLanguage(e.target.value)}><option value="vi">Tiếng Việt</option><option value="en">English</option></select></label><label>Giọng điệu<select value={tone} onChange={e=>setTone(e.target.value)}><option value="neutral">Trung tính, rõ ràng</option><option value="friendly">Thân thiện</option><option value="formal">Trang trọng</option></select></label></div><label>Lý do cập nhật<input value={note} onChange={e=>setNote(e.target.value)} required maxLength={2000}/></label><button className="cp-primary" disabled={saving}>Lưu thông tin doanh nghiệp</button></form></section>
 <section className="cp-card"><div className="cp-card-head"><h2>Cấu hình agent</h2><span>Cần thiết lập doanh nghiệp trước</span></div><label className="cp-checkbox"><input type="checkbox" checked={optional} onChange={e=>setOptional(e.target.checked)}/>Bật vai trò phân tích bằng chứng khi có dữ liệu</label><label>Ngưỡng chuyển xem xét (0–1, có thể để trống)<input type="number" min="0" max="1" step=".01" value={threshold} onChange={e=>setThreshold(e.target.value)}/></label><p className="cp-muted">Không có độ tin cậy đã kiểm chứng sẽ được chuyển xem xét. Cấu hình này không thay thế quyết định của nhân viên.</p><p className="cp-safety">✓ Xác thực · Nguồn được phép · Kiểm tra an toàn · Nhân viên xác nhận gửi luôn được bật.</p><button className="cp-secondary" disabled={!config||saving||!note.trim()} onClick={()=>save('agents')}>Lưu cấu hình agent</button></section></div>;
}
