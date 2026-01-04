import requests

# Stock API 정보 (포트폴리오용 예시)
APP_KEY = "your-stock-api-key-here"
APP_SECRET = "your-stock-api-secret-here"
STOCK_CODE = "SAMPLE"  # 예제 종목 코드

# ✅ 1. OAuth Access Token 발급
def get_access_token():
    url = "https://api.example-stock-provider.com/oauth2/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
    }

    payload = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }

    response = requests.post(url, data=payload, headers=headers) 
    data = response.json()
    
    if "access_token" in data:
        return data["access_token"]
    else:
        print("❌ OAuth 토큰 발급 실패:", data)
        return None

# ✅ 2. 주식 기본 정보 조회 (GET 요청)
def get_stock_info(access_token):
    url = "https://api.example-stock-provider.com/api/v1/stock/info"

    params = {
        "PRDT_TYPE_CD": "300",  # ✅ 상품 유형: 주식, ETF, ETN, ELW (문서에서 요구한 값)
        "PDNO": STOCK_CODE  # ✅ 종목 코드 (문서 기준으로 수정)
    }

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "custtype": "P",  # ✅ 개인 계정 (문서에 명시된 필수값)
        "tr_id": "CTPF1002R"  # ✅ 문서에서 제시한 거래 ID (기본정보 조회용)
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if "output" in data:
        return data["output"]
    else:
        print("❌ 주식 정보 조회 실패:", data)
        return None

# ✅ 실행 흐름
access_token = get_access_token()
if access_token:
    stock_info = get_stock_info(access_token)
    if stock_info:
        print("📌 주식 정보:", stock_info)
