"""
POM 패턴을 적용한 로그인 상태 확인 관련 테스트
"""
import pytest
from src.utils.slack_notifier import send_slack_message
from config.config import ENVIRONMENT, get_url, get_test_nickname
from src.pages.home_page import HomePage


def test_check_login_status(browser):
    try:
        page = browser.new_page()
        login_page = HomePage(page)
        
        # 페이지 열기
        login_page.navigate()
    
        
        # 로그인 상태 확인
        if login_page.is_logged_in():
            print("✅ 로그인 상태 유지됨")
            send_slack_message(f"[{ENVIRONMENT}] test_check_login_status_POM: 로그인 상태 유지됨 ✅")
        else:
            send_slack_message(f"[{ENVIRONMENT}] test_check_login_status_POM: 로그인 세션이 유지되지 않음 ❌")
            raise Exception("❌ 로그인 세션이 유지되지 않음!")
    except Exception as e:
        error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)
        send_slack_message(f"[{ENVIRONMENT}] test_check_login_status_POM: 테스트 실패 ❌ - {error_msg}")
        raise 


