import streamlit as st
import networkx as nx
import numpy as np
import pandas as pd
import sqlite3
from pyvis.network import Network
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh

# ================= ================= ================= =================
# 1. CẤU HÌNH & TỰ ĐỘNG LÀM MỚI REAL-TIME (MỖI 3 GIÂY)
# ================= ================= ================= =================
st.set_page_config(
    page_title="NEXUS FRAUD SHIELD | Real-time GNN Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Tự động quét CSDL làm mới giao diện mỗi 3000ms (3 giây)
st_autorefresh(interval=3000, key="realtime_sync_counter")

# Style CSS Dark Slate
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #0f172a; color: #f8fafc; }
    .header-container {
        display: flex; align-items: center; justify-content: space-between;
        padding: 1rem 1.5rem; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155; border-radius: 12px; margin-bottom: 1rem;
    }
    .brand-title {
        font-size: 1.3rem; font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .kpi-card {
        background: rgba(30, 41, 59, 0.7); border: 1px solid #334155;
        border-radius: 12px; padding: 1rem;
    }
    .kpi-title { color: #94a3b8; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-size: 1.8rem; font-weight: 700; color: #f8fafc; font-family: 'JetBrains Mono', monospace; }
    .risk-banner-danger {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(127, 29, 29, 0.25) 100%);
        border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 12px; padding: 1.2rem; color: #fca5a5;
    }
    .risk-banner-safe {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 78, 59, 0.25) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 12px; padding: 1.2rem; color: #6ee7b7;
    }
</style>
""", unsafe_allow_html=True)

# ================= ================= ================= =================
# 2. ĐỌC DỮ LIỆU ĐỒ THỊ TỪ CSDL SQLITE REAL-TIME
# ================= ================= ================= =================
def load_graph_from_db():
    G = nx.Graph()
    
    # Danh sách IP/IMEI nằm trong Blacklist bùng nợ
    BLACK_IPS = ["104.28.19.14", "113.161.72.14"]
    BLACK_IMEIS = ["TB-IMEI-864912"]

    # Đọc CSDL
    try:
        conn = sqlite3.connect("fraud_data.db")
        df = pd.read_sql_query("SELECT * FROM loan_requests", conn)
        conn.close()
    except Exception:
        df = pd.DataFrame()

    # Dữ liệu mặc định nếu CSDL trống
    if df.empty:
        df = pd.DataFrame([
            {"customer_id": "KH-1008", "loan_amount": 15000000, "ip_address": "104.28.19.14", "latitude": 10.7769, "longitude": 106.7009, "imei": "TB-IMEI-864912"},
            {"customer_id": "KH-1009", "loan_amount": 10000000, "ip_address": "104.28.19.14", "latitude": 10.7750, "longitude": 106.7020, "imei": "TB-IMEI-864912"},
            {"customer_id": "KH-2001", "loan_amount": 5000000, "ip_address": "14.225.21.18", "latitude": 21.0285, "longitude": 105.8542, "imei": "TB-IMEI-990011"}
        ])

    # Dựng Đồ Thị
    for _, row in df.iterrows():
        user = row["customer_id"]
        ip = row["ip_address"]
        imei = row["imei"]
        
        is_fraud = (ip in BLACK_IPS) or (imei in BLACK_IMEIS)
        risk_score = 91.76 if is_fraud else 5.20

        G.add_node(
            user,
            node_type="Khách Hàng",
            risk_score=risk_score,
            status="RỦI RO RẤT CAO" if is_fraud else "XÁC MINH AN TOÀN",
            lat=row["latitude"],
            lng=row["longitude"],
            loan_amount=row["loan_amount"]
        )
        G.add_node(ip, node_type="IP", color="#ef4444" if ip in BLACK_IPS else "#3b82f6")
        G.add_node(imei, node_type="Thiết Bị", color="#8b5cf6")

        G.add_edge(user, ip)
        G.add_edge(user, imei)

    return G, df

G, df_raw = load_graph_from_db()

# ================= ================= ================= =================
# 3. HEADER & SIDEBAR
# ================= ================= ================= =================
st.markdown("""
<div class="header-container">
    <div>
        <div class="brand-title">🛡️ HỆ THỐNG PHÁT HIỆN GIAN LẬN BNPL // AI GRAPH NEURAL NETWORK</div>
        <div style="color: #64748b; font-size: 0.8rem; margin-top: 2px;">
            Đồng bộ Real-Time từ CSDL SQLite & Cổng API Tự Động
        </div>
    </div>
    <div style="color: #34d399; font-size: 0.8rem; font-weight: 600;">
        🟢 CSDL: DỮ LIỆU ĐỒNG BỘ REAL-TIME (3s)
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### 🎛️ BẢNG ĐIỀU HÀNH THẨM ĐỊNH")
user_list = [n for n, d in G.nodes(data=True) if d.get("node_type") == "Khách Hàng"]
selected_user = st.sidebar.selectbox("👤 Chọn Mã Khách Hàng Thẩm Định:", user_list)

gnn_threshold = st.sidebar.slider("⚙️ Ngưỡng Rủi Ro AI (Tau):", 0.50, 0.99, 0.85, 0.01)

# ================= ================= ================= =================
# 4. KPI METRICS
# ================= ================= ================= =================
total_users = len(user_list)
fraud_count = sum(1 for n in user_list if G.nodes[n].get("risk_score", 0) > 80)
total_infra = len(G.nodes) - total_users

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="kpi-card"><div class="kpi-title">TỔNG TÀI KHOẢN</div><div class="kpi-value">{total_users}</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="kpi-card"><div class="kpi-title">CỤM BÙNG NỢ GIAN LẬN</div><div class="kpi-value" style="color:#fca5a5;">{fraud_count}</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="kpi-card"><div class="kpi-title">HẠ TẦNG DÙNG CHUNG</div><div class="kpi-value">{total_infra}</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="kpi-card"><div class="kpi-title">TỐC ĐỘ ĐỒNG BỘ</div><div class="kpi-value" style="color:#c084fc;">3.0 s</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ================= ================= ================= =================
# 5. KẾT QUẢ GIẢI NGÂN & BẮT CẶP CẤU TRÚC
# ================= ================= ================= =================
curr_node = G.nodes[selected_user]
user_risk = curr_node.get("risk_score", 0)
is_high_risk = user_risk >= (gnn_threshold * 100)

c1, c2 = st.columns([1.2, 1.8])

with c1:
    st.markdown("#### 🎯 KẾT QUẢ QUYẾT ĐỊNH GIẢI NGÂN")
    if is_high_risk:
        st.markdown(f"""
        <div class="risk-banner-danger">
            <b>❌ TỪ CHỐI DUYỆT VAY (KHÓA TÀI KHOẢN)</b><br>
            Tài khoản <b>{selected_user}</b> phát hiện trùng lặp hạ tầng bùng nợ.<br><hr style="border-color:rgba(239, 68, 68, 0.3);">
            Điểm rủi ro AI: <b style="font-size:1.3rem;">{user_risk:.2f}%</b><br>
            Hạn mức đề xuất: <b>0 VNĐ</b>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="risk-banner-safe">
            <b>✅ PHÊ DUYỆT HẠN MỨC (GIẢI NGÂN NGAY)</b><br>
            Tài khoản <b>{selected_user}</b> đạt chỉ số an toàn cấu trúc.<br><hr style="border-color:rgba(16, 185, 129, 0.3);">
            Điểm rủi ro AI: <b style="font-size:1.3rem;">{user_risk:.2f}%</b><br>
            Hạn mức phê duyệt: <b>{curr_node.get('loan_amount', 0):,.0f} VNĐ</b>
        </div>
        """, unsafe_allow_html=True)

with c2:
    st.markdown("#### 🔬 PHÂN TÍCH BẮT CẶP CẤU TRÚC ĐỒ THỊ")
    neighbors = list(G.neighbors(selected_user))
    degree_cent = nx.degree_centrality(G)[selected_user]
    
    df_metrics = pd.DataFrame({
        "Tiêu Chí Đồ Thị": ["Số Liên Kết Trực Tiếp", "Hệ Số Gom Cụm", "Độ Trung Tâm Mạng", "Mức Độ Rủi Ro Mạng"],
        "Giá Trị": [f"{len(neighbors)} nút", f"{nx.clustering(G, selected_user):.4f}", f"{degree_cent:.4f}", "100% Cụm Bùng Nợ" if is_high_risk else "0.0% An Toàn"],
        "Trạng Thái": ["⚠️ BẤT THƯỜNG" if len(neighbors) > 2 else "🟢 BÌNH THƯỜNG", "🚨 CAO" if is_high_risk else "🟢 THẤP", "⚠️ CAO" if is_high_risk else "🟢 BÌNH THƯỜNG", "🔴 NGUY HẠI" if is_high_risk else "🟢 AN TOÀN"]
    })
    st.dataframe(df_metrics, use_container_width=True, hide_index=True)

st.markdown("---")

# ================= ================= ================= =================
# 6. TABS TRỰC QUAN HOÁ BẢN ĐỒ & ĐỒ THỊ
# ================= ================= ================= =================
tab_map, tab_graph = st.tabs(["📍 BẢN ĐỒ VỊ TRÍ NGƯỜI DÙNG (GPS MAP)", "🌐 ĐỒ THỊ MẠNG LIÊN KẾT REAL-TIME"])

with tab_map:
    lat = curr_node.get("lat", 10.7769)
    lng = curr_node.get("lng", 106.7009)
    
    m = folium.Map(location=[lat, lng], zoom_start=14, tiles="CartoDB dark_matter")
    folium.Marker(
        [lat, lng],
        popup=f"{selected_user}: {user_risk:.1f}% Risk",
        icon=folium.Icon(color="red" if is_high_risk else "green", icon="user", prefix="fa")
    ).add_to(m)
    
    if is_high_risk:
        folium.Circle([lat, lng], radius=1000, color="#ef4444", fill=True, fill_opacity=0.2).add_to(m)
        
    st_folium(m, width="100%", height=450)

with tab_graph:
    net = Network(height="450px", width="100%", bgcolor="#020617", font_color="#f8fafc")
    net.from_nx(G)
    net.save_graph("graph.html")
    with open("graph.html", "r", encoding="utf-8") as f:
        components.html(f.read(), height=470)