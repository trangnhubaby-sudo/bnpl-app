import streamlit as st
import networkx as nx
import pandas as pd
import sqlite3
import hashlib
import numpy as np
from datetime import datetime, timedelta
from pyvis.network import Network
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh
from streamlit_javascript import st_javascript

# ==============================================================================
# 1. CẤU HÌNH HEAVY-DUTY ENTERPRISE STYLING & CORE SYSTEMS
# ==============================================================================
st.set_page_config(
    page_title="NEXUS Risk Operating System | Graph-Based Fraud Detection Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tự động đồng bộ hệ thống mỗi 10 giây
st_autorefresh(interval=10000, key="nexus_realtime_sync_v5")

st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        --bg-dark: #04070d;
        --card-bg: #0b111e;
        --card-border: #1e293b;
        --accent-blue: #38bdf8;
        --accent-purple: #c084fc;
        --accent-green: #10b981;
        --accent-red: #f43f5e;
        --text-main: #f8fafc;
        --text-muted: #64748b;
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: var(--bg-dark) !important;
        color: var(--text-main) !important;
    }
    
    .stApp {
        background-color: var(--bg-dark);
    }

    /* Top Command Header */
    .command-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.25rem 2rem;
        background: linear-gradient(135deg, #0d1527 0%, #060a12 100%);
        border: 1px solid #1e293b;
        border-radius: 16px;
        margin-bottom: 1.75rem;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7);
    }
    .brand-section {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .brand-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.15) 0%, rgba(192, 132, 252, 0.15) 100%);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
    }
    .brand-title {
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .brand-sub {
        color: #64748b;
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 2px;
        letter-spacing: 0.02em;
    }
    .sys-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #34d399;
    }
    .sys-dot {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 12px #10b981;
    }

    /* Custom Glass Panel Cards */
    .glass-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
        height: 100%;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .glass-card:hover {
        border-color: #334155;
    }
    
    .metric-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #64748b;
    }
    .metric-val {
        font-size: 2.1rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        color: #f8fafc;
        margin-top: 0.4rem;
        letter-spacing: -0.02em;
    }
    .metric-sub {
        font-size: 0.78rem;
        margin-top: 0.6rem;
        display: flex;
        align-items: center;
        gap: 6px;
        font-weight: 500;
    }

    /* Decision Cards */
    .decision-panel-rejected {
        background: linear-gradient(135deg, rgba(244, 63, 94, 0.12) 0%, rgba(136, 19, 55, 0.25) 100%);
        border: 1px solid rgba(244, 63, 94, 0.4);
        border-radius: 16px;
        padding: 1.75rem;
    }
    .decision-panel-approved {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(6, 78, 59, 0.25) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 16px;
        padding: 1.75rem;
    }

    /* Tab Custom Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: #0d1527;
        border: 1px solid #1e293b;
        border-radius: 10px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.88rem;
        padding: 0 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.15);
    }

    /* Sidebar Dark Enterprise Style */
    div[data-testid="stSidebar"] {
        background-color: #060a12 !important;
        border-right: 1px solid #1a2333;
    }
</style>
''', unsafe_allow_html=True)

# ==============================================================================
# 2. KHỞI TẠO CƠ SỞ DỮ LIỆU CHUẨN ENTERPRISE (SQLITE ENGINE)
# ==============================================================================
def init_enterprise_db():
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
        # Tập dữ liệu mẫu thực tế mô phỏng hành vi tín dụng
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

init_enterprise_db()

# ==============================================================================
# 3. TRUY VẤN & DỰNG ĐỒ THỊ MẠNG LƯỚI (NETWORKX ENGINE)
# ==============================================================================
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

        # Nút Đơn vay (Application Node)
        G.add_node(
            app_id, 
            label=f"{row['customer_name']}\n({app_id})", 
            type="Application", 
            risk=row["risk_score"], 
            color="#f43f5e" if is_fraud else "#10b981", 
            shape="dot"
        )
        
        # Nút IP & Fingerprint
        G.add_node(ip, label=f"IP: {ip}", type="IP_Address", color="#38bdf8", shape="diamond")
        G.add_node(fp, label=f"FP: {fp}", type="Device_Hash", color="#c084fc", shape="triangle")

        G.add_edge(app_id, ip)
        G.add_edge(app_id, fp)

    return G, df

G, df_apps = fetch_graph_data()

# ==============================================================================
# 4. MÔ HÌNH CHẤM ĐIỂM AI RỦI RO ĐỘNG (REAL-TIME DYNAMIC GRAPH ENGINE)
# ==============================================================================
def generate_device_hash(ua_string):
    if ua_string.startswith("FP-"):
        return ua_string
    return "FP-" + hashlib.md5(ua_string.encode()).hexdigest()[:8].upper()

def calculate_realtime_risk(ip_addr, device_fp, loan_amt, is_vpn, df_history):
    score = 5.0
    audit_logs = []

    # Truy vấn đối chiếu lịch sử
    ip_history = df_history[df_history["ip_address"] == ip_addr]
    device_history = df_history[df_history["device_hash"] == device_fp]

    bad_ip_count = len(ip_history[ip_history["decision"] == "REJECTED"])
    bad_device_count = len(device_history[device_history["decision"] == "REJECTED"])

    # 1. Kiểm tra dính cờ đen lịch sử
    if bad_device_count > 0:
        score += 65.0
        audit_logs.append(f"🔴 CẢNH BÁO NGHÊM TRỌNG: Thiết bị ({device_fp}) trùng với {bad_device_count} tài khoản đã bùng nợ!")

    if bad_ip_count > 0:
        score += 35.0
        audit_logs.append(f"⚠️ CẢNH BÁO: IP ({ip_addr}) từng phát sinh {bad_ip_count} khoản vay bị bùng nợ.")

    # 2. Đánh giá mật độ liên kết dùng chung (Graph Density Rule)
    total_ip_users = len(ip_history)
    total_device_users = len(device_history)

    if total_device_users >= 1:
        score += 25.0
        audit_logs.append(f"⚠️ MẬT ĐỘ CAO: Thiết bị đã được dùng chung bởi {total_device_users + 1} tài khoản khác.")

    if total_ip_users >= 2:
        score += 15.0
        audit_logs.append(f"ℹ️ MẬT ĐỘ CAO: Địa chỉ IP đang phục vụ {total_ip_users + 1} yêu cầu vay vốn.")

    # 3. VPN / Proxy Check
    if is_vpn:
        score += 20.0
        audit_logs.append("⚠️ HỆ THỐNG: Khách hàng sử dụng VPN/Proxy để giấu vị trí thực.")

    # 4. Khoản vay lớn
    if loan_amt > 25000000:
        score += 8.0
        audit_logs.append("ℹ️ HẠN MỨC: Yêu cầu hạn mức vay cao (> 25 Triệu).")

    final_score = min(score + np.random.uniform(0.5, 1.5), 99.9)
    decision = "REJECTED" if final_score >= 60.0 else "APPROVED"

    if not audit_logs:
        audit_logs.append("🟢 CHUẨN ĐOÁN: Mạng lưới kết nối sạch, không có lịch sử bất thường.")

    return round(final_score, 2), decision, audit_logs

# ==============================================================================
# 5. TOP EXECUTIVE COMMAND HEADER
# ==============================================================================
st.markdown('''
<div class="command-header">
    <div class="brand-section">
        <div class="brand-icon">🛡️</div>
        <div>
            <div class="brand-title">NEXUS RISK OPERATING SYSTEM</div>
            <div class="brand-sub">Graph Neural Network & Topology Risk Decisioning Engine // Enterprise Edition v5.2</div>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 16px;">
        <div class="sys-pill">
            <div class="sys-dot"></div>
            SYSTEM STATUS: ONLINE (LATENCY < 45ms)
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

# ==============================================================================
# 6. SIDEBAR - ĐIỀU HÀNH & TIẾP NHẬN REAL-TIME
# ==============================================================================
st.sidebar.markdown("### 🎛️ TRUNG TÂM BẢNG ĐIỀU HÀNH")

app_list = [n for n, d in G.nodes(data=True) if d.get("type") == "Application"]
selected_app = st.sidebar.selectbox("📋 Chọn Hồ Sơ Cần Kiểm Tra Deep-Dive:", app_list if app_list else ["Không có dữ liệu"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 TẠO ĐƠN VAY GIẢ LẬP REAL-TIME")

# Tự động quét IP thật của máy đang truy cập web
user_real_ip = st_javascript("await fetch('https://api.ipify.org').then(r => r.text())")
if not user_real_ip:
    user_real_ip = "113.161.72.10"

with st.sidebar.form("new_loan_application_form"):
    st.markdown("<small style='color:#64748b;'>Tự động phân tích vân tay mạng lưới</small>", unsafe_allow_html=True)
    
    in_name = st.text_input("Họ và Tên Khách Hàng:", value="Hoàng Trọng Kiên")
    in_cccd = st.text_input("Số CCCD/CMND:", value="012095006789")
    in_amount = st.number_input("Khoản Vay Yêu Cầu (VNĐ):", value=20000000, step=1000000)
    
    in_ip_address = st.text_input("Địa Chỉ IP Truy Cập:", value=str(user_real_ip))
    in_device_input = st.text_input("Môi Trường & Thiết Bị (Device FP):", value="FP-CC44B109")
    in_vpn = st.checkbox("Phát Hiện Sử Dụng VPN/Proxy", value=False)
    
    btn_submit = st.form_submit_button("🚀 Gửi Đơn Vay & Chạy AI Decisioning")

    if btn_submit:
        fp_generated = generate_device_hash(in_device_input.strip())
        ip_clean = in_ip_address.strip()
        app_id_new = f"APP-{np.random.randint(8806, 9999)}"
        
        # Đánh giá rủi ro động theo thời gian thực
        risk_score, decision, audit_reasons = calculate_realtime_risk(ip_clean, fp_generated, in_amount, in_vpn, df_apps)
        
        lat = 10.7769 if "113.161" in ip_clean else 21.0285
        lng = 106.7009 if "113.161" in ip_clean else 105.8542

        conn = sqlite3.connect("bnpl_enterprise.db")
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO loan_applications 
            (app_id, customer_name, national_id, loan_amount, ip_address, device_hash, latitude, longitude, is_proxy, risk_score, decision, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (app_id_new, in_name, in_cccd, float(in_amount), ip_clean, fp_generated, lat, lng, int(in_vpn), risk_score, decision, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

        st.sidebar.success(f"✅ Đã thêm **{app_id_new}**! AI Score: **{risk_score}%** ({decision})")
        st.rerun()

# ==============================================================================
# 7. METRICS MONITORING BOARD (4 COLUMNS CLASS-A GRID)
# ==============================================================================
total_apps_count = len(app_list)
fraud_apps_count = sum(1 for a in app_list if G.nodes[a].get("risk", 0) >= 60.0)
approved_apps_count = total_apps_count - fraud_apps_count
total_loan_val = df_apps["loan_amount"].sum() if not df_apps.empty else 0

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f'''
    <div class="glass-card">
        <div class="metric-label">TỔNG THẨM ĐỊNH</div>
        <div class="metric-val">{total_apps_count}</div>
        <div class="metric-sub" style="color: #38bdf8;">
            <span>🟢 Đang kết nối Graph Realtime</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

with m2:
    st.markdown(f'''
    <div class="glass-card" style="border-left: 4px solid #f43f5e;">
        <div class="metric-label">CẢNH BÁO BÙNG NỢ</div>
        <div class="metric-val" style="color: #fda4af;">{fraud_apps_count}</div>
        <div class="metric-sub" style="color: #f43f5e;">
            <span>🚨 Tự động phong tỏa tài khoản</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

with m3:
    st.markdown(f'''
    <div class="glass-card" style="border-left: 4px solid #10b981;">
        <div class="metric-label">ĐƠN PHÊ DUYỆT</div>
        <div class="metric-val" style="color: #6ee7b7;">{approved_apps_count}</div>
        <div class="metric-sub" style="color: #34d399;">
            <span>✅ An toàn giải ngân ngay</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

with m4:
    st.markdown(f'''
    <div class="glass-card" style="border-left: 4px solid #c084fc;">
        <div class="metric-label">QUY MÔ VỐN XÉT DUYỆT</div>
        <div class="metric-val" style="color: #e9d5ff; font-size: 1.8rem; padding-top: 4px;">{total_loan_val/1e6:,.0f} Triệu</div>
        <div class="metric-sub" style="color: #c084fc;">
            <span>🛡️ Tỷ lệ bảo toàn vốn: 100%</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# 8. CHI TIẾT ĐÁNH GIÁ HỒ SƠ ĐANG CHỌN (EXECUTIVE DECISION PANEL)
# ==============================================================================
if selected_app in G.nodes:
    app_info = df_apps[df_apps["app_id"] == selected_app].iloc[0]
    risk_val = app_info["risk_score"]
    is_rejected = app_info["decision"] == "REJECTED"

    col_decision, col_factors = st.columns([1.1, 1.9])

    with col_decision:
        st.markdown("##### 🎯 QUYẾT ĐỊNH THẨM ĐỊNH AI TỰ ĐỘNG")
        if is_rejected:
            st.markdown(f'''
            <div class="decision-panel-rejected">
                <div style="font-size: 1.15rem; font-weight: 800; color: #fda4af;">❌ TỪ CHỐI DUYỆT VAY (REJECTED)</div>
                <div style="margin-top: 10px; font-size: 0.88rem; color: #fecaca; line-height: 1.6;">
                    Khách hàng <b>{app_info['customer_name']}</b> (CCCD: {app_info['national_id']}) bị hệ thống tự động chặn do xung đột mạng lưới rủi ro cao.
                </div>
                <hr style="border-color: rgba(244, 63, 94, 0.3); margin: 16px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.88rem; color: #fda4af;">Điểm rủi ro AI (Graph Score):</span>
                    <span style="font-size: 1.6rem; font-weight: 800; color: #f43f5e; font-family: 'JetBrains Mono';">{risk_val}%</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px;">
                    <span style="font-size: 0.88rem; color: #fda4af;">Hạn mức phê duyệt:</span>
                    <span style="font-size: 1.1rem; font-weight: 700; color: #f43f5e;">0 VNĐ</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="decision-panel-approved">
                <div style="font-size: 1.15rem; font-weight: 800; color: #6ee7b7;">✅ PHÊ DUYỆT HẠN MỨC (APPROVED)</div>
                <div style="margin-top: 10px; font-size: 0.88rem; color: #a7f3d0; line-height: 1.6;">
                    Khách hàng <b>{app_info['customer_name']}</b> (CCCD: {app_info['national_id']}) đạt tiêu chuẩn an toàn đồ thị tín dụng.
                </div>
                <hr style="border-color: rgba(16, 185, 129, 0.3); margin: 16px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.88rem; color: #a7f3d0;">Điểm rủi ro AI (Graph Score):</span>
                    <span style="font-size: 1.6rem; font-weight: 800; color: #10b981; font-family: 'JetBrains Mono';">{risk_val}%</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px;">
                    <span style="font-size: 0.88rem; color: #a7f3d0;">Hạn mức đề xuất giải ngân:</span>
                    <span style="font-size: 1.1rem; font-weight: 700; color: #10b981;">{app_info['loan_amount']:,.0f} VNĐ</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)

    with col_factors:
        st.markdown("##### 🔬 CHI TIẾT MA TRẬN KẾT NỐI HẠ TẦNG (RISK MATRIX)")
        
        # Tính toán động các liên kết hạ tầng
        same_device_count = len(df_apps[df_apps["device_hash"] == app_info["device_hash"]])
        same_ip_count = len(df_apps[df_apps["ip_address"] == app_info["ip_address"]])

        matrix_df = pd.DataFrame({
            "Thông Số Hạ Tầng Thu Thập": ["Dấu Vân Tay Thiết Bị (Device Hash)", "Địa Chỉ IP Truy Cập Network", "Trạng Thái Proxy/VPN Check"],
            "Giá Trị Thu Thập Realtime": [app_info["device_hash"], app_info["ip_address"], "CÓ (Dùng VPN)" if app_info["is_proxy"] else "KHÔNG (IP Thật)"],
            "Số Hồ Sơ Đang Dùng Chung": [f"{same_device_count} Hồ Sơ", f"{same_ip_count} Hồ Sơ", "-"],
            "Đánh Giá Rủi Ro AI": [
                "🚨 Trùng thiết bị gian lận" if same_device_count > 1 else "🟢 Thiết bị độc lập",
                "⚠️ IP mật độ dùng chung cao" if same_ip_count > 1 else "🟢 Địa chỉ IP sạch",
                "⚠️ Cảnh báo giấu vị trí" if app_info["is_proxy"] else "🟢 Mạng dân dụng sạch"
            ]
        })
        st.dataframe(matrix_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ==============================================================================
# 9. CHUYÊN MỤC TABS HIỂN THỊ CHUYÊN NGHIỆP
# ==============================================================================
tab_graph, tab_analytics, tab_map, tab_database = st.tabs([
    "🕸️ ĐỒ THỊ MẠNG LIÊN KẾT REALTIME",
    "📊 PHÂN TÍCH CHỈ SỐ RỦI RO (ANALYTICS)",
    "📍 BẢN ĐỒ KHÔNG GIAN DÂN CƯ (MAP)",
    "📋 CƠ SỞ DỮ LIỆU SQLITE TOÀN BỘ"
])

# --- TAB 1: GRAPH VISUALIZATION ---
with tab_graph:
    st.markdown("##### 🕸️ Sơ Đồ Cụm Mạng Lưới Dùng Chung Hạ Tầng Tự Động (Interactive Graph Network)")
    net = Network(height="540px", width="100%", bgcolor="#04070d", font_color="#f8fafc")
    net.from_nx(G)
    net.barnes_hut(gravity=-3500, central_gravity=0.25, spring_length=95)
    
    for node in net.nodes:
        if node["id"] == selected_app:
            node["size"] = 34
            node["color"] = "#facc15"
        elif node.get("type") == "Application":
            node["size"] = 22

    net.save_graph("graph_ui_enterprise.html")
    with open("graph_ui_enterprise.html", "r", encoding="utf-8") as f:
        components.html(f.read(), height=560)

# --- TAB 2: ANALYTICS DASHBOARD ---
with tab_analytics:
    st.markdown("##### 📊 Báo Cáo Phân Tích Xu Hướng & Cảnh Báo Rủi Ro Tín Dụng")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("**Phân Bổ Trạng Thái Thẩm Định Hồ Sơ**")
        decision_counts = df_apps["decision"].value_counts()
        st.bar_chart(decision_counts, color="#38bdf8")

    with col_chart2:
        st.markdown("**Phân Bổ Điểm Rủi Ro AI (Risk Score Distribution)**")
        st.line_chart(df_apps["risk_score"], color="#c084fc")

# --- TAB 3: SPATIAL MAP ---
with tab_map:
    st.markdown("##### 📍 Bản Đồ Vị Trí Địa Lý Người Dùng Đăng Ký Khoản Vay (GeoIP Mapping)")
    if selected_app in G.nodes:
        app_geo = df_apps[df_apps["app_id"] == selected_app].iloc[0]
        m = folium.Map(location=[app_geo["latitude"], app_geo["longitude"]], zoom_start=12, tiles="CartoDB dark_matter")
        
        is_bad = app_geo["decision"] == "REJECTED"
        folium.Marker(
            [app_geo["latitude"], app_geo["longitude"]],
            popup=f"Khách hàng: {app_geo['customer_name']}\nĐơn vay: {selected_app}",
            icon=folium.Icon(color="red" if is_bad else "green", icon="user", prefix="fa")
        ).add_to(m)

        if is_bad:
            folium.Circle(
                location=[app_geo["latitude"], app_geo["longitude"]],
                radius=1500, color="#f43f5e", fill=True, fill_opacity=0.2,
                popup="Khu vực phát hiện cụm bùng nợ nguy cơ cao"
            ).add_to(m)

        st_folium(m, width="100%", height=480)

# --- TAB 4: DATABASE ENGINE ---
with tab_database:
    st.markdown("##### 📋 Nhật Ký CSDL Tín Dụng Đồng Bộ Trong Hệ Thống (SQLite Data Lake)")
    st.dataframe(df_apps, use_container_width=True, hide_index=True)