import os
import json
import time
from modules.google_sheets import GoogleSheets
from modules.stock_api import StockAPI
from modules.data_processing import prepare_data
from config.config import SHEET_TAB, SPREADSHEET_ID, RANGE_WRITE, STOCK_API_KEY, STOCK_API_SECRET, CACHE

CHECKPOINT_FILE = "checkpoint.json"  # ✅ 진행 상태 저장 파일

def load_checkpoint():
    """✅ GitHub Actions 환경 변수 또는 체크포인트 파일에서 마지막으로 처리한 인덱스를 로드"""
    checkpoint_str = os.getenv("LAST_PROCESSED_INDEX")

    if checkpoint_str:
        try:
            checkpoint_data = json.loads(checkpoint_str)
            return checkpoint_data.get("last_processed_index", 0)
        except json.JSONDecodeError:
            return 0

    try:
        with open(CHECKPOINT_FILE, "r") as file:
            content = file.read().strip()
            return json.loads(content).get("last_processed_index", 0) if content else 0
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def save_checkpoint(index):
    """✅ 체크포인트를 GitHub Actions 환경 변수와 파일에 저장"""
    checkpoint_data = {"last_processed_index": index}

    with open(CHECKPOINT_FILE, "w") as file:
        json.dump(checkpoint_data, file)

    if os.getenv("GITHUB_ENV"):
        with open(os.getenv("GITHUB_ENV"), "a") as env_file:
            env_file.write(f'LAST_PROCESSED_INDEX={json.dumps(checkpoint_data)}\n')

def main():
    sheets = GoogleSheets("config/service-account-key.json", SPREADSHEET_ID, SHEET_TAB)
    api = StockAPI(STOCK_API_KEY, STOCK_API_SECRET)  # Stock API 초기화

    # ✅ 마지막으로 처리된 위치 로드
    last_index = load_checkpoint()

    # ✅ Step 1: Read stock codes (50개 단위로 가져오기)
    stock_codes = sheets.read_column() or []
    if not stock_codes:
        print("🚨 종목 코드가 없습니다. 프로그램을 종료합니다.")
        return

    batch_size = 50  # ✅ 50개씩 처리
    for i in range(last_index, len(stock_codes), batch_size):
        batch_codes = stock_codes[i : i + batch_size]

        # ✅ Step 2: Fetch and process data (체크포인트 방식 적용)
        data = prepare_data(batch_codes, api.fetch_stock_data, CACHE)
        if not data:
            print(f"⚠️ 데이터 없음: {batch_codes}. 다음 배치로 넘어갑니다.")
            continue

        # ✅ Step 3: Write data to Google Sheets
        write_result = sheets.write_columns(data, RANGE_WRITE)
        if write_result:
            print(f"✅ Google Sheets 업데이트 완료: {len(data)}개 종목.")
        else:
            print(f"⚠️ Google Sheets 업데이트 실패: {batch_codes}.")

        # ✅ 진행 상태 저장 (체크포인트 업데이트)
        save_checkpoint(i + batch_size)
        print(f"✅ Checkpoint 저장 완료: {i + batch_size}까지 처리됨")

        # ✅ API 요청 간격 조절
        time.sleep(1)  

if __name__ == "__main__":
    main()
