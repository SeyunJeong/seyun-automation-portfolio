import requests
from modules.data_processing import clean_stock_code
from datetime import datetime, timedelta

class StockDataAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_quote_url = "https://api.example-stock-data.com/market-data/quote/"
        self.base_shares_url = "https://api.example-stock-data.com/fundamentals/outstanding-shares/"
        self.base_historical_url = "https://api.example-stock-data.com/market-data/historical/"
        self.cache = {}  # 캐싱

    def fetch_stock_data(self, symbol):
        """
        주어진 종목(symbol)의 종목명, 종가(close price), 시가총액을 반환
        """
        formatted_symbol = clean_stock_code(symbol)  # ✅ 종목 코드 변환
        print(f"🔄 API 요청 종목 코드 변환: {symbol} → {formatted_symbol}")  # ✅ 디버깅 추가

        if formatted_symbol in self.cache:
            return self.cache[formatted_symbol]  # ✅ 캐싱된 데이터 반환

        try:
            # ✅ 1. 종목명 가져오기
            quote_response = requests.get(
                f"{self.base_quote_url}{formatted_symbol}",
                params={"token": self.api_key}
            )
            if quote_response.status_code != 200:
                print(f"⚠️ Failed to fetch quote data for {formatted_symbol}. Status code: {quote_response.status_code}")
                return None
            
            quote_data = quote_response.json()
            stock_name = quote_data.get("name", "Unknown")

            # ✅ 2. 전일 종가 가져오기
            price = self.get_previous_close_price(formatted_symbol)

            if price == 0:
                print(f"⚠️ No valid close price found for {formatted_symbol}.")
                return None

            # ✅ 3. 발행 주식 수 가져오기
            outstanding_shares = self.get_outstanding_shares(formatted_symbol)

            # ✅ 4. 시가총액 계산
            market_cap = price * outstanding_shares if price and outstanding_shares else 0

            stock_data = {
                "name": stock_name,
                "price": price,  # ✅ 전일 종가 사용
                "market_cap": market_cap
            }
            self.cache[formatted_symbol] = stock_data  # ✅ 캐싱 저장

            return stock_data

        except requests.RequestException as e:
            print(f"🚨 API 요청 실패: {formatted_symbol}, 오류: {e}")
            return {
                "name": "Unknown",
                "price": 0,
                "market_cap": 0
            }

    def get_previous_close_price(self, symbol):
        """
        가장 최근 거래일의 종가(close price)를 가져오는 함수
        """
        days_checked = 0
        price = 0

        while days_checked < 7:  # 최대 7일간 체크 (거래일이 아닌 경우 대비)
            today = (datetime.now() - timedelta(days=days_checked)).strftime("%Y-%m-%d")  # ✅ 오늘 날짜
            yesterday = (datetime.now() - timedelta(days=days_checked + 1)).strftime("%Y-%m-%d")  # ✅ 어제 날짜

            print(f"📅 데이터 요청 날짜 범위: {yesterday} ~ {today}")  # ✅ 날짜 확인

            historical_url = f"{self.base_historical_url}{symbol}"
            historical_params = {
                "token": self.api_key,
                "start_date": yesterday,  # ✅ 어제 날짜
                "end_date": today,  # ✅ 오늘 날짜
            }
            print(f"📡 요청 URL: {historical_url}")
            print(f"📄 요청 파라미터: {historical_params}")

            historical_response = requests.get(historical_url, params=historical_params)

            if historical_response.status_code != 200:
                print(f"⚠️ Failed to fetch historical data for {symbol}. Status code: {historical_response.status_code}")
                return 0

            historical_data = historical_response.json()
            print(f"📊 API 응답 데이터: {historical_data}")  # ✅ 응답 확인

            if historical_data and isinstance(historical_data, list) and len(historical_data) > 0:
                price = historical_data[-1].get("c", 0)  # ✅ 마지막 거래일의 종가 가져오기
                return price  # 종가를 찾으면 바로 반환

            days_checked += 1  # 하루 전으로 이동

        return 0  # 7일간 데이터가 없으면 0 반환


    def get_outstanding_shares(self, symbol):
        """
        종목의 발행 주식 수를 가져오는 함수
        """
        shares_response = requests.get(
            f"{self.base_shares_url}{symbol}",
            params={"token": self.api_key}
        )
        outstanding_shares = 0

        if shares_response.status_code == 200:
            shares_data = shares_response.json()
            if shares_data and isinstance(shares_data, list) and len(shares_data) > 0:
                outstanding_shares = shares_data[0].get("annual", 0) * 1e6
            else:
                print(f"⚠️ No outstanding shares data for {symbol}.")
        elif shares_response.status_code == 404:
            print(f"⚠️ Shares data not found for {symbol} (404). Setting default values.")
        else:
            print(f"⚠️ Failed to fetch shares data for {symbol}. Status code: {shares_response.status_code}")

        return outstanding_shares
