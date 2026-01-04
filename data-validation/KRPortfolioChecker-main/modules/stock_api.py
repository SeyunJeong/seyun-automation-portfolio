import requests
import time
from modules.data_processing import clean_stock_code

class StockAPI:
    def __init__(self, app_key, app_secret):
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = "https://api.example-stock-provider.com"
        self.last_request_time = 0  # ✅ last_request_time을 먼저 초기화
        self.min_delay = 0.5
        self.access_token = self.get_access_token()  # access_token은 마지막에 초기화

    def _wait_for_rate_limit(self):
        """API 요청 간 지연 시간을 관리"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self.last_request_time = time.time()

    def get_access_token(self):
        """OAuth 토큰 발급 (유효기간: 24시간)"""
        self._wait_for_rate_limit()
        url = f"{self.base_url}/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
        payload = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        for attempt in range(3):  # 최대 3번 재시도
            try:
                response = requests.post(url, data=payload, headers=headers)
                data = response.json()
                if "access_token" in data:
                    return data["access_token"]
                else:
                    print(f"❌ OAuth 토큰 발급 실패 (시도 {attempt + 1}/3):", data)
                    if attempt < 2:  # 마지막 시도가 아니면 대기
                        time.sleep(2 ** attempt)  # 지수 백오프
            except requests.exceptions.RequestException as e:
                print(f"❌ 요청 실패 (시도 {attempt + 1}/3):", e)
                if attempt < 2:
                    time.sleep(2 ** attempt)
        
        return None

    def fetch_stock_data(self, symbol):
        """종목 정보 조회 (종목명, 종가, 시가총액)"""
        self._wait_for_rate_limit()
        stock_code = clean_stock_code(symbol)
        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/search-stock-info"
        params = {"PRDT_TYPE_CD": "300", "PDNO": stock_code}
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "custtype": "P",
            "tr_id": "CTPF1002R"
        }

        for attempt in range(3):  # 최대 3번 재시도
            try:
                response = requests.get(url, headers=headers, params=params)
                data = response.json()
                if "output" in data:
                    stock_info = data["output"]
                    return {
                        "name": stock_info.get("prdt_name", "Unknown"),
                        "price": int(stock_info.get("thdt_clpr", 0)),
                        "market_cap": round((int(stock_info.get("thdt_clpr", 0)) * 
                                          int(stock_info.get("lstg_stqt", 0))) / 1e5, 2)
                    }
                else:
                    print(f"❌ 주식 정보 조회 실패 (시도 {attempt + 1}/3):", data)
                    if attempt < 2:
                        time.sleep(2 ** attempt)
            except requests.exceptions.RequestException as e:
                print(f"❌ 요청 실패 (시도 {attempt + 1}/3):", e)
                if attempt < 2:
                    time.sleep(2 ** attempt)
        
        return None
