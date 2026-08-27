from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sqlite3
from datetime import datetime
import uvicorn

app = FastAPI(
    title="NEXUS Anti-Fraud API Gateway",
    description="Cổng tiếp nhận và phân tích dữ liệu rủi ro BNPL Real-time",
    version="4.2.0-PROD"
)

# Cấu hình CORS để cho phép gọi API từ mọi nguồn (Streamlit, Web App, Mobile App)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khai báo cấu trúc dữ liệu JSON gửi lên
class LoanApplication(BaseModel):
    customer_id: str = Field(..., example="KH-9999")
    loan_amount: float = Field(..., example=15000000)
    latitude: float = Field(..., example=10.7769)
    longitude: float = Field(..., example=106.7009)
    imei: str = Field(..., example="TB-IMEI-864912")

def init_db():
    """Khởi tạo CSDL SQLite chung với Streamlit"""
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
    conn.commit()
    conn.close()

# Khởi chạy tạo bảng khi server chạy
init_db()

@app.get("/")
def read_root():
    return {"status": "online", "system": "NEXUS Anti-Fraud API Gateway v4.2"}

@app.post("/api/v1/submit-loan", summary="Gửi hồ sơ vay & Tự động kiểm tra rủi ro")
async def receive_loan_request(request: Request, data: LoanApplication):
    # 1. Tự động trích xuất địa chỉ IP thực tế của thiết bị gửi request
    client_ip = request.client.host
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0]
        
    if client_ip in ["127.0.0.1", "testclient"]:
        client_ip = "104.28.19.14"  # Gắn IP mẫu để test cụm rủi ro trên Localhost

    # 2. Quy tắc phát hiện cụm bùng nợ (Blacklist)
    BLACK_IPS = ["104.28.19.14", "113.161.72.14"]
    BLACK_IMEIS = ["TB-IMEI-864912"]
    
    is_fraud = (client_ip in BLACK_IPS) or (data.imei in BLACK_IMEIS)
    status = "RỦI RO RẤT CAO" if is_fraud else "XÁC MINH AN TOÀN"

    # 3. Ghi/Cập nhật dữ liệu vào SQLite
    conn = sqlite3.connect("fraud_data.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO loan_requests 
            (customer_id, loan_amount, ip_address, latitude, longitude, imei, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(customer_id) DO UPDATE SET
                loan_amount=excluded.loan_amount,
                ip_address=excluded.ip_address,
                latitude=excluded.latitude,
                longitude=excluded.longitude,
                imei=excluded.imei,
                status=excluded.status,
                created_at=excluded.created_at
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
        "message": "Đã tiếp nhận dữ liệu và đồng bộ vào CSDL",
        "data": {
            "customer_id": data.customer_id,
            "assigned_ip": client_ip,
            "evaluated_status": status
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)