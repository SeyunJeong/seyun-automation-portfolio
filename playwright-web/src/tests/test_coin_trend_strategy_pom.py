"""
코인 트렌드 전략 테스트 (전략 예시, 백테스트 실행 등) - POM 패턴 적용
"""
import os
import pytest
from src.utils.slack_notifier import send_slack_message
from config.config import ENVIRONMENT
from src.pages.coin_trend_strategy_page import CoinTrendStrategyPage


class TestCoinTrendStrategyPOM:
    def test_코인투자_전략예시_백테스트(self, browser):
        try:
            page = browser.new_page()
            coin_page = CoinTrendStrategyPage(page)
            
            # POM 패턴을 사용한 메소드 체이닝
            save_path = (coin_page
                .navigate_to_home()
                .go_to_coin_strategy()
                .click_strategy_example()
                .apply_strategy()
                .run_backtest()
                .download_backtest_result())
                
            # 파일 내용 검증
            coin_page.check_html_content(save_path)
            
            print("테스트 통과 ✅: 정상적으로 실행됨.")
            send_slack_message(f"[{ENVIRONMENT}] test_코인투자_전략예시_백테스트: 테스트 통과 ✅")
        except Exception as e:
            # 간단한 오류 메시지만 슬랙으로 전송
            error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)
            send_slack_message(f"[{ENVIRONMENT}] test_코인투자_전략예시_백테스트: 테스트 실패 ❌ - {error_msg}")
            raise

    def test_코인투자_추세전략_백테스트(self, browser):
        try:
            page = browser.new_page()
            coin_page = CoinTrendStrategyPage(page)
            
            # POM 패턴을 사용한 메소드 체이닝   
            save_path = (coin_page
                .navigate_to_home()
                .go_to_coin_strategy()
                .add_parameters()
                .run_backtest()
                .download_backtest_result())
                
            # 파일 내용 검증
            coin_page.check_html_content(save_path)
            
            print("테스트 통과 ✅: 정상적으로 실행됨.")
            send_slack_message(f"[{ENVIRONMENT}] test_코인투자_추세전략_백테스트: 테스트 통과 ✅")
        except Exception as e:
            # 간단한 오류 메시지만 슬랙으로 전송
            error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)
            send_slack_message(f"[{ENVIRONMENT}] test_코인투자_추세전략_백테스트: 테스트 실패 ❌ - {error_msg}")
            raise

 