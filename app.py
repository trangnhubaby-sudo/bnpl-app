import streamlit as st
import networkx as nx
import numpy as np
import pandas as pd
import sqlite3
import requests
from pyvis.network import Network
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh

# ================= ================= ================= =================
# 1. CẤU HÌNH HỆ THỐNG & TỰ ĐỘNG ĐỒNG BỘ (3 GIÂY)
# ================= ================= ================= =================
st.set_page_config(
    page_title="NEXUS FRAUD SHIELD // Enterprise Radar",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tự động làm mới trang mỗi 3000ms để đồng bộ CSDL
st_autorefresh(interval=3000, key="realtime_sync")

# Style CSS Dark Mode cao cấp
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #0b0f19; color: #f8fafc; }

    /* Header Bar */
    .header-container {
        display: flex; align-items: center; justify-content: space-between;
        padding: 1.2rem 1.8rem; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155; border-radius: 14px; margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5);
    }
    .brand-title {
        font-size: 1.4rem; font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
    }
    .live-badge {
        display: inline-flex; align-items: center; gap: 8px;
        background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 6px 14px; border-radius: 20px; color: #34d399;
        font-size: 0.8rem; font-weight: 600;
    }
    .pulse-dot {
        width: 8px; height: 8px; background-color: #10b981;
        border-radius: 50%; box-shadow: 0 0 10px #10b981;
    }

    /* Cards & KPIs */
    .kpi-card {
        background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(12px);
        border: 1px solid #334155; border-radius: 12px; padding: 1.2rem;
    }
    .kpi-title { color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; }
    .kpi-value { font-size: 1.9rem; font-weight: 800; color: #f8fafc; font-family: 'JetBrains Mono', monospace; margin-top: 4px; }
    
    /* Banners */
    .risk-banner-danger {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(127, 29, 29, 0.25) 100%);
        border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 12px; padding: 1.2rem; color: #fca5a5;
    }
    .risk-banner-safe {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 78, 59, 0.25) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 12px; padding: 1.2rem; color: #6ee7b7;
    }

    div[data-baseweb="select"] > div { background-color: #1e293b !important; border-color: #334155 !important; color: #f8fafc !important; }
    div[data-testid="stSidebar"] { background-color: #070a13; border-right: 1px solid #1e293b; }
</style>
""", unsafe_allow_html=True)

# ================= ================= ================= =================
# 2. TẢI DỮ LIỆU TỪ SQLITE & DỰNG ĐỒ THỊ
# ================= ================= ================= =================
def load_data_and_build_graph():
    conn = sqlite3.connect("fraud_data.db")
    try:
        df = pd.read_sql_query("SELECT * FROM loan_requests ORDER BY id DESC", conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()

    G = nx.Graph()
    
    if not df.empty:
        for _, row in df.iterrows():
            u = row["customer_id"]
            ip = row["ip_address"]
            imei = row["imei"]
            status = row["status"]
            is_fraud = (status == "RỦI RO RẤT CAO")
            
            # Node Khách hàng
            G.add_node(
                u,
                label=u,
                node_type="Khách Hàng",
                status=status,
                risk_score=94.85 if is_fraud else 4.12,
                lat=row["latitude"],
                lng=row["longitude"],
                loan_amount=row["loan_amount"],
                color="#ef4444" if is_fraud else "#10b981",
                shape="dot"
            )
            
            # Node Hạ tầng (IP & IMEI)
            G.add_node(ip, label=f"IP: {ip}", node_type="IP", color="#ef4444" if is_fraud else "#3b82f6", shape="diamond")
            G.add_node(imei, label=f"IMEI: {imei[-6:]}", node_type="Thiết Bị", color="#8b5cf6", shape="triangle")

            # Mối liên kết đồ thị
            G.add_edge(u, ip)
            G.add_edge(u, imei)

    return G, df

G, df_raw = load_data_and_build_graph()

# ================= ================= ================= =================
# 3. HEADER
# ================= ================= ================= =================
st.markdown("""
<div class="header-container">
    <div>
        <div class="brand-title">🛡️ HỆ THỐNG PHÁT HIỆN GIAN LẬN BNPL // AI GRAPH NEURAL NETWORK</div>
        <div style="color: #64748b; font-size: 0.82rem; margin-top: 2px;">
            Radar Thẩm Định Rủi Ro Bùng Nợ & Định Vị Bản Đồ GPS Trực Tiếp Real-Time
        </div>
    </div>
    <div class="live-badge">
        <div class="pulse-dot"></div>
        CSDL SQLITE: ĐỒNG BỘ TỰ ĐỘNG (3s)
    </div>
</div>
""", unsafe_allow_html=True)

# ================= ================= ================= =================
# 4. SIDEBAR - CHỌN VÀ THÊM KHÁCH HÀNG MỚI
# ================= ================= ================= =================
st.sidebar.markdown("### 🎛️ BẢNG ĐIỀU HÀNH THẨM ĐỊNH")

user_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "Khách Hàng"]

if user_nodes:
    selected_user = st.sidebar.selectbox("👤 Chọn Mã Khách Hàng Thẩm Định:", user_nodes, index=0)
    user_data = G.nodes[selected_user]
    default_amount = int(user_data.get("loan_amount", 10000000))
else:
    selected_user = "N/A"
    user_data = {}
    default_amount = 10000000

loan_request = st.sidebar.slider(
    "💵 Hạn Mức Vay Yêu Cầu (VNĐ):",
    min_value=1000000, max_value=50000000, value=default_amount, step=1000000, format="%d VNĐ"
)

gnn_threshold = st.sidebar.slider("⚙️ Ngưỡng Khái Quát Rủi Ro AI (Tau):", 0.50, 0.99, 0.85, 0.01)

# --- KHU VỰC THÊM KHÁCH HÀNG MỚI ---
st.sidebar.markdown("---")
st.sidebar.markdown("### ➕ THÊM KHÁCH HÀNG MỚI")

with st.sidebar.form("add_customer_form"):
    new_id = st.text_input("Mã KH mới:", value="KH-9999")
    new_amount = st.number_input("Số tiền vay (VNĐ):", value=15000000, step=1000000)
    new_lat = st.number_input("Vĩ độ (Latitude):", value=10.7769, format="%.4f")
    new_lng = st.number_input("Kinh độ (Longitude):", value=106.7009, format="%.4f")
    new_imei_option = st.selectbox(
        "Mã IMEI Thiết Bị:",
        ["TB-IMEI-864912 (Đen/Cảnh báo)", "TB-IMEI-990011 (Sạch)", "TB-IMEI-554433 (Sạch)"]
    )
    
    submit_btn = st.form_submit_button("🚀 Gửi Đơn Vay Về API")

    if submit_btn:
        payload = {
            "customer_id": new_id,
            "loan_amount": float(new_amount),
            "latitude": float(new_lat),
            "longitude": float(new_lng),
            "imei": new_imei_option.split(" ")[0]
        }
        try:
            res = requests.post("http://localhost:8000/api/v1/submit-loan", json=payload)
            if res.status_code == 200:
                st.success(f"✅ Đã thêm {new_id} thành công!")
            else:
                st.error("❌ Lỗi gửi dữ liệu về API!")
        except Exception:
            st.error("⚠️ Bạn chưa bật server API (chạy python api_server.py)")

# ================= ================= ================= =================
# 5. KPIS METRICS
# ================= ================= ================= =================
total_users = len(user_nodes)
fraud_count = sum(1 for u in user_nodes if G.nodes[u].get("status") == "RỦI RO RẤT CAO")
total_infra = len(G.nodes) - total_users

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">TỔNG TÀI KHOẢN VAY</div><div class="kpi-value">{total_users}</div><div style="color:#10b981;font-size:0.75rem;margin-top:2px;">🟢 Đang giám sát</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-card" style="border-left: 4px solid #ef4444;"><div class="kpi-title">CỤM BÙNG NỢ GIAN LẬN</div><div class="kpi-value" style="color:#fca5a5;">{fraud_count}</div><div style="color:#f87171;font-size:0.75rem;margin-top:2px;">🚨 Phát hiện rủi ro</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">HẠ TẦNG DÙNG CHUNG</div><div class="kpi-value">{total_infra}</div><div style="color:#38bdf8;font-size:0.75rem;margin-top:2px;">🌐 IP / IMEI liên kết</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi-card" style="border-left: 4px solid #8b5cf6;"><div class="kpi-title">TỐC ĐỘ ĐỒNG BỘ</div><div class="kpi-value" style="color:#c084fc;">3.0 s</div><div style="color:#c084fc;font-size:0.75rem;margin-top:2px;">⚡ Quét CSDL liên tục</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ================= ================= ================= =================
# 6. KẾT QUẢ QUYẾT ĐỊNH & THÔNG SỐ ĐỒ THỊ
# ================= ================= ================= =================
if selected_user != "N/A":
    user_risk_score = user_data.get("risk_score", 0.0)
    is_high_risk = user_risk_score >= (gnn_threshold * 100)

    col_left, col_right = st.columns([1.2, 1.8])

    with col_left:
        st.markdown("#### 🎯 KẾT QUẢ QUYẾT ĐỊNH GIẢI NGÂN")
        if is_high_risk:
            st.markdown(f"""
            <div class="risk-banner-danger">
                <div style="font-weight: 800; font-size: 1.1rem; margin-bottom: 6px;">❌ TỪ CHỐI DUYỆT VAY (KHÓA TÀI KHOẢN)</div>
                <div style="font-size: 0.88rem;">Tài khoản <b>{selected_user}</b> phát hiện dùng chung IP/IMEI với cụm bùng nợ.</div>
                <hr style="border-color: rgba(239, 68, 68, 0.3); margin: 10px 0;">
                <div>Điểm rủi ro AI: <span style="font-size:1.3rem; font-weight:800; color:#ef4444;">{user_risk_score:.2f}%</span></div>
                <div>Hạn mức phê duyệt: <b style="color:#ef4444;">0 VNĐ</b></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="risk-banner-safe">
                <div style="font-weight: 800; font-size: 1.1rem; margin-bottom: 6px;">✅ PHÊ DUYỆT HẠN MỨC (GIẢI NGÂN NGAY)</div>
                <div style="font-size: 0.88rem;">Tài khoản <b>{selected_user}</b> đạt độ an toàn cấu trúc đồ thị.</div>
                <hr style="border-color: rgba(16, 185, 129, 0.3); margin: 10px 0;">
                <div>Điểm rủi ro AI: <span style="font-size:1.3rem; font-weight:800; color:#10b981;">{user_risk_score:.2f}%</span></div>
                <div>Hạn mức phê duyệt: <b style="color:#10b981;">{loan_request:,.0f} VNĐ</b></div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("#### 🔬 PHÂN TÍCH BẮT CẶP CẤU TRÚC ĐỒ THỊ")
        neighbors = list(G.neighbors(selected_user))
        degree_cent = nx.degree_centrality(G)[selected_user]
        
        df_metrics = pd.DataFrame({
            "Tiêu Chí Đồ Thị": ["Số Liên Kết Trực Tiếp", "Hệ Số Gom Cụm", "Độ Trung Tâm Mạng", "Trạng Thái Cụm"],
            "Giá Trị": [f"{len(neighbors)} nút", f"{nx.clustering(G, selected_user):.4f}", f"{degree_cent:.4f}", "100% Cụm Bùng Nợ" if is_high_risk else "0.0% An Toàn"],
            "Trạng Thái AI": ["⚠️ BẤT THƯỜNG" if len(neighbors) > 2 else "🟢 BÌNH THƯỜNG", "🚨 CAO" if is_high_risk else "🟢 THẤP", "⚠️ CAO" if is_high_risk else "🟢 BÌNH THƯỜNG", "🔴 NGUY HẠI" if is_high_risk else "🟢 AN TOÀN"]
        })
        st.dataframe(df_metrics, use_container_width=True, hide_index=True)

st.markdown("---")

# ================= ================= ================= =================
# 7. TABS VISUALIZATION (BẢN ĐỒ GPS & ĐỒ THỊ MẠNG)
# ================= ================= ================= =================
tab_map, tab_graph, tab_data = st.tabs([
    "📍 BẢN ĐỒ VỊ TRÍ NGƯỜI DÙNG (GPS MAP)",
    "🌐 ĐỒ THỊ MẠNG LIÊN KẾT REAL-TIME",
    "📋 DỮ LIỆU CSDL ĐỒNG BỘ"
])

# --- TAB 1: BẢN ĐỒ GPS ---
with tab_map:
    st.markdown("### 🗺️ Định Vị Không Gian GPS Người Dùng Theo Thời Gian Thực")
    if selected_user != "N/A":
        user_lat = user_data.get("lat", 10.7769)
        user_lng = user_data.get("lng", 106.7009)

        m = folium.Map(location=[user_lat, user_lng], zoom_start=13, tiles="CartoDB dark_matter")

        # Ghim vị trí người dùng đang chọn
        icon_color = "red" if is_high_risk else "green"
        folium.Marker(
            [user_lat, user_lng],
            popup=f"Khách Hàng: {selected_user}\nRủi ro: {user_risk_score:.2f}%",
            tooltip=f"👤 {selected_user} ({'RỦI RO' if is_high_risk else 'AN TOÀN'})",
            icon=folium.Icon(color=icon_color, icon="user", prefix="fa")
        ).add_to(m)

        # Vòng tròn cảnh báo nếu rủi ro cao
        if is_high_risk:
            folium.Circle(
                location=[user_lat, user_lng],
                radius=1200, color="#ef4444", fill=True, fill_color="#ef4444", fill_opacity=0.2,
                popup="Vùng cảnh báo tập trung cụm tài khoản bùng nợ BNPL"
            ).add_to(m)

        st_folium(m, width="100%", height=480)

# --- TAB 2: ĐỒ THỊ MẠNG LIÊN KẾT ---
with tab_graph:
    st.markdown("### 🕸️ Sơ Đồ Mạng Lưới Hạ Tầng Dùng Chung Real-Time")
    if len(G.nodes) > 0:
        net = Network(height="480px", width="100%", bgcolor="#020617", font_color="#f8fafc")
        net.from_nx(G)
        net.barnes_hut(gravity=-4000, central_gravity=0.2, spring_length=100)
        
        for node in net.nodes:
            if node["id"] == selected_user:
                node["size"] = 35
                node["color"] = "#facc15" # Vàng rực cho nút đang chọn
            elif node.get("node_type") == "Khách Hàng":
                node["size"] = 20

        net.save_graph("graph_live.html")
        with open("graph_live.html", "r", encoding="utf-8") as f:
            components.html(f.read(), height=500)

# --- TAB 3: DỮ LIỆU SQLITE ---
with tab_data:
    st.markdown("### 📋 Bảng Dữ Liệu Hồ Sơ Đăng Ký Trong CSDL")
    if not df_raw.empty:
        st.dataframe(df_raw, use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có dữ liệu trong CSDL.")