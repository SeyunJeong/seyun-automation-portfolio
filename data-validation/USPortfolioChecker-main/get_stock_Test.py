import requests

def get_stock_data(api_key, symbol):
    """
    주어진 종목(symbol)의 종목명, 종가(price), 시가총액(market_cap)을 반환하는 함수.
    """
    base_quote_url = "https://api.example-stock-data.com/market-data/quote/"
    base_shares_url = "https://api.example-stock-data.com/fundamentals/outstanding-shares/"
    
    # 1. 종목명과 종가 가져오기
    quote_url = f"{base_quote_url}{symbol}"
    quote_params = {"token": api_key}
    
    try:
        quote_response = requests.get(quote_url, params=quote_params)
        quote_response.raise_for_status()
        quote_data = quote_response.json()
        
        stock_name = quote_data.get("name", "종목명 정보를 찾을 수 없습니다.")
        price = quote_data.get("price", "가격 정보를 찾을 수 없습니다.")
        
    except requests.exceptions.RequestException as e:
        print(f"시세 데이터 요청 중 오류 발생: {e}")
        return None
    
    # 2. 발행 주식 수 가져오기
    shares_url = f"{base_shares_url}{symbol}"
    shares_params = {"token": api_key}
    
    try:
        shares_response = requests.get(shares_url, params=shares_params)
        shares_response.raise_for_status()
        shares_data = shares_response.json()
        
        # 최근 연도의 연간 발행 주식 수 사용 (단위: 백만)
        outstanding_shares = shares_data[0].get("annual", 0) * 1e6  # 백만 단위 변환
        
    except requests.exceptions.RequestException as e:
        print(f"발행 주식 데이터 요청 중 오류 발생: {e}")
        return None
    
    # 3. 시가총액 계산
    try:
        market_cap = price * outstanding_shares  # 시가총액 = 가격 x 발행 주식 수
    except TypeError:
        print("가격 또는 발행 주식 수 데이터가 유효하지 않습니다.")
        return None
    
    # 결과 반환
    return {
        "name": stock_name,
        "price": price,
        "market_cap": market_cap
    }

if __name__ == "__main__":
    # 여기에 API 키와 종목 코드를 입력하세요
    api_key = "47d4a902a68e4447834e634a397bec74"  # API 키 입력
    symbol = "RNW"           # 테스트할 종목 코드
    
    stock_data = get_stock_data(api_key, symbol)
    if stock_data:
        print(f"종목명: {stock_data['name']}")
        print(f"현재 가격: {stock_data['price']} USD")
        print(f"시가총액: {stock_data['market_cap']:.2f} USD")
    else:
        print("데이터 가져오기 실패!")
