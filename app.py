import streamlit as st
import networkx as nx
import pandas as pd
import sqlite3
import numpy as np
from datetime import datetime
from pyvis.network import Network
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# ==============================================================================
# 1. ENTERPRISE PAGE CONFIG & MODERN DARK UI STYLING
# ==============================================================================
st.set_page_config(
    page_title="NEXUS Operating System | Enterprise Risk & Fraud Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tự động làm mới dữ liệu mỗi 10 giây
st_autorefresh(interval=10000, key="nexus_sync_v6")

# Custom CSS dựng đúng Bố cục Wireframe
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

    /* 1. TOP NAVBAR / NAVIGATION HEADER (Thanh trên cùng) */
    .top-navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.85rem 1.75rem;
        background: #0d1527;
        border: 1px solid #1e293b;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
    }
    .brand-group {
        display: flex;
        align-items: center;
        gap: 12px;
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
        font-size: 1.25rem;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #38bdf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .nav-links {
        display: flex;
        align-items: center;
        gap: 28px;
        font-size: 0.88rem;
        font-weight: 600;
        color: var(--text-muted);
    }
    .nav-item-active {
        color: #38bdf8 !important;
        border-bottom: 2px solid #38bdf8;
        padding-bottom: 2px;
    }

    /* 2. HERO SLIDER BANNER PANEL (Khu vực Carousel ở giữa) */
    .hero-carousel-container {
        position: relative;
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #090d16 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 2.2rem 2.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 20px 40px -15px rgba(0,0,0,0.6);
        min-height: 240px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.3);
        color: #38bdf8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        width: fit-content;
        margin-bottom: 0.75rem;
    }
    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.03em;
        margin-bottom: 0.5rem;
    }
    .hero-desc {
        color: #94a3b8;
        font-size: 0.95rem;
        max-width: 850px;
        line-height: 1.6;
    }
    .carousel-dots {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-top: 1.25rem;
    }
    .dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #334155;
        transition: all 0.3s ease;
    }
    .dot-active {
        background: #38bdf8;
        width: 28px;
        border-radius: 10px;
    }

    /* 3. THREE-COLUMN CONTENT CARDS GRID (3 Cột thông tin phía dưới) */
    .feature-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 1.25rem;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.4);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .feature-card:hover {
        border-color: #38bdf8;
        transform: translateY(-2px);
    }
    .card-banner {
        width: 100%;
        height: 120px;
        background: #1e293b;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.2rem;
        border: 1px dashed #334155;
    }
    .card-heading {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.4rem;
    }
    .card-text {
        font-size: 0.85rem;
        color: #94a3b8;
        line-height: 1.5;
        margin-bottom: 1rem;
    }
    .card-cta {
        align-self: flex-start;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.3);
        color: #38bdf8;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Sidebar Styling */
    div[data-testid="stSidebar"] {
        background-color: #060a12 !important;
        border-right: 1px solid #1a2333;
    }
</style>
''', unsafe_allow_html=True)

# ==============================================================================
# 2. KHỞI TẠO CSDL SQLITE VÀ DỮ LIỆU ĐỒ THỊ CORE
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

init_db()

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

G, df_apps = fetch_data()

# Sidebar: Lựa chọn hồ sơ kiểm tra
st.sidebar.title("🎛️ Điều Hướng System")
app_list = [n for n, d in G.nodes(data=True) if d.get("type") == "Application"]
selected_app = st.sidebar.selectbox("📋 Pilih/Chọn Hồ Sơ Cần Xem:", app_list if app_list else ["N/A"])

# ==============================================================================
# SECTION 1: TOP NAVBAR (KHU VỰC THANH ĐIỀU HƯỚNG TRÊN CÙNG)
# ==============================================================================
st.markdown('''
<div class="top-navbar">
    <div class="brand-group">
        <div class="brand-logo">N</div>
        <div>
            <div class="brand-name">NEXUS RISK PLATFORM</div>
        </div>
    </div>
    <div class="nav-links">
        <span class="nav-item-active">🌐 Tổng Quan</span>
        <span>🕸️ Đồ Thị Mạng</span>
        <span>📊 Analytics AI</span>
        <span>📍 Bản Đồ Vị Trí</span>
        <span>⚙️ Rules Cấu Hình</span>
    </div>
    <div style="font-size: 0.8rem; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); color: #34d399; padding: 4px 12px; border-radius: 20px; font-weight: 600;">
        🟢 System Online
    </div>
</div>
''', unsafe_allow_html=True)

# ==============================================================================
# SECTION 2: SLIDER BANNER Ở GIỮA (HERO CAROUSEL)
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
        "badge": "🗺️ SPATIAL GEOLOCATION MATRIX",
        "title": "Phân Tích Mật Độ Gian Lận Theo Tọa Độ Địa Lý",
        "desc": "Tích hợp GIS GeoIP theo dõi chính xác vị trí thực tế của đơn vay, phát hiện việc giả lập vị trí thông qua VPN hoặc Proxy."
    }
]

cur_slide = slides[st.session_state.slide_idx]

col_hero, col_controls = st.columns([0.88, 0.12])

with col_hero:
    st.markdown(f'''
    <div class="hero-carousel-container">
        <div class="hero-badge">{cur_slide['badge']}</div>
        <div class="hero-title">{cur_slide['title']}</div>
        <div class="hero-desc">{cur_slide['desc']}</div>
        <div class="carousel-dots">
            <div class="dot {'dot-active' if st.session_state.slide_idx == 0 else ''}"></div>
            <div class="dot {'dot-active' if st.session_state.slide_idx == 1 else ''}"></div>
            <div class="dot {'dot-active' if st.session_state.slide_idx == 2 else ''}"></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

with col_controls:
    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)
    if st.button("◀ Prev", use_container_width=True):
        st.session_state.slide_idx = (st.session_state.slide_idx - 1) % len(slides)
        st.rerun()
    if st.button("Next ▶", use_container_width=True):
        st.session_state.slide_idx = (st.session_state.slide_idx + 1) % len(slides)
        st.rerun()

# ==============================================================================
# SECTION 3: THREE-COLUMN FEATURE CARDS GRID (3 CỘT NỘI DUNG BÊN DƯỚI)
# ==============================================================================
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown('''
    <div class="feature-card">
        <div>
            <div class="card-banner" style="background: linear-gradient(135deg, rgba(56, 189, 248, 0.1), rgba(14, 165, 233, 0.2)); color: #38bdf8;">
                🕸️
            </div>
            <div class="card-heading">Đồ Thị Mạng Liên Kết Realtime</div>
            <div class="card-text">Mô phỏng cụm liên kết đa chiều giữa đơn vay, IP và Fingerprint thiết bị để phát hiện các vòng bùng nợ chéo.</div>
        </div>
        <div class="card-cta">Khám Phá Graph →</div>
    </div>
    ''', unsafe_allow_html=True)

with c2:
    st.markdown('''
    <div class="feature-card">
        <div>
            <div class="card-banner" style="background: linear-gradient(135deg, rgba(192, 132, 252, 0.1), rgba(168, 85, 247, 0.2)); color: #c084fc;">
                📊
            </div>
            <div class="card-heading">Chấm Điểm Rủi Ro AI Score</div>
            <div class="card-text">Bảng tổng hợp chỉ số rủi ro, ma trận xét duyệt tự động và chi tiết các trường dữ liệu nghi vấn của từng hồ sơ.</div>
        </div>
        <div class="card-cta">Xem Analytics AI →</div>
    </div>
    ''', unsafe_allow_html=True)

with c3:
    st.markdown('''
    <div class="feature-card">
        <div>
            <div class="card-banner" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.2)); color: #10b981;">
                📍
            </div>
            <div class="card-heading">Truy Vết Tọa Độ Địa Lý GeoIP</div>
            <div class="card-text">Theo dõi bản đồ vị trí thực tế của khách hàng vay, phân tích các dải IP bất thường hoặc VPN che giấu vị trí.</div>
        </div>
        <div class="card-cta">Bản Đồ Vệ Tinh →</div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown("<br><hr style='border-color: #1e293b;'><br>", unsafe_allow_html=True)

# ==============================================================================
# SECTION 4: TƯƠNG TÁC CHI TIẾT (GRAPH & CSDL)
# ==============================================================================
tab1, tab2 = st.tabs(["🕸️ TƯƠNG TÁC ĐỒ THỊ & HỒ SƠ CHỌN", "📋 BẢNG DỮ LIỆU CSDL SQLITE"])

with tab1:
    col_graph, col_info = st.columns([1.8, 1.2])
    
    with col_graph:
        st.markdown("##### 🕸️ Mạng Lưới Đồ Thị Liên Kết Đơn Vay")
        net = Network(height="460px", width="100%", bgcolor="#070c14", font_color="#f8fafc")
        net.from_nx(G)
        net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=90)
        
        for node in net.nodes:
            if node["id"] == selected_app:
                node["size"] = 32
                node["color"] = "#facc15"
            elif node.get("type") == "Application":
                node["size"] = 20

        net.save_graph("graph_ui_layout.html")
        with open("graph_ui_layout.html", "r", encoding="utf-8") as f:
            components.html(f.read(), height=480)

    with col_info:
        st.markdown(f"##### 🎯 Chi Tiết Hồ Sơ Đang Chọn: `{selected_app}`")
        if selected_app in G.nodes:
            app_info = df_apps[df_apps["app_id"] == selected_app].iloc[0]
            is_bad = (app_info["decision"] == "REJECTED")
            
            st.metric("Khách hàng", app_info["customer_name"])
            st.metric("Số CCCD/CMND", app_info["national_id"])
            st.metric("Khoản Vay Yêu Cầu", f"{app_info['loan_amount']:,.0f} VNĐ")
            st.metric("Điểm Rủi Ro AI", f"{app_info['risk_score']}%", 
                      delta="RỦI RO CAO (CẢNH BÁO)" if is_bad else "AN TOÀN", 
                      delta_color="inverse" if is_bad else "normal")

with tab2:
    st.markdown("##### 📋 Danh Sách Hồ Sơ Đăng Ký Vay Trong CSDL")
    st.dataframe(df_apps, use_container_width=True, hide_index=True)