"""
모든 페이지에 공통적으로 적용되는 기본 페이지 클래스
"""
import time
from playwright.sync_api import Page, expect
from config.config import get_timeout, get_long_timeout, get_download_timeout


class BasePage:
    """모든 페이지의 기본이 되는 클래스"""
    
    def __init__(self, page: Page):
        """페이지 객체 초기화"""
        self.page = page
        self.timeout = get_timeout()
        self.long_timeout = get_long_timeout()
        self.download_timeout = get_download_timeout()
        
    def wait_for_loading(self, timeout=None):
        """페이지 로딩 대기"""
        if timeout is None:
            timeout = self.timeout
        
        # 로딩 인디케이터가 사라질 때까지 대기
        try:
            # 페이지에 있는 로딩 인디케이터 선택자 조정 필요
            loading_locator = self.page.locator('.loading-indicator')
            if loading_locator.count() > 0:
                self.page.wait_for_selector('.loading-indicator', state='hidden', timeout=timeout)
        except:
            # 로딩 인디케이터가 없거나 이미 숨겨져 있을 수 있음
            pass
        
        return self
    
    def wait_for_page_load(self, timeout=10000):
        """안정적인 페이지 로딩 대기"""
        try:
            # DOM이 로드될 때까지 대기
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
            
            # body 요소가 나타날 때까지 대기
            self.page.wait_for_selector("body", timeout=timeout)
            
            # 추가 안정화를 위한 짧은 대기
            self.page.wait_for_timeout(1000)
            
        except Exception as e:
            # 실패해도 계속 진행
            pass
        
        return self
    
    def click_element(self, selector, nth=0):
        """nth 요소 클릭"""
        self.page.locator(selector).nth(nth).click(timeout=self.timeout)
        return self

    def click_long_element(self, selector):
        """로딩이 긴 요소 클릭"""
        self.page.locator(selector).click(timeout=self.long_timeout)
        return self
    
    def click_text(self, text, nth=0):
        """
        주어진 텍스트를 포함하는 n번째 요소를 찾아 클릭합니다.
        텍스트가 정확히 일치하지 않고 일부만 포함해도 동작합니다.
        """
        self.page.get_by_text(text).nth(nth).click(timeout=self.timeout)
        return self
    
    def fill_input(self, selector, value):
        """입력 필드 채우기"""
        self.page.locator(selector).fill(value)
        return self
    
    def get_text(self, selector):
        """요소의 텍스트 반환"""
        return self.page.locator(selector).text_content()
    
    def is_visible(self, selector):
        """요소가 보이는지 확인"""
        return self.page.locator(selector).is_visible(timeout=self.timeout)
    
    def wait_for_selector(self, selector, state='visible'):
        """selector 요소가 특정 상태가 될 때까지 대기"""
        self.page.wait_for_selector(selector, state=state, timeout=self.timeout)
        return self
    
    def take_screenshot(self, name='screenshot'):
        """스크린샷 촬영"""
        self.page.screenshot(path=f"./screenshots/{name}_{int(time.time())}.png")
        return self 