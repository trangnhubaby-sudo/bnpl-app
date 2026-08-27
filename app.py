import streamlit as st
import networkx as nx
import numpy as np
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components

# --- 1. CẤU HÌNH TRANG WEB & STYLING ---
st.set_page_config(
    page_title="BNPL Enterprise Fraud Radar",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS cho giao diện chuẩn Enterprise/Fintech
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #0066cc;
    }
    .metric-card-danger {
        border-left-color: #ff4d4f;
    }
    .metric-card-warning {
        border-left-color: #faad14;
    }
    .metric-card-success {
        border-left-color: #52c41a;
    }
    .status-badge-red {
        background-color: #fff1f0;
        color: #cf1322;
        padding: 4px 12px;
        border-radius: 15px;
        font-weight: bold;
        border: 1px solid #ffa39e;
    }
    .status-badge-green {
        background-color: #f6ffed;
        color: #389e0d;
        padding: 4px 12px;
        border-radius: 15px;
        font-weight: bold;
        border: 1px solid #b7eb8f;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. TẠO DỮ LIỆU ĐỒ THỊ MẠNG LƯỚI BÙNG NỢ (GRAPH DATA) ---
@st.cache_data
def generate_fraud_network():
    G = nx.Graph()
    
    # Danh sách Users, IPs, Devices
    users = [f"User_{i:02d}" for i in range(1, 16)]
    ips = [f"192.168.1.{i}" for i in range(101, 106)]
    devices = [f"DEV_ID_{i}" for i in range(1001, 1005)]
    
    # Nút Gian lận (Fraud Syndicate Cluster)
    fraud_group = ["User_05", "User_06", "User_07", "User_08"]
    
    for u in users:
        is_fraud = u in fraud_group
        G.add_node(
            u, 
            label=u, 
            type="User", 
            group="Fraud_User" if is_fraud else "Normal_User",
            color="#ff4d4f" if is_fraud else "#52c41a",
            title=f"Loại: Người dùng | Trạng thái: {'Cảnh báo Gian lận' if is_fraud else 'Bình thường'}"
        )
        
    for ip in ips:
        G.add_node(
            ip, 
            label=ip, 
            type="IP", 
            group="IP",
            color="#1890ff",
            title=f"Loại: Địa chỉ IP ({ip})"
        )
        
    for dev in devices:
        G.add_node(
            dev, 
            label=dev, 
            type="Device", 
            group="Device",
            color="#722ed1",
            title=f"Loại: Mã phần cứng Thiết bị ({dev})"
        )

    # Cụm kết nối Gian lận (Nghi vấn Farm tài khoản bùng nợ)
    G.add_edge("User_05", "192.168.1.103", title="Giao dịch trùng IP")
    G.add_edge("User_06", "192.168.1.103", title="Giao dịch trùng IP")
    G.add_edge("User_07", "192.168.1.103", title="Giao dịch trùng IP")
    G.add_edge("User_08", "192.168.1.103", title="Giao dịch trùng IP")
    
    G.add_edge("User_05", "DEV_ID_1002", title="Dùng chung thiết bị")
    G.add_edge("User_06", "DEV_ID_1002", title="Dùng chung thiết bị")
    G.add_edge("User_07", "DEV_ID_1003", title="Dùng chung thiết bị")

    # Mạng lưới người dùng hợp lệ
    G.add_edge("User_01", "192.168.1.101", title="Đăng nhập")
    G.add_edge("User_01", "DEV_ID_1001", title="Thiết bị chính")
    G.add_edge("User_02", "192.168.1.101", title="Đăng nhập")
    G.add_edge("User_03", "192.168.1.102", title="Đăng nhập")
    G.add_edge("User_04", "192.168.1.104", title="Đăng nhập")
    G.add_edge("User_09", "192.168.1.105", title="Đăng nhập")
    G.add_edge("User_10", "DEV_ID_1004", title="Thiết bị chính")
    
    return G

G = generate_fraud_network()

# --- 3. HEADER & SIDEBAR CONTROLS ---
st.markdown("## 🛡️ Hệ Thống Giám Sát & Phát Hiện Gian Lận BNPL (GNN Radar)")
st.markdown("*Mô hình Mạng Đồ thị Nơ-ron (Graph Neural Networks) kết hợp Phân tích Mạng lưới Liên kết Thời gian thực*")
st.markdown("---")

# Sidebar
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2092/2092663.png", width=70)
st.sidebar.title("Điều Khiển Hệ Thống")

selected_user = st.sidebar.selectbox(
    "👤 Chọn Tài khoản Truy vấn:",
    [n for n, d in G.nodes(data=True) if d["type"] == "User"],
    index=4 # Mặc định chọn User_05 gian lận
)

loan_amount = st.sidebar.slider(
    "💰 Hạn mức đăng ký BNPL (VNĐ):",
    min_value=500000,
    max_value=20000000,
    value=5000000,
    step=500000,
    format="%d"
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Gợi ý demo:**\n- Chọn `User_05` hoặc `User_06` để xem phát hiện cụm gian lận.\n- Chọn `User_01` hoặc `User_02` để xem giao dịch an toàn.")

# --- 4. TÍNH TOÁN & HIỂN THỊ KPI tổng quan ---
total_users = sum(1 for _, d in G.nodes(data=True) if d["type"] == "User")
fraud_users = sum(1 for _, d in G.nodes(data=True) if d.get("group") == "Fraud_User")
ip_count = sum(1 for _, d in G.nodes(data=True) if d["type"] == "IP")
device_count = sum(1 for _, d in G.nodes(data=True) if d["type"] == "Device")

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.markdown(f"""
        <div class="metric-card">
            <small style="color: #8c8c8c;">Tổng Tài Khoản Đã Quét</small>
            <h3 style="margin: 5px 0; color: #1f1f1f;">{total_users} Users</h3>
            <small style="color: #52c41a;">⚡ Giám sát 24/7</small>
        </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    st.markdown(f"""
        <div class="metric-card metric-card-danger">
            <small style="color: #8c8c8c;">Nghi Vấn Gian Lận / Bùng Nợ</small>
            <h3 style="margin: 5px 0; color: #cf1322;">{fraud_users} Users ({fraud_users/total_users*100:.0f}%)</h3>
            <small style="color: #cf1322;">⚠️ Phát hiện cụm rủi ro cao</small>
        </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    st.markdown(f"""
        <div class="metric-card">
            <small style="color: #8c8c8c;">Địa Chỉ IP Độc Lập</small>
            <h3 style="margin: 5px 0; color: #1890ff;">{ip_count} IPs</h3>
            <small style="color: #1890ff;">🌐 Mạng lưới kết nối</small>
        </div>
    """, unsafe_allow_html=True)

with col_kpi4:
    st.markdown(f"""
        <div class="metric-card">
            <small style="color: #8c8c8c;">Mã Thiết Bị (Hardware IDs)</small>
            <h3 style="margin: 5px 0; color: #722ed1;">{device_count} Devices</h3>
            <small style="color: #722ed1;">📱 Vân tay thiết bị</small>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. ĐÁNH GIÁ CHI TIẾT TÀI KHOẢN ĐƯỢC CHỌN ---
is_selected_fraud = G.nodes[selected_user].get("group") == "Fraud_User"
risk_score = np.random.uniform(88.0, 97.5) if is_selected_fraud else np.random.uniform(1.5, 8.0)

st.subheader(f"📊 Kết Quả Phân Tích Rủi Ro Tín Dụng: {selected_user}")

col_detail1, col_detail2 = st.columns([1, 1.8])

with col_detail1:
    if is_selected_fraud:
        st.error(f"🚨 **TRẠNG THÁI: CẢNH BÁO ĐỎ (HIGH RISK)**")
        st.markdown(f"""
            - **Xác suất Gian lận / Bùng nợ (GNN Score):** <span style='color:red; font-size: 20px; font-weight: bold;'>{risk_score:.1f}%</span>
            - **Đề xuất Hệ thống:** ❌ **TỪ CHỐI GIẢI NGÂN (REJECT)**
            - **Hạn mức đề xuất:** 0 VNĐ
        """, unsafe_allow_html=True)
        st.warning("""
            **🔍 Giải thích nguyên nhân (GNN Explainer):**
            * Tài khoản liên kết trực tiếp với **IP 192.168.1.103** - Địa chỉ IP chứa nhiều tài khoản bùng nợ quá hạn.
            * Phát hiện hành vi **Dùng chung vân tay thiết bị (Hardware Fingerprint)** với các tài khoản trong danh sách đen.
        """)
    else:
        st.success(f"✅ **TRẠNG THÁI: AN TOÀN (LOW RISK)**")
        st.markdown(f"""
            - **Xác suất Gian lận / Bùng nợ (GNN Score):** <span style='color:green; font-size: 20px; font-weight: bold;'>{risk_score:.1f}%</span>
            - **Đề xuất Hệ thống:** ✔️ **CHẤP NHẬN GIẢI NGÂN (APPROVE)**
            - **Hạn mức duyệt:** {loan_amount:,.0f} VNĐ
        """, unsafe_allow_html=True)
        st.info("""
            **🔍 Giải thích nguyên nhân (GNN Explainer):**
            * Lịch sử kết nối sạch, thiết bị độc lập.
            * Không ghi nhận mối liên kết với bất kỳ cụm tài khoản gian lận nào trong bán kính 3-hops đồ thị.
        """)

with col_detail2:
    # Bảng Ma trận Tính chất Đồ thị (Graph Metrics Matrix)
    neighbors = list(G.neighbors(selected_user))
    st.write("**📌 Thông số Đồ thị Mạng lưới của Tài khoản:**")
    
    metrics_df = pd.DataFrame({
        "Chỉ số Đồ thị (Graph Metric)": [
            "Bậc nút (Degree - Số kết nối)", 
            "Hệ số cụm (Clustering Coefficient)", 
            "Số thiết bị liên kết", 
            "Trùng lặp IP với User gian lận"
        ],
        "Giá trị": [
            len(neighbors),
            f"{nx.clustering(G, selected_user):.2f}",
            sum(1 for n in neighbors if G.nodes[n]["type"] == "Device"),
            "Có (Phát hiện Cụm Nợ xấu)" if is_selected_fraud else "Không (Sạch)"
        ],
        "Đánh giá": [
            "Bất thường" if len(neighbors) > 2 else "Bình thường",
            "Nguy cơ Cụm" if is_selected_fraud else "An toàn",
            "Cao" if is_selected_fraud else "Bình thường",
            "🔴 Nguy cơ cao" if is_selected_fraud else "🟢 An toàn"
        ]
    })
    st.table(metrics_df)

st.markdown("---")

# --- 6. TÁC VỤ TAB: TRỰC QUAN HÓA ĐỒ THỊ & DỮ LIỆU ---
tab1, tab2 = st.tabs(["🌐 Đồ Thị Mạng Lưới Liên Kết (Interactive Graph)", "📋 Bảng Dữ Liệu Chi Tiết"])

with tab1:
    st.markdown("### 🕸️ Bản Đồ Mạng Lưới Gian Lận Bùng Nợ BNPL")
    st.caption("🔴 **Tài khoản Gian lận/Bùng nợ** | 🟢 **Tài khoản Hợp lệ** | 🔵 **Địa chỉ IP** | 🟣 **Mã Thiết bị**")

    # Tạo đồ thị tương tác PyVis
    net = Network(height="520px", width="100%", bgcolor="#1a1a1a", font_color="white")
    net.from_nx(G)
    
    # Cấu hình lực đẩy vật lý cho đồ thị tự sắp xếp đẹp mắt
    net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=95)
    
    # Highlight nút được chọn
    for node in net.nodes:
        if node["id"] == selected_user:
            node["size"] = 35
            node["borderWidth"] = 4
            node["color"] = "#ffec3d" # Màu vàng nổi bật nút đang chọn
        elif node["type"] == "User":
            node["size"] = 20
        else:
            node["size"] = 15

    net.save_graph("graph_pro.html")

    # Load HTML lên Streamlit
    with open("graph_pro.html", "r", encoding="utf-8") as f:
        html_code = f.read()
    components.html(html_code, height=540)

with tab2:
    st.markdown("### 📋 Danh Sách Tất Cả Tài Khoản & Chỉ Số Phân Tích")
    
    table_data = []
    for node, data in G.nodes(data=True):
        if data["type"] == "User":
            is_f = data.get("group") == "Fraud_User"
            table_data.append({
                "Mã Người Dùng": node,
                "Loại Tài Khoản": "BNPL Customer",
                "Trạng Thái Rủi Ro": "🔴 Cảnh báo Gian lận" if is_f else "🟢 Hợp lệ",
                "Mức Rủi Ro Dự Báo": f"{np.random.uniform(85, 98):.1f}%" if is_f else f"{np.random.uniform(1, 8):.1f}%",
                "Hành Vi Khuyến Nghị": "Khóa tài khoản / Chặn cho vay" if is_f else "Cho phép giải ngân"
            })
            
    df_display = pd.DataFrame(table_data)
    st.dataframe(df_display, use_container_width=True)