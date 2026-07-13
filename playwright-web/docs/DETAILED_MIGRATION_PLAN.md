# 상세 마이그레이션 실행 계획

## 📋 개요

영향 범위 분석 보고서(`IMPACT_ANALYSIS.md`)를 기반으로 실제 코드 변경을 위한 단계별 상세 계획입니다.
**시나리오 2: 함수 인터페이스 유지** 방식을 채택하여 하위 호환성을 완벽히 보장합니다.

## 🎯 마이그레이션 전략

### 핵심 원칙
1. **하위 호환성 100% 보장**: 기존 함수 인터페이스 완전 유지
2. **단일 파일 수정**: `config/config.py`만 변경
3. **점진적 검증**: 각 단계별 검증 후 진행
4. **롤백 가능**: Git을 통한 안전한 롤백

### 변경 범위
- **수정 파일**: 1개 (`config/config.py`)
- **영향 파일**: 11개 (수정 불필요, 검증만 필요)
- **예상 작업 시간**: 1-2시간
- **위험도**: 🟢 매우 낮음

## 📝 단계별 상세 계획

### Phase 1: 사전 준비

#### 1.1 의존성 추가
**파일**: `requirements.txt`

**변경 전**:
```txt
pytest>=7.0.0
pytest-playwright>=0.3.0
playwright>=1.36.0
requests>=2.28.0
python-dotenv>=0.20.0
pyyaml>=6.0
slack-sdk>=3.18.0
python-dateutil>=2.8.2
pandas>=1.5.0
six>=1.16.0
```

**변경 후**:
```txt
pytest>=7.0.0
pytest-playwright>=0.3.0
playwright>=1.36.0
requests>=2.28.0
python-dotenv>=0.20.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
pyyaml>=6.0
slack-sdk>=3.18.0
python-dateutil>=2.8.2
pandas>=1.5.0
six>=1.16.0
```

**검증 방법**:
```bash
pip install -r requirements.txt
python -c "from pydantic_settings import BaseSettings; print('OK')"
```

**리스크**: 🟢 없음 (의존성 추가만)

---

#### 1.2 .env.example 파일 생성
**파일**: `.env.example` (새 파일)

**내용**:
```bash
# ============================================
# 환경 설정 (환경 분기용)
# ============================================
ENVIRONMENT=live  # live 또는 staging

# ============================================
# 공통 설정 (모든 환경에서 동일하게 사용)
# ============================================
TIMEOUT=30000
LONG_TIMEOUT=100000
DOWNLOAD_TIMEOUT=1200000
DOWNLOAD_DIR=downloads

# ============================================
# Live 환경 설정
# ============================================
LIVE_BASE_URL=https://service.example.com/ko
LIVE_TEST_NICKNAME=TestAdminAccount
LIVE_STOCK_ACCOUNT=자동화테스트주식계좌
LIVE_COIN_ACCOUNT=자동화테스트코인계좌
LIVE_STOCK_STRATEGY_ALL_WEATHER=Global All Weather Active Strategy
LIVE_STOCK_STRATEGY_LONG_SHORT=Index Long Short Active Strategy
LIVE_COIN_STRATEGY_ALL_WEATHER=크립토 올웨더 액티브 전략

# ============================================
# Staging 환경 설정
# ============================================
STAGING_BASE_URL=https://dev.example.com/ko
STAGING_TEST_NICKNAME=안녕하세요
STAGING_STOCK_ACCOUNT=qa자동화테스트주식계좌
STAGING_COIN_ACCOUNT=qa자동화테스트코인계좌
STAGING_STOCK_STRATEGY_ALL_WEATHER=Global All Weather Active Strategy
STAGING_STOCK_STRATEGY_LONG_SHORT=Index Long Short Active Strategy
STAGING_COIN_STRATEGY_ALL_WEATHER=크립토 올웨더 액티브 전략

# ============================================
# Google OAuth 설정
# ============================================
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REFRESH_TOKEN_LIVE=your_refresh_token_live_here
GOOGLE_REFRESH_TOKEN_STAGING=your_refresh_token_staging_here

# ============================================
# Slack 설정
# ============================================
SLACK_WEBHOOK_URL=your_slack_webhook_url_here

# ============================================
# 테스트 데이터 (공통 설정)
# ============================================
TEST_INVESTMENT_AMOUNT=10000
TEST_STOCK_COUNT_1=80
TEST_STOCK_COUNT_2=85
TEST_FUTURE_DATE=2025.12.31
TEST_TREND_PARAM_1=1
TEST_TREND_PARAM_2=2
TEST_TREND_PARAM_3=3
TEST_TREND_PARAM_4=4

# ============================================
# 브라우저 환경 (Docker/CI용, 공통)
# ============================================
DISPLAY=:99
XDG_RUNTIME_DIR=/tmp/runtime-root
```

**검증 방법**:
- 파일 생성 확인
- Git에 커밋 가능한지 확인 (실제 값 없음)

**리스크**: 🟢 없음 (새 파일 생성)

---

### Phase 2: 핵심 변경 - config/config.py

#### 2.1 변경 전 코드 구조 분석

**현재 구조**:
- 하드코딩된 딕셔너리: `COMMON`, `LIVE`, `STAGING`
- 하드코딩된 상수: `ENVIRONMENT = "live"`
- 함수 기반 인터페이스: 11개 함수

**사용되는 함수들** (48회 호출):
1. `get_url()` - 5회
2. `get_test_nickname()` - 2회
3. `get_stock_account()` - 1회
4. `get_coin_account()` - 0회 (미사용)
5. `get_timeout()` - 3회
6. `get_long_timeout()` - 5회
7. `get_download_timeout()` - 1회
8. `get_download_dir()` - 3회
9. `get_stock_strategy()` - 2회
10. `get_coin_strategy()` - 0회 (미사용)
11. `get_config()` - 0회 (내부 사용)

**사용되는 상수**:
- `ENVIRONMENT` - 26회

---

#### 2.2 변경 후 코드 구조

**새로운 구조**:
- pydantic-settings 클래스 기반
- 환경변수 자동 로드
- 함수 인터페이스 유지 (하위 호환성)

**변경 후 코드**:

```python
"""
테스트 환경 설정 관리를 위한 config 파일
환경에 따라 URL, 계정, 계좌 정보 등을 쉽게 변경할 수 있습니다.
pydantic-settings를 사용하여 환경변수에서 설정을 로드합니다.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from functools import lru_cache


class CommonSettings(BaseSettings):
    """공통 설정 (모든 환경에서 동일)"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # 공통 설정
    timeout: int = 30000
    long_timeout: int = 100000
    download_timeout: int = 1200000
    download_dir: str = "downloads"
    
    # 환경 설정
    environment: Literal["live", "staging"] = "live"


class LiveSettings(BaseSettings):
    """Live 환경 설정"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="LIVE_",
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
    """Staging 환경 설정"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="STAGING_",
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
    """공통 설정 싱글톤"""
    return CommonSettings()


@lru_cache()
def get_env_settings():
    """환경별 설정 싱글톤 (ENVIRONMENT에 따라 분기)"""
    common = get_common_settings()
    
    if common.environment == "live":
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

# ENVIRONMENT 상수는 get_common_settings()를 통해 동적으로 가져옴
# 하지만 기존 코드와의 호환성을 위해 모듈 레벨 변수로도 제공
# 주의: 모듈 로드 시점에 초기화되므로 환경변수 변경 시 재시작 필요
ENVIRONMENT = get_common_settings().environment
```

**주요 변경 사항**:
1. ✅ pydantic-settings 클래스 도입
2. ✅ 환경변수 자동 로드 (`.env` 파일)
3. ✅ `env_prefix`를 통한 환경별 변수 자동 매핑
4. ✅ 싱글톤 패턴 (`@lru_cache()`)
5. ✅ 기존 함수 인터페이스 100% 유지
6. ✅ `ENVIRONMENT` 상수 유지 (하위 호환성)

---

#### 2.3 검증 체크리스트

**기능 검증**:
- [ ] `get_url()` 반환값 검증
- [ ] `get_test_nickname()` 반환값 검증
- [ ] `get_stock_account()` 반환값 검증
- [ ] `get_coin_account()` 반환값 검증
- [ ] `get_timeout()` 반환값 검증
- [ ] `get_long_timeout()` 반환값 검증
- [ ] `get_download_timeout()` 반환값 검증
- [ ] `get_download_dir()` 반환값 검증
- [ ] `get_stock_strategy("all_weather")` 반환값 검증
- [ ] `get_stock_strategy("long_short")` 반환값 검증
- [ ] `get_coin_strategy("all_weather")` 반환값 검증
- [ ] `ENVIRONMENT` 상수 값 검증

**환경 분기 검증**:
- [ ] `ENVIRONMENT=live`일 때 Live 설정 로드 확인
- [ ] `ENVIRONMENT=staging`일 때 Staging 설정 로드 확인
- [ ] 환경변수 없을 때 기본값 동작 확인

**타입 검증**:
- [ ] 모든 함수 반환 타입 확인
- [ ] pydantic 검증 에러 처리 확인

---

### Phase 3: 영향 파일 검증

#### 3.1 검증 대상 파일 목록

**핵심 페이지 클래스** (5개):
1. `src/pages/base_page.py` - `get_timeout()`, `get_long_timeout()`, `get_download_timeout()`
2. `src/pages/home_page.py` - `get_url()`, `get_test_nickname()`
3. `src/pages/stock_factor_strategy_page.py` - `get_url()`, `get_timeout()`, `get_long_timeout()`, `get_download_dir()`
4. `src/pages/coin_trend_strategy_page.py` - `get_url()`, `get_timeout()`, `get_long_timeout()`, `get_download_dir()`
5. `src/pages/stock_investment_page.py` - `get_url()`, `get_long_timeout()`, `get_stock_account()`, `get_stock_strategy()`

**테스트 파일** (3개):
6. `src/tests/conftest.py` - `get_url()`, `get_timeout()`, `ENVIRONMENT`
7. `src/tests/test_home_pom.py` - `get_url()`, `get_test_nickname()`, `ENVIRONMENT`
8. `src/tests/test_stock_factor_strategy_pom.py` - `ENVIRONMENT` (12회)
9. `src/tests/test_coin_trend_strategy_pom.py` - `ENVIRONMENT` (4회)

**유틸리티 파일** (2개):
10. `src/utils/test_utils.py` - `get_download_dir()`, `ENVIRONMENT`
11. `src/utils/refresh_token_test.py` - `ENVIRONMENT` (3회)

---

#### 3.2 파일별 검증 방법

**검증 스크립트 예시**:

```python
# test_config_compatibility.py
"""config.py 변경 후 하위 호환성 검증 스크립트"""
import sys
from config.config import (
    get_url, get_test_nickname, get_stock_account, get_coin_account,
    get_timeout, get_long_timeout, get_download_timeout, get_download_dir,
    get_stock_strategy, get_coin_strategy, get_config, ENVIRONMENT
)

def test_all_functions():
    """모든 함수가 정상 동작하는지 검증"""
    print("=== 함수 반환값 검증 ===")
    
    # 기본 함수들
    assert isinstance(get_url(), str), "get_url() should return str"
    assert isinstance(get_test_nickname(), str), "get_test_nickname() should return str"
    assert isinstance(get_stock_account(), str), "get_stock_account() should return str"
    assert isinstance(get_coin_account(), str), "get_coin_account() should return str"
    assert isinstance(get_timeout(), int), "get_timeout() should return int"
    assert isinstance(get_long_timeout(), int), "get_long_timeout() should return int"
    assert isinstance(get_download_timeout(), int), "get_download_timeout() should return int"
    assert isinstance(get_download_dir(), str), "get_download_dir() should return str"
    
    # 전략 함수들
    assert isinstance(get_stock_strategy("all_weather"), str), "get_stock_strategy() should return str"
    assert isinstance(get_stock_strategy("long_short"), str), "get_stock_strategy() should return str"
    assert isinstance(get_coin_strategy("all_weather"), str), "get_coin_strategy() should return str"
    
    # ENVIRONMENT 상수
    assert ENVIRONMENT in ["live", "staging"], "ENVIRONMENT should be 'live' or 'staging'"
    
    # get_config() 반환값 구조 검증
    config = get_config()
    assert "base_url" in config, "get_config() should contain 'base_url'"
    assert "nickname" in config, "get_config() should contain 'nickname'"
    assert "stock_accounts" in config, "get_config() should contain 'stock_accounts'"
    
    print("✅ 모든 함수 검증 통과")


def test_import_compatibility():
    """모든 import 구문이 정상 동작하는지 검증"""
    print("=== Import 호환성 검증 ===")
    
    # 각 파일에서 사용하는 import 패턴 검증
    from config.config import get_url, get_test_nickname  # home_page.py
    from config.config import get_timeout, get_long_timeout, get_download_timeout  # base_page.py
    from config.config import get_url, get_timeout, get_long_timeout, get_download_dir  # stock_factor_strategy_page.py
    from config.config import ENVIRONMENT  # test files
    
    print("✅ 모든 import 검증 통과")


if __name__ == "__main__":
    try:
        test_all_functions()
        test_import_compatibility()
        print("\n🎉 모든 검증 통과!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 검증 실패: {e}")
        sys.exit(1)
```

---

#### 3.3 각 파일별 상세 검증

**파일 1: `src/pages/base_page.py`**
```python
# 변경 전
from config.config import get_timeout, get_long_timeout, get_download_timeout

# 변경 후 (동일)
from config.config import get_timeout, get_long_timeout, get_download_timeout
```
**검증**: ✅ 변경 불필요, import 구문 동일

**파일 2: `src/pages/home_page.py`**
```python
# 변경 전
from config.config import get_test_nickname, get_url

# 변경 후 (동일)
from config.config import get_test_nickname, get_url
```
**검증**: ✅ 변경 불필요, import 구문 동일

**파일 3-11**: 동일한 패턴으로 검증

---

### Phase 4: 통합 테스트

#### 4.1 단위 테스트 실행
```bash
# config 모듈 직접 테스트
python -c "from config.config import *; print('Import OK')"

# 각 함수 개별 테스트
python test_config_compatibility.py
```

#### 4.2 기존 테스트 실행
```bash
# 기존 테스트가 정상 동작하는지 확인
pytest src/tests/ -v

# 특정 테스트만 실행
pytest src/tests/test_home_pom.py -v
pytest src/tests/test_stock_factor_strategy_pom.py -v
```

#### 4.3 실제 사용 시나리오 테스트
```bash
# BasePage 인스턴스 생성 테스트
python -c "
from playwright.sync_api import sync_playwright
from src.pages.base_page import BasePage
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    base = BasePage(page)
    print(f'Timeout: {base.timeout}')
    print('✅ BasePage 생성 성공')
"

# HomePage 인스턴스 생성 테스트
python -c "
from playwright.sync_api import sync_playwright
from src.pages.home_page import HomePage
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    home = HomePage(page)
    print(f'URL: {home.url}')
    print(f'Nickname: {home.nickname}')
    print('✅ HomePage 생성 성공')
"
```

---

### Phase 5: 추가 파일 마이그레이션 (선택사항)

#### 5.1 token_manager.py
**현재**: 하드코딩된 `CLIENT_ID`, `CLIENT_SECRET`
**변경 계획**: pydantic-settings 사용 (별도 작업)

#### 5.2 slack_notifier.py
**현재**: 하드코딩된 `SLACK_WEBHOOK_URL`
**변경 계획**: pydantic-settings 사용 (별도 작업)

#### 5.3 conftest.py
**현재**: 하드코딩된 `REFRESH_TOKENS`
**변경 계획**: pydantic-settings 사용 (별도 작업)

**참고**: 이 파일들은 Phase 1에서 다루지 않고, 별도 작업으로 진행합니다.

---

## 🔍 검증 체크리스트

### 사전 검증
- [ ] `requirements.txt`에 `pydantic-settings>=2.0.0` 추가 확인
- [ ] `.env.example` 파일 생성 확인
- [ ] Git 상태 확인 (변경사항 커밋 전)

### 코드 변경 검증
- [ ] `config/config.py` 변경 완료
- [ ] 모든 함수 인터페이스 유지 확인
- [ ] `ENVIRONMENT` 상수 유지 확인
- [ ] 타입 힌트 추가 확인

### 기능 검증
- [ ] 모든 함수 반환값 검증 (12개 함수)
- [ ] `ENVIRONMENT` 상수 값 검증
- [ ] 환경 분기 동작 검증 (live/staging)
- [ ] 환경변수 없을 때 기본값 동작 확인

### 호환성 검증
- [ ] 11개 영향 파일 import 구문 검증
- [ ] 48회 함수 호출 검증
- [ ] 26회 `ENVIRONMENT` 사용 검증
- [ ] BasePage 상속 구조 검증

### 통합 테스트
- [ ] 단위 테스트 실행
- [ ] 기존 테스트 실행
- [ ] 실제 사용 시나리오 테스트

---

## 📊 예상 결과

### 변경 전후 비교

| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| **하드코딩된 값** | 있음 | 없음 (환경변수로 이동) |
| **타입 안전성** | 없음 | 있음 (pydantic) |
| **환경변수 지원** | 없음 | 있음 (자동 로드) |
| **함수 인터페이스** | 11개 | 11개 (동일) |
| **하위 호환성** | - | 100% 유지 |
| **수정 필요 파일** | - | 1개만 |

### 성공 기준
1. ✅ 모든 기존 함수가 동일한 반환값 반환
2. ✅ 모든 import 구문이 정상 동작
3. ✅ 기존 테스트가 모두 통과
4. ✅ 환경변수를 통한 설정 변경 가능
5. ✅ 하위 호환성 100% 유지

---

## 🚨 리스크 관리

### 잠재적 리스크

#### 리스크 1: 환경변수 로드 실패
**확률**: 🟡 중간
**영향**: 설정값을 가져오지 못함
**대응**:
- 기본값 제공 (이미 구현)
- 명확한 에러 메시지
- `.env.example` 파일 제공

#### 리스크 2: 타입 변환 실패
**확률**: 🟢 낮음
**영향**: pydantic 검증 실패
**대응**:
- 기본값 타입 명시
- `extra="ignore"` 설정으로 추가 필드 무시

#### 리스크 3: 싱글톤 패턴 문제
**확률**: 🟢 매우 낮음
**영향**: 환경 변경 시 이전 값 유지
**대응**:
- `@lru_cache()` 사용 (이미 구현)
- 필요 시 캐시 클리어 함수 제공

### 롤백 계획
1. Git을 통한 이전 버전 복원
2. `requirements.txt`에서 pydantic-settings 제거
3. 기존 `config/config.py` 복원

---

## 📝 작업 일정

### 예상 작업 시간
- **Phase 1**: 30분 (의존성 추가, .env.example 생성)
- **Phase 2**: 1시간 (config.py 변경)
- **Phase 3**: 30분 (검증)
- **Phase 4**: 30분 (통합 테스트)
- **총 예상 시간**: 2-3시간

### 작업 순서
1. Git 브랜치 생성 (`git checkout -b feature/env-migration`)
2. Phase 1 실행
3. Phase 2 실행
4. Phase 3 검증
5. Phase 4 통합 테스트
6. 모든 검증 통과 시 커밋
7. PR 생성 및 리뷰

---

## ✅ 최종 검증 체크리스트

### 코드 변경
- [ ] `requirements.txt` 업데이트 완료
- [ ] `.env.example` 생성 완료
- [ ] `config/config.py` 변경 완료

### 기능 검증
- [ ] 모든 함수 반환값 검증 통과 (12개 함수)
- [ ] 환경 분기 동작 확인 (live/staging)
- [ ] 타입 검증 통과
- [ ] 기본값 동작 확인 (환경변수 없을 때)

### 호환성 검증
- [ ] 11개 파일 import 검증 통과
  - [ ] `src/pages/base_page.py` - `get_timeout, get_long_timeout, get_download_timeout`
  - [ ] `src/pages/home_page.py` - `get_test_nickname, get_url`
  - [ ] `src/pages/stock_factor_strategy_page.py` - `get_url, get_timeout, get_long_timeout, get_download_dir`
  - [ ] `src/pages/coin_trend_strategy_page.py` - `get_url, get_timeout, get_long_timeout, get_download_dir`
  - [ ] `src/pages/stock_investment_page.py` - `get_url, get_long_timeout, get_stock_account, get_stock_strategy`
  - [ ] `src/tests/conftest.py` - `get_url, get_timeout, ENVIRONMENT`
  - [ ] `src/tests/test_home_pom.py` - `ENVIRONMENT, get_url, get_test_nickname`
  - [ ] `src/tests/test_stock_factor_strategy_pom.py` - `ENVIRONMENT`
  - [ ] `src/tests/test_coin_trend_strategy_pom.py` - `ENVIRONMENT`
  - [ ] `src/utils/test_utils.py` - `get_download_dir, ENVIRONMENT`
  - [ ] `src/utils/refresh_token_test.py` - `ENVIRONMENT`
- [ ] 48회 함수 호출 검증 통과
- [ ] 26회 ENVIRONMENT 사용 검증 통과

### 통합 테스트
- [ ] 단위 테스트 통과
- [ ] 기존 테스트 통과
- [ ] 실제 사용 시나리오 테스트 통과
  - [ ] BasePage 인스턴스 생성 테스트
  - [ ] HomePage 인스턴스 생성 테스트
  - [ ] StockFactorStrategyPage 인스턴스 생성 테스트
  - [ ] CoinTrendStrategyPage 인스턴스 생성 테스트
  - [ ] StockInvestmentPage 인스턴스 생성 테스트

### 문서화
- [ ] `.env.example` 주석 추가
- [ ] `config/config.py` docstring 업데이트
- [ ] README 업데이트 (선택사항)

---

## 🎯 완료 기준

다음 조건을 모두 만족할 때 마이그레이션이 완료된 것으로 간주:

1. ✅ **기능적 완성도**: 모든 함수가 기존과 동일하게 동작
2. ✅ **호환성**: 11개 영향 파일 모두 정상 동작
3. ✅ **검증**: 모든 테스트 통과
4. ✅ **문서화**: `.env.example` 및 주석 완료
5. ✅ **안정성**: 롤백 계획 수립 및 검증

---

## 📚 참고 자료

- [pydantic-settings 공식 문서](https://docs.pydantic.dev/latest/usage/pydantic_settings/)
- 영향 범위 분석: `docs/IMPACT_ANALYSIS.md`
- 마이그레이션 계획: `docs/ENV_MIGRATION_PLAN.md`

