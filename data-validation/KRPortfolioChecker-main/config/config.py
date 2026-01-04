# Google Sheets Configuration
SPREADSHEET_ID = "your-google-spreadsheet-id-here"
SHEET_TAB = "Portfolio_Validation"  # 기본 검수 탭 이름
RANGE_READ = "A3:A"
RANGE_WRITE = {
    "NAME": "L3:L",
    "MARKET_CAP": "M3:M",
    "CLOSE_PRICE": "N3:N",
}

# Stock API 설정 (포트폴리오용 예시)
STOCK_API_KEY = "your-stock-api-key-here"
STOCK_API_SECRET = "your-stock-api-secret-here"

# Other Settings
CACHE = {}
