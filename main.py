from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import httpx
import time
from collections import deque

app = FastAPI()

# ==== CONFIGURATION ====
RATE_LIMIT = 1000
RATE_WINDOW = 5
DEVELOPER_INFO = "SB-SAKIB @sakib01994"

# Rate Limit Storage (In-memory)
user_requests = {}

def is_rate_limited(client_ip: str) -> bool:
    now = time.time()
    if client_ip not in user_requests:
        user_requests[client_ip] = deque()
    window = user_requests[client_ip]
    while window and window[0] < now - RATE_WINDOW:
        window.popleft()
    if len(window) >= RATE_LIMIT:
        return True
    window.append(now)
    return False

@app.get("/")
async def root():
    return {"status": "Online", "developer": DEVELOPER_INFO}

@app.get("/fetch")
async def fetch_data(url: str = Query(None)):
    # ১. ভ্যালিডেশন
    if not url:
        return JSONResponse(status_code=400, content={"error": "Missing 'url' parameter"})

    # ২. রেট লিমিট চেক
    if is_rate_limited("system"):
        return JSONResponse(status_code=429, content={"error": "Rate limit exceeded. Please wait."})

    # ৩. সোর্স এপিআই কল
    api_endpoint = "https://utdqxiuahh.execute-api.ap-south-1.amazonaws.com/pro/fetch"
    params = {"url": url, "user_id": "h2"}
    headers = {
        "x-api-key": "fAtAyM17qm9pYmsaPlkAT8tRrDoHICBb2NnxcBPM",
        "User-Agent": "okhttp/4.12.0",
        "Accept-Encoding": "gzip"
    }

    try:
        async with httpx.AsyncClient(timeout=25.0, follow_redirects=True) as client:
            response = await client.get(api_endpoint, params=params, headers=headers)
            
            # ৪. রেসপন্স প্রসেসিং
            try:
                data = response.json()
            except:
                return JSONResponse(status_code=500, content={"error": "Source API returned invalid data"})

            # ৫. প্রিমিয়াম টাচ (আপনার নাম ও আইডি যুক্ত করা)
            if isinstance(data, dict):
                # এটি অরিজিনাল ডেটার সাথে আপনার ইনফো মার্জ করে দিবে
                data = {"developer": DEVELOPER_INFO, **data}
            
            return data

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
