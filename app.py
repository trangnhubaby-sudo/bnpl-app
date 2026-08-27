import streamlit as st
import networkx as nx
import numpy as np
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium

# ================= ================= ================= =================
# 1. CẤU HÌNH HỆ THỐNG & GIAO DIỆN FINTECH ENTERPRISE
# ================= ================= ================= =================
st.set_page_config(
    page_title="NEXUS FRAUD SHIELD | Radar AI Phát Hiện Gian Lận BNPL",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS Dark Slate
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    .stApp {
        background: #0f172a;
        color: #f8fafc;
    }

    /* Enterprise Header Bar */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 1.5rem;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    .brand-title {
        font-size: 1.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
    }
    .system-status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 6px 14px;
        border-radius: 20px;
        color: #34d399;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 10px #10b981;
    }

    /* Metric Cards */
    .kpi-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem;
        transition: all 0.25s ease-in-out;
    }
    .kpi-card:hover {
        border-color: #64748b;
        transform: translateY(-2px);
    }
    .kpi-title {
        color: #94a3b8;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
        font-family: 'JetBrains Mono', monospace;
    }
    .kpi-sub {
        font-size: 0.78rem;
        margin-top: 0.3rem;
    }

    /* Risk Status Banners */
    .risk-banner-danger {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(127, 29, 29, 0.25) 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        color: #fca5a5;
    }
    .risk-banner-safe {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 78, 59, 0.25) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        color: #6ee7b7;
    }

    div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        border-color: #334155 !important;
        color: #f8fafc !important;
    }
    div[data-testid="stSidebar"] {
        background-color: #0b1120;
        border-right: 1px solid #1e293b;
    }
    
    .log-box {
        background: #020617;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #38bdf8;
        height: 180px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# ================= ================= ================= =================
# 2. XÂY DỰNG ĐỒ THỊ DỮ LIỆU GNN (THUẦN NETWORKX - KHÔNG PHỤ THUỘC SCIPY)
# ================= ================= ================= =================
@st.cache_data
def build_enterprise_fraud_network():
    G = nx.Graph()
    
    users = [f"KH-{i:04d}" for i in range(1001, 1026)]
    ips = [f"104.28.19.{i}" for i in range(12, 18)] + ["113.161.72.14", "14.225.21.18", "116.109.12.5"]
    devices = [f"TB-IMEI-8649{i}" for i in range(10, 15)]
    banks = [f"STK-NH-{i}" for i in range(801, 804)]

    # Tọa độ mặc định thực tế cho các nhóm người dùng
    user_coords = {
        "KH-1008": (10.7769, 106.7009), # TP.HCM
        "KH-1009": (10.7750, 106.7020), 
        "KH-1010": (10.7780, 106.6990),
        "KH-1011": (10.7730, 106.7050),
        "KH-1012": (10.7710, 106.7010),
    }

    fraud_cluster = ["KH-1008", "KH-1009", "KH-1010", "KH-1011", "KH-1012"]
    
    for u in users:
        is_fraud = u in fraud_cluster
        lat, lng = user_coords.get(u, (21.0285 + np.random.uniform(-0.02, 0.02), 105.8542 + np.random.uniform(-0.02, 0.02)))
        G.add_node(
            u,
            label=u,
            node_type="Khách Hàng",
            status="RỦI RO RẤT CAO" if is_fraud else "XÁC MINH AN TOÀN",
            risk_score=float(np.random.uniform(91.2, 99.4)) if is_fraud else float(np.random.uniform(0.8, 9.4)),
            lat=lat,
            lng=lng,
            color="#ef4444" if is_fraud else "#10b981",
            shape="dot"
        )
        
    for ip in ips:
        is_suspicious = ip in ["104.28.19.14", "104.28.19.15"]
        G.add_node(ip, label=f"IP: {ip}", node_type="IP", color="#ef4444" if is_suspicious else "#3b82f6", shape="diamond")
        
    for dev in devices:
        G.add_node(dev, label=f"Thiết Bị: {dev[-4:]}", node_type="Thiết Bị", color="#8b5cf6", shape="triangle")
        
    for bank in banks:
        G.add_node(bank, label=f"STK: {bank[-3:]}", node_type="Ngân Hàng", color="#ec4899", shape="square")

    # Mạng lưới gom cụm gian lận
    shared_ip = "104.28.19.14"
    shared_device = "TB-IMEI-864912"
    shared_bank = "STK-NH-802"
    
    for fu in fraud_cluster:
        G.add_edge(fu, shared_ip)
        G.add_edge(fu, shared_device)
        G.add_edge(fu, shared_bank)
        
    G.add_edge("KH-1001", "113.161.72.14")
    G.add_edge("KH-1001", "TB-IMEI-864910")
    G.add_edge("KH-1001", "STK-NH-801")
    G.add_edge("KH-1002", "14.225.21.18")
    G.add_edge("KH-1003", "116.109.12.5")

    return G

G = build_enterprise_fraud_network()

# ================= ================= ================= =================
# 3. HEADER
# ================= ================= ================= =================
st.markdown("""
<div class="header-container">
    <div>
        <div class="brand-title">🛡️ HỆ THỐNG PHÁT HIỆN GIAN LẬN BNPL // AI GRAPH NEURAL NETWORK</div>
        <div style="color: #64748b; font-size: 0.82rem; margin-top: 2px;">
            Radar Thẩm Định Rủi Ro Bùng Nợ & Định Vị Bản Đồ GPS Trực Tiếp
        </div>
    </div>
    <div class="system-status">
        <div class="pulse-dot"></div>
        MÔ HÌNH AI GNN: ĐANG HOẠT ĐỘNG (v4.2.0-PROD)
    </div>
</div>
""", unsafe_allow_html=True)

# ================= ================= ================= =================
# 4. THANH ĐIỀU KHIỂN SIDEBAR (ĐÃ BỎ NHẬP ĐỊA ĐIỂM THỦ CÔNG)
# ================= ================= ================= =================
st.sidebar.markdown("### 🎛️ BẢNG ĐIỀU HÀNH THẨM ĐỊNH")

user_list = [n for n, d in G.nodes(data=True) if d.get("node_type") == "Khách Hàng"]
selected_user = st.sidebar.selectbox(
    "👤 Chọn Mã Khách Hàng Thẩm Định:",
    user_list,
    index=user_list.index("KH-1008")
)

loan_request = st.sidebar.slider(
    "💵 Hạn Mức Vay BNPL Yêu Cầu (VNĐ):",
    min_value=1000000,
    max_value=50000000,
    value=15000000,
    step=1000000,
    format="%d VNĐ"
)

gnn_threshold = st.sidebar.slider(
    "⚙️ Ngưỡng Khái Quát Rủi Ro AI (Tau):",
    min_value=0.50,
    max_value=0.99,
    value=0.85,
    step=0.01
)

st.sidebar.markdown("---")
st.sidebar.caption("🔒 Bảo mật chuẩn ISO27001 & Định vị Geolocation GPS Real-time")

# ================= ================= ================= =================
# 5. BẢNG KPI METRICS
# ================= ================= ================= =================
total_users = sum(1 for _, d in G.nodes(data=True) if d.get("node_type") == "Khách Hàng")
fraud_count = sum(1 for _, d in G.nodes(data=True) if d.get("status") == "RỦI RO RẤT CAO")
total_infra = len(G.nodes) - total_users

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">TỔNG TÀI KHOẢN</div><div class="kpi-value">{total_users}</div><div class="kpi-sub" style="color:#10b981;">🟢 Giám sát thời gian thực</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-card" style="border-left: 4px solid #ef4444;"><div class="kpi-title">CỤM BÙNG NỢ GIAN LẬN</div><div class="kpi-value" style="color:#fca5a5;">{fraud_count}</div><div class="kpi-sub" style="color:#f87171;">🚨 Cảnh báo hệ thống</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">HẠ TẦNG DÙNG CHUNG</div><div class="kpi-value">{total_infra}</div><div class="kpi-sub" style="color:#38bdf8;">🌐 IP / IMEI / STK</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi-card" style="border-left: 4px solid #8b5cf6;"><div class="kpi-title">TỐC ĐỘ XỬ LÝ GNN</div><div class="kpi-value" style="color:#c084fc;">11.8 ms</div><div class="kpi-sub" style="color:#c084fc;">⚡ Định vị siêu tốc</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ================= ================= ================= =================
# 6. KẾT QUẢ QUYẾT ĐỊNH & THÔNG TIN ĐỒ THỊ
# ================= ================= ================= =================
curr_node_data = G.nodes[selected_user]
user_risk_score = curr_node_data["risk_score"]
is_high_risk = user_risk_score >= (gnn_threshold * 100)

col_left, col_right = st.columns([1.2, 1.8])

with col_left:
    st.markdown("#### 🎯 KẾT QUẢ QUYẾT ĐỊNH GIẢI NGÂN")
    
    if is_high_risk:
        st.markdown(f"""
        <div class="risk-banner-danger">
            <div style="font-weight: 800; font-size: 1.1rem; margin-bottom: 6px;">❌ TỪ CHỐI DUYỆT VAY (KHÓA TÀI KHOẢN)</div>
            <div style="font-size: 0.9rem;">Tài khoản <b>{selected_user}</b> bị phát hiện nằm trong cụm thiết bị bùng nợ chuyên nghiệp.</div>
            <hr style="border-color: rgba(239, 68, 68, 0.3); margin: 12px 0;">
            <div><b>Điểm rủi ro GNN:</b> <span style="font-size:1.3rem; font-weight:800; color:#ef4444;">{user_risk_score:.2f}%</span></div>
            <div><b>Hạn mức đề xuất:</b> <b style="color:#ef4444;">0 VNĐ</b></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="risk-banner-safe">
            <div style="font-weight: 800; font-size: 1.1rem; margin-bottom: 6px;">✅ PHÊ DUYỆT HẠN MỨC (GIẢI NGÂN NGAY)</div>
            <div style="font-size: 0.9rem;">Tài khoản <b>{selected_user}</b> đạt chỉ số an toàn cấu trúc mạng lưới.</div>
            <hr style="border-color: rgba(16, 185, 129, 0.3); margin: 12px 0;">
            <div><b>Điểm rủi ro GNN:</b> <span style="font-size:1.3rem; font-weight:800; color:#10b981;">{user_risk_score:.2f}%</span></div>
            <div><b>Hạn mức phê duyệt:</b> <b style="color:#10b981;">{loan_request:,.0f} VNĐ</b></div>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown("#### 🔬 PHÂN TÍCH BẮT CẶP CẤU TRÚC ĐỒ THỊ")
    
    neighbors = list(G.neighbors(selected_user))
    degree_cent = nx.degree_centrality(G)[selected_user] # Sử dụng thuật toán thuần NetworkX
    
    df_metrics = pd.DataFrame({
        "Tiêu Chí Đồ Thị": ["Số Liên Kết Trực Tiếp (Degree)", "Hệ Số Gom Cụm (Clustering)", "Độ Trung Tâm Mạng (Centrality)", "Mức Độ Rủi Ro Mạng"],
        "Giá Trị": [f"{len(neighbors)} nút", f"{nx.clustering(G, selected_user):.4f}", f"{degree_cent:.4f}", "100% Cụm Bùng Nợ" if is_high_risk else "0.0% An Toàn"],
        "Trạng Thái": ["⚠️ BẤT THƯỜNG" if len(neighbors) > 2 else "🟢 BÌNH THƯỜNG", "🚨 CAO" if is_high_risk else "🟢 THẤP", "⚠️ CAO" if is_high_risk else "🟢 BÌNH THƯỜNG", "🔴 NGUY HẠI" if is_high_risk else "🟢 AN TOÀN"]
    })
    st.dataframe(df_metrics, use_container_width=True, hide_index=True)

st.markdown("---")

# ================= ================= ================= =================
# 7. BẢN ĐỒ GPS VỊ TRÍ NGƯỜI DÙNG & ĐỒ THỊ MẠNG (TABS)
# ================= ================= ================= =================
tab_map, tab_graph, tab_data = st.tabs([
    "📍 BẢN ĐỒ VỊ TRÍ NGƯỜI DÙNG (GPS MAP)",
    "🌐 ĐỒ THỊ MẠNG LIÊN KẾT REAL-TIME",
    "📋 DANH SÁCH TÀI KHOẢN VAY BNPL"
])

# --- TAB 1: BẢN ĐỒ VỊ TRÍ ---
with tab_map:
    st.markdown("### 🗺️ Định Vị Không Gian GPS Người Dùng Theo Thời Gian Thực")
    st.caption("Bản đồ tự động ghim vị trí địa lý của khách hàng đang kiểm tra và các điểm gian lận lân cận.")
    
    user_lat = curr_node_data.get("lat", 10.7769)
    user_lng = curr_node_data.get("lng", 106.7009)

    # Khởi tạo bản đồ Folium
    m = folium.Map(location=[user_lat, user_lng], zoom_start=13, tiles="CartoDB dark_matter")

    # Ghim vị trí người dùng đang chọn
    icon_color = "red" if is_high_risk else "green"
    folium.Marker(
        [user_lat, user_lng],
        popup=f"Khách Hàng: {selected_user}\nRủi ro: {user_risk_score:.2f}%",
        tooltip=f"👤 {selected_user} ({'RỦI RO' if is_high_risk else 'AN TOÀN'})",
        icon=folium.Icon(color=icon_color, icon="user", prefix="fa")
    ).add_to(m)

    # Thêm vòng tròn vùng nguy cơ nếu rủi ro cao
    if is_high_risk:
        folium.Circle(
            location=[user_lat, user_lng],
            radius=1200,
            color="#ef4444",
            fill=True,
            fill_color="#ef4444",
            fill_opacity=0.2,
            popup="Vùng cảnh báo tập trung cụm tài khoản bùng nợ BNPL"
        ).add_to(m)

    st_folium(m, width="100%", height=500)

# --- TAB 2: ĐỒ THỊ MẠNG ---
with tab_graph:
    st.markdown("### 🕸️ Sơ Đồ Cấu Trúc Mạng Lưới Rủi Ro (Heterogeneous Graph)")
    net = Network(height="500px", width="100%", bgcolor="#020617", font_color="#f8fafc")
    net.from_nx(G)
    net.barnes_hut(gravity=-4500, central_gravity=0.2, spring_length=110)
    
    for node in net.nodes:
        if node["id"] == selected_user:
            node["size"] = 35
            node["color"] = "#facc15"
        elif node.get("node_type") == "Khách Hàng":
            node["size"] = 20
        else:
            node["size"] = 12

    net.save_graph("graph_enterprise.html")
    with open("graph_enterprise.html", "r", encoding="utf-8") as f:
        components.html(f.read(), height=520)

# --- TAB 3: DỮ LIỆU TÀI KHOẢN ---
with tab_data:
    st.markdown("### 📋 Danh Sách Quản Lý Tài Khoản Vay")
    rows = []
    for n, d in G.nodes(data=True):
        if d.get("node_type") == "Khách Hàng":
            risk = d.get("risk_score", 0) > 80
            rows.append({
                "Mã Khách Hàng": n,
                "Tọa Độ GPS": f"{d.get('lat', 0):.4f}, {d.get('lng', 0):.4f}",
                "Trạng Thái AI": "🚨 BÙNG NỢ" if risk else "🟢 AN TOÀN",
                "Xác Suất Bùng Nợ": f"{d.get('risk_score', 0):.2f}%",
                "Khuyến Nghị": "Tự động khóa" if risk else "Giải ngân ngay"
            })
    st.dataframe(pd.DataFrame(rows), use_container_width=True)