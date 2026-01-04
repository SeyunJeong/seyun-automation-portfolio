"""
주식 투자 페이지를 나타내는 페이지 객체 모델(POM) 클래스
"""
import time
from playwright.sync_api import Page, expect
from config.config import get_url, get_long_timeout, get_stock_account, get_stock_strategy
from src.pages.base_page import BasePage
from src.utils.test_utils import TEST_DATA


class StockInvestmentPage(BasePage):
    """주식 투자 페이지와 관련된 기능을 제공하는 클래스"""
    
    def __init__(self, page: Page):
        """페이지 객체 초기화"""
        super().__init__(page)
        
    def navigate_to_home(self):
        """홈페이지로 이동"""
        self.page.goto(get_url())
        time.sleep(1)
        return self
        
    def go_to_prime_strategy(self):
        """주식 프라임 전략 페이지로 이동"""
        self.click_element('text="주식 프라임 전략 더보기"')
        time.sleep(1)
        return self
        
    def select_strategy(self, strategy_type="all_weather"):
        """전략 선택"""
        strategy_name = get_stock_strategy(strategy_type)
        self.page.locator(f'text="{strategy_name}"').first.click(timeout=get_long_timeout())
        return self
        
    def click_invest_button(self):
        """투자 버튼 클릭"""
        self.click_element('[data-testid="invest-button"]')
        return self
        
    def select_account(self):
        """계좌 선택"""
        self.click_element('[data-testid="account-select-button"]')
        time.sleep(1)
        return self
        
    def set_start_date(self, date=None):
        """시작 날짜 설정"""
        if date is None:
            date = TEST_DATA["future_date"]
        self.fill_input('[data-testid="start-date-input"]', date)
        time.sleep(1)
        return self
        
    def click_next_button(self):
        """다음 버튼 클릭"""
        self.click_element('[data-testid="next-button"]')
        return self
        
    def check_all_agreements(self):
        """모든 동의사항 체크"""
        for i in range(3):
            self.page.locator('[data-testid="agreement-checkbox"]').nth(i).click(timeout=self.timeout)
        return self
        
    def complete_prime_investment(self):
        """프라임 투자 완료"""
        self.click_element('text="투자 예약 완료"')
        time.sleep(1)
        self.click_element('text="위 내용을 전부 숙지하였고, 이에 동의합니다."')
        time.sleep(1)
        self.click_element('text="네, 동의합니다."')
        time.sleep(1)
        self.click_element('text="네, 동의합니다."')
        self.click_element('text="네"')
        self.click_element('text="확인"')
        return self
        
    def go_to_my_stock_account(self):
        """내 주식 계좌로 이동"""
        self.click_element('text="내 주식 계좌"')
        self.page.locator(f'text="{get_stock_account()}"').first.click(timeout=self.timeout)
        return self
        
    def change_strategy(self):
        """전략 변경"""
        self.click_element('text="전략 교체"')
        return self
        
    def complete_strategy_change(self):
        """전략 변경 완료"""
        self.click_element('text="투자 예약 수정 완료"')
        self.click_element('text="네"')
        self.click_element('text="확인"')
        return self
        
    def cancel_investment(self):
        """투자 취소"""
        self.click_element('text="취소하기"')
        self.click_element('text="네"')
        self.click_element('text="확인"')
        return self
        
    def verify_scheduled_rebalancing(self):
        """예약된 리밸런싱 확인"""
        locator = self.page.locator("h3").filter(has_text="예약된 리밸런싱 날짜는").nth(0)
        locator.wait_for(timeout=self.timeout)
        text_content = locator.inner_text()
        assert "예약된 리밸런싱 날짜는" in text_content, f"기대한 텍스트가 없음. 현재 텍스트: {text_content}"
        return self
        
    def verify_investment_cancelled(self):
        """투자 취소 확인"""
        self.page.reload()
        expect(self.page.locator('text="투자 전"')).to_be_visible(timeout=self.timeout)
        return self 