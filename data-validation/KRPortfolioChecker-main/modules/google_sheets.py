import time
import json
import requests
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from modules.data_processing import clean_stock_code


CHECKPOINT_FILE = "checkpoint.json"

class GoogleSheets:
    def __init__(self, service_account_file, spreadsheet_id, sheet_tab="Sheet1"):
        self.service_account_file = service_account_file
        self.spreadsheet_id = spreadsheet_id
        self.sheet_tab = sheet_tab
        self.credentials = None
        self.service = None
        self.cached_data = None
        self.refresh_credentials()
        self.checkpoint = self.load_checkpoint()

    def refresh_credentials(self):
        """🔥 Google API 인증 토큰 자동 갱신"""
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        self.credentials = Credentials.from_service_account_file(self.service_account_file, scopes=scopes)
        if self.credentials.expired or not self.credentials.valid:
            self.credentials.refresh(Request())
        self.service = build("sheets", "v4", credentials=self.credentials)
        print("🔄 Google API 인증 토큰이 갱신되었습니다.")

    def load_checkpoint(self):
        """✅ 체크포인트 로드 (JSON 오류 방지)"""
        try:
            with open(CHECKPOINT_FILE, "r") as file:
                content = file.read().strip()
                return json.loads(content) if content else {"last_processed_index": 0}
        except (FileNotFoundError, json.JSONDecodeError):
            return {"last_processed_index": 0}

    def save_checkpoint(self, index):
        """✅ 체크포인트 저장"""
        with open(CHECKPOINT_FILE, "w") as file:
            json.dump({"last_processed_index": index}, file)

    def get_last_row(self):
        """✅ A열에서 마지막 데이터가 있는 행 번호를 찾음"""
        sheet = self.service.spreadsheets()
        try:
            result = sheet.values().get(spreadsheetId=self.spreadsheet_id, range=f"{self.sheet_tab}!A:A").execute()
            values = result.get("values", [])
            return len(values)  # ✅ 실제 데이터가 있는 마지막 행 번호 반환
        except HttpError as e:
            print(f"🚨 Google Sheets API 오류 발생: {e}")
            return 0  # 오류 발생 시 기본값 반환

    def read_column(self):
        """🔥 A열에서 데이터가 있는 마지막 행까지만 읽어오기"""
        last_row = self.get_last_row()
        if last_row == 0:
            print("🚨 A열에 데이터가 없습니다.")
            return []

        sheet = self.service.spreadsheets()
        
        try:
            # ✅ A열 전체에서 종목 코드를 가져옴
            result = sheet.values().get(spreadsheetId=self.spreadsheet_id, range=f"{self.sheet_tab}!A1:A{last_row}").execute()
            values = result.get("values", [])
            print(f"📌 A열에서 가져온 종목 코드 개수: {len(values)}")  # ✅ 디버깅 추가
        except HttpError as e:
            print(f"🚨 Google Sheets API 오류 발생: {e}")
            return []

        # ✅ 범위를 나누어서 읽기 (50개 단위)
        range_segments = [f"A{i}:A{i+49}" for i in range(3, last_row + 1, 50)]  
        result_values = []
        last_index = self.checkpoint["last_processed_index"]

        for i, full_range in enumerate(range_segments):
            if i * 50 < last_index:
                continue  # ✅ 체크포인트를 지나간 경우 스킵

            try:
                result = sheet.values().get(spreadsheetId=self.spreadsheet_id, range=f"{self.sheet_tab}!{full_range}").execute()
                result_values.extend(result.get('values', []))
                self.save_checkpoint(i * 50)
                time.sleep(3)  # ✅ API 요청 속도 조절
            except HttpError as e:
                print(f"🚨 Google Sheets API 오류 발생: {e}")
                return []

        self.cached_data = result_values
        return result_values


    def write_columns(self, data, ranges):
        """🔥 기존 데이터를 유지하면서, 각 종목의 위치에 맞게 값 입력"""
        sheet = self.service.spreadsheets()
        batch_size = 50  

        # ✅ 기존 A열(종목 코드) 데이터 읽어오기
        try:
            result = sheet.values().get(spreadsheetId=self.spreadsheet_id, range=f"{self.sheet_tab}!A:A").execute()
            stock_list = result.get("values", [])
        except HttpError as e:
            print(f"🚨 A열 데이터를 가져오는 중 오류 발생: {e}")
            return

        if not stock_list:
            print("🚨 A열에 데이터가 없습니다.")
            return

        # ✅ 종목 코드 → 해당 행 번호 매핑 (Google Sheets는 1부터 시작)
        stock_map = {clean_stock_code(stock_list[i][0]): i + 1 for i in range(len(stock_list)) if stock_list[i]}  
        print(f"📌 stock_map에 저장된 종목 개수: {len(stock_map)}")

        # ✅ 배치 업데이트 준비
        for i in range(0, len(data), batch_size):
            batch_data = data[i : i + batch_size]
            update_data = []

            for item in batch_data:
                stock_code = item.get("stock_code", "UNKNOWN")
                formatted_code = clean_stock_code(stock_code)  # ✅ API 요청 후 변환된 코드 사용

                # ✅ stock_code가 stock_map에 존재하는지 디버깅 추가
                if formatted_code not in stock_map:
                    print(f"⚠️ 종목 코드 불일치: {formatted_code} (stock_map에서 찾을 수 없음)")  
                    continue  # 찾을 수 없는 경우 업데이트 제외

                row = stock_map[formatted_code]  # ✅ A열에서 찾은 해당 종목의 행 번호
                print(f"📌 업데이트 준비: 종목 {formatted_code} (행 {row})")  

                update_data.append({"range": f"'{self.sheet_tab}'!L{row}", "values": [[item["product_name"]]]})  
                update_data.append({"range": f"'{self.sheet_tab}'!M{row}", "values": [[item["market_cap"]]]})  
                update_data.append({"range": f"'{self.sheet_tab}'!N{row}", "values": [[item["price"]]]})  

            # ✅ 값이 있으면 업데이트 실행
            if update_data:
                print(f"📝 API 요청 개수: {len(update_data)}")
                for attempt in range(3):  
                    try:
                        body = {
                            "valueInputOption": "RAW",
                            "data": update_data
                        }
                        response = sheet.values().batchUpdate(spreadsheetId=self.spreadsheet_id, body=body).execute()
                        print(f"✅ batchUpdate 성공! 응답 데이터: {response}")  
                        break

                    except HttpError as e:
                        print(f"🚨 Google Sheets API 오류 발생 (재시도 {attempt+1}/3): {e}")
                        time.sleep(5)
                        if attempt == 2:
                            print("❌ 3회 시도 후 실패. 업데이트 중단.")
            else:
                print("⚠️ 업데이트할 데이터가 없습니다. stock_map을 확인하세요.")



