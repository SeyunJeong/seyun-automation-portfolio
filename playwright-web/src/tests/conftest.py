# conftest.py
import os
import time
import pytest
from playwright.sync_api import sync_playwright
from src.utils.token_manager import refresh_google_token
from config.config import get_url, get_timeout, ENVIRONMENT

# 환경별 리프레시 토큰 설정 (포트폴리오용 - 실제 사용 시 환경변수로 설정하세요)
REFRESH_TOKENS = {
    "live": "YOUR-GOOGLE-REFRESH-TOKEN-LIVE",
    "staging": "YOUR-GOOGLE-REFRESH-TOKEN-STAGING"
}

@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    """모든 테스트 실행 전에 환경 변수 설정"""
    os.environ["DISPLAY"] = ":99"
    os.environ["XDG_RUNTIME_DIR"] = "/tmp/runtime-root"
    print(f"환경 변수가 설정되었습니다. 현재 환경: {ENVIRONMENT}")

@pytest.fixture(scope="function")
def browser():
    with sync_playwright() as p:
        # 브라우저 시작
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        # 현재 환경에 맞는 토큰 선택
        current_refresh_token = REFRESH_TOKENS.get(ENVIRONMENT)
        
        # 토큰 설정
        try:
            page = context.new_page()
            page.goto(get_url())
            time.sleep(2)  # 페이지 로드 대기

            print(f"현재 환경: {ENVIRONMENT}")
            print(f"REFRESH_TOKEN: {current_refresh_token}")

            access_token = refresh_google_token(current_refresh_token).get('access_token')
            print(f"구글 토큰 획득 완료: {access_token}")
            
            # 토큰 설정
            page.evaluate("""(token) => {
                localStorage.setItem('google', '"' + token + '"');
            }""", access_token)
            
            time.sleep(1)  # 설정 대기
            page.reload()
            time.sleep(2)  # 새로고침 후 대기
            
            page.close()
        except Exception as e:
            print(f"⚠️ 토큰 설정 중 오류: {str(e)}")
        
        yield context
        context.close()
        browser.close()
