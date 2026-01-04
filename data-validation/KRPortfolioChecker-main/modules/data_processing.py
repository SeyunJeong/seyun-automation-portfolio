def process_market_cap(market_cap):
    """🔥 시가총액을 천 단위로 변환 (None 방지)"""
    return round((market_cap or 0) / 1000, 2)

def clean_stock_code(stock_code):
    """
    ✅ 종목 코드에서 맨 앞의 "A"를 제거 (예: A005930 → 005930)
    """
    return stock_code[1:] if stock_code.startswith("A") else stock_code

def prepare_data(raw_codes, api_fetch_function, cache):
    data = []
    for raw_code in raw_codes:
        stock_code = clean_stock_code(raw_code[0]) if raw_code and len(raw_code) > 0 else "UNKNOWN"

        # ✅ 종목 코드 가공 후 API 요청 전에 확인
        formatted_code = clean_stock_code(stock_code)  # ✅ API 요청 전에 종목 코드 변환
        print(f"🔄 API 요청 종목 코드 변환: {stock_code} → {formatted_code}")  # ✅ 디버깅 추가

        if formatted_code in cache:
            stock_data = cache[formatted_code]
        else:
            stock_data = api_fetch_function(formatted_code)  # ✅ 변환된 코드로 API 요청
            cache[formatted_code] = stock_data

        # ✅ API에서 데이터를 가져오지 못하는 경우 확인
        if not stock_data or stock_data.get("name") is None:
            print(f"⚠️ API에서 데이터를 가져오지 못함: {formatted_code}")  # ✅ 디버깅 추가
            stock_data = {
                "name": "N/A",
                "market_cap": 0,
                "price": 0
            }

        data.append({
            "stock_code": formatted_code,  # ✅ stock_code 추가 (write_columns에서 필요)
            "product_name": stock_data.get("name", "N/A"),  
            "market_cap": process_market_cap(stock_data.get("market_cap")),  
            "price": stock_data.get("price", 0)  
        })

    print(f"📌 준비된 데이터 개수: {len(data)}")  # ✅ 디버깅 추가
    return data

