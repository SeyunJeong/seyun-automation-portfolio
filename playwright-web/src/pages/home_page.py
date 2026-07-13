"""
홈 페이지를 나타내는 페이지 객체 모델(POM) 클래스
"""
import time
from playwright.sync_api import Page
from config.config import get_test_nickname, get_url
from src.pages.base_page import BasePage


class HomePage(BasePage):
    """홈 페이지와 관련된 기능을 제공하는 클래스"""
    
    def __init__(self, page: Page):
        """페이지 객체 초기화"""
        super().__init__(page)
        self.url = get_url()
        self.nickname = get_test_nickname()
        
    def navigate(self):
        """로그인 페이지로 이동"""
        self.page.goto(self.url)
        time.sleep(2)  # 페이지 로드 대기
        return self
        
    def is_logged_in(self) -> bool:
        nickname_count = self.page.get_by_text("TestAdminAccount").count()
        print(f"'{nickname_count}'개의 닉네임 요소를 찾았습니다.")
        return nickname_count > 0
    
    
    def set_token(self, token: str):
        """로컬 스토리지에 토큰 설정"""
        self.page.evaluate("""(token) => {
            localStorage.setItem('google', '"' + token + '"');
        }""", token)
        time.sleep(10)  # 설정 대기
        self.page.reload()
        time.sleep(2)  # 새로고침 후 대기
        return self 