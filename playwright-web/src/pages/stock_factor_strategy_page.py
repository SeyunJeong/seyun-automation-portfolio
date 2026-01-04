"""
스톡 팩터 전략 페이지 객체 모듈
POM(Page Object Model) 패턴 구현
"""
import time
import logging
import os
import re
from datetime import datetime
from playwright.sync_api import Page, expect
from config.config import get_url, get_timeout, get_long_timeout, get_download_dir
from src.pages.base_page import BasePage
from src.utils.test_utils import TEST_DATA, clean_download_directory, check_csv_content, check_html_content

logger = logging.getLogger(__name__)

class StockFactorStrategyPage(BasePage):
    """스톡 팩터 전략 페이지 객체 클래스"""
    
    def __init__(self, page: Page):
        """
        페이지 객체 초기화
        
        Args:
            page: Playwright 페이지 객체
        """
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
    
    def click_reset_button(self, button_text):
        """지정된 텍스트의 버튼 클릭"""
        logger.info(f"{button_text} 버튼 클릭")
        self.page.locator(f"text='{button_text}'").click(timeout=self.timeout, force=True)
        return self
    
    def go_to_stock_strategy(self):
        """주식 파운드리"""
        logger.info("홈에서 주식 파운드리 페이지로 이동")
        self.click_text("주식 파운드리") 
        return self
    
    def go_to_stock_asset_allocation(self):
        """주식 자산배분"""
        logger.info("주식 자산배분 페이지로 이동")
        self.click_text("주식 파운드리") 
        self.click_text("자산배분") 
        time.sleep(2)
        return self
    
    def reset_settings(self):
        """설정 초기화"""
        logger.info("설정 초기화")
        self.page.locator('text="설정 값 초기화"').click(timeout=self.timeout, force=True)
        time.sleep(2)
        return self
    
    def select_universe(self, universe_name):
        """
        유니버스 선택
        
        Args:
            universe_name: 선택할 유니버스 이름 (예: "한국", "미국")
        """
        logger.info(f"유니버스 선택: {universe_name}")
        self.page.locator('[data-testid="universe-select-button"]').click(timeout=self.timeout)
        self.page.locator(f'text="{universe_name}"').first.click(timeout=self.timeout)
        self.page.locator('[data-testid="next-button"]').click()
        time.sleep(1)
        return self
    
    def select_factor(self, *factors):
        """
        팩터 선택
        
        Args:
            *factors: 선택할 팩터 목록 (예: "PER", "시가총액")
        """
        logger.info(f"팩터 선택: {', '.join(factors)}")
        
        for factor in factors:
            self.page.locator(f'text="{factor}"').click(timeout=self.timeout)
        
        self.page.locator('[data-testid="next-button"]').click()
        return self
    

    def select_saved_asset_allocation_strategy(self, strategy_name):
        """저장된 자산배분 전략 선택"""

        logger.info("저장된 자산배분 전략 선택")
        self.page.locator('text="저장된 전략"').click(timeout=self.timeout, force=True)
        time.sleep(2)
        self.page.locator(f'text="{strategy_name}"').click(timeout=self.timeout, force=True)
        return self
    

    def select_saved_asset_allocation_algorithm(self, algorithm_name):
        """동적자산배분 알고리즘 선택"""
        logger.info("동적자산배분 알고리즘 선택")
        self.page.locator('[data-testid="select-trigger"]').first.click(timeout=self.timeout, force=True)
        time.sleep(2)
        self.page.locator(f'text="{algorithm_name}"').click(timeout=self.timeout, force=True)
        return self



        logger.info("동적자산배분 알고리즘 선택")
        self.page.locator('[data-testid="select-trigger"]').click(timeout=self.timeout, force=True)
        self.page.locator(f'text="{strategy_name}"').click(timeout=self.timeout, force=True)
        return self
    


    def set_investment_amount(self, amount):
        """
        투자 금액 설정
        
        Args:
            amount: 투자 금액 (원)
        """
        logger.info(f"투자 금액 설정: {amount}원")
        self.page.locator('[id="initialInvestmentMoney"]').fill(amount)
        return self
    
    
    def select_rebalancing_period_for_asset_allocation (self,  period):
        """
        주기 리밸런싱을 선택해주세요.
        
        Args:
            period: 리밸런싱 주기 (예: "월별", "분기별")
        """
        logger.info("자산배분 주기 리밸런싱을 선택")
        self.page.locator('text="주기 리밸런싱을 선택해주세요."').click(timeout=self.timeout, force=True)
        self.page.locator(f'text="{period}"').first.click(timeout=self.timeout)
        return self
    
    
    def set_rebalancing_period(self, period):
        """
        리밸런싱 주기 설정
        
        Args:
            period: 리밸런싱 주기 (예: "월별", "분기별")
        """
        logger.info(f"리밸런싱 주기 설정: {period}")
        self.page.locator('[data-testid="rebalancing-period-button"]').click()
        self.page.locator(f'text="{period}"').first.click(timeout=self.timeout)
        return self
    
    def set_stock_count(self, count):
        """
        종목 수 설정
        
        Args:
            count: 선택할 종목 수
        """
        logger.info(f"종목 수 설정: {count}")
        self.page.locator('[id="numbOfStock"]').fill(count)
        return self
    
    def select_backtest_tab(self):
        """
        백테스트 탭 선택
        
        Args:
            tab_name: 선택할 탭 이름 (예: "백테스트", "포트 추출", "10분위 테스트", "과거 거래내역 보기")
        """
        logger.info('[data-testid="backtest-tab"]')
        self.page.locator('[data-testid="backtest-tab"]').nth(0).click()
        time.sleep(1)
        return self
    
    
    def select_tab(self, tab_name):
        """
        탭 선택 (ID 값 기준)
        
        Args:
            tab_name: 선택할 탭의 ID 값 (예: "백테스트", "포트 추출", "10분위 테스트", "과거 거래내역 보기")
        """
        logger.info(f'{tab_name} 탭 선택')
        # 1. ID로 요소를 찾도록 locator 수정
        tab_locator = self.page.locator((f'[id="{tab_name}"]'))
        tab_locator.click()
        return self
    
    def run_backtest_top(self):
        """상단 백테스트 버튼 클릭"""
        logger.info("상단 백테스트 버튼 클릭")
        self.page.locator('[data-testid="stock-backtest-button-logged-in-top"]').first.click(timeout=self.long_timeout)
        return self
    
    def run_backtest_bottom(self):
        """하단 백테스트 버튼 클릭"""
        logger.info("하단 백테스트 버튼 클릭")
        self.page.locator('[data-testid="stock-backtest-button-logged-in-bottom"]').first.click(timeout=self.long_timeout)
        return self
    
    def download_backtest_result(self):
        """
        백테스트 결과 다운로드
        
        Returns:
            다운로드된 파일 경로
        """
        logger.info("백테스트 결과 다운로드")
        
        # 파일 다운로드 대기 및 저장
        with self.page.expect_download(timeout=self.long_timeout) as download_info:
            if self.page.locator('[data-testid="stock-backtest-button-logged-in-top"]').first.is_visible():
                self.page.locator('[data-testid="stock-backtest-button-logged-in-top"]').first.click(timeout=self.long_timeout)
            else:
                self.page.locator('[data-testid="stock-backtest-button-logged-in-bottom"]').first.click(timeout=self.long_timeout)
            
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
    
    def extract_portfolio_top(self):
        """상단 포트폴리오 추출 버튼 클릭"""
        logger.info("상단 포트폴리오 추출 버튼 클릭")
        self.page.locator('text="포트 추출"').first.click()
        self.page.locator('[data-testid="extract-portfolio-button-top"]').first.click()
        self.page.wait_for_selector('[data-testid="portfolio-row-id"]', timeout=self.long_timeout)
        return self
    
    
    def verify_portfolio_rows(self):
        """
        포트폴리오 행 검증
        
        Returns:
            포트폴리오 행 수
        """
        logger.info("포트폴리오 행 검증")
        # portfolio-row-id 요소들의 갯수를 확인
        portfolio_rows = self.page.locator('[data-testid="portfolio-row-id"]')
        count = portfolio_rows.count()
        return count
    
    def run_decile_test_top(self):
        """
        상단 10분위 테스트 실행
        
        Returns:
            다운로드된 파일 경로
        """
        logger.info("상단 10분위 테스트 실행")
        
        # 테스트 시작 전 downloads 폴더 정리
        download_dir = clean_download_directory()
        
        # 현재 시간을 파일명에 포함하여 유니크한 파일명 생성
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        expected_filename = f"decile_test_{timestamp}.csv"
        
        # CSV 다운로드 대기 및 확인
        with self.page.expect_download(timeout=self.long_timeout) as download_info:
            self.page.locator('text="검증"').nth(0).click(timeout=self.long_timeout)
            
            # 다운로드 완료 대기
            download = download_info.value
            
            # 다운로드된 파일명 확인
            actual_filename = download.suggested_filename
            print(f"다운로드된 파일명: {actual_filename}")
            
            # 다운로드 경로 설정
            save_path = os.path.join(download_dir, expected_filename)
            
            # 파일 저장
            download.save_as(save_path)
        
        return save_path
    
    def run_decile_test_bottom(self):
        """
        하단 10분위 테스트 실행
        
        Returns:
            다운로드된 파일 경로
        """
        logger.info("하단 10분위 테스트 실행")
        
        # 테스트 시작 전 downloads 폴더 정리
        download_dir = clean_download_directory()
        
        # 현재 시간을 파일명에 포함하여 유니크한 파일명 생성
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        expected_filename = f"decile_test_{timestamp}.csv"
        
        # CSV 다운로드 대기 및 확인
        with self.page.expect_download(timeout=self.long_timeout) as download_info:
            self.page.locator('text="검증"').nth(1).click(timeout=self.long_timeout)
            
            # 다운로드 완료 대기
            download = download_info.value
            
            # 다운로드된 파일명 확인
            actual_filename = download.suggested_filename
            print(f"다운로드된 파일명: {actual_filename}")
            
            # 다운로드 경로 설정
            save_path = os.path.join(download_dir, expected_filename)
            
            # 파일 저장
            download.save_as(save_path)
        
        return save_path
    
    def download_trade_history_top(self):
        """
        상단 과거 거래내역 다운로드
        
        Returns:
            다운로드된 파일 경로
        """
        logger.info("상단 과거 거래내역 다운로드")
        
        # 테스트 시작 전 downloads 폴더 정리
        download_dir = clean_download_directory()
        
        # 현재 시간을 파일명에 포함하여 유니크한 파일명 생성
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        expected_filename = f"trade_history_{timestamp}.csv"
        
        # 파일 다운로드 대기 및 확인
        with self.page.expect_download(timeout=self.long_timeout) as download_info:
            self.page.locator('text="과거 거래내역 보기"').nth(0).click(timeout=self.long_timeout)
            
            # 다운로드 완료 대기
            download = download_info.value
            
            # 다운로드된 파일명 확인
            actual_filename = download.suggested_filename
            print(f"다운로드된 파일명: {actual_filename}")
            
            # 다운로드 경로 설정
            save_path = os.path.join(download_dir, actual_filename)
            
            # 파일 저장
            download.save_as(save_path)
        
        return save_path
    
    def download_trade_history_bottom(self):
        """
        하단 과거 거래내역 다운로드
        
        Returns:
            다운로드된 파일 경로
        """
        logger.info("하단 과거 거래내역 다운로드")
        
        # 테스트 시작 전 downloads 폴더 정리
        download_dir = clean_download_directory()
        
        # 현재 시간을 파일명에 포함하여 유니크한 파일명 생성
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        expected_filename = f"trade_history_{timestamp}.csv"
        
        # 파일 다운로드 대기 및 확인
        with self.page.expect_download(timeout=self.long_timeout) as download_info:
            self.page.locator('text="과거 거래내역 보기"').nth(2).click(timeout=self.long_timeout)
            
            # 다운로드 완료 대기
            download = download_info.value
            
            # 다운로드된 파일명 확인
            actual_filename = download.suggested_filename
            print(f"다운로드된 파일명: {actual_filename}")
            
            # 다운로드 경로 설정
            save_path = os.path.join(download_dir, actual_filename)
            
            # 파일 저장
            download.save_as(save_path)
        
        return save_path
    
    def check_html_content(self, file_path):
        """HTML 파일에 nan 또는 inf 값이 포함되었는지 검사합니다."""
        logger.info(f"백테스트 결과 파일 검증: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if re.search(r'\b(nan|inf)\b', content, re.IGNORECASE):
            raise Exception("백테스트 결과에 nan 또는 inf 값이 포함됨.")
            
        return self
    
    def verify_decile_file(self, file_path):
        """
        10분위 테스트 결과 파일 검증
        
        Args:
            file_path: 검증할 파일 경로
        """
        logger.info(f"10분위 테스트 결과 파일 검증: {file_path}")
        
        # 파일명에 "decile", "quantile" 또는 "10분위" 포함 여부 확인
        filename = os.path.basename(file_path)
        assert any(keyword in filename.lower() for keyword in ["decile", "quantile", "10분위"]), \
            f"다운로드된 파일({filename})이 10분위 테스트 결과가 아닙니다"
        
        # CSV 파일 내용 확인
        check_csv_content(file_path, ["분위", "decile", "rank", "1st", "10st"])
        
        return self
    
    def verify_trade_history_file(self, file_path):
        """
        과거 거래내역 파일 검증
        
        Args:
            file_path: 검증할 파일 경로
        """
        logger.info(f"과거 거래내역 파일 검증: {file_path}")
        
        # 파일 확장자 확인 (.csv 또는 .xlsx)
        assert file_path.lower().endswith(('.csv', '.xlsx')), \
            f"다운로드된 파일({file_path})이 CSV 또는 Excel 형식이 아닙니다"
        
        # CSV 파일인 경우 내용 확인
        if file_path.lower().endswith('.csv'):
            check_csv_content(file_path, ["거래일자", "종목코드", "종목명", "시가총액", "매수수량", "매도수량"])
        
        return self 
    
    def timesleep(self, seconds):
        """
        지정된 시간 동안 대기
        
        Args:
            seconds: 대기할 시간 (초)
        """ 
        logger.info(f"지정된 시간 동안 대기: {seconds}초")
        time.sleep(seconds)
        return self
    


    def download_asset_allocation_backtest_result(self):
        """
        자산배분 백테스트 결과 다운로드

        Returns:
            다운로드된 파일 경로
        """
        logger.info("자산배분 백테스트 결과 다운로드")

        # 파일 다운로드 대기 및 저장
        with self.page.expect_download(timeout=self.download_timeout) as download_info:
            # "백테스트" 버튼이 보이면 클릭 (여러 위치에 있을 수 있으므로 첫 번째 사용)
            self.page.locator("text='백테스트'").first.click(timeout=self.download_timeout)

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
