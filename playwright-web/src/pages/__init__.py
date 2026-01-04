"""
페이지 객체 모델(POM) 모듈
"""
from src.pages.base_page import BasePage
from src.pages.home_page import HomePage
from src.pages.stock_investment_page import StockInvestmentPage
from src.pages.coin_trend_strategy_page import CoinTrendStrategyPage
from src.pages.stock_factor_strategy_page import StockFactorStrategyPage

__all__ = [
    'BasePage',
    'HomePage',
    'StockInvestmentPage',
    'CoinTrendStrategyPage',
    'StockFactorStrategyPage'
] 