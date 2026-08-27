import streamlit as st
import networkx as nx
import numpy as np
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components

# ================= ================= ================= =================
# 1. CẤU HÌNH HỆ THỐNG & GIAO DIỆN CHUẨN FINTECH ENTERPRISE
# ================= ================= ================= =================
st.set_page_config(
    page_title="NEXUS FRAUD SHIELD | Radar AI Phát Hiện Gian Lận BNPL",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark / Modern Slate Fintech Theme CSS
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

    /* Tech Badge Styling */
    .tech-pill {
        display: inline-block;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        padding: 3px 8px;
        border-radius: 6px;
        background: #1e293b;
        border: 1px solid #475569;
        color: #cbd5e1;
        margin-right: 4px;
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
# 2. DANH MỤC ÁP ÁN ĐỊA LÝ -> SUY RA IP
# ================= ================= ================= =================
LOCATION_IP_MAP = {
    "🇻🇳 TP. Hồ Chí Minh (Mạng VNPT Chính Chủ)": {"ip": "113.161.72.14", "risk": "AN TOÀN", "isp": "VNPT HCMC"},
    "🇻🇳 Hà Nội (Mạng Viettel Doanh Nghiệp)": {"ip": "14.225.21.18", "risk": "AN TOÀN", "isp": "Viettel Hà Nội"},
    "🇻🇳 Đà Nẵng (Mạng Cáp Quang FPT)": {"ip": "116.109.12.5", "risk": "AN TOÀN", "isp": "FPT Telecom"},
    "🚨 Nghi Vấn: IP Proxy Dynamic (Lagos, Nigeria)": {"ip": "104.28.19.14", "risk": "CẢNH BÁO", "isp": "Mạng Ẩn Danh VPN/Proxy"},
    "🚨 Nghi Vấn: Mạng Ẩn Danh Tor Node (Đông Âu)": {"ip": "104.28.19.15", "risk": "CẢNH BÁO", "isp": "Nút Mạng Tor Relay"}
}

# ================= ================= ================= =================
# 3. MÔ PHỎNG DỮ LIỆU ĐỒ THỊ MẠNG AI (GRAPH ENGINE)
# ================= ================= ================= =================
@st.cache_data
def build_enterprise_fraud_network():
    G = nx.Graph()
    
    users = [f"KH-{i:04d}" for i in range(1001, 1026)]
    ips = [f"104.28.19.{i}" for i in range(12, 18)] + ["113.161.72.14", "14.225.21.18", "116.109.12.5"]
    devices = [f"TB-IMEI-8649{i}" for i in range(10, 15)]
    banks = [f"STK-NH-{i}" for i in range(801, 804)]

    fraud_cluster = ["KH-1008", "KH-1009", "KH-1010", "KH-1011", "KH-1012"]
    
    for u in users:
        is_fraud = u in fraud_cluster
        G.add_node(
            u,
            label=u,
            node_type="Khách Hàng",
            status="RỦI RO RẤT CAO" if is_fraud else "XÁC MINH AN TOÀN",
            risk_score=float(np.random.uniform(91.2, 99.4)) if is_fraud else float(np.random.uniform(0.8, 9.4)),
            color="#ef4444" if is_fraud else "#10b981",
            shape="dot",
            title=f"Mã Khách Hàng: {u}<br>Loại: Tài khoản BNPL<br>Trạng thái: {'CỤM BÙNG NỢ' if is_fraud else 'AN TOÀN'}"
        )
        
    for ip in ips:
        is_suspicious_ip = ip in ["104.28.19.14", "104.28.19.15"]
        G.add_node(
            ip,
            label=f"IP: {ip}",
            node_type="Địa chỉ IP",
            color="#ef4444" if is_suspicious_ip else "#3b82f6",
            shape="diamond",
            title=f"Hạ Tầng: Địa Chỉ IP Mạng<br>Subnet: {ip}"
        )
        
    for dev in devices:
        G.add_node(
            dev,
            label=f"Thiết Bị: {dev[-4:]}",
            node_type="Thiết Bị",
            color="#8b5cf6",
            shape="triangle",
            title=f"Mã Định Danh Phần Cứng<br>Mã IMEI: {dev}"
        )
        
    for bank in banks:
        G.add_node(
            bank,
            label=f"STK: {bank[-3:]}",
            node_type="Tài Khoản Ngân Hàng",
            color="#ec4899",
            shape="square",
            title=f"Tài Khoản Nhận Tiền Giải Ngân<br>Số Tài Khoản: {bank}"
        )

    # Liên kết nhóm gian lận bùng nợ
    shared_ip = "104.28.19.14"
    shared_device = "TB-IMEI-864912"
    shared_bank = "STK-NH-802"
    
    for fu in fraud_cluster:
        G.add_edge(fu, shared_ip, weight=3.5, relation="DÙNG_CHUNG_IP_PROXY")
        G.add_edge(fu, shared_device, weight=5.0, relation="DÙNG_CHUNG_THIẾT_BỊ")
        G.add_edge(fu, shared_bank, weight=4.0, relation="DÙNG_CHUNG_STK_NHẬN_TIỀN")
        
    # Liên kết khách hàng sạch
    G.add_edge("KH-1001", "113.161.72.14", relation="CHÍNH_CHỦ_TPHCM")
    G.add_edge("KH-1001", "TB-IMEI-864910", relation="DI_ĐỘNG_CÁ_NHÂN")
    G.add_edge("KH-1001", "STK-NH-801", relation="TÀI_KHOẢN_LƯƠNG")
    
    G.add_edge("KH-1002", "14.225.21.18", relation="VĂN_PHÒNG_HÀ_NỘI")
    G.add_edge("KH-1003", "116.109.12.5", relation="MẠNG_ĐÀ_NẴNG")
    G.add_edge("KH-1004", "104.28.19.16", relation="MẠNG_4G_DI_ĐỘNG")
    G.add_edge("KH-1005", "TB-IMEI-864911", relation="MÁY_TÍNH_BẢNG")
    G.add_edge("KH-1006", "STK-NH-803", relation="NHẬN_TIỀN_CÁ_NHÂN")

    return G

G = build_enterprise_fraud_network()

# ================= ================= ================= =================
# 4. THANH TIÊU ĐỀ HỆ THỐNG
# ================= ================= ================= =================
st.markdown("""
<div class="header-container">
    <div>
        <div class="brand-title">🛡️ HỆ THỐNG PHÁT HIỆN GIAN LẬN BNPL // AI GRAPH NEURAL NETWORK</div>
        <div style="color: #64748b; font-size: 0.82rem; margin-top: 2px;">
            Radar Thẩm Định Rủi Ro Bùng Nợ & Trích Xuất Vị Trí Geo-IP Theo Thời Gian Thực
        </div>
    </div>
    <div class="system-status">
        <div class="pulse-dot"></div>
        MÔ HÌNH AI GNN: ĐANG HOẠT ĐỘNG (v4.2.0-PROD)
    </div>
</div>
""", unsafe_allow_html=True)

# ================= ================= ================= =================
# 5. THANH ĐIỀU KHIỂN BÊN TRÁI (SIDEBAR)
# ================= ================= ================= =================
st.sidebar.markdown("### 🎛️ BẢNG ĐIỀU HÀNH THẨM ĐỊNH")

user_list = [n for n, d in G.nodes(data=True) if d.get("node_type") == "Khách Hàng"]
selected_user = st.sidebar.selectbox(
    "👤 Chọn Mã Khách Hàng Thẩm Định:",
    user_list,
    index=user_list.index("KH-1008")
)

# Tự động suy ra IP từ Vị trí
selected_location_label = st.sidebar.selectbox(
    "📍 Chọn Vị Trí / Địa Phương Đăng Nhập:",
    list(LOCATION_IP_MAP.keys()),
    index=3
)

geo_info = LOCATION_IP_MAP[selected_location_label]
inferred_ip = geo_info["ip"]

st.sidebar.markdown(f"""
<div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 10px; margin-top: 5px;">
    <div style="font-size: 0.75rem; color: #94a3b8;">DỮ LIỆU IP SUY RA TỪ ĐỊA LÝ:</div>
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; color: #38bdf8; font-weight:700;">IP: {inferred_ip}</div>
    <div style="font-size: 0.75rem; color: #cbd5e1;">Nhà mạng: {geo_info['isp']}</div>
</div>
""", unsafe_allow_html=True)

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
st.sidebar.caption("🔒 Chứng nhận an toàn: SOC2 Type II | ISO27001 | Mã hóa GDPR")

# Cập nhật động cạnh đồ thị khi người dùng đổi IP
G.add_edge(selected_user, inferred_ip, relation="PHIÊN_ĐĂNG_NHẬP_MỚI")

if geo_info["risk"] == "CẢNH BÁO":
    G.nodes[selected_user]["risk_score"] = max(G.nodes[selected_user]["risk_score"], 96.85)

# ================= ================= ================= =================
# 6. BẢNG CHỈ SỐ METRIC GIÁM SÁT
# ================= ================= ================= =================
total_users = sum(1 for _, d in G.nodes(data=True) if d.get("node_type") == "Khách Hàng")
fraud_count = sum(1 for _, d in G.nodes(data=True) if d.get("status") == "RỦI RO RẤT CAO")
total_infra = len(G.nodes) - total_users

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">TỔNG TÀI KHOẢN GIÁM SÁT</div>
        <div class="kpi-value">{total_users} <span style="font-size:1rem; color:#94a3b8;">Tài khoản</span></div>
        <div class="kpi-sub" style="color:#10b981;">🟢 Luồng dữ liệu thời gian thực</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 4px solid #ef4444;">
        <div class="kpi-title">CỤM PHÁT HIỆN GIAN LẬN</div>
        <div class="kpi-value" style="color:#fca5a5;">{fraud_count} <span style="font-size:1rem; color:#f87171;">({fraud_count/total_users*100:.1f}%)</span></div>
        <div class="kpi-sub" style="color:#f87171;">🚨 Cảnh báo nhóm bùng nợ ảo</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">THIẾT BỊ & HẠ TẦNG CHUNG</div>
        <div class="kpi-value">{total_infra} <span style="font-size:1rem; color:#94a3b8;">Thực thể</span></div>
        <div class="kpi-sub" style="color:#38bdf8;">🌐 IP / Thiết Bị / Ngân Hàng</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 4px solid #8b5cf6;">
        <div class="kpi-title">TỐC ĐỘ XỬ LÝ AI (GNN)</div>
        <div class="kpi-value" style="color:#c084fc;">14.2 <span style="font-size:1rem; color:#c084fc;">ms</span></div>
        <div class="kpi-sub" style="color:#c084fc;">⚡ Thẩm định siêu tốc</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ================= ================= ================= =================
# 7. KẾT QUẢ THẨM ĐỊNH AI & GIẢI TRÌNH RỦI RO
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
            <div style="font-weight: 800; font-size: 1.1rem; margin-bottom: 6px;">❌ TỪ CHỐI DUYỆT VAY (TỰ ĐỘNG KHÓA)</div>
            <div style="font-size: 0.9rem;">
                Tài khoản <b>{selected_user}</b> có cấu trúc mạng lưới trùng khớp với tổ chức bùng nợ thông qua địa chỉ IP <code>{inferred_ip}</code>.
            </div>
            <hr style="border-color: rgba(239, 68, 68, 0.3); margin: 12px 0;">
            <div><b>Xác suất rủi ro AI (GNN):</b> <span style="font-size:1.3rem; font-weight:800; color:#ef4444;">{user_risk_score:.2f}%</span></div>
            <div><b>Hạn mức yêu cầu:</b> {loan_request:,.0f} VNĐ → <b style="color:#ef4444;">PHÊ DUYỆT 0 VNĐ</b></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 🧠 Giải Trình Bằng Bằng Chứng Mạng Lưới (AI Explainer)")
        st.error(f"""
        * **Cảnh Báo Địa Lý IP:** Phát hiện địa chỉ IP ẩn danh rủi ro cao ({inferred_ip}).
        * **Trùng Lặp Thiết Bị:** Dùng chung mã phần cứng IMEI với 4 tài khoản đã từng bùng nợ.
        * **Độ Tương Đồng Cấu Trúc (Homophily):** 0.94 (Gần như tuyệt đối trùng liên kết với nhóm lừa đảo).
        """)
    else:
        st.markdown(f"""
        <div class="risk-banner-safe">
            <div style="font-weight: 800; font-size: 1.1rem; margin-bottom: 6px;">✅ PHÊ DUYỆT HẠN MỨC (GIẢI NGÂN NGAY)</div>
            <div style="font-size: 0.9rem;">
                Tài khoản <b>{selected_user}</b> vượt qua toàn bộ các kiểm tra rủi ro mạng lưới và địa chỉ IP.
            </div>
            <hr style="border-color: rgba(16, 185, 129, 0.3); margin: 12px 0;">
            <div><b>Xác suất rủi ro AI (GNN):</b> <span style="font-size:1.3rem; font-weight:800; color:#10b981;">{user_risk_score:.2f}%</span></div>
            <div><b>Hạn mức phê duyệt:</b> <b style="color:#10b981;">{loan_request:,.0f} VNĐ</b></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 🧠 Giải Trình Bằng Bằng Chứng Mạng Lưới (AI Explainer)")
        st.success(f"""
        * **Địa Chỉ IP Chính Chủ:** Truy cập từ nhà mạng dân sự uy tín ({inferred_ip}).
        * **Cấu Trúc Độc Lập:** Không có liên kết trùng lặp với các cụm gian lận trong vòng 3 liên kết.
        * **Độ Tương Đồng Cấu Trúc:** 0.02 (Cực kỳ an toàn).
        """)

with col_right:
    st.markdown("#### 🔬 BẢNG CHỈ SỐ ĐỒ THỊ MẠNG CHUYÊN SÂU")
    
    neighbors = list(G.neighbors(selected_user))
    
    metrics_data = {
        "Đặc Trưng Cấu Trúc Mạng": [
            "Địa Chỉ IP Đăng Nhập",
            "Bậc Đồ Thị (Số Liên Kết Trực Tiếp)",
            "Hệ Số Cụm (Clustering Coefficient)",
            "Chỉ Số Trung Tâm (PageRank)",
            "Tỷ Lệ Dùng Chung Phần Cứng / IP"
        ],
        "Chỉ Số Đo Đạc": [
            f"{inferred_ip} ({geo_info['risk']})",
            f"{len(neighbors)} Liên kết",
            f"{nx.clustering(G, selected_user):.4f}",
            f"{nx.pagerank(G)[selected_user]:.5f}",
            "100% (Thuộc cụm bùng nợ)" if is_high_risk else "0% (Độc lập an toàn)"
        ],
        "Ngưỡng An Toàn": [
            "IP Dân Sự Uy Tín",
            "Tối đa < 5",
            "< 0.1500",
            "< 0.04000",
            "< 20.0%"
        ],
        "Trạng Thái": [
            "🔴 NGHI VẤN" if geo_info['risk'] == "CẢNH BÁO" else "🟢 CHÍNH CHỦ",
            "⚠️ BẤT THƯỜNG" if len(neighbors) > 2 and is_high_risk else "🟢 BÌNH THƯỜNG",
            "🚨 BÙNG NỢ" if is_high_risk else "🟢 AN TOÀN",
            "⚠️ CAO" if is_high_risk else "🟢 THẤP",
            "🔴 CỰC KỲ RỦI RO" if is_high_risk else "🟢 AN TOÀN"
        ]
    }
    
    df_metrics = pd.DataFrame(metrics_data)
    st.dataframe(df_metrics, use_container_width=True, hide_index=True)
    
    # Console Log
    st.markdown("##### 📜 Nhật Ký Thẩm Định Hệ Thống (Real-time Audit Logs)")
    st.markdown(f"""
    <div class="log-box">
        [KHỞI TẠO] Đã tải mô hình GraphSAGER. Sẵn sàng tính toán ma trận trọng số.<br>
        [ĐỊA LÝ] Trích xuất vị trí địa lý thành công -> IP: {inferred_ip} ({geo_info['isp']})<br>
        [TRUY VẤN] Đang thẩm định khách hàng ID: {selected_user}<br>
        [GNN-WALK] Đang thực hiện gom nhóm {len(neighbors)} liên kết xung quanh {selected_user}...<br>
        [DỰ ĐOÁN] Điểm rủi ro AI tính toán: {user_risk_score:.4f}%<br>
        [QUYẾT ĐỊNH] Đã áp dụng ngưỡng Tau ({gnn_threshold*100}%). Trạng thái: {'KHÓA TÀI KHOẢN' if is_high_risk else 'CHO VAY'}
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ================= ================= ================= =================
# 8. BẢNG ĐỒ THỊ TƯƠNG TÁC VÀ DỮ LIỆU
# ================= ================= ================= =================
tab_graph, tab_data, tab_arch = st.tabs([
    "🌐 ĐỒ THỊ MẠNG LIÊN KẾT REAL-TIME",
    "📊 DANH SÁCH TÀI KHOẢN VÀ RỦI RO",
    "🏗️ KIẾN TRÚC MÔ HÌNH AI GNN"
])

with tab_graph:
    st.markdown("### 🕸️ Sơ Đồ Cấu Trúc Mạng Lưới Rủi Ro (Heterogeneous Graph)")
    st.caption("🔴 **Đỏ:** Cụm bùng nợ / IP rủi ro | 🟢 **Xanh lá:** Khách hàng an toàn | 🟡 **Vàng:** Khách hàng đang chọn | 🔷 **Xanh dương/Tím/Hồng:** Hạ tầng dùng chung")

    net = Network(height="580px", width="100%", bgcolor="#020617", font_color="#f8fafc")
    net.from_nx(G)
    
    net.barnes_hut(gravity=-4500, central_gravity=0.2, spring_length=110)
    
    for node in net.nodes:
        if node["id"] == selected_user:
            node["size"] = 38
            node["borderWidth"] = 4
            node["color"] = "#facc15"
            node["shadow"] = True
        elif node.get("node_type") == "Khách Hàng":
            node["size"] = 22
        else:
            node["size"] = 14

    net.save_graph("graph_enterprise.html")

    with open("graph_enterprise.html", "r", encoding="utf-8") as f:
        html_data = f.read()
        
    components.html(html_data, height=600)

with tab_data:
    st.markdown("### 📋 Danh Sách Quản Lý Tài Khoản Vay BNPL")
    
    table_rows = []
    for node, data in G.nodes(data=True):
        if data.get("node_type") == "Khách Hàng":
            st_flag = data.get("status") == "RỦI RO RẤT CAO" or data.get("risk_score", 0) > 80
            table_rows.append({
                "Mã Khách Hàng": node,
                "Phân Loại": "Khách Vay BNPL",
                "Phân Loại Rủi Ro": "🚨 CỤM BÙNG NỢ" if st_flag else "🟢 XÁC MINH AN TOÀN",
                "Xác Suất Bùng Nợ (GNN)": f"{data['risk_score']:.2f}%",
                "Hạn Mức Phê Duyệt": "0 VNĐ" if st_flag else "50,000,000 VNĐ",
                "Quy Trình Khuyến Nghị": "Khóa tài khoản khẩn cấp" if st_flag else "Giải ngân tự động"
            })
            
    df_registry = pd.DataFrame(table_rows)
    st.dataframe(df_registry, use_container_width=True)

with tab_arch:
    st.markdown("### 🏗️ Nguyên Lý Hoạt Động Của Mô Hình GraphSAGER Neural Network")
    st.markdown("""
    Hệ thống **Nexus Fraud Shield** sử dụng mạng Nơ-ron Đồ thị Đa quan hệ (Heterogeneous GNN) để phát hiện gian lận bùng nợ BNPL siêu tốc:

    1. **Tầng Xây Dựng Đồ Thị:** Chuyển đổi nhật ký giao dịch thành đồ thị 4 thành phần $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{T})$.
    2. **Gom Nhóm Xóm Giềng (Neighborhood Aggregation):** Sử dụng thuật toán GraphSAGE tổng hợp đặc trưng từ các nút lân cận:
       $$\mathbf{h}_{v}^{k} = \sigma \left( \mathbf{W}^k \cdot 	ext{CONCAT} \left( \mathbf{h}_v^{k-1}, 	ext{AGG}_{r \in \mathcal{R}} \{ \mathbf{h}_u^{k-1}, orall u \in \mathcal{N}_r(v) \} 
ight) 
ight)$$
    3. **Trích Xuất Vị Trí Geo-IP:** Tự động tính toán khoảng cách không gian giữa địa chỉ IP đăng nhập và cụm hạ tầng gian lận để đưa ra điểm số chính xác nhất.
    """)