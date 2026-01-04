import requests
from datetime import datetime, timedelta

# 테스트용 API 정보 (포트폴리오용 예시)
API_KEY = "your-stock-data-api-key-here"
BASE_HISTORICAL_URL = "https://api.example-stock-data.com/market-data/historical/"
BASE_QUOTE_URL = "https://api.example-stock-data.com/market-data/quote/"

# ✅ 테스트할 종목 리스트
test_symbols = ["TSLA", "AAPL", "GOOGL", "ZENV", "OPAL", "AIRT", "WILC"]  # 🔴 필요한 종목 추가 가능

def test_historical_api(symbol):
    """
    특정 종목(symbol)에 대한 전일 종가 데이터를 가져와 테스트하는 함수
    """
    days_checked = 0
    max_days = 7  # 최대 7일 전까지 데이터 확인
    price = None

    while days_checked < max_days:
        end_date = (datetime.now() - timedelta(days=days_checked + 1)).strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days_checked + 2)).strftime("%Y-%m-%d")  # ✅ 종료일보다 하루 전으로 설정

        print(f"\n🔍 [테스트] {symbol} - 요청 날짜: {start_date} ~ {end_date}")

        historical_url = f"{BASE_HISTORICAL_URL}{symbol}"
        params = {
            "token": API_KEY,
            "start_date": start_date,  # ✅ 종료일보다 하루 전으로 설정
            "end_date": end_date,
        }
        
        response = requests.get(historical_url, params=params)
        print(f"📡 요청 URL: {response.url}")  # ✅ 요청 URL 출력

        if response.status_code != 200:
            print(f"⚠️ API 요청 실패! 상태 코드: {response.status_code}")
            print(f"🔍 응답 내용: {response.text}")
            return

        historical_data = response.json()
        print(f"📊 API 응답 데이터: {historical_data}")  # ✅ 응답 데이터 출력

        if historical_data and isinstance(historical_data, list) and len(historical_data) > 0:
            price = historical_data[0].get("c", 0)  # ✅ 종가 가져오기
            print(f"✅ {symbol}의 전일 종가: {price} (날짜: {end_date})")
            return  # 데이터를 찾았으면 종료

        days_checked += 1  # 하루 전으로 이동

    print(f"⚠️ {symbol}에 대한 최근 7일간 거래 데이터 없음!")

def test_quote_api(symbol):
    """
    특정 종목(symbol)이 존재하는지 확인하는 함수
    """
    quote_url = f"{BASE_QUOTE_URL}{symbol}"
    params = {"token": API_KEY}

    response = requests.get(quote_url, params=params)
    print(f"\n📡 [테스트] {symbol} - 요청 URL: {response.url}")

    if response.status_code != 200:
        print(f"⚠️ API 요청 실패! 상태 코드: {response.status_code}")
        print(f"🔍 응답 내용: {response.text}")
        return

    quote_data = response.json()
    print(f"📊 API 응답 데이터: {quote_data}")  # ✅ 응답 데이터 출력

    stock_name = quote_data.get("name", "Unknown")
    print(f"✅ 종목명 확인: {stock_name}")

if __name__ == "__main__":
    for symbol in test_symbols:
        print("\n==============================")
        print(f"🚀 테스트 시작: {symbol}")
        print("==============================")
        
        test_quote_api(symbol)  # ✅ 종목이 실제 존재하는지 확인
        test_historical_api(symbol)  # ✅ 전일 종가를 가져올 수 있는지 확인
