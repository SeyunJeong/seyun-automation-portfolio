# Quantus 웹 자동화 테스트

본 프로젝트는 Quantus 웹사이트에 대한 자동화 테스트 프레임워크입니다. Playwright를 사용하여 웹 테스트를 자동화하고, 페이지 객체 모델(POM) 패턴을 통해 유지보수성과 재사용성을 높였습니다.

## 목차
1. [환경 설정 방법](#환경-설정-방법)
2. [테스트 실행 방법](#테스트-실행-방법)
3. [페이지 객체 모델(POM) 구조](#페이지-객체-모델pom-구조)
4. [프로젝트 디렉토리 구조](#프로젝트-디렉토리-구조)

## 환경 설정 방법

### 1. 환경 전환 방법

테스트 환경은 `config.py` 파일에서 관리됩니다. 라이브 환경과 개발 환경 간 전환이 필요한 경우 다음과 같이 설정하세요:

```python
# config.py 파일 내에서 ENVIRONMENT 변수 수정
ENVIRONMENT = "live"  # "live" 또는 "dev"로 설정
```

### 2. 환경별 설정 값 관리

- **URL, 계정, 계좌, 타임아웃 등의 설정값**은 `config.py` 파일에서 수정할 수 있습니다.
- 라이브 환경은 `LIVE` 딕셔너리에, 개발 환경은 `DEV` 딕셔너리에 설정값을 관리합니다.

```python
# 라이브 환경 설정 예시
LIVE = {
    "base_url": "https://www.quantus.kr/",
    "accounts": {
        "test_account": "퀀터스관리자계정",
    },
    # 기타 설정값...
}

# 개발 환경 설정 예시
DEV = {
    "base_url": "https://dev.quantus.kr/",
    "accounts": {
        "test_account": "dev자동화테스트계정",
    },
    # 기타 설정값...
}
```

### 3. 테스트 코드에서 설정값 사용 방법

테스트 코드에서는 다음과 같이 설정값을 가져와 사용합니다:

```python
from config import get_url, get_timeout, get_test_account

# URL 사용 예시
page.goto(get_url())

# 타임아웃 사용 예시
element.wait_for(timeout=get_timeout())

# 계정명 사용 예시
page.locator(f'text="{get_test_account()}"')
```

### 4. 사용 가능한 설정 함수

- `get_url()`: 현재 환경의 기본 URL
- `get_timeout()`: 기본 타임아웃 값
- `get_long_timeout()`: 긴 작업용 타임아웃 값
- `get_download_dir()`: 다운로드 디렉토리 경로
- `get_test_account()`: 테스트 계정명
- `get_stock_account()`: 테스트 주식 계좌명
- `get_coin_account()`: 테스트 코인 계좌명
- `get_stock_strategy(key)`: 주식 전략 이름 (예: `get_stock_strategy("all_weather")`)
- `get_coin_strategy(key)`: 코인 전략 이름 (예: `get_coin_strategy("all_weather")`)

## 테스트 실행 방법

```bash
# 모든 테스트 실행
pytest

# 특정 테스트 파일만 실행
pytest test_QuantusUser.py

# 특정 테스트 함수만 실행
pytest test_QuantusUser.py::test_check_login_status

# 특정 클래스의 테스트만 실행
pytest test_QuantusUser.py::TestStockFactorStrategy
```

## 페이지 객체 모델(POM) 구조

### 개요
이 프로젝트는 페이지 객체 모델(Page Object Model, POM) 패턴을 사용하여 구현되었습니다. POM 패턴은 웹 UI 요소와 해당 요소에 대한 작업을 캡슐화하여 테스트 코드를 더 유지보수하기 쉽고 가독성 있게 만드는 디자인 패턴입니다.

### 클래스 구조

#### 1. BasePage
모든 페이지 클래스의 기본이 되는 추상 기본 클래스입니다. 페이지 탐색, 요소 조작과 같은 공통 기능이 구현되어 있습니다.

주요 기능:
- 요소 클릭
- 입력 필드 채우기
- 요소 텍스트 가져오기
- 요소 가시성 검사
- 대기 및 로딩 처리
- 스크린샷 촬영

#### 2. LoginPage
로그인 기능과 관련된 페이지 객체 클래스입니다.

주요 기능:
- 로그인 페이지 이동
- 로그인 상태 확인
- 토큰 기반 인증

#### 3. StockInvestmentPage
주식 투자 기능과 관련된 페이지 객체 클래스입니다.

주요 기능:
- 주식 프라임 전략 선택
- 투자 계좌 선택
- 투자 예약 및 완료
- 전략 변경
- 투자 취소
- 리밸런싱 일정 확인

#### 4. CoinInvestmentPage
코인 투자 기능과 관련된 페이지 객체 클래스입니다.

주요 기능:
- IP 등록
- 코인 전략 선택
- 투자 예약 및 완료
- 투자 청산, 재개, 일시정지
- 투자 취소
- 투자 상태 검증

#### 5. StockFactorStrategyPage
주식 팩터 전략 기능과 관련된 페이지 객체 클래스입니다.

주요 기능:
- 유니버스 선택
- 팩터 선택
- 백테스트 실행
- 포트폴리오 확인
- 결과 다운로드

#### 6. CoinTrendStrategyPage
코인 트렌드 전략 기능과 관련된 페이지 객체 클래스입니다.

주요 기능:
- 코인 선택
- 지표 선택
- 백테스트 실행
- 결과 다운로드
- 전략 적용

### 사용 방법

```python
# 테스트 코드 예시
def test_로그인_상태_확인(browser):
    page = browser.new_page()
    login_page = LoginPage(page)
    
    # 메서드 체이닝 패턴으로 여러 작업을 연속적으로 수행
    login_page.navigate().is_logged_in()
    
    # 또는 단계별로 수행
    login_page.navigate()
    assert login_page.is_logged_in(), "로그인되어 있지 않습니다."
```

### 장점
1. **코드 재사용성**: 여러 테스트에서 동일한 페이지 객체를 재사용할 수 있습니다.
2. **유지보수 용이성**: UI 변경 시 페이지 객체 클래스만 수정하면 됩니다.
3. **가독성 향상**: 테스트 코드가 더 명확하고 이해하기 쉬워집니다.
4. **테스트 안정성**: 셀렉터 및 대기 로직이 한 곳에 집중되어 관리됩니다.

## 프로젝트 디렉토리 구조

```
/
├── config/             # 설정 파일 디렉토리
├── src/                # 소스 코드 디렉토리
│   ├── pages/          # 페이지 객체 모델 클래스
│   ├── tests/          # 테스트 코드
│   └── utils/          # 유틸리티 함수
├── docs/               # 프로젝트 문서
├── .vscode/            # VS Code 설정
├── downloads/          # 다운로드 파일 저장 디렉토리
└── screenshots/        # 스크린샷 저장 디렉토리
``` 