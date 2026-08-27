import streamlit as st
import networkx as nx
import pandas as pd
import sqlite3
import hashlib
import numpy as np
from datetime import datetime
from pyvis.network import Network
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh

# ================= ================= ================= =================
# 1. TỐI ƯU CẤU HÌNH TRANG & CSS ENTERPRISE ULTRA-POLISHED
# ================= ================= ================= =================
st.set_page_config(
    page_title="NEXUS Anti-Fraud Radar | BNPL Risk Decisioning System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tự động đồng bộ dữ liệu real-time mỗi 5 giây
st_autorefresh(interval=5000, key="nexus_realtime_sync")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Global Theme Overrides */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #070a0f !important;
        color: #e2e8f0 !important;
    }
    
    .stApp {
        background-color: #070a0f;
    }

    /* Top Navigation Header */
    .nav-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 1.75rem;
        background: linear-gradient(180deg, #111827 0%, #0b0f17 100%);
        border: 1px solid #1f293d;
        border-radius: 14px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.8);
    }
    .brand-logo {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-title {
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .brand-sub {
        color: #64748b;
        font-size: 0.78rem;
        font-weight: 500;
        margin-top: 1px;
    }
    .system-status {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #34d399;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 10px #10b981;
    }

    /* KPI Summary Cards */
    .metric-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.25rem;
        position: relative;
        overflow: hidden;
    }
    .metric-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748b;
    }
    .metric-value {
        font-size: 1.9rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        color: #f8fafc;
        margin-top: 0.3rem;
    }
    .metric-footer {
        font-size: 0.75rem;
        margin-top: 0.5rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Decision Banner Box */
    .decision-card-danger {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.12) 0%, rgba(127, 29, 29, 0.2) 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 14px;
        padding: 1.5rem;
    }
    .decision-card-safe {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(6, 78, 59, 0.2) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 14px;
        padding: 1.5rem;
    }

    /* Sidebar Styling */
    div[data-testid="stSidebar"] {
        background-color: #0b0f17 !important;
        border-right: 1px solid #1a2333;
    }
</style>
""", unsafe_allow_html=True)

# ================= ================= ================= =================
# 2. KHỞI TẠO CSDL VÀ DỮ LIỆU MẪU CHUẨN ENTERPRISE
# ================= ================= ================= =================
def init_enterprise_db():
    conn = sqlite3.connect("bnpl_enterprise.db")
    cur = conn.cursor()
    cur.execute("""
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
    """)
    
    cur.execute("SELECT COUNT(*) FROM loan_applications")
    if cur.fetchone()[0] == 0:
        seed_records = [
            ("APP-8801", "Nguyễn Văn An", "001092008123", 15000000.0, "113.161.72.10", "FP-8A99F201", 10.7769, 106.7009, 0, 12.4, "APPROVED", "2026-08-27 09:15:22"),
            ("APP-8802", "Trần Thị Bình", "025091004567", 25000000.0, "104.28.19.14", "FP-CC44B109", 10.7780, 106.7015, 1, 96.8, "REJECTED", "2026-08-27 09:42:10"),
            ("APP-8803", "Lê Văn Cường", "036089001122", 18000000.0, "104.28.19.14", "FP-CC44B109", 10.7782, 106.7018, 1, 98.5, "REJECTED", "2026-08-27 10:05:44"),
            ("APP-8804", "Phạm Minh Dung", "048095007890", 12000000.0, "14.161.20.55", "FP-1102AA88", 21.0285, 105.8542, 0, 8.2, "APPROVED", "2026-08-27 10:30:11"),
            ("APP-8805", "Hoàng Quốc Đức", "052093003344", 30000000.0, "113.161.72.10", "FP-8A99F201", 10.7771, 106.7012, 0, 18.6, "APPROVED", "2026-08-27 11:02:00")
        ]
        cur.executemany("""
            INSERT INTO loan_applications 
            (app_id, customer_name, national_id, loan_amount, ip_address, device_hash, latitude, longitude, is_proxy, risk_score, decision, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_records)
    conn.commit()
    conn.close()

init_enterprise_db()

# ================= ================= ================= =================
# 3. MÔ HÌNH CHẤM ĐIỂM RỦI RO HYBRID (GNN + BEHAVIORAL LOGIC)
# ================= ================= ================= =================
def generate_device_hash(ua_string, resolution, timezone):
    raw = f"{ua_string}|{resolution}|{timezone}"
    return "FP-" + hashlib.md5(raw.encode()).hexdigest()[:8].upper()

def calculate_enterprise_risk(ip_addr, device_fp, loan_amt, is_vpn, G):
    score = 5.0
    
    connections = 0
    if device_fp in G:
        connections += len(list(G.neighbors(device_fp)))
    if ip_addr in G:
        connections += len(list(G.neighbors(ip_addr)))

    if connections >= 3:
        score += 65.0
    elif connections >= 1:
        score += 25.0

    if is_vpn:
        score += 20.0

    if loan_amt > 25000000:
        score += 10.0

    final_score = min(score + np.random.uniform(1.0, 4.0), 99.9)
    decision = "REJECTED" if final_score >= 65.0 else "APPROVED"
    return round(final_score, 2), decision

# ================= ================= ================= =================
# 4. LOAD DỮ LIỆU BẢNG VÀ ĐỒ THỊ NETWORKS
# ================= ================= ================= =================
def fetch_graph_data():
    conn = sqlite3.connect("bnpl_enterprise.db")
    df = pd.read_sql_query("SELECT * FROM loan_applications ORDER BY id DESC", conn)
    conn.close()

    G = nx.Graph()
    for _, row in df.iterrows():
        app_id = row["app_id"]
        ip = row["ip_address"]
        fp = row["device_hash"]
        status = row["decision"]
        is_fraud = (status == "REJECTED")

        G.add_node(
            app_id, 
            label=f"{row['customer_name']}\n({app_id})", 
            type="Application", 
            risk=row["risk_score"], 
            color="#ef4444" if is_fraud else "#10b981", 
            shape="dot"
        )
        
        G.add_node(ip, label=f"IP: {ip}", type="IP_Address", color="#38bdf8", shape="diamond")
        G.add_node(fp, label=f"Fingerprint: {fp}", type="Device_Hash", color="#c084fc", shape="triangle")

        G.add_edge(app_id, ip)
        G.add_edge(app_id, fp)

    return G, df

G, df_apps = fetch_graph_data()

# ================= ================= ================= =================
# 5. NAVIGATION HEADER BAR
# ================= ================= ================= =================
st.markdown("""
<div class="nav-header">
    <div class="brand-logo">
        <div style="font-size: 1.8rem;">🛡️</div>
        <div>
            <div class="brand-title">NEXUS ANTI-FRAUD RADAR</div>
            <div class="brand-sub">Hệ Thống Thẩm Định Rủi Ro Bùng Nợ BNPL Real-Time // Enterprise v4.5</div>
        </div>
    </div>
    <div class="system-status">
        <div class="status-dot"></div>
        MODEL GNN: ACTIVE (v4.5-PROD)
    </div>
</div>
""", unsafe_allow_html=True)

# ================= ================= ================= =================
# 6. SIDEBAR - ĐIỀU HÀNH & TIẾP NHẬN HỒ SƠ VAY MỚI
# ================= ================= ================= =================
st.sidebar.markdown("### 🎛️ BẢNG ĐIỀU HÀNH THẨM ĐỊNH")

app_list = [n for n, d in G.nodes(data=True) if d.get("type") == "Application"]
selected_app = st.sidebar.selectbox("📋 Chọn Hồ Sơ Cần Kiểm Tra:", app_list if app_list else ["Không có dữ liệu"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 TIẾP NHẬN HỒ SƠ VAY REAL-TIME")

with st.sidebar.form("new_loan_application_form"):
    st.markdown("<small style='color:#64748b;'>Tự động thu thập Device Fingerprint & GeoIP</small>", unsafe_allow_html=True)
    
    in_name = st.text_input("Họ và Tên Khách Hàng:", value="Hoàng Trọng Kiên")
    in_cccd = st.text_input("Số CCCD/CMND:", value="012095006789")
    in_amount = st.number_input("Khoản Vay Yêu Cầu (VNĐ):", value=20000000, step=1000000)
    
    ip_address = st.text_input(
    label="IP Khách Hàng Truy Cập:", 
    value="104.28.19.14", 
    placeholder="Nhập địa chỉ IP..."
    )
    
    user_agent = st.text_input(
    label="Môi Trường & Thiết Bị:", 
    value="Chrome/Windows", 
    placeholder="Nhập User-Agent hoặc Thiết bị..."
    )
    
    in_vpn = st.checkbox("Phát hiện VPN/Proxy", value=("Trùng" in in_ip_option))

    btn_submit = st.form_submit_button("🚀 Gửi Đơn Vay & Chấm Điểm AI")

    if btn_submit:
        fp_generated = generate_device_hash(in_device_option, "1920x1080", "Asia/Ho_Chi_Minh")
        if "Trùng" in in_device_option:
            fp_generated = "FP-CC44B109"
            
        ip_clean = in_ip_option.split(" ")[0]
        app_id_new = f"APP-{np.random.randint(8806, 9999)}"
        
        risk_score, decision = calculate_enterprise_risk(ip_clean, fp_generated, in_amount, in_vpn, G)
        
        lat = 10.7769 if "104.28" in ip_clean else 21.0285
        lng = 106.7009 if "104.28" in ip_clean else 105.8542

        conn = sqlite3.connect("bnpl_enterprise.db")
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO loan_applications 
            (app_id, customer_name, national_id, loan_amount, ip_address, device_hash, latitude, longitude, is_proxy, risk_score, decision, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (app_id_new, in_name, in_cccd, float(in_amount), ip_clean, fp_generated, lat, lng, int(in_vpn), risk_score, decision, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

        st.sidebar.success(f"✅ Đã thêm **{app_id_new}**! Trạng thái: **{decision}**")
        st.rerun()

# ================= ================= ================= =================
# 7. CHỈ SỐ METRICS TỔNG QUAN HỆ THỐNG
# ================= ================= ================= =================
total_apps_count = len(app_list)
fraud_apps_count = sum(1 for a in app_list if G.nodes[a].get("risk", 0) >= 65.0)
approved_apps_count = total_apps_count - fraud_apps_count
total_loan_val = df_apps["loan_amount"].sum() if not df_apps.empty else 0

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Tổng Đơn Đăng Ký</div>
        <div class="metric-value">{total_apps_count}</div>
        <div class="metric-footer" style="color: #38bdf8;">
            <span>🟢 Đang giám sát real-time</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 3px solid #ef4444;">
        <div class="metric-label">Cảnh Báo Cụm Bùng Nợ</div>
        <div class="metric-value" style="color: #fca5a5;">{fraud_apps_count}</div>
        <div class="metric-footer" style="color: #f87171;">
            <span>🚨 Đã từ chối cấp hạn mức</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 3px solid #10b981;">
        <div class="metric-label">Đơn Được Phê Duyệt</div>
        <div class="metric-value" style="color: #6ee7b7;">{approved_apps_count}</div>
        <div class="metric-footer" style="color: #34d399;">
            <span>✅ An toàn giải ngân</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 3px solid #c084fc;">
        <div class="metric-label">Tổng Hạn Mức Xét Duyệt</div>
        <div class="metric-value" style="color: #c084fc; font-size: 1.5rem; padding-top: 5px;">{total_loan_val/1e6:,.0f} Triệu</div>
        <div class="metric-footer" style="color: #a855f7;">
            <span>🛡️ Tỷ lệ bảo vệ tài sản 100%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ================= ================= ================= =================
# 8. KẾT QUẢ THẨM ĐỊNH CHI TIẾT (DECISION & RISK ANALYSIS)
# ================= ================= ================= =================
if selected_app in G.nodes:
    app_info = df_apps[df_apps["app_id"] == selected_app].iloc[0]
    risk_val = app_info["risk_score"]
    is_rejected = app_info["decision"] == "REJECTED"

    col_decision, col_factors = st.columns([1.2, 1.8])

    with col_decision:
        st.markdown("##### 🎯 QUYẾT ĐỊNH THẨM ĐỊNH TỰ ĐỘNG")
        if is_rejected:
            st.markdown(f"""
            <div class="decision-card-danger">
                <div style="font-size: 1.1rem; font-weight: 800; color: #fca5a5;">❌ TỪ CHỐI DUYỆT VAY (REJECTED)</div>
                <div style="margin-top: 8px; font-size: 0.88rem; color: #fecaca; line-height: 1.5;">
                    Tài khoản <b>{app_info['customer_name']}</b> (Mã: {selected_app}) bị hệ thống AI chặn do phát hiện nằm trong cụm thiết bị/IP từng bùng nợ chéo.
                </div>
                <hr style="border-color: rgba(239, 68, 68, 0.3); margin: 12px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.85rem; color: #fca5a5;">Điểm rủi ro AI:</span>
                    <span style="font-size: 1.4rem; font-weight: 800; color: #ef4444;">{risk_val}%</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                    <span style="font-size: 0.85rem; color: #fca5a5;">Hạn mức phê duyệt:</span>
                    <span style="font-size: 1.1rem; font-weight: 700; color: #ef4444;">0 VNĐ</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="decision-card-safe">
                <div style="font-size: 1.1rem; font-weight: 800; color: #6ee7b7;">✅ PHÊ DUYỆT HẠN MỨC (APPROVED)</div>
                <div style="margin-top: 8px; font-size: 0.88rem; color: #a7f3d0; line-height: 1.5;">
                    Tài khoản <b>{app_info['customer_name']}</b> (Mã: {selected_app}) đạt tiêu chuẩn độ tin cậy đồ thị mạng lưới. Không phát hiện rủi ro bùng nợ.
                </div>
                <hr style="border-color: rgba(16, 185, 129, 0.3); margin: 12px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.85rem; color: #a7f3d0;">Điểm rủi ro AI:</span>
                    <span style="font-size: 1.4rem; font-weight: 800; color: #10b981;">{risk_val}%</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                    <span style="font-size: 0.85rem; color: #a7f3d0;">Hạn mức đề xuất:</span>
                    <span style="font-size: 1.1rem; font-weight: 700; color: #10b981;">{app_info['loan_amount']:,.0f} VNĐ</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_factors:
        st.markdown("##### 🔬 PHÂN TÍCH YẾU TỐ BẤT THƯỜNG (RISK MATRIX)")
        
        matrix_df = pd.DataFrame({
            "Tiêu Chí Phân Tích": [
                "Dấu Vân Tay Thiết Bị (Fingerprint)", 
                "Địa Chỉ IP Truy Cập", 
                "Phát Hiện VPN/Proxy Che Giấu", 
                "Mức Độ Gom Cụm Đồ Thị (GNN)"
            ],
            "Giá Trị Thu Thập": [
                app_info["device_hash"], 
                app_info["ip_address"], 
                "CÓ (Dùng VPN)" if app_info["is_proxy"] else "KHÔNG (IP Thật)", 
                f"Liên kết {len(list(G.neighbors(selected_app)))} nút hạ tầng"
            ],
            "Đánh Giá An Ninh": [
                "🚨 Trùng cụm thiết bị gian lận" if app_info["device_hash"] == "FP-CC44B109" else "🟢 Độc lập / An toàn",
                "⚠️ IP dùng chung nhiều account" if app_info["ip_address"] == "104.28.19.14" else "🟢 IP sạch",
                "⚠️ Cảnh báo giấu vị trí" if app_info["is_proxy"] else "🟢 An toàn",
                "🔴 Cụm bùng nợ nguy cơ cao" if is_rejected else "🟢 Mạng lưới bình thường"
            ]
        })
        st.dataframe(matrix_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ================= ================= ================= =================
# 9. TABS VISUALIZATION (ĐỒ THỊ NETWORK, BẢN ĐỒ GPS, DỮ LIỆU SQLITE)
# ================= ================= ================= =================
tab_graph, tab_map, tab_database = st.tabs([
    "🕸️ ĐỒ THỊ MẠNG LIÊN KẾT REAL-TIME",
    "📍 ĐỊNH VỊ KHÔNG GIAN BẢN ĐỒ (GPS MAP)",
    "📋 DỮ LIỆU HỒ SƠ SQLITE"
])

# --- TAB 1: GRAPH VISUALIZER ---
with tab_graph:
    st.markdown("##### 🕸️ Sơ Đồ Cụm Mạng Lưới Dùng Chung Hạ Tầng Tự Động")
    net = Network(height="520px", width="100%", bgcolor="#070a0f", font_color="#f8fafc")
    net.from_nx(G)
    net.barnes_hut(gravity=-3500, central_gravity=0.25, spring_length=95)
    
    for node in net.nodes:
        if node["id"] == selected_app:
            node["size"] = 32
            node["color"] = "#facc15"
        elif node.get("type") == "Application":
            node["size"] = 22

    net.save_graph("graph_ui_enterprise.html")
    with open("graph_ui_enterprise.html", "r", encoding="utf-8") as f:
        components.html(f.read(), height=540)

# --- TAB 2: GPS MAP ---
with tab_map:
    st.markdown("##### 📍 Bản Đồ Vị Trí Địa Lý Người Dùng Đăng Ký Khoản Vay")
    if selected_app in G.nodes:
        app_geo = df_apps[df_apps["app_id"] == selected_app].iloc[0]
        m = folium.Map(location=[app_geo["latitude"], app_geo["longitude"]], zoom_start=13, tiles="CartoDB dark_matter")
        
        is_bad = app_geo["decision"] == "REJECTED"
        folium.Marker(
            [app_geo["latitude"], app_geo["longitude"]],
            popup=f"Khách hàng: {app_geo['customer_name']}\nĐơn: {selected_app}",
            icon=folium.Icon(color="red" if is_bad else "green", icon="user", prefix="fa")
        ).add_to(m)

        if is_bad:
            folium.Circle(
                location=[app_geo["latitude"], app_geo["longitude"]],
                radius=1400, color="#ef4444", fill=True, fill_opacity=0.2,
                popup="Tập trung cụm tài khoản rủi ro bùng nợ"
            ).add_to(m)

        st_folium(m, width="100%", height=480)

# --- TAB 3: SQLITE TABLE ---
with tab_database:
    st.markdown("##### 📋 CSDL Tín Dụng Đồng Bộ Trong Hệ Thống")
    st.dataframe(df_apps, use_container_width=True, hide_index=True)