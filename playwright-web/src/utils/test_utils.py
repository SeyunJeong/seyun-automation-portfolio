"""
테스트에 사용되는 공통 유틸리티 함수와 상수
"""
import os
import re
from config.config import get_download_dir, ENVIRONMENT

# 테스트 데이터
TEST_DATA = {
    "investment_amount": "10000",
    "stock_count_1": "80",
    "stock_count_2": "85",
    "future_date": "2025.12.31",
    "trend_params": ["1", "2", "3", "4"]
}

# 헬퍼 함수
def clean_download_directory():
    """다운로드 디렉토리를 정리합니다."""
    download_dir = os.path.abspath(get_download_dir())
    if os.path.exists(download_dir):
        for file in os.listdir(download_dir):
            file_path = os.path.join(download_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error cleaning download directory: {e}")
    return download_dir

def check_file_validity(file_path):
    """파일의 유효성을 검사합니다."""
    # 파일이 실제로 존재하는지 확인
    assert os.path.exists(file_path), f"다운로드된 파일이 없습니다: {file_path}"
    
    # 파일 크기가 0보다 큰지 확인
    assert os.path.getsize(file_path) > 0, "다운로드된 파일이 비어있습니다"

def check_csv_content(file_path, keywords):
    """CSV 파일 내용을 검사합니다."""
    if file_path.lower().endswith('.csv'):
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            # 키워드 포함 여부 확인
            assert any(keyword in first_line for keyword in keywords), \
                f"파일 내용이 기대한 형식이 아닙니다. 첫 줄: {first_line}"

def check_html_content(file_path):
    """HTML 파일에 nan 또는 inf 값이 포함되었는지 검사합니다."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if re.search(r'\b(nan|inf)\b', content, re.IGNORECASE):
        raise Exception("백테스트 결과에 nan 또는 inf 값이 포함됨.")
