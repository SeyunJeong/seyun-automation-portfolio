# Playwright-Web 프로젝트 환경변수 마이그레이션 계획

## 📋 개요
playwright-web 프로젝트 내부의 하드코딩된 값들을 환경변수로 마이그레이션하여 보안성과 유연성을 향상시키는 계획입니다.

## 🔍 현재 상태 분석

### 1. 하드코딩된 값 현황

#### 1.1 `config/config.py`
- **ENVIRONMENT**: `"live"` (하드코딩)
- **LIVE 환경 설정**:
  - `base_url`: `"https://service.quantus.kr/ko"`
  - `nickname.test_nickname`: `"퀀터스관리자계정"`
  - `stock_accounts.test_account`: `"자동화테스트주식계좌"`
  - `coin_accounts.test_account`: `"자동화테스트코인계좌"`
  - `stock_strategies`: 전략명들
  - `coin_strategies`: 전략명들
- **STAGING 환경 설정**:
  - `base_url`: `"https://dev.quantus.kr/ko"`
  - `nickname.test_nickname`: `"안녕하세요"`
  - `stock_accounts.test_account`: `"qa자동화테스트주식계좌"`
  - `coin_accounts.test_account`: `"qa자동화테스트코인계좌"`
- **COMMON 설정**:
  - `timeout`: `30000` (ms)
  - `long_timeout`: `100000` (ms)
  - `download_timeout`: `1200000` (ms)
  - `download_dir`: `"downloads"`

#### 1.2 `src/tests/conftest.py`
- **REFRESH_TOKENS**: Google 리프레시 토큰 (live/staging 모두 하드코딩)
- **환경변수**: `DISPLAY`, `XDG_RUNTIME_DIR` (하드코딩)

#### 1.3 `src/utils/token_manager.py`
- **CLIENT_ID**: `'YOUR-CLIENT-ID.apps.googleusercontent.com'`
- **CLIENT_SECRET**: `'YOUR-CLIENT-SECRET'`
- **token_url**: `"https://oauth2.googleapis.com/token"` (상수이므로 유지 가능)

#### 1.4 `slack_notifier.py` 및 `src/utils/slack_notifier.py`
- **SLACK_WEBHOOK_URL**: `"https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"` (하드코딩)

#### 1.5 `src/pages/home_page.py`
- **하드코딩된 닉네임**: `"퀀터스관리자계정"` (26번째 줄)

#### 1.6 `src/utils/test_utils.py`
- **TEST_DATA**: 테스트 데이터 딕셔너리 (투자금액, 종목수, 날짜, 파라미터 등)

## 📝 마이그레이션 계획

### Phase 1: 환경변수 인프라 구축

#### 1.1 `.env` 파일 구조 설계

**핵심 원칙**: 환경별로 달라지는 값만 환경 접두사로 분기하고, 공통으로 사용되는 값은 단일 환경변수로 관리

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
# 환경별 설정 (ENVIRONMENT 값에 따라 분기)
# ============================================
# Live 환경
LIVE_BASE_URL=https://service.quantus.kr/ko
LIVE_TEST_NICKNAME=퀀터스관리자계정
LIVE_STOCK_ACCOUNT=자동화테스트주식계좌
LIVE_COIN_ACCOUNT=자동화테스트코인계좌
LIVE_STOCK_STRATEGY_ALL_WEATHER=퀀터스 글로벌 올웨더 액티브
LIVE_STOCK_STRATEGY_LONG_SHORT=퀀터스 지수 롱숏 액티브
LIVE_COIN_STRATEGY_ALL_WEATHER=크립토 올웨더 액티브 전략

# Staging 환경
STAGING_BASE_URL=https://dev.quantus.kr/ko
STAGING_TEST_NICKNAME=안녕하세요
STAGING_STOCK_ACCOUNT=qa자동화테스트주식계좌
STAGING_COIN_ACCOUNT=qa자동화테스트코인계좌
STAGING_STOCK_STRATEGY_ALL_WEATHER=퀀터스 글로벌 올웨더 액티브
STAGING_STOCK_STRATEGY_LONG_SHORT=퀀터스 지수 롱숏 액티브
STAGING_COIN_STRATEGY_ALL_WEATHER=크립토 올웨더 액티브 전략

# ============================================
# 인증 정보 (환경별로 다를 수 있음)
# ============================================
GOOGLE_CLIENT_ID=YOUR-CLIENT-ID.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR-CLIENT-SECRET
GOOGLE_REFRESH_TOKEN_LIVE=YOUR-GOOGLE-REFRESH-TOKEN-LIVE
GOOGLE_REFRESH_TOKEN_STAGING=YOUR-GOOGLE-REFRESH-TOKEN-STAGING

# ============================================
# 외부 서비스 (공통 또는 환경별)
# ============================================
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

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

**환경변수 분류 설명**:
- **공통 변수**: `TIMEOUT`, `LONG_TIMEOUT`, `DOWNLOAD_TIMEOUT`, `DOWNLOAD_DIR` 등은 모든 환경에서 동일하게 사용되므로 환경 접두사 없이 단일 변수로 관리
- **환경별 변수**: `BASE_URL`, `TEST_NICKNAME`, `STOCK_ACCOUNT` 등은 `ENVIRONMENT` 값에 따라 `LIVE_*` 또는 `STAGING_*` 접두사를 가진 변수를 읽음
- **코드 로직**: `config.py`에서 `ENVIRONMENT` 값을 확인하여 적절한 환경변수를 동적으로 선택

#### 1.2 환경변수 분기 전략

**핵심 개념**: `ENVIRONMENT` 환경변수 하나로 모든 환경별 설정을 분기

**동작 방식**:
1. `ENVIRONMENT` 환경변수로 현재 환경 확인 (기본값: "live")
2. 공통 변수는 환경 접두사 없이 직접 읽기
3. 환경별 변수는 `{ENVIRONMENT}_{KEY}` 형식으로 동적 구성하여 읽기

**예시**:
```python
ENVIRONMENT = os.getenv("ENVIRONMENT", "live").lower()  # "live" 또는 "staging"

# 공통 변수 (환경 분기 없음)
timeout = int(os.getenv("TIMEOUT", "30000"))  # 모든 환경에서 동일

# 환경별 변수 (ENVIRONMENT로 분기)
env_prefix = ENVIRONMENT.upper()  # "LIVE" 또는 "STAGING"
base_url = os.getenv(f"{env_prefix}_BASE_URL")  # LIVE_BASE_URL 또는 STAGING_BASE_URL
```

**장점**:
- 공통 설정 중복 제거 (타임아웃, 디렉토리 등)
- 환경 전환 시 `ENVIRONMENT` 하나만 변경하면 됨
- 코드에서 환경 분기 로직 단순화
- 새로운 환경 추가 시 확장 용이

#### 1.3 `.env.example` 파일 생성
- 실제 값 없이 변수명과 설명만 포함
- Git에 커밋하여 팀원들이 참고할 수 있도록 함
- 환경변수 분기 전략 설명 포함

#### 1.4 `.gitignore` 업데이트
- `.env` 파일이 Git에 커밋되지 않도록 확인

### Phase 2: 코드 수정

#### 2.1 `config/config.py` 수정
- `pydantic-settings`를 사용하여 타입 안전하고 깔끔한 환경변수 관리
- `BaseSettings`를 상속받아 설정 클래스 정의
- 자동 타입 변환 및 검증
- `.env` 파일 자동 로드 (python-dotenv 내장)
- `ENVIRONMENT` 환경변수로 현재 환경 확인 (기본값: "live")
- **공통 변수**: 환경 접두사 없이 직접 읽기
  - `TIMEOUT`, `LONG_TIMEOUT`, `DOWNLOAD_TIMEOUT`, `DOWNLOAD_DIR`
- **환경별 변수**: `ENVIRONMENT` 값에 따라 동적으로 변수명 구성
  - 예: `ENVIRONMENT=live` → `LIVE_BASE_URL` 읽기
  - 예: `ENVIRONMENT=staging` → `STAGING_BASE_URL` 읽기
- 기본값(fallback) 제공
- 기존 함수 인터페이스 유지 (하위 호환성)

**구현 예시 (pydantic-settings 사용)**:
```python
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
    """현재 환경 설정 반환 (공통 + 환경별 설정 병합)"""
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


# 기존 함수들 유지 (하위 호환성)
def get_url():
    return get_config()["base_url"]


def get_test_nickname():
    return get_config()["nickname"]["test_nickname"]


def get_stock_account():
    return get_config()["stock_accounts"]["test_account"]


def get_coin_account():
    return get_config()["coin_accounts"]["test_account"]


def get_timeout():
    return get_config()["timeout"]


def get_long_timeout():
    return get_config()["long_timeout"]


def get_download_timeout():
    return get_config()["download_timeout"]


def get_download_dir():
    return get_config()["download_dir"]


def get_stock_strategy(strategy_key: str):
    return get_config()["stock_strategies"][strategy_key]


def get_coin_strategy(strategy_key: str):
    return get_config()["coin_strategies"][strategy_key]


# 환경 변수 직접 접근 (필요시)
ENVIRONMENT = get_common_settings().environment
```

**pydantic-settings 장점**:
- ✅ 타입 안전성: 자동 타입 변환 및 검증
- ✅ 자동 검증: 필수 필드 누락 시 명확한 에러 메시지
- ✅ IDE 지원: 자동완성 및 타입 힌트
- ✅ 깔끔한 코드: 클래스 기반 구조로 가독성 향상
- ✅ 환경변수 자동 로드: `.env` 파일 자동 인식
- ✅ `env_prefix` 지원: `LIVE_*`, `STAGING_*` 자동 매핑
- ✅ 싱글톤 패턴: `@lru_cache()`로 성능 최적화

**동작 예시**:
- `ENVIRONMENT=live` → `LiveSettings` 인스턴스 생성, `LIVE_*` 접두사 변수 자동 매핑
- `ENVIRONMENT=staging` → `StagingSettings` 인스턴스 생성, `STAGING_*` 접두사 변수 자동 매핑
- `TIMEOUT`, `DOWNLOAD_DIR` 등은 `CommonSettings`에서 환경과 무관하게 동일한 값 사용

#### 2.2 `src/tests/conftest.py` 수정
- `pydantic-settings`를 사용하여 환경변수 읽기
- `REFRESH_TOKENS`를 환경변수에서 읽도록 변경
  - `ENVIRONMENT` 값에 따라 `GOOGLE_REFRESH_TOKEN_LIVE` 또는 `GOOGLE_REFRESH_TOKEN_STAGING` 읽기
- `DISPLAY`, `XDG_RUNTIME_DIR`도 환경변수에서 읽기 (공통 변수)

**구현 예시 (pydantic-settings 사용)**:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from config.config import get_common_settings
import os

class AuthSettings(BaseSettings):
    """인증 관련 설정"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    google_client_id: str
    google_client_secret: str
    google_refresh_token_live: str
    google_refresh_token_staging: str


class BrowserSettings(BaseSettings):
    """브라우저 환경 설정"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    display: str = ":99"
    xdg_runtime_dir: str = "/tmp/runtime-root"


@lru_cache()
def get_auth_settings() -> AuthSettings:
    return AuthSettings()


@lru_cache()
def get_browser_settings() -> BrowserSettings:
    return BrowserSettings()


# 환경별 리프레시 토큰
def get_refresh_token() -> str:
    """현재 환경에 맞는 리프레시 토큰 반환"""
    common = get_common_settings()
    auth = get_auth_settings()
    
    if common.environment == "live":
        return auth.google_refresh_token_live
    else:
        return auth.google_refresh_token_staging


# 브라우저 환경변수 설정
browser_settings = get_browser_settings()
os.environ["DISPLAY"] = browser_settings.display
os.environ["XDG_RUNTIME_DIR"] = browser_settings.xdg_runtime_dir

# 기존 코드와의 호환성을 위한 딕셔너리 (필요시)
REFRESH_TOKENS = {
    "live": get_auth_settings().google_refresh_token_live,
    "staging": get_auth_settings().google_refresh_token_staging
}
```

#### 2.3 `src/utils/token_manager.py` 수정
- `pydantic-settings`를 사용하여 `CLIENT_ID`, `CLIENT_SECRET`을 환경변수에서 읽기

**구현 예시 (pydantic-settings 사용)**:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class GoogleAuthSettings(BaseSettings):
    """Google OAuth 설정"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    google_client_id: str
    google_client_secret: str


@lru_cache()
def get_google_auth_settings() -> GoogleAuthSettings:
    return GoogleAuthSettings()


def refresh_google_token(refresh_token: str):
    """리프레시 토큰을 사용하여 새 액세스 토큰을 획득하는 함수"""
    auth = get_google_auth_settings()
    
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": auth.google_client_id,
        "client_secret": auth.google_client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    
    # ... 기존 로직 유지
```

#### 2.4 `slack_notifier.py` 및 `src/utils/slack_notifier.py` 수정
- `pydantic-settings`를 사용하여 `SLACK_WEBHOOK_URL`을 환경변수에서 읽기

**구현 예시 (pydantic-settings 사용)**:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import requests


class SlackSettings(BaseSettings):
    """Slack 설정"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    slack_webhook_url: str


@lru_cache()
def get_slack_settings() -> SlackSettings:
    return SlackSettings()


class SlackNotifier:
    """Slack 메시지 전송을 위한 클래스"""
    
    def __init__(self, webhook_url: str | None = None):
        if webhook_url is None:
            webhook_url = get_slack_settings().slack_webhook_url
        self.webhook_url = webhook_url
    
    def send_message(self, message: str) -> bool:
        """Slack 메시지 전송"""
        payload = {"text": message}
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error sending message to Slack: {e}")
            return False


def send_slack_message(message: str):
    """기존 함수 인터페이스 유지"""
    notifier = SlackNotifier()
    notifier.send_message(message)
```

#### 2.5 `src/pages/home_page.py` 수정
- 하드코딩된 닉네임을 `get_test_nickname()` 함수 사용으로 변경

#### 2.6 `src/utils/test_utils.py` 수정
- `TEST_DATA`의 값들을 환경변수에서 읽도록 변경 (선택사항)

### Phase 3: 문서화 및 테스트

#### 3.1 README 업데이트
- 환경변수 설정 방법 문서화
- `.env.example` 사용 방법 설명

#### 3.2 테스트
- 기존 테스트가 정상 동작하는지 확인
- 환경변수가 없을 때 기본값 동작 확인
- 환경변수 우선순위 확인

## 🎯 우선순위

### 높음 (보안 관련)
1. ✅ Google OAuth 클라이언트 ID/Secret
2. ✅ Google 리프레시 토큰
3. ✅ Slack 웹훅 URL

### 중간 (유연성 관련)
4. ✅ 환경 설정 (ENVIRONMENT)
5. ✅ Base URL (live/staging)
6. ✅ 테스트 계정 정보 (닉네임, 계좌명)

### 낮음 (설정 관련)
7. ⚠️ 타임아웃 값들 (기본값 유지 가능)
8. ⚠️ 다운로드 디렉토리 (기본값 유지 가능)
9. ⚠️ 테스트 데이터 (기본값 유지 가능)

## 📦 필요한 작업

### 1. 의존성 확인
- `pydantic-settings` 추가 필요 (기존 `python-dotenv`는 선택사항, pydantic-settings가 내장 지원)
- `pydantic` 및 `pydantic-settings` 패키지 설치 필요

### 2. 파일 생성/수정 목록
- [ ] `requirements.txt`에 `pydantic-settings>=2.0.0` 추가
- [ ] `.env.example` 파일 생성
- [ ] `.gitignore` 확인/업데이트
- [ ] `config/config.py` 수정 (pydantic-settings 사용)
- [ ] `src/tests/conftest.py` 수정 (pydantic-settings 사용)
- [ ] `src/utils/token_manager.py` 수정 (pydantic-settings 사용)
- [ ] `slack_notifier.py` 수정 (pydantic-settings 사용)
- [ ] `src/utils/slack_notifier.py` 수정 (pydantic-settings 사용)
- [ ] `src/pages/home_page.py` 수정
- [ ] `src/utils/test_utils.py` 수정 (선택사항)
- [ ] `README.md` 업데이트

### 3. 마이그레이션 체크리스트
- [ ] `.env.example` 생성 및 문서화
- [ ] 모든 하드코딩된 값 환경변수로 변경
- [ ] 기본값(fallback) 제공
- [ ] 기존 코드와의 호환성 유지
- [ ] 테스트 실행 및 검증
- [ ] 문서 업데이트

## 🔒 보안 고려사항

1. **민감한 정보 보호**
   - `.env` 파일은 절대 Git에 커밋하지 않음
   - `.env.example`에는 실제 값 대신 예시만 포함
   - 프로덕션 환경에서는 환경변수를 안전하게 관리

2. **환경변수 관리**
   - CI/CD 파이프라인에서 환경변수 설정
   - Docker 컨테이너에서 환경변수 주입
   - 로컬 개발 환경에서는 `.env` 파일 사용

3. **기본값 처리**
   - 민감한 정보는 기본값을 제공하지 않음
   - 필수 환경변수 누락 시 명확한 에러 메시지 제공

## 📚 참고사항

### 의존성
- `pydantic-settings` 추가 필요: `pip install pydantic-settings`
- `pydantic-settings`는 `.env` 파일 자동 로드 지원 (python-dotenv 내장)
- `requirements.txt`에 추가: `pydantic-settings>=2.0.0`

### pydantic-settings 장점
- ✅ **타입 안전성**: 자동 타입 변환 및 검증
- ✅ **자동 검증**: 필수 필드 누락 시 명확한 에러 메시지
- ✅ **IDE 지원**: 자동완성 및 타입 힌트
- ✅ **깔끔한 코드**: 클래스 기반 구조로 가독성 향상
- ✅ **환경변수 자동 로드**: `.env` 파일 자동 인식
- ✅ **env_prefix 지원**: `LIVE_*`, `STAGING_*` 자동 매핑
- ✅ **싱글톤 패턴**: `@lru_cache()`로 성능 최적화

### 기존 코드 호환성
- 기존 코드의 함수 인터페이스는 유지하여 하위 호환성 보장
- 환경변수 우선순위: 환경변수 > 기본값

### 환경변수 분기 전략
- 공통 변수: 환경 접두사 없이 단일 변수로 관리 (예: `TIMEOUT`)
- 환경별 변수: `ENVIRONMENT` 값에 따라 접두사가 붙은 변수 읽기 (예: `LIVE_BASE_URL`, `STAGING_BASE_URL`)
- 코드에서 `ENVIRONMENT` 값을 확인하여 동적으로 적절한 환경변수 선택
- `pydantic-settings`의 `env_prefix` 기능으로 환경별 변수 자동 매핑

### 유지보수성
- 환경별 설정 분리를 통해 유연성 확보
- 공통 설정은 중복 없이 단일 소스로 관리하여 유지보수성 향상
- 타입 안전성으로 런타임 에러 방지

