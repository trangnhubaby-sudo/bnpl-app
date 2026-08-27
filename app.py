import streamlit as st
import networkx as nx
import pandas as pd
import sqlite3
import numpy as np
import pydeck as pdk
from datetime import datetime
from pyvis.network import Network
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# ==============================================================================
# 1. ENTERPRISE PAGE CONFIG & MODERN DARK UI STYLING
# ==============================================================================
st.set_page_config(
    page_title="NEXUS Operating System | Enterprise Risk Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tự động làm mới dữ liệu
st_autorefresh(interval=15000, key="nexus_sync_v7")

# Khởi tạo trạng thái Navigation Tab
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Tổng Quan"

# Custom CSS
st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        --bg-dark: #070c14;
        --card-bg: #0f172a;
        --card-border: #1e293b;
        --accent-blue: #38bdf8;
        --accent-purple: #c084fc;
        --accent-green: #10b981;
        --accent-red: #f43f5e;
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: var(--bg-dark) !important;
        color: var(--text-main) !important;
    }
    
    .stApp {
        background-color: var(--bg-dark);
    }

    /* Styling Top Nav Container */
    .top-navbar-container {
        background: #0d1527;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 0.5rem 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
    }

    .brand-logo {
        width: 38px;
        height: 38px;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.2rem;
        color: #070c14;
    }
    .brand-name {
        font-weight: 800;
        font-size: 1.2rem;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #38bdf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Custom Streamlit Buttons in Navbar to look like Tab Links */
    div[data-testid="stColumn"] > div > div > button {
        background-color: transparent !important;
        border: none !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.5rem 0.8rem !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stColumn"] > div > div > button:hover {
        color: #38bdf8 !important;
        background: rgba(56, 189, 248, 0.08) !important;
    }

    /* Hero Banner Styling */
    .hero-carousel-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #090d16 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 20px 40px -15px rgba(0,0,0,0.6);
    }
    .hero-badge {
        display: inline-block;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.3);
        color: #38bdf8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }
    .hero-title {
        font-size: 1.75rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    .hero-desc {
        color: #94a3b8;
        font-size: 0.92rem;
        line-height: 1.6;
    }

    /* Cards Grid */
    .feature-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 1.25rem;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.4);
        height: 100%;
    }
    .card-banner {
        width: 100%;
        height: 90px;
        background: #1e293b;
        border-radius: 10px;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
    }
    .card-heading {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.3rem;
    }
    .card-text {
        font-size: 0.83rem;
        color: #94a3b8;
        line-height: 1.5;
    }

    /* Sidebar */
    div[data-testid="stSidebar"] {
        background-color: #060a12 !important;
        border-right: 1px solid #1a2333;
    }
</style>
''', unsafe_allow_html=True)

# ==============================================================================
# 2. KHỞI TẠO CSDL SQLITE VÀ XỬ LÝ DỮ LIỆU
# ==============================================================================
def init_db():
    conn = sqlite3.connect("bnpl_enterprise.db")
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS loan_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id TEXT UNIQUE,
            customer_name TEXT,
            national_id TEXT,
            loan_amount REAL,
            ip_address TEXT,
            device_hash TEXT,
            latitude REAL,
            longitude REAL,
            is_proxy INTEGER,
            risk_score REAL,
            decision TEXT,
            created_at TEXT
        )
    ''')
    cur.execute("SELECT COUNT(*) FROM loan_applications")
    if cur.fetchone()[0] == 0:
        seed_records = [
            ("APP-8801", "Nguyễn Văn An", "001092008123", 15000000.0, "113.161.72.10", "FP-8A99F201", 10.7769, 106.7009, 0, 12.4, "APPROVED", "2026-08-27 08:15:22"),
            ("APP-8802", "Trần Thị Bình", "025091004567", 25000000.0, "27.67.42.19", "FP-CC44B109", 10.7780, 106.7015, 0, 88.5, "REJECTED", "2026-08-27 09:12:10"),
            ("APP-8803", "Lê Văn Cường", "036089001122", 18000000.0, "27.67.42.19", "FP-8A99F201", 10.7782, 106.7018, 0, 14.2, "APPROVED", "2026-08-27 09:45:44"),
            ("APP-8804", "Phạm Minh Dung", "048095007890", 12000000.0, "14.161.20.55", "FP-1102AA88", 21.0285, 105.8542, 0, 8.2, "APPROVED", "2026-08-27 10:11:05"),
            ("APP-8805", "Vũ Quốc Đạt", "052093003344", 30000000.0, "27.67.42.19", "FP-CC44B109", 10.7775, 106.7011, 1, 96.0, "REJECTED", "2026-08-27 10:50:00")
        ]
        cur.executemany('''
            INSERT INTO loan_applications 
            (app_id, customer_name, national_id, loan_amount, ip_address, device_hash, latitude, longitude, is_proxy, risk_score, decision, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', seed_records)
    conn.commit()
    conn.close()

def add_new_application(name, nid, amount, ip, fp, lat, lng, is_proxy):
    conn = sqlite3.connect("bnpl_enterprise.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM loan_applications")
    count = cur.fetchone()[0] + 1
    app_id = f"APP-88{count:02d}"
    
    # AI Engine đơn giản đánh giá Risk Score
    risk = 10.0
    if is_proxy: risk += 40.0
    # Kiểm tra trùng IP/Device với hồ sơ gian lận trước
    cur.execute("SELECT COUNT(*) FROM loan_applications WHERE (ip_address=? OR device_hash=?) AND decision='REJECTED'", (ip, fp))
    if cur.fetchone()[0] > 0:
        risk += 45.0
    
    decision = "REJECTED" if risk >= 50.0 else "APPROVED"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute('''
        INSERT INTO loan_applications 
        (app_id, customer_name, national_id, loan_amount, ip_address, device_hash, latitude, longitude, is_proxy, risk_score, decision, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (app_id, name, nid, amount, ip, fp, lat, lng, 1 if is_proxy else 0, risk, decision, now_str))
    
    conn.commit()
    conn.close()
    return app_id, risk, decision

def fetch_data():
    conn = sqlite3.connect("bnpl_enterprise.db")
    df = pd.read_sql_query("SELECT * FROM loan_applications ORDER BY id DESC", conn)
    conn.close()

    G = nx.Graph()
    for _, row in df.iterrows():
        app_id = row["app_id"]
        ip = row["ip_address"]
        fp = row["device_hash"]
        is_fraud = (row["decision"] == "REJECTED")

        G.add_node(app_id, label=f"{row['customer_name']}\n({app_id})", type="Application", risk=row["risk_score"], color="#f43f5e" if is_fraud else "#10b981")
        G.add_node(ip, label=f"IP: {ip}", type="IP_Address", color="#38bdf8")
        G.add_node(fp, label=f"FP: {fp}", type="Device_Hash", color="#c084fc")

        G.add_edge(app_id, ip)
        G.add_edge(app_id, fp)

    return G, df

init_db()
G, df_apps = fetch_data()

# ==============================================================================
# SIDEBAR: KHU VỰC NHẬP HỒ SƠ MỚI & BỘ LỌC
# ==============================================================================
st.sidebar.title("🛠️ Quản Lý Hệ Thống")

with st.sidebar.expander("➕ **NHẬP HỒ SƠ VAY MỚI**", expanded=True):
    with st.form("add_loan_form", clear_on_submit=True):
        new_name = st.text_input("Họ và Tên", "Trần Văn Mới")
        new_nid = st.text_input("Số CCCD", "038099005566")
        new_amount = st.number_input("Số tiền vay (VNĐ)", min_value=1000000, value=20000000, step=1000000)
        new_ip = st.text_input("Địa chỉ IP", "27.67.42.19")
        new_fp = st.text_input("Fingerprint Thiết bị", "FP-CC44B109")
        c_lat, c_lng = st.columns(2)
        with c_lat:
            new_lat = st.number_input("Vĩ độ", value=10.7769, format="%.4f")
        with c_lng:
            new_lng = st.number_input("Kinh độ", value=106.7009, format="%.4f")
        new_proxy = st.checkbox("Sử dụng Proxy/VPN nghi vấn?")
        
        submit_btn = st.form_submit_button("🚀 Gửi Đơn Vay & AI Scored", use_container_width=True)
        if submit_btn:
            app_id, risk, decision = add_new_application(new_name, new_nid, new_amount, new_ip, new_fp, new_lat, new_lng, new_proxy)
            if decision == "APPROVED":
                st.success(f"✅ Đã duyệt đơn {app_id}! Risk: {risk}%")
            else:
                st.error(f"🚨 Từ chối đơn {app_id}! Risk: {risk}%")
            st.rerun()

app_list = [n for n, d in G.nodes(data=True) if d.get("type") == "Application"]
selected_app = st.sidebar.selectbox("📋 Chọn Hồ Sơ Xem Chi Tiết:", app_list if app_list else ["N/A"])

# ==============================================================================
# SECTION 1: TOP NAVBAR (ĐÃ ĐƯỢC TÍCH HỢP TƯƠNG TÁC THỰC SỰ)
# ==============================================================================
st.markdown('<div class="top-navbar-container">', unsafe_allow_html=True)
nav_col1, nav_col2, nav_col3 = st.columns([0.28, 0.58, 0.14])

with nav_col1:
    st.markdown('''
    <div style="display: flex; align-items: center; gap: 10px;">
        <div class="brand-logo">N</div>
        <div class="brand-name">NEXUS RISK PLATFORM</div>
    </div>
    ''', unsafe_allow_html=True)

with nav_col2:
    t1, t2, t3, t4, t5 = st.columns(5)
    if t1.button("🌐 Tổng Quan"): st.session_state.active_tab = "Tổng Quan"
    if t2.button("🕸️ Đồ Thị Mạng"): st.session_state.active_tab = "Đồ Thị Mạng"
    if t3.button("📊 Analytics AI"): st.session_state.active_tab = "Analytics AI"
    if t4.button("📍 Bản Đồ Vị Trí"): st.session_state.active_tab = "Bản Đồ Vị Trí"
    if t5.button("⚙️ Rules Cấu Hình"): st.session_state.active_tab = "Rules Cấu Hình"

with nav_col3:
    st.markdown('''
    <div style="text-align: right; margin-top: 5px;">
        <span style="font-size: 0.78rem; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); color: #34d399; padding: 5px 10px; border-radius: 20px; font-weight: 600;">
            🟢 System Online
        </span>
    </div>
    ''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# HERO BANNER CAROUSEL SLIDER
# ==============================================================================
if "slide_idx" not in st.session_state:
    st.session_state.slide_idx = 0

slides = [
    {
        "badge": "⚡ GRAPH NEURAL NETWORK v5.2",
        "title": "Phát Hiện Chuỗi Bùng Nợ Tín Dụng Realtime",
        "desc": "Thuật toán AI tự động quét phân tích Topology kết nối thiết bị (Device Fingerprint) và IP truy cập để phát hiện các hành vi gian lận mở nhiều tài khoản ảo."
    },
    {
        "badge": "🛡️ HIGH-RISK PROXY & DEVICE DETECTOR",
        "title": "Cảnh Báo Sớm Thiết Bị Dùng Chung Bất Thường",
        "desc": "Truy vết tức thì các nhóm đối tượng sử dụng chung 1 phần cứng điện thoại/máy tính để đăng ký nhiều khoản vay cùng lúc."
    },
    {
        "badge": "MAP SPATIAL GEOLOCATION MATRIX",
        "title": "Phân Tích Mật Độ Gian Lận Theo Tọa Độ Địa Lý",
        "desc": "Tích hợp GIS GeoIP theo dõi chính xác vị trí thực tế của đơn vay, phát hiện việc giả lập vị trí thông qua VPN hoặc Proxy."
    }
]

cur_slide = slides[st.session_state.slide_idx]
c_hero, c_btn = st.columns([0.88, 0.12])

with c_hero:
    st.markdown(f'''
    <div class="hero-carousel-container">
        <div class="hero-badge">{cur_slide['badge']}</div>
        <div class="hero-title">{cur_slide['title']}</div>
        <div class="hero-desc">{cur_slide['desc']}</div>
    </div>
    ''', unsafe_allow_html=True)

with c_btn:
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    if st.button("◀ Prev", use_container_width=True, key="h_prev"):
        st.session_state.slide_idx = (st.session_state.slide_idx - 1) % len(slides)
        st.rerun()
    if st.button("Next ▶", use_container_width=True, key="h_next"):
        st.session_state.slide_idx = (st.session_state.slide_idx + 1) % len(slides)
        st.rerun()

# ==============================================================================
# DYNAMIC VIEW CONTROLLER (XỬ LÝ CHUYỂN TRANG THEO CÁC NÚT TOP NAV)
# ==============================================================================
st.markdown(f"### 📌 Đang hiển thị view: **{st.session_state.active_tab}**")

if st.session_state.active_tab == "Tổng Quan":
    # 3 CARDS FEATURE GRID
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('''
        <div class="feature-card">
            <div class="card-banner" style="color: #38bdf8;">🕸️</div>
            <div class="card-heading">Đồ Thị Mạng Realtime</div>
            <div class="card-text">Mô phỏng cụm liên kết đa chiều giữa đơn vay, IP và Fingerprint thiết bị để phát hiện vòng bùng nợ.</div>
        </div>
        ''', unsafe_allow_html=True)
    with c2:
        st.markdown('''
        <div class="feature-card">
            <div class="card-banner" style="color: #c084fc;">📊</div>
            <div class="card-heading">AI Risk Scoring</div>
            <div class="card-text">Bảng tổng hợp chỉ số rủi ro, ma trận xét duyệt tự động và chi tiết các trường dữ liệu nghi vấn.</div>
        </div>
        ''', unsafe_allow_html=True)
    with c3:
        st.markdown('''
        <div class="feature-card">
            <div class="card-banner" style="color: #10b981;">📍</div>
            <div class="card-heading">GeoIP Tracking</div>
            <div class="card-text">Theo dõi bản đồ vị trí thực tế của khách hàng vay, phát hiện VPN/Proxy che giấu vị trí.</div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_graph, col_info = st.columns([1.8, 1.2])
    
    with col_graph:
        st.markdown("##### 🕸️ Mạng Lưới Đồ Thị Mẫu")
        net = Network(height="420px", width="100%", bgcolor="#070c14", font_color="#f8fafc")
        net.from_nx(G)
        net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=90)
        
        for node in net.nodes:
            if node["id"] == selected_app:
                node["size"] = 30
                node["color"] = "#facc15"
            elif node.get("type") == "Application":
                node["size"] = 18

        net.save_graph("graph_overview.html")
        with open("graph_overview.html", "r", encoding="utf-8") as f:
            components.html(f.read(), height=440)

    with col_info:
        st.markdown(f"##### 🎯 Chi Tiết Hồ Sơ: `{selected_app}`")
        if selected_app in G.nodes:
            app_info = df_apps[df_apps["app_id"] == selected_app].iloc[0]
            is_bad = (app_info["decision"] == "REJECTED")
            
            st.metric("Khách hàng", app_info["customer_name"])
            st.metric("Số CCCD/CMND", app_info["national_id"])
            st.metric("Khoản Vay", f"{app_info['loan_amount']:,.0f} VNĐ")
            st.metric("Điểm Rủi Ro AI", f"{app_info['risk_score']}%", 
                      delta="🚨 TỪ CHỐI (RỦI RO CAO)" if is_bad else "✅ DUYỆT (AN TOÀN)", 
                      delta_color="inverse" if is_bad else "normal")

elif st.session_state.active_tab == "Đồ Thị Mạng":
    st.markdown("##### 🕸️ Toàn Màn Hình Đồ Thị Mạng Lưới Liên Kết Gian Lận")
    net = Network(height="600px", width="100%", bgcolor="#070c14", font_color="#f8fafc")
    net.from_nx(G)
    net.barnes_hut(gravity=-4000, central_gravity=0.2, spring_length=100)
    net.save_graph("graph_full.html")
    with open("graph_full.html", "r", encoding="utf-8") as f:
        components.html(f.read(), height=620)

elif st.session_state.active_tab == "Analytics AI":
    st.markdown("##### 📊 Thống Kê & Dữ Liệu Hồ Sơ Chi Tiết")
    
    m1, m2, m3, m4 = st.columns(4)
    total_apps = len(df_apps)
    rejected_apps = len(df_apps[df_apps["decision"] == "REJECTED"])
    approved_apps = len(df_apps[df_apps["decision"] == "APPROVED"])
    fraud_rate = (rejected_apps / total_apps * 100) if total_apps > 0 else 0

    m1.metric("Tổng Hồ Sơ Vay", total_apps)
    m2.metric("Hồ Sơ Đã Duyệt", approved_apps)
    m3.metric("Hồ Sơ Từ Chối", rejected_apps)
    m4.metric("Tỷ Lệ Gian Lận", f"{fraud_rate:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(df_apps, use_container_width=True, hide_index=True)

elif st.session_state.active_tab == "Bản Đồ Vị Trí":
    st.markdown("##### 📍 Bản Đồ Phân Bố Đơn Vay Về Địa Lý (GeoIP)")
    
    map_df = df_apps.copy()
    map_df["color"] = map_df["decision"].apply(lambda x: [244, 63, 94, 200] if x == "REJECTED" else [16, 185, 129, 200])

    view_state = pdk.ViewState(
        latitude=map_df["latitude"].mean() if not map_df.empty else 10.7769,
        longitude=map_df["longitude"].mean() if not map_df.empty else 106.7009,
        zoom=10,
        pitch=45
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position=["longitude", "latitude"],
        get_fill_color="color",
        get_radius=300,
        pickable=True
    )

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "Đơn vay: {app_id}\nTên: {customer_name}\nTrạng thái: {decision}"}))

elif st.session_state.active_tab == "Rules Cấu Hình":
    st.markdown("##### ⚙️ Cấu Hình Quy Tắc Chấm Điểm Rủi Ro (Risk Rules)")
    st.slider("Trọng số phạt khi trùng IP bị từ chối:", 0, 100, 45)
    st.slider("Trọng số phạt khi dùng Proxy/VPN:", 0, 100, 40)
    st.number_input("Ngưỡng điểm Risk Score để TỪ CHỐI tự động:", value=50)
    st.button("💾 Lưu Cấu Hình Engine")