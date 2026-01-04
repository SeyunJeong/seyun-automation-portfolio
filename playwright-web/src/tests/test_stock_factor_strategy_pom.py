"""
주식 전략 테스트 (백테스트, 포트 추출, 10분위 테스트, 과거 거래내역) - POM 패턴 적용
"""
import os
import pytest
from src.utils.slack_notifier import send_slack_message
from config.config import ENVIRONMENT
from src.pages.stock_factor_strategy_page import StockFactorStrategyPage
from src.utils.test_utils import TEST_DATA

DYNAMIC_ALLOCATION_ALGORITHMS_MAP = {
    #"DualMomentum": "듀얼모멘텀",
    "VAA": "VAA",
    "DAA": "DAA",
    "BAA_Aggressive": "BAA 공격형",
    "BAA_Moderate": "BAA 중도형",
    "LAA": "LAA",
    "HAA": "HAA",
    "ModifiedDualMomentum": "변형듀얼모멘텀",
    "AcceleratedDualMomentum": "가속듀얼모멘텀",
}

# parametrize에 전달할 영문 별칭 리스트
DYNAMIC_ALLOCATION_ALGORITHM_ALIASES = list(DYNAMIC_ALLOCATION_ALGORITHMS_MAP.keys())


class TestStockFactorStrategyPOM:
    def test_주식백테스트_한국(self, browser):
        try:
            page = browser.new_page()
            stock_page = StockFactorStrategyPage(page)
            
            # POM 패턴을 사용한 메소드 체이닝
            save_path = (stock_page
                .navigate_to_home()
                .go_to_stock_strategy()
                .reset_settings()
                .select_universe("한국")
                .select_factor("시가총액")
                .select_tab("백테스트")
                .set_investment_amount(TEST_DATA["investment_amount"])
                .set_rebalancing_period("월별")
                .run_backtest_top()
                .download_backtest_result())
                
            # 파일 내용 검증
            stock_page.check_html_content(save_path)
                
            print("테스트 통과 ✅: 정상적으로 실행됨.")
            send_slack_message(f"[{ENVIRONMENT}] test_주식백테스트_한국: 테스트 통과 ✅")
        except Exception as e:
            error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)
            send_slack_message(f"[{ENVIRONMENT}] test_주식백테스트_한국: 테스트 실패 ❌ - {error_msg}")
            raise

    def test_주식백테스트_미국(self, browser):
        try:
            page = browser.new_page()
            stock_page = StockFactorStrategyPage(page)
            
            # POM 패턴을 사용한 메소드 체이닝
            save_path = (stock_page
                .navigate_to_home()
                .go_to_stock_strategy()
                .reset_settings()
                .select_universe("미국")
                .select_factor("시가총액")
                .select_tab("백테스트")
                .set_investment_amount(TEST_DATA["investment_amount"])
                .set_rebalancing_period("월별")
                .run_backtest_top()
                .download_backtest_result())
                
            # 파일 내용 검증
            stock_page.check_html_content(save_path)
                
            print("테스트 통과 ✅: 정상적으로 실행됨.")
            send_slack_message(f"[{ENVIRONMENT}] test_주식백테스트_미국: 테스트 통과 ✅")
        except Exception as e:
            error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)
            send_slack_message(f"[{ENVIRONMENT}] test_주식백테스트_미국: 테스트 실패 ❌ - {error_msg}")
            raise

    def test_주식포트추출_한국(self, browser):
        try:
            n = TEST_DATA["stock_count_1"]
            page = browser.new_page()
            stock_page = StockFactorStrategyPage(page)
            
            # POM 패턴을 사용한 메소드 체이닝
            (stock_page
                .navigate_to_home()
                .go_to_stock_strategy()
                .reset_settings()
                .select_universe("한국")
                .select_factor("시가총액", "PER")
                .select_tab("포트 추출")
                .set_investment_amount(TEST_DATA["investment_amount"])
                .set_stock_count(n)
                .extract_portfolio_top())
                
            # 포트폴리오 행 검증
            count = stock_page.verify_portfolio_rows()
            assert count == int(n), f"Expected {n} portfolio rows, but got {count}"
                
            send_slack_message(f"[{ENVIRONMENT}] test_주식포트추출_한국: 테스트 통과 ✅")
        except Exception as e:
            error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)
            send_slack_message(f"[{ENVIRONMENT}] test_주식포트추출_한국: 테스트 실패 ❌ - {error_msg}")
            raise

    def test_주식포트추출_미국(self, browser):
        try:
            n = TEST_DATA["stock_count_2"]
            page = browser.new_page()
            stock_page = StockFactorStrategyPage(page)
            
            # POM 패턴을 사용한 메소드 체이닝
            (stock_page
                .navigate_to_home()
                .go_to_stock_strategy()
                .reset_settings()
                .select_universe("미국")
                .select_factor("시가총액", "PER")
                .select_tab("포트 추출")
                .set_investment_amount(TEST_DATA["investment_amount"])
                .set_stock_count(n)
                .extract_portfolio_top())
                
            # 포트폴리오 행 검증
            count = stock_page.verify_portfolio_rows()
            assert count == int(n), f"Expected {n} portfolio rows, but got {count}"
                
            send_slack_message(f"[{ENVIRONMENT}] test_주식포트추출_미국: 테스트 통과 ✅")
        except Exception as e:
            error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)
            send_slack_message(f"[{ENVIRONMENT}] test_주식포트추출_미국: 테스트 실패 ❌ - {error_msg}")
            raise

    def test_주식10분위테스트_한국(self, browser):
        try:
            page = browser.new_page()
            stock_page = StockFactorStrategyPage(page)
            
            # POM 패턴을 사용한 메소드 체이닝
            save_path = (stock_page
                .navigate_to_home()
                .go_to_stock_strategy()
                .reset_settings()
                .select_tab("10분위 테스트")
                .select_universe("한국")
                .select_factor("시가총액")
                .set_investment_amount(TEST_DATA["investment_amount"])
                .set_rebalancing_period("월별")
                .run_decile_test_top())
                
            # 파일 내용 검증
            stock_page.verify_decile_file(save_path)
                
            print(f"10분위 테스트 결과 파일 다운로드 완료: {save_path}")
            send_slack_message(f"[{ENVIRONMENT}] test_주식10분위테스트_한국: 테스트 통과 ✅")
        except Exception as e:
            error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)
            send_slack_message(f"[{ENVIRONMENT}] test_주식10분위테스트_한국: 테스트 실패 ❌ - {error_msg}")
            raise

    def test_주식10분위테스트_미국(self, browser):
        try:
            page = browser.new_page()
            stock_page = StockFactorStrategyPage(page)
            
            # POM 패턴을 사용한 메소드 체이닝
            save_path = (stock_page
                .navigate_to_home()
                .go_to_stock_strategy()
                .reset_settings()
                .select_universe("미국")
                .select_tab("10분위 테스트")
                .select_factor("시가총액")
                .set_investment_amount(TEST_DATA["investment_amount"])
                .set_rebalancing_period("월별")
                .run_decile_test_top())
                
            # 파일 내용 검증
            stock_page.verify_decile_file(save_path)
                
            print(f"10분위 테스트 결과 파일 다운로드 완료: {save_path}")
            send_slack_message(f"[{ENVIRONMENT}] test_주식10분위테스트_미국: 테스트 통과 ✅")
        except Exception as e:
            error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)
            send_slack_message(f"[{ENVIRONMENT}] test_주식10분위테스트_미국: 테스트 실패 ❌ - {error_msg}")
            raise

    def test_주식과거거래내역보기_한국(self, browser):
        try:
            page = browser.new_page()
            stock_page = StockFactorStrategyPage(page)
            
            # POM 패턴을 사용한 메소드 체이닝
            save_path = (stock_page
                .navigate_to_home()
                .go_to_stock_strategy()
                .reset_settings()
                .select_tab("과거 거래내역 보기")
                .select_universe("한국")
                .select_factor("시가총액")
                .set_investment_amount(TEST_DATA["investment_amount"])
                .set_rebalancing_period("월별")
                .download_trade_history_top())
                
            # 파일 내용 검증
            stock_page.verify_trade_history_file(save_path)
                
            print(f"과거 거래내역 파일 다운로드 완료: {save_path}")
            send_slack_message(f"[{ENVIRONMENT}] test_주식과거거래내역보기_한국: 테스트 통과 ✅")
        except Exception as e:
            error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)
            send_slack_message(f"[{ENVIRONMENT}] test_주식과거거래내역보기_한국: 테스트 실패 ❌ - {error_msg}")
            raise

    def test_주식과거거래내역보기_KOSPI(self, browser):
        try:
            page = browser.new_page()
            stock_page = StockFactorStrategyPage(page)
            
            # POM 패턴을 사용한 메소드 체이닝
            save_path = (stock_page
                .navigate_to_home()
                .go_to_stock_strategy()
                .reset_settings()
                .select_tab("과거 거래내역 보기")
                .select_universe("KOSPI")
                .select_factor("시가총액")
                .set_investment_amount(TEST_DATA["investment_amount"])
                .set_rebalancing_period("월별")
                .download_trade_history_top())
                
            # 파일 내용 검증
            stock_page.verify_trade_history_file(save_path)
                
            print(f"과거 거래내역 파일 다운로드 완료: {save_path}")
            send_slack_message(f"[{ENVIRONMENT}] test_주식과거거래내역보기_KOSPI: 테스트 통과 ✅")
        except Exception as e:
            error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)
            send_slack_message(f"[{ENVIRONMENT}] test_주식과거거래내역보기_KOSPI: 테스트 실패 ❌ - {error_msg}")
            raise 


    def test_정적자산배분_백테스트(self, browser):
        try:
            page = browser.new_page()
            stock_page = StockFactorStrategyPage(page)
            
            # POM 패턴을 사용한 메소드 체이닝
            save_path = (stock_page
                .navigate_to_home()
                .go_to_stock_asset_allocation()
                .reset_settings()
                .select_saved_asset_allocation_strategy("test")
                .download_asset_allocation_backtest_result())

            # 파일 내용 검증
            stock_page.check_html_content(save_path)
                
            print("테스트 통과 ✅: 정상적으로 실행됨.")
            send_slack_message(f"[{ENVIRONMENT}] test_정적자산배분_백테스트: 테스트 통과 ✅")
        except Exception as e:
            error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)
            send_slack_message(f"[{ENVIRONMENT}] test_정적자산배분_백테스트: 테스트 실패 ❌ - {error_msg}")
            raise



    @pytest.mark.parametrize("algorithm_alias", DYNAMIC_ALLOCATION_ALGORITHM_ALIASES)
    def test_동적자산배분_백테스트(self, browser, algorithm_alias):
        """
        주어진 동적 자산배분 알고리즘에 대해 백테스트를 수행하고 결과를 검증합니다.
        영문 별칭을 사용하여 Pytest 출력의 한글 깨짐을 방지합니다.
        """
        # 영문 별칭을 사용하여 실제 한글 알고리즘 이름을 가져옵니다.
        actual_algorithm_name = DYNAMIC_ALLOCATION_ALGORITHMS_MAP[algorithm_alias]

        try:
            page = browser.new_page()
            stock_page = StockFactorStrategyPage(page)
            
            print(f"테스트 시작: 동적 자산배분 알고리즘 - {actual_algorithm_name} (Alias: {algorithm_alias})")

            # POM 패턴을 사용한 메소드 체이닝
            # 실제 한글 알고리즘 이름을 select_saved_asset_allocation_algorithm 메서드에 전달합니다.
            save_path = (stock_page
                .navigate_to_home()
                .go_to_stock_asset_allocation()
                .reset_settings()
                .select_saved_asset_allocation_strategy("test")
                .select_saved_asset_allocation_algorithm(actual_algorithm_name)
                .download_asset_allocation_backtest_result())

            # 파일 내용 검증
            stock_page.check_html_content(save_path)
                
            print(f"테스트 통과 ✅: 동적 자산배분 알고리즘 - {actual_algorithm_name} 정상적으로 실행됨.")
            send_slack_message(f"[{ENVIRONMENT}] test_동적자산배분_백테스트 ({actual_algorithm_name}): 테스트 통과 ✅")
        except Exception as e:
            error_message = f"[{ENVIRONMENT}] test_동적자산배분_백테스트 ({actual_algorithm_name}): 테스트 실패 ❌ - {str(e)}"
            send_slack_message(error_message)
            print(error_message) # 콘솔에도 출력
            raise # pytest가 실패로 처리하도록 예외를 다시 발생시킵니다.






    # def test_정적자산배분_저장(self, browser):
    #     try:
    #         page = browser.new_page()
    #         stock_page = StockFactorStrategyPage(page)
            
    #         # POM 패턴을 사용한 메소드 체이닝
    #         save_path = (stock_page
    #             .navigate_to_home()
    #             .go_to_stock_asset_allocation()
    #             .reset_settings()
    #             .set_investment_amount(10000)
    #             .select_rebalancing_period_for_asset_allocation("월별")


    #         )
    #                     # 파일 내용 검증
    #         stock_page.check_html_content(save_path)
                
    #         print("테스트 통과 ✅: 정상적으로 실행됨.")
    #         send_slack_message(f"[{ENVIRONMENT}] test_주식백테스트_미국: 테스트 통과 ✅")
    #     except Exception as e:
    #         send_slack_message(f"[{ENVIRONMENT}] test_주식백테스트_미국: 테스트 실패 ❌ - {str(e)}")
    #         raise