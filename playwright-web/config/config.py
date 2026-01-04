"""
테스트 환경 설정 관리를 위한 config 파일
환경에 따라 URL, 계정, 계좌 정보 등을 쉽게 변경할 수 있습니다.
pydantic-settings를 사용하여 환경변수에서 설정을 로드합니다.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from functools import lru_cache
import os
from dotenv import load_dotenv


class CommonSettings(BaseSettings):
    """공통 설정 (모든 환경에서 동일) - .env 파일에서 읽음"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # 공통 설정
    timeout: int
    long_timeout: int
    download_timeout: int
    download_dir: str


class LiveSettings(BaseSettings):
    """Live 환경 설정 - .env.live 파일에서 읽음"""
    model_config = SettingsConfigDict(
        env_file=".env.live",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    base_url: str
    test_nickname: str
    stock_account: str
    coin_account: str
    stock_strategy_all_weather: str
    stock_strategy_long_short: str
    coin_strategy_all_weather: str


class StagingSettings(BaseSettings):
    """Staging 환경 설정 - .env.stg 파일에서 읽음"""
    model_config = SettingsConfigDict(
        env_file=".env.stg",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    base_url: str
    test_nickname: str
    stock_account: str
    coin_account: str
    stock_strategy_all_weather: str
    stock_strategy_long_short: str
    coin_strategy_all_weather: str


@lru_cache()
def get_common_settings() -> CommonSettings:
    """공통 설정 싱글톤 - .env 파일에서 읽음"""
    return CommonSettings()


@lru_cache()
def get_env_settings():
    """환경별 설정 싱글톤 (ENVIRONMENT에 따라 분기)"""
    # 환경변수에서 ENVIRONMENT 확인 (없으면 live)
    env = os.getenv("ENVIRONMENT", "live")
    
    if env == "live":
        return LiveSettings()
    else:
        return StagingSettings()


def get_config():
    """현재 환경 설정 반환 (공통 + 환경별 설정 병합) - 하위 호환성 유지"""
    common = get_common_settings()
    env = get_env_settings()
    
    return {
        # 공통 설정
        "timeout": common.timeout,
        "long_timeout": common.long_timeout,
        "download_timeout": common.download_timeout,
        "download_dir": common.download_dir,
        # 환경별 설정
        "base_url": env.base_url,
        "nickname": {
            "test_nickname": env.test_nickname,
        },
        "stock_accounts": {
            "test_account": env.stock_account,
        },
        "coin_accounts": {
            "test_account": env.coin_account,
        },
        "stock_strategies": {
            "all_weather": env.stock_strategy_all_weather,
            "long_short": env.stock_strategy_long_short,
        },
        "coin_strategies": {
            "all_weather": env.coin_strategy_all_weather,
        }
    }


# ============================================
# 하위 호환성을 위한 함수 인터페이스 (기존 코드와 100% 호환)
# ============================================

def get_url():
    """현재 환경의 기본 URL을 반환합니다."""
    return get_config()["base_url"]


def get_test_nickname():
    """현재 환경의 테스트 계정명을 반환합니다."""
    return get_config()["nickname"]["test_nickname"]


def get_stock_account():
    """현재 환경의 테스트 주식 계좌명을 반환합니다."""
    return get_config()["stock_accounts"]["test_account"]


def get_coin_account():
    """현재 환경의 테스트 코인 계좌명을 반환합니다."""
    return get_config()["coin_accounts"]["test_account"]


def get_timeout():
    """기본 타임아웃 값을 반환합니다."""
    return get_config()["timeout"]


def get_long_timeout():
    """긴 작업용 타임아웃 값을 반환합니다."""
    return get_config()["long_timeout"]


def get_download_timeout():
    """다운로드 타임아웃 값을 반환합니다."""
    return get_config()["download_timeout"]


def get_stock_strategy(strategy_key):
    """현재 환경의 주식 전략 이름을 반환합니다."""
    return get_config()["stock_strategies"][strategy_key]


def get_coin_strategy(strategy_key):
    """현재 환경의 코인 전략 이름을 반환합니다."""
    return get_config()["coin_strategies"][strategy_key]


def get_download_dir():
    """다운로드 디렉토리 경로를 반환합니다."""
    return get_config()["download_dir"]


# ============================================
# 하위 호환성을 위한 상수 (기존 코드와 100% 호환)
# ============================================

# ENVIRONMENT 상수는 환경변수에서 직접 읽음
ENVIRONMENT = os.getenv("ENVIRONMENT", "live")
