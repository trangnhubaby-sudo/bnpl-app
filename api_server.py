from fastapi import FastAPI, Request, BackgroundTasks
from pydantic import BaseModel, Field
import sqlite3
from datetime import datetime
import uvicorn

app = FastAPI(
    title="NEXUS Anti-Fraud API Gateway",
    description="Cổng tiếp nhận và phân tích dữ liệu rủi ro BNPL Real-time",
    version="4.2.0-PROD"
)

# Structure dữ liệu gửi lên từ App Vay
class LoanApplication(BaseModel):
    customer_id: str = Field(..., example="KH-8899")
    loan_amount: float = Field(..., example=15000000)
    latitude: float = Field(..., example=10.7769)
    longitude: float = Field(..., example=106.7009)
    imei: str = Field(..., example="TB-IMEI-864912")

def init_db():
    """Khởi tạo CSDL SQLite chuẩn Enterprise"""
    conn = sqlite3.connect("fraud_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loan_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT UNIQUE,
            loan_amount REAL,
            ip_address TEXT,
            latitude REAL,
            longitude REAL,
            imei TEXT,
            status TEXT,
            created_at TEXT
        )
    """)
    
    # Nạp dữ liệu mẫu ban đầu nếu CSDL trống
    cursor.execute("SELECT COUNT(*) FROM loan_requests")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("KH-1008", 15000000, "104.28.19.14", 10.7769, 106.7009, "TB-IMEI-864912", "RỦI RO RẤT CAO", "2026-08-27 10:00:00"),
            ("KH-1009", 12000000, "104.28.19.14", 10.7750, 106.7020, "TB-IMEI-864912", "RỦI RO RẤT CAO", "2026-08-27 10:05:00"),
            ("KH-1010", 20000000, "104.28.19.14", 10.7780, 106.6990, "TB-IMEI-864912", "RỦI RO RẤT CAO", "2026-08-27 10:10:00"),
            ("KH-2001", 8000000, "14.225.21.18", 21.0285, 105.8542, "TB-IMEI-990011", "XÁC MINH AN TOÀN", "2026-08-27 10:15:00"),
            ("KH-2002", 5000000, "116.109.12.5", 16.0544, 108.2022, "TB-IMEI-771122", "XÁC MINH AN TOÀN", "2026-08-27 10:20:00")
        ]
        cursor.executemany("""
            INSERT INTO loan_requests (customer_id, loan_amount, ip_address, latitude, longitude, imei, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_data)
    conn.commit()
    conn.close()

init_db()

@app.post("/api/v1/submit-loan", summary="Gửi hồ sơ vay & Tự động quét IP/GPS")
async def receive_loan_request(request: Request, data: LoanApplication):
    # 1. Tự động đọc IP thực tế từ Request Header
    client_ip = request.client.host
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0]

    # 2. Quy tắc phát hiện rủi ro cơ bản
    BLACK_IPS = ["104.28.19.14", "113.161.72.14"]
    BLACK_IMEIS = ["TB-IMEI-864912"]
    
    is_fraud = (client_ip in BLACK_IPS) or (data.imei in BLACK_IMEIS)
    status = "RỦI RO RẤT CAO" if is_fraud else "XÁC MINH AN TOÀN"

    # 3. Ghi dữ liệu vào CSDL dùng chung với Streamlit
    conn = sqlite3.connect("fraud_data.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO loan_requests 
            (customer_id, loan_amount, ip_address, latitude, longitude, imei, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.customer_id,
            data.loan_amount,
            client_ip,
            data.latitude,
            data.longitude,
            data.imei,
            status,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
    finally:
        conn.close()

    return {
        "status": "success",
        "message": "Đã đồng bộ dữ liệu vào hệ thống thẩm định AI",
        "evaluated_risk": status,
        "assigned_ip": client_ip
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)