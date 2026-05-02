from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx
import time
from collections import deque

app = FastAPI()

# ==== CONFIGURATION ====
RATE_LIMIT = 1000          # Max requests
RATE_WINDOW = 5            # Seconds
DEVELOPER_INFO = "SB-SAKIB @sakib01994"

# Rate limiting storage
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
    return {"message": "API is running", "developer": DEVELOPER_INFO}

@app.get("/fetch")
async def fetch_data(url: str = Query(None)):
    # 1. Validation
    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url' parameter")

    # 2. Rate Limit Check
    # Note: In Vercel, use 'x-forwarded-for' to get real IP
    client_ip = "system" # Default
    
    if is_rate_limited(client_ip):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded. Try again later."}
        )

    # 3. Build API Call
    api_endpoint = f"https://utdqxiuahh.execute-api.ap-south-1.amazonaws.com/pro/fetch"
    params = {
        "url": url,
        "user_id": "h2"
    }
    headers = {
        "x-api-key": "fAtAyM17qm9pYmsaPlkAT8tRrDoHICBb2NnxcBPM",
        "User-Agent": "okhttp/4.12.0",
        "Accept-Encoding": "gzip"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_endpoint, params=params, headers=headers)
            
            if response.status_code != 200:
                return JSONResponse(status_code=response.status_code, content=response.json())
            
            data = response.json()
            
            # 4. Add Developer Attribution
            if isinstance(data, dict):
                data["developer"] = DEVELOPER_INFO
            
            return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))