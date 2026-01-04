"""
코인 트렌드 전략 페이지를 나타내는 페이지 객체 모델(POM) 클래스
"""
import os
import time
import logging
import re
from datetime import datetime
from playwright.sync_api import Page, expect
from config.config import get_url, get_timeout, get_long_timeout, get_download_dir
from src.pages.base_page import BasePage
from src.utils.test_utils import TEST_DATA

logger = logging.getLogger(__name__)

class CoinTrendStrategyPage(BasePage):
    """코인 트렌드 전략 페이지와 관련된 기능을 제공하는 클래스"""
    
    def __init__(self, page: Page):
        """페이지 객체 초기화"""
        super().__init__(page)
        self.download_dir = os.path.join(os.getcwd(), "downloads")
        
        # 다운로드 디렉토리가 없으면 생성
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        
    def navigate_to_home(self):
        """홈페이지로 이동"""
        logger.info("홈페이지로 이동")
        self.page.goto(get_url())
        self.page.wait_for_load_state("load")
        return self
        
        
    def go_to_coin_strategy(self):
        """코인 파운드리"""
        logger.info("홈에서 코인 파운드리 페이지로 이동")
        self.click_text("코인 파운드리") 
        return self
        
    def click_strategy_example(self):
        """전략 예시 클릭"""
        logger.info("전략 예시 클릭")
        self.page.locator('text="전략 예시"').click(timeout=self.timeout, force=True)
        self.page.wait_for_timeout(1000)
        return self
        
    def apply_strategy(self):
        """전략 적용"""
        logger.info("전략 적용")
        self.page.locator('text="전략적용"').first.click(timeout=self.timeout)
        self.page.locator('text="확인"').first.click(timeout=self.timeout)
        self.page.locator('text="확인"').first.click(timeout=self.timeout)
        return self
        
    def run_backtest(self):
        """백테스트 실행"""
        logger.info("백테스트 실행")
        
        # 여러 방법으로 클릭 시도
        button_locator = self.page.locator('[data-testid="coin-backtest-button"]').first
        
        try:
            # 방법 1: force 클릭으로 요소 가림 무시
            button_locator.click(force=True, timeout=self.download_timeout)
        except Exception as e:
            logger.warning(f"force 클릭 실패: {e}")
            try:
                # 방법 2: JavaScript로 직접 클릭
                button_locator.evaluate("element => element.click()")
            except Exception as e2:
                logger.warning(f"JavaScript 클릭 실패: {e2}")
                # 방법 3: 마우스 이벤트로 클릭
                button_locator.hover()
                button_locator.click(force=True)
        
        return self
        
    def download_backtest_result(self):
        """백테스트 결과 다운로드"""
        logger.info("백테스트 결과 다운로드")
        # 파일 다운로드 대기 및 저장
        with self.page.expect_download(timeout=self.download_timeout) as download_info:
            # 백테스트 버튼 클릭 (force=True로 요소 가림 무시)
            button_locator = self.page.locator('[data-testid="coin-backtest-button"]').first
            
            try:
                button_locator.click(force=True, timeout=self.download_timeout)
            except Exception as e:
                logger.warning(f"일반 클릭 실패, JavaScript로 시도: {e}")
                button_locator.evaluate("element => element.click()")
            
            # 다운로드 완료 대기
            download = download_info.value
            
            # 다운로드 디렉토리 생성
            download_dir = os.path.abspath(get_download_dir())
            os.makedirs(download_dir, exist_ok=True)
            
            # 파일 저장
            save_path = os.path.join(download_dir, "backtest_result.html")
            download.save_as(save_path)
            
            print(f"파일 다운로드 완료: {save_path}")
            
        return save_path
        
    def add_parameters(self):
        """트렌드 파라미터 추가"""
        logger.info("트렌드 파라미터 추가")
        self.page.locator("text='조건 추가'").first.click(timeout=self.timeout)
        
        inputs = self.page.locator('input')
        
        inputs.nth(1).fill(TEST_DATA["trend_params"][0])
        inputs.nth(2).fill(TEST_DATA["trend_params"][1])
        inputs.nth(3).fill(TEST_DATA["trend_params"][2])
        inputs.nth(4).fill(TEST_DATA["trend_params"][3])
        
        return self
        
        
    def check_html_content(self, file_path):
        """HTML 파일에 nan 또는 inf 값이 포함되었는지 검사합니다."""
        logger.info(f"백테스트 결과 파일 검증: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if re.search(r'\b(nan|inf)\b', content, re.IGNORECASE):
            raise Exception("백테스트 결과에 nan 또는 inf 값이 포함됨.")
            
        return self 