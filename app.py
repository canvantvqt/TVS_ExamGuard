# TVS - ExamGuard AI — Demo 1.1
"""Streamlit dashboard: prerecorded simulated video and preserved H14/H15 audit data."""
from pathlib import Path
import base64
import csv
import html
import io
import statistics
import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent
CSV = ROOT / 'H15_event_audit.csv'
VIDEO_CHOICES = ('V15_8s_alert_v2_web.mp4','V15_8s_alert_web.mp4')
VIDEO = next((ROOT / name for name in VIDEO_CHOICES if (ROOT / name).is_file()), None)
EVIDENCE = ROOT / 'evidence'

st.set_page_config(page_title='TVS | ExamGuard AI — Demo 1.1',page_icon='📹',layout='wide',initial_sidebar_state='collapsed')
st.markdown('''<style>
.stApp{background:#f3f7fc;color:#172d49}.block-container{max-width:1470px;padding-top:1.3rem}
[data-testid="stHeader"]{background:transparent}
.brand{display:flex;align-items:center;gap:14px;padding:12px 0 18px;border-bottom:1px solid #dce5f0;margin-bottom:18px}
.logo{display:grid;place-items:center;width:52px;height:52px;border-radius:15px;background:#172d49;color:#fff;font-size:28px}
.brand h1{font-size:29px!important;line-height:1.2!important;margin:0!important;color:#172d49!important}
.brand p{font-size:13px;color:#64748b;margin:5px 0 0}
.note{border:1px solid #cbd9e9;background:white;border-radius:12px;padding:12px 16px;color:#435b76;font-size:13px;margin:8px 0 15px}
div[data-testid="stTabs"] button{font-weight:700}
</style>''',unsafe_allow_html=True)
st.markdown('''<div class="brand"><div class="logo">📹</div><div><h1>TVS – ExamGuard AI | Demo 1.1</h1><p>THỊ GIÁC MÁY TÍNH · PHÂN TÍCH VIDEO · CẢNH BÁO HỖ TRỢ BÁO GIÁM THỊ GIÁM SÁT PHÒNG THI (PHÒNG HỌC) </p></div></div>''',unsafe_allow_html=True)

if not CSV.exists():
    st.error('Thiếu H15_event_audit.csv.');st.stop()
with CSV.open(encoding='utf-8-sig',newline='') as f:
    raw=list(csv.DictReader(f))
if not raw:
    st.error('CSV H.15 không có dữ liệu.');st.stop()

def summarize(rows):
    grouped={}
    for r in rows:
        grouped.setdefault((r['seat_id'],r['h14_event_time_s'],r['h14_event_type']),[]).append(r)
    out=[]
    for (seat,t,_),rr in grouped.items():
        out.append({'Vị trí':seat,'Thời điểm (s)':float(t),'Số mẫu H.15':len(rr),
                    'ROI trung vị':round(statistics.median(float(x['roi_mean_absdiff_0to1']) for x in rr),3),
                    'Tỷ lệ quỹ đạo ra ngoài':round(float(rr[0]['h14_outward_fraction']),3),
                    'Nhãn H.15':rr[0]['review_label'],
                    'Vai trò':'Tình huống minh họa' if seat=='G06' else 'Tín hiệu phụ cần rà soát'})
    return sorted(out,key=lambda x:x['Thời điểm (s)'])
events=summarize(raw)

def to_csv(rows):
    output=io.StringIO()
    writer=csv.DictWriter(output,fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode('utf-8-sig')

tab_demo, tab_research = st.tabs(['🎬 TRÌNH DIỄN','🔬 DỮ LIỆU NGHIÊN CỨU'])
with tab_demo:
    if VIDEO:
        encoded=base64.b64encode(VIDEO.read_bytes()).decode('ascii')
        # The media is embedded for compatibility with Streamlit Community Cloud iframe hosting.
        page=r'''<!doctype html><html lang="vi"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<style>
:root{font-family:Inter,system-ui,Arial,sans-serif;color:#172d49}*{box-sizing:border-box}body{margin:0;background:#f3f7fc}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:17px}.stat{border:1px solid #dbe5f1;background:#fff;border-radius:15px;padding:16px 20px;box-shadow:0 4px 15px #1c385408}.stat label{display:block;font-size:13px;color:#61748b}.stat strong{display:block;font-size:31px;letter-spacing:-.6px;margin-top:7px}.stat.active{background:#fff0f0;border-color:#f5a4a8}.stat.active strong{color:#b91c1c}
.layout{display:grid;grid-template-columns:minmax(0,1.65fr) minmax(290px,1fr);gap:16px}.panel{border:1px solid #dbe5f1;background:#fff;border-radius:16px;padding:16px;box-shadow:0 5px 20px #1c385407}.heading{font-weight:850;font-size:16px;display:flex;align-items:center;gap:8px;margin-bottom:13px}.pill{font-size:10px;font-weight:800;color:#5b7088;background:#edf3fa;padding:6px 8px;border-radius:8px;margin-left:auto}
video{display:block;width:100%;border-radius:10px;background:#09131f;aspect-ratio:16/9}.timeline{display:flex;justify-content:space-between;align-items:center;margin:13px 0 6px;font-size:12px;color:#516a85}.timeline b{font-size:14px;color:#173b5e}.help{font-size:12px;line-height:1.6;color:#72839a;margin-top:10px}
.status{border-radius:12px;padding:17px;font-weight:700;font-size:15px;line-height:1.5}.ready{background:#e8f7ef;color:#176644;border:1px solid #c3e8d2}.playing{background:#e8f2ff;color:#20598e;border:1px solid #c4daf5}.alert{background:linear-gradient(145deg,#a10d1c,#e12e38);border:3px solid #ffcc66;color:white;box-shadow:0 12px 35px #c4213330}.alert h2{font-size:clamp(21px,2.7vw,34px);line-height:1.16;margin:0 0 15px;font-weight:950}.alert p{font-size:clamp(17px,1.9vw,24px);font-weight:850;line-height:1.45;margin:0}.alert small{display:block;font-size:12px;line-height:1.6;margin-top:16px;color:#ffe3e5}.seatmap{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:14px}.seat{background:#f7faff;border:1px solid #d8e3f0;border-radius:9px;text-align:center;padding:12px 2px;font-size:12px;font-weight:800}.seat.g06{border:2px solid #f0a245;background:#fff7e8}.seat.g06.active{background:#b91c1c;border-color:#b91c1c;color:white}
.muted{color:#72839a;font-size:12px;line-height:1.55;margin-top:14px}.footer{border-top:1px solid #e5ecf5;margin-top:15px;padding-top:12px;font-size:12px;color:#657a90}
[hidden]{display:none!important}@media(max-width:780px){.layout{grid-template-columns:1fr}.stats{gap:7px}.stat{padding:12px}.stat strong{font-size:25px}.stat label{font-size:11px}}
</style></head><body>
<div class="stats"><div class="stat"><label>VỊ TRÍ MÔ PHỎNG</label><strong>16</strong></div><div class="stat" id="m1"><label>TÌNH HUỐNG ĐÃ XUẤT HIỆN</label><strong id="count">00</strong></div><div class="stat" id="m2"><label>VỊ TRÍ CẦN RÀ SOÁT</label><strong id="seat">—</strong></div></div>
<div class="layout"><section class="panel"><div class="heading">📹 CAMERA 01 · PHÒNG THI MÔ PHỎNG <span class="pill">YOLO ONNX · PHÁT LẠI</span></div>
<video id="vid" controls playsinline preload="metadata" poster=""><source src="data:video/mp4;base64,__MEDIA__" type="video/mp4">Không hỗ trợ video MP4.</video>
<div class="timeline"><span>▶ Nhấn Play để bắt đầu</span><b id="time">00:00 / 00:08</b></div><div class="help">Có thể tạm dừng hoặc kéo thanh thời gian để xem lại. Cảnh báo xuất hiện từ mốc 4,067 giây trên video đã xử lý.</div>
<div class="footer">YOLO phát hiện người trong video mô phỏng. Khung người không đồng nghĩa với nhận dạng danh tính hoặc xác nhận ghế trống.</div></section>
<section class="panel"><div class="heading">🔔 TRẠNG THÁI CẢNH BÁO</div>
<div id="ready" class="status ready">● SẴN SÀNG<br><span style="font-size:13px;font-weight:500">Chưa phát video. Chưa có cảnh báo được trình chiếu.</span></div>
<div id="playing" class="status playing" hidden>● ĐANG PHÁT VIDEO<br><span style="font-size:13px;font-weight:500">Chưa đến thời điểm sự kiện cần rà soát.</span></div>
<div id="alert" class="status alert" role="alert" aria-live="assertive" hidden><h2>⚠ CẢNH BÁO — VỊ TRÍ G06</h2><p>HỌC SINH TẠI VỊ TRÍ G06 CÓ DẤU HIỆU DI CHUYỂN KHỎI CHỖ NGỒI TRONG GIỜ THI. ĐỀ NGHỊ GIÁM THỊ KIỂM TRA!</p><small>H.15 · Mốc 4,067 giây · Tín hiệu tính trước, phát lại trên video mô phỏng.</small></div>
<div class="heading" style="margin-top:23px">🪑 SƠ ĐỒ 16 VỊ TRÍ</div><div class="seatmap" id="map"></div>
<div class="muted">Sơ đồ ký hiệu, không phải tọa độ ghế xác định bằng camera. Chỉ G06 là tình huống được chọn trình diễn.</div>
</section></div>
<script>
const v=document.getElementById('vid'),ready=document.getElementById('ready'),playing=document.getElementById('playing'),alertBox=document.getElementById('alert');
const count=document.getElementById('count'),seat=document.getElementById('seat'),m1=document.getElementById('m1'),m2=document.getElementById('m2'),clock=document.getElementById('time');
const map=document.getElementById('map');for(let i=1;i<=16;i++){const n='G'+String(i).padStart(2,'0'),el=document.createElement('div');el.className='seat'+(n==='G06'?' g06':'');el.textContent=n;el.id='s'+n;map.appendChild(el)}
function sync(){const t=v.currentTime||0,started=t>0.04||(!v.paused&&!v.ended),trigger=t>=4.067;
count.textContent=trigger?'01':'00';seat.textContent=trigger?'G06':'—';m1.classList.toggle('active',trigger);m2.classList.toggle('active',trigger);document.getElementById('sG06').classList.toggle('active',trigger);
ready.hidden=started;playing.hidden=!started||trigger;alertBox.hidden=!trigger;
clock.textContent='00:'+String(Math.floor(t)).padStart(2,'0')+' / 00:'+String(Math.round(v.duration||8)).padStart(2,'0');}
for(const ev of ['loadedmetadata','timeupdate','seeked','play','pause','ended'])v.addEventListener(ev,sync);
v.autoplay=false;v.pause();v.currentTime=0;sync();
</script></body></html>'''
        page=page.replace('__MEDIA__',encoded)
        components.html(page,height=840,scrolling=True)
    else:
        st.error('Chưa có video triển khai. Chép V15_8s_alert_v2_web.mp4 từ máy thầy vào cùng thư mục app.py, sau đó tải lại trang.')
    st.markdown('<div class="note"><b>GIỚI THIỆU DEMO:</b> Phiên bản 1.1 minh họa quy trình nhận diện người bằng YOLO, phân tích biến động hình ảnh và hỗ trợ cảnh báo tại vị trí cần kiểm tra, thông qua video mô phỏng đã xử lý.</div>',unsafe_allow_html=True)

# The research tab is kept separate so demo counters never imply that all three signals are departures.
with tab_research:
    st.subheader('Nhật ký H.14–H.15: Dữ liệu gốc được bảo toàn')
    st.info('G06 là tình huống minh họa; G10 và G15 là tín hiệu phụ cần rà soát. Ba tín hiệu không có nghĩa ba học sinh rời chỗ.')
    st.markdown('**Bảng tổng hợp sự kiện (không phải dữ liệu gốc):**')
    st.dataframe(events,hide_index=True,use_container_width=True)
    st.markdown('**Toàn bộ mẫu đo H.15 gốc:**')
    st.dataframe(raw,hide_index=True,use_container_width=True)
    st.download_button('⬇ TẢI CSV H.15 GỐC — KHÔNG CHỈNH SỬA',data=CSV.read_bytes(),file_name='H15_event_audit_original.csv',mime='text/csv')
    st.download_button('⬇ TẢI BẢNG TỔNG HỢP 03 SỰ KIỆN',data=to_csv(events),file_name='H15_events_summary.csv',mime='text/csv')
    choice=st.selectbox('Xem minh chứng ROI theo vị trí',['— Chọn vị trí —','G06','G10','G15'])
    if choice!='— Chọn vị trí —':
        images=sorted(EVIDENCE.glob(f'*_{choice}_*.jpg')) if EVIDENCE.exists() else []
        if images:
            for p in images: st.image(str(p),caption=p.name,use_container_width=True)
        else:
            st.caption('Chưa có ảnh JPG minh chứng trong evidence/. Sao chép ảnh H.15 gốc từ máy nghiên cứu, không chỉnh sửa.')
    with st.expander('Phương pháp, giới hạn và giải thích số liệu'):
        st.markdown('''**YOLO ONNX:** phát hiện người và vẽ khung lên video ngoại tuyến; số khung phát hiện không phải số học sinh được xác nhận.

**H.14:** ghi nhận tín hiệu quỹ đạo ảnh từ vùng ghế. **H.15:** đối chiếu biến đổi ROI theo ba mốc sau sự kiện. Chỉ số ROI không phải xác suất ghế trống. G10 và G15 có thể liên quan chuyển động hoặc che khuất.


**Cảnh báo G06:** Hệ thống minh họa tín hiệu cảnh báo tại vị trí G06 ở thời điểm 4,067 giây, dựa trên kết quả phân tích biến động hình ảnh và kiểm chứng bằng thuật toán H14–H15.''')
