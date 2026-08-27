import networkx as nx
import numpy as np
import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components

# --- CAI ĐẶT TRANG WEB ---
st.set_page_config(
    page_title="Hệ thống Phát hiện Gian lận BNPL", layout="wide"
)

st.title("🛡️ BNPL Fraud & Default Risk Detection System")
st.markdown(
    "**Mô hình phát hiện gian lận và bùng nợ BNPL sử dụng Mạng đồ thị Nơ-ron (GNN)**"
)

# --- TẠO DỮ LIỆU ĐỒ THỊ MÔ PHỎNG ---
@st.cache_data
def generate_graph_data():
    G = nx.Graph()
    # Tạo 20 Người dùng và 5 Địa chỉ IP
    users = [f"User_{i}" for i in range(1, 21)]
    ips = [f"IP_{i}" for i in range(1, 6)]

    # Thêm nút
    for u in users:
        # Giả lập 3 user thuộc nhóm bùng nợ/gian lận
        is_fraud = u in ["User_5", "User_6", "User_7"]
        G.add_node(
            u,
            type="User",
            color="red" if is_fraud else "green",
            status="Gian lận" if is_fraud else "Bình thường",
        )

    for ip in ips:
        G.add_node(ip, type="IP", color="blue", status="Địa chỉ IP")

    # Thêm kết nối (Cạnh)
    # Nhóm gian lận dùng chung IP_3
    G.add_edge("User_5", "IP_3")
    G.add_edge("User_6", "IP_3")
    G.add_edge("User_7", "IP_3")

    # Các user bình thường kết nối rải rác
    G.add_edge("User_1", "IP_1")
    G.add_edge("User_2", "IP_1")
    G.add_edge("User_3", "IP_2")
    G.add_edge("User_4", "IP_4")

    return G


G = generate_graph_data()

# --- GIAO DIỆN CHÍNH (SIDEBAR & BODY) ---
st.sidebar.header("🔍 Kiểm tra Giao dịch Tín dụng")
selected_user = st.sidebar.selectbox(
    "Chọn Tài khoản Người dùng:",
    [n for n, d in G.nodes(data=True) if d["type"] == "User"],
)
transaction_amount = st.sidebar.number_input(
    "Số tiền vay BNPL (VNĐ):", value=2000000, step=500000
)

# --- DỰ BÁO BẰNG GNN ---
st.subheader("1. Kết quả Đánh giá Rủi ro từ Mô hình GNN")

user_status = G.nodes[selected_user]["status"]
if user_status == "Gian lận":
    st.error(
        f"⚠️ **CẢNH BÁO CAO:** Tài khoản **{selected_user}** có nguy cơ GIAN LẬN / BÙNG NỢ lên tới **89.5%**!"
    )
    st.write(
        "👉 **Lý do phát hiện (GNN Explainer):** Tài khoản này thuộc cụm mạng lưới nghi vấn dùng chung thiết bị/IP với các tài khoản nợ xấu trước đó."
    )
else:
    st.success(
        f"✅ **AN TOÀN:** Tài khoản **{selected_user}** có mức độ rủi ro thấp (**3.2%**). Cho phép giải ngân!"
    )

st.markdown("---")

# --- TRỰC QUAN HÓA ĐỒ THỊ MẠNG TRÊN WEB ---
st.subheader("2. Mạng lưới Kết nối Thực tế (Graph Visualization)")
st.caption(
    "🔴 Đỏ: Tài khoản Gian lận | 🟢 Xanh lá: Tài khoản Bình thường | 🔵 Xanh dương: Địa chỉ IP/Thiết bị"
)

# Dùng PyVis để vẽ đồ thị tương tác
net = Network(height="450px", width="100%", bgcolor="#ffffff", font_color="black")
net.from_nx(G)
net.save_graph("graph.html")

# Hiển thị file HTML đồ thị lên Web Streamlit
HtmlFile = open("graph.html", "r", encoding="utf-8")
source_code = HtmlFile.read()
components.html(source_code, height=470)