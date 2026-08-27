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
# 1. PAGE CONFIG & MODERN AI PORTAL THEME CSS
# ==============================================================================
st.set_page_config(
    page_title="NEXUS AI - Hệ Thống Phân Tích Rủi Ro Tín Dụng",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st_autorefresh(interval=15000, key="nexus_ai_sync")

# Session State
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Overview"
if "risk_threshold" not in st.session_state:
    st.session_state.risk_threshold = 50.0
if "proxy_penalty" not in st.session_state:
    st.session_state.proxy_penalty = 40.0
if "blacklist_penalty" not in st.session_state:
    st.session_state.blacklist_penalty = 45.0

# CSS Bố Cục Portal Chuyên Nghiệp Chuẩn Đề Tài AI
st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif !important;
        background-color: #f8f9fa !important;
        color: #333333 !important;
    }
    
    .stApp {
        background-color: #ffffff;
    }

    header[data-testid="stHeader"] {
        display: none !important;
    }
    .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }

    /* 1. TOP NAVBAR HEADER */
    .top-header {
        background: #ffffff;
        padding: 0.8rem 4%;
        border-bottom: 1px solid #eee;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    .brand-logo {
        font-size: 1.8rem;
        font-weight: 900;
        color: #2e7d32;
        letter-spacing: -0.5px;
    }
    .brand-logo span {
        color: #0284c7;
    }

    /* Styling nút bấm trên Menu Navbar */
    div[data-testid="stColumn"] > div > div > button {
        background-color: transparent !important;
        border: none !important;
        color: #444444 !important;
        font-weight: 700 !important;
        font-size: 0.82rem !important;
        padding: 0.5rem 0.2rem !important;
    }
    div[data-testid="stColumn"] > div > div > button:hover {
        color: #2ecc71 !important;
    }

    /* 2. HERO BANNER */
    .hero-container {
        width: 100%;
        height: 380px;
        background: url('https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=2070&auto=format&fit=crop') center/cover no-repeat;
        position: relative;
    }

    /* 3. SEARCH BAR (GREEN ZONE) */
    .search-section {
        background-color: #2ecc71;
        padding: 1.2rem 8%;
        margin-top: -5px;
    }

    /* 4. SECTION HEADER */
    .section-title-box {
        text-align: center;
        padding: 2.5rem 1rem 1rem 1rem;
    }
    .section-subtitle {
        color: #2ecc71;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.2rem;
    }
    .section-main-title {
        font-size: 2rem;
        font-weight: 800;
        color: #2c3e50;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .section-desc {
        color: #7f8c8d;
        font-size: 0.95rem;
        margin-top: 0.3rem;
    }

    /* 5. AI APPLICATION CARDS */
    .bds-card {
        background: #ffffff;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        overflow: hidden;
        transition: transform 0.3s, box-shadow 0.3s;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .bds-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .card-img-container {
        position: relative;
        height: 180px;
        width: 100%;
    }
    .card-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .badge-new {
        position: absolute;
        top: 10px;
        left: 10px;
        background: #0284c7;
        color: white;
        font-size: 0.7rem;
        font-weight: bold;
        padding: 3px 8px;
        border-radius: 3px;
    }
    .badge-vip {
        position: absolute;
        top: 0;
        right: 0;
        width: 0;
        height: 0;
        border-top: 50px solid #2ecc71;
        border-left: 50px solid transparent;
    }
    .badge-vip-rejected {
        border-top-color: #e74c3c !important;
    }
    .badge-vip-text {
        position: absolute;
        top: 8px;
        right: 4px;
        color: white;
        font-size: 0.65rem;
        font-weight: bold;
        transform: rotate(45deg);
    }
    .card-body {
        padding: 1rem;
    }
    .card-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .card-info {
        font-size: 0.85rem;
        color: #555555;
        margin-bottom: 0.3rem;
    }
    .price-tag {
        color: #e74c3c;
        font-weight: 800;
        font-size: 1.15rem;
    }

    /* 6. WHY CHOOSE US FOOTER SECTION */
    .why-section {
        background-color: #1a252f;
        color: white;
        padding: 3.5rem 8% 2rem 8%;
        text-align: center;
        margin-top: 3rem;
    }
    .why-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .why-subtitle {
        color: #bdc3c7;
        font-size: 0.95rem;
        margin-bottom: 2.5rem;
    }
    .feature-icon {
        font-size: 2.2rem;
        color: #2ecc71;
        margin-bottom: 0.8rem;
    }
    .feature-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }
    .feature-desc {
        color: #95a5a6;
        font-size: 0.85rem;
        line-height: 1.5;
    }

    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }
</style>
''', unsafe_allow_html=True)

# ==============================================================================
# 2. CSDL SQLITE & GRAPH ENGINE (NỘI DUNG NGUYÊN BẢN)
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
    
    risk = 10.0
    if is_proxy: 
        risk += st.session_state.proxy_penalty
    
    cur.execute("SELECT COUNT(*) FROM loan_applications WHERE (ip_address=? OR device_hash=?) AND decision='REJECTED'", (ip, fp))
    if cur.fetchone()[0] > 0:
        risk += st.session_state.blacklist_penalty
    
    risk = min(risk, 99.9)
    decision = "REJECTED" if risk >= st.session_state.risk_threshold else "APPROVED"
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

def render_pyvis_graph(graph, highlight_node=None, height="450px"):
    net = Network(height=height, width="100%", bgcolor="#ffffff", font_color="#333333")
    net.from_nx(graph)
    net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=90)
    
    for node in net.nodes:
        if highlight_node and node["id"] == highlight_node:
            node["size"] = 30
            node["color"] = "#f1c40f"
        elif node.get("type") == "Application":
            node["size"] = 18

    net.save_graph("temp_graph.html")
    with open("temp_graph.html", "r", encoding="utf-8") as f:
        return f.read()

init_db()
G, df_apps = fetch_data()

# ==============================================================================
# 3. SIDEBAR: TẠO HỒ SƠ VAY MỚI (NỘI DUNG NGUYÊN BẢN)
# ==============================================================================
st.sidebar.title("🤖 AI Risk Management")

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
        
        submit_btn = st.form_submit_button("🚀 Gửi Đơn Vay & AI Evaluation", use_container_width=True)
        if submit_btn:
            app_id, risk, decision = add_new_application(new_name, new_nid, new_amount, new_ip, new_fp, new_lat, new_lng, new_proxy)
            if decision == "APPROVED":
                st.sidebar.success(f"✅ Đã duyệt đơn {app_id}! Risk: {risk}%")
            else:
                st.sidebar.error(f"🚨 Từ chối đơn {app_id}! Risk: {risk}%")
            st.rerun()

app_list = [n for n, d in G.nodes(data=True) if d.get("type") == "Application"]
selected_app = st.sidebar.selectbox("📋 Chọn Hồ Sơ Xem Chi Tiết:", app_list if app_list else ["N/A"])

# ==============================================================================
# 4. TOP NAVBAR HEADER (ĐÚNG CHUYÊN NGÀNH AI / TÍN DỤNG)
# ==============================================================================
st.markdown('''
<div class="top-header">
    <div class="brand-logo">NEXUS<span>AI</span></div>
</div>
''', unsafe_allow_html=True)

nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6 = st.columns([1.2, 1.2, 1.3, 1.2, 1.3, 1.3])

with nav_col1: 
    if st.button("TRANG CHỦ", key="nb1"): st.session_state.active_tab = "Overview"
with nav_col2: 
    if st.button("MÔ HÌNH AI", key="nb2"): st.session_state.active_tab = "Rules Engine"
with nav_col3: 
    if st.button("ĐỒ THỊ NETWORK", key="nb3"): st.session_state.active_tab = "Network Graph"
with nav_col4: 
    if st.button("BẢN ĐỒ GEOIP", key="nb4"): st.session_state.active_tab = "GeoIP Map"
with nav_col5: 
    if st.button("ANALYTICS & BÁO CÁO", key="nb5"): st.session_state.active_tab = "Analytics AI"
with nav_col6:
    st.button("Liên hệ ngay", key="btn_contact")

# ==============================================================================
# 5. HERO BANNER
# ==============================================================================
st.markdown('<div class="hero-container"></div>', unsafe_allow_html=True)

# ==============================================================================
# 6. GREEN SEARCH BAR (BAR LỌC NHANH TRUY VẤN AI)
# ==============================================================================
st.markdown('<div class="search-section">', unsafe_allow_html=True)
s_col1, s_col2, s_col3, s_col4 = st.columns([1, 1, 1, 1])

with s_col1:
    st.markdown("<span style='color:white; font-weight:bold; font-size:0.85rem;'>Chọn tỉnh/thành phố</span>", unsafe_allow_html=True)
    sel_city = st.selectbox("", ["Chọn tỉnh/thành phố", "TP. Hồ Chí Minh", "Hà Nội", "Đà Nẵng"], label_visibility="collapsed")

with s_col2:
    st.markdown("<span style='color:white; font-weight:bold; font-size:0.85rem;'>Chọn loại rủi ro</span>", unsafe_allow_html=True)
    sel_type = st.selectbox("", ["Chọn loại rủi ro", "Gian lận IP/Device", "Proxy / VPN", "Blacklist trùng lặp"], label_visibility="collapsed")

with s_col3:
    st.markdown("<span style='color:white; font-weight:bold; font-size:0.85rem;'>Chọn trạng thái AI</span>", unsafe_allow_html=True)
    sel_status = st.selectbox("", ["Chọn trạng thái AI", "Đã duyệt (APPROVED)", "Từ chối (REJECTED)"], label_visibility="collapsed")

with s_col4:
    st.markdown("<div style='height: 22px;'></div>", unsafe_allow_html=True)
    if st.button("🔍 PHÂN TÍCH NHANH", use_container_width=True, key="search_btn"):
        st.session_state.active_tab = "Analytics AI"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# 7. SECTION CONTROLLER (CÁC CHỨC NĂNG BÊN TRONG CỦA BẠN)
# ==============================================================================

if st.session_state.active_tab == "Overview":
    st.markdown('''
    <div class="section-title-box">
        <div class="section-subtitle">//</div>
        <div class="section-main-title">HỒ SƠ AI PHÂN TÍCH NỔI BẬT</div>
        <div class="section-desc">Tổng hợp các hồ sơ xin cấp hạn mức tín dụng BNPL được đánh giá bởi thuật toán AI & Graph Neural Network thời điểm hiện tại</div>
    </div>
    ''', unsafe_allow_html=True)

    # Hiển thị dạng Card 3 cột chuẩn Portal BDS05
    card_imgs = [
        "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=1000&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=1000&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?q=80&w=1000&auto=format&fit=crop"
    ]
    
    grid_cols = st.columns(3)
    for idx, (_, row) in enumerate(df_apps.head(3).iterrows()):
        with grid_cols[idx % 3]:
            is_fraud = (row["decision"] == "REJECTED")
            badge_class = "badge-vip badge-vip-rejected" if is_fraud else "badge-vip"
            badge_text = "REJECTED" if is_fraud else "APPROVED"
            
            st.markdown(f'''
            <div class="bds-card">
                <div class="card-img-container">
                    <img src="{card_imgs[idx % 3]}" class="card-img" />
                    <div class="badge-new">Mới đánh giá</div>
                    <div class="{badge_class}"></div>
                    <div class="badge-vip-text">{badge_text}</div>
                </div>
                <div class="card-body">
                    <div class="card-title">Hồ sơ: {row["customer_name"]} – Mã: {row["app_id"]}</div>
                    <div style="color: #7f8c8d; font-size: 0.8rem; margin-bottom: 0.5rem;">
                        <b>Điểm nổi bật của AI Engine:</b><br>
                        Phân tích liên kết mạng lưới IP, Device Hash & Tọa độ GeoIP...
                    </div>
                    <div class="card-info">📍 CCCD: <b>{row["national_id"]}</b></div>
                    <div class="card-info">🌐 Địa chỉ IP: <b>{row["ip_address"]}</b></div>
                    <div class="card-info">📐 Device Hash: <b>{row["device_hash"]}</b></div>
                    <div class="card-info">🚨 Risk Score: <b>{row["risk_score"]}%</b></div>
                    <div class="card-footer-custom" style="display:flex; justify-content:space-between; align-items:center; margin-top:10px;">
                        <div class="price-tag">{row["loan_amount"]:,.0f} VNĐ</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            if st.button("Xem chi tiết ➔", key=f"btn_det_{row['app_id']}", use_container_width=True):
                st.session_state.active_tab = "Network Graph"
                st.rerun()

    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    
    col_graph, col_info = st.columns([1.8, 1.2])
    with col_graph:
        st.markdown("##### 🕸️ Mạng Lưới Đồ Thị Liên Kết Đơn Vay")
        graph_html = render_pyvis_graph(G, highlight_node=selected_app, height="430px")
        components.html(graph_html, height=450)

    with col_info:
        st.markdown(f"##### 🎯 Chi Tiết Hồ Sơ Đang Chọn: `{selected_app}`")
        if selected_app in G.nodes:
            app_info = df_apps[df_apps["app_id"] == selected_app].iloc[0]
            is_bad = (app_info["decision"] == "REJECTED")
            
            st.metric("Khách hàng", app_info["customer_name"])
            st.metric("Số CCCD/CMND", app_info["national_id"])
            st.metric("Khoản Vay Yêu Cầu", f"{app_info['loan_amount']:,.0f} VNĐ")
            st.metric("Điểm Rủi Ro AI", f"{app_info['risk_score']}%", 
                      delta="🚨 TỪ CHỐI (RỦI RO CAO)" if is_bad else "✅ DUYỆT (AN TOÀN)", 
                      delta_color="inverse" if is_bad else "normal")

elif st.session_state.active_tab == "Network Graph":
    st.markdown('''
    <div class="section-title-box">
        <div class="section-subtitle">//</div>
        <div class="section-main-title">ĐỒ THỊ MẠNG LƯỚI INTERACTIVE</div>
        <div class="section-desc">Kéo thả các Node, cuộn chuột để Zoom in/out hoặc di chuột vào các Node để xem thuộc tính liên kết giữa các tài khoản vay</div>
    </div>
    ''', unsafe_allow_html=True)
    
    graph_html = render_pyvis_graph(G, highlight_node=selected_app, height="600px")
    components.html(graph_html, height=620)

elif st.session_state.active_tab == "Analytics AI":
    st.markdown('''
    <div class="section-title-box">
        <div class="section-subtitle">//</div>
        <div class="section-main-title">ANALYTICS AI & QUẢN LÝ DỮ LIỆU</div>
        <div class="section-desc">Hệ thống tổng hợp chỉ số rủi ro, bộ lọc dữ liệu thông minh và xuất báo cáo CSV</div>
    </div>
    ''', unsafe_allow_html=True)
    
    total_apps = len(df_apps)
    rejected_apps = len(df_apps[df_apps["decision"] == "REJECTED"])
    approved_apps = len(df_apps[df_apps["decision"] == "APPROVED"])
    fraud_rate = (rejected_apps / total_apps * 100) if total_apps > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tổng Số Đơn Vay", total_apps)
    m2.metric("Số Đơn Đã Duyệt", approved_apps)
    m3.metric("Số Đơn Từ Chối", rejected_apps)
    m4.metric("Tỷ Lệ Rủi Ro (Fraud Rate)", f"{fraud_rate:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 🔍 Bộ Lọc & Tìm Kiếm Dữ Liệu Hồ Sơ")
    
    flt1, flt2, flt3 = st.columns([1.5, 1, 1])
    search_q = flt1.text_input("🔎 Tìm theo Tên hoặc Mã đơn:", "")
    status_q = flt2.selectbox("Trạng thái:", ["Tất cả", "APPROVED", "REJECTED"])
    risk_q = flt3.slider("Khoảng Risk Score:", 0.0, 100.0, (0.0, 100.0))

    filtered_df = df_apps.copy()
    if search_q:
        filtered_df = filtered_df[filtered_df["customer_name"].str.contains(search_q, case=False) | filtered_df["app_id"].str.contains(search_q, case=False)]
    if status_q != "Tất cả":
        filtered_df = filtered_df[filtered_df["decision"] == status_q]
    filtered_df = filtered_df[(filtered_df["risk_score"] >= risk_q[0]) & (filtered_df["risk_score"] <= risk_q[1])]

    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Xuất Báo Cáo Dữ Liệu AI (CSV)", data=csv_data, file_name="nexus_ai_risk_report.csv", mime="text/csv")

elif st.session_state.active_tab == "GeoIP Map":
    st.markdown('''
    <div class="section-title-box">
        <div class="section-subtitle">//</div>
        <div class="section-main-title">BẢN ĐỒ VỊ TRÍ REALTIME GEOIP</div>
        <div class="section-desc">Theo dõi tọa độ thực tế của khách hàng vay, phát hiện VPN/Proxy che giấu vị trí địa lý</div>
    </div>
    ''', unsafe_allow_html=True)
    
    map_df = df_apps.copy()
    map_df["color"] = map_df["decision"].apply(lambda x: [244, 63, 94, 200] if x == "REJECTED" else [16, 185, 129, 200])
    map_df["elevation"] = map_df["risk_score"] * 50

    view_state = pdk.ViewState(
        latitude=map_df["latitude"].mean() if not map_df.empty else 10.7769,
        longitude=map_df["longitude"].mean() if not map_df.empty else 106.7009,
        zoom=10,
        pitch=45
    )

    layer_column = pdk.Layer(
        "ColumnLayer",
        data=map_df,
        get_position=["longitude", "latitude"],
        get_elevation="elevation",
        elevation_scale=1,
        radius=180,
        get_fill_color="color",
        pickable=True,
        extruded=True
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer_column], 
        initial_view_state=view_state, 
        tooltip={"text": "Mã đơn: {app_id}\nKhách hàng: {customer_name}\nĐiểm Risk: {risk_score}%\nTrạng thái: {decision}"}
    ))

elif st.session_state.active_tab == "Rules Engine":
    st.markdown('''
    <div class="section-title-box">
        <div class="section-subtitle">//</div>
        <div class="section-main-title">MÔ HÌNH & RULES CẤU HÌNH AI ENGINE</div>
        <div class="section-desc">Thay đổi trọng số rủi ro trực tiếp trên giao diện và áp dụng tức thời vào thuật toán chấm điểm</div>
    </div>
    ''', unsafe_allow_html=True)

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.session_state.risk_threshold = st.slider(
            "Ngưỡng Risk Score TỪ CHỐI (Reject Threshold):", 
            min_value=10.0, max_value=90.0, value=float(st.session_state.risk_threshold), step=5.0
        )
        st.session_state.proxy_penalty = st.slider(
            "Điểm phạt khi phát hiện Proxy/VPN:", 
            min_value=0.0, max_value=50.0, value=float(st.session_state.proxy_penalty), step=5.0
        )

    with col_r2:
        st.session_state.blacklist_penalty = st.slider(
            "Điểm phạt khi trùng IP/Device từng bị Từ chối:", 
            min_value=0.0, max_value=50.0, value=float(st.session_state.blacklist_penalty), step=5.0
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.success(f"✅ **Cấu hình hiện tại:** Đơn vay sẽ bị TỪ CHỐI nếu Điểm Rủi Ro >= **{st.session_state.risk_threshold}%**.")

# ==============================================================================
# 8. SECTION FOOTER "VÌ SAO BẠN CHỌN NEXUS AI?"
# ==============================================================================
st.markdown('''
<div class="why-section">
    <div class="why-title">Vì sao bạn chọn NEXUS AI?</div>
    <div class="why-subtitle">Chúng tôi cung cấp đầy đủ và chính xác nhất thông tin đánh giá rủi ro tín dụng trên toàn quốc song hành với dịch vụ tư vấn nhanh chóng và hiệu quả</div>
</div>
''', unsafe_allow_html=True)

f_col1, f_col2, f_col3 = st.columns(3)

with f_col1:
    st.markdown('''
    <div style="text-align: center; padding: 0 1rem;">
        <div class="feature-icon">⚙️</div>
        <div class="feature-title">Chất lượng tốt nhất</div>
        <div class="feature-desc">Nghiên cứu, thiết kế và phát triển mô hình AI xét duyệt tín dụng với hệ thống dịch vụ chất lượng tốt nhất.</div>
    </div>
    ''', unsafe_allow_html=True)

with f_col2:
    st.markdown('''
    <div style="text-align: center; padding: 0 1rem;">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">Tìm kiếm thông tin dễ dàng</div>
        <div class="feature-desc">Tìm kiếm lịch sử tín dụng và ma trận rủi ro bạn muốn theo danh mục cực kỳ dễ dàng.</div>
    </div>
    ''', unsafe_allow_html=True)

with f_col3:
    st.markdown('''
    <div style="text-align: center; padding: 0 1rem;">
        <div class="feature-icon">🔗</div>
        <div class="feature-title">Kết nối với nhà đầu tư</div>
        <div class="feature-desc">Nền tảng AI sẽ mang đến những giải pháp bảo vệ dòng vốn tốt nhất đáp ứng nhu cầu của bạn.</div>
    </div>
    ''', unsafe_allow_html=True)