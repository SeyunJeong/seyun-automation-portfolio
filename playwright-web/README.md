# Playwright Web E2E Testing Automation

## 프로젝트 개요
Playwright 기반의 웹 UI 자동화 테스트 시스템으로, Page Object Model (POM) 패턴을 적용하여 유지보수가 쉬운 E2E 테스트를 구현했습니다.

## 주요 기능

### 1. Page Object Model (POM) 패턴
- 페이지별로 독립적인 클래스 구조
- UI 요소와 테스트 로직의 분리
- 코드 재사용성 및 유지보수성 향상
- BasePage 클래스를 통한 공통 기능 상속

### 2. 다중 환경 지원
- 환경별 설정 파일 (.env, .env.stg, .env.live)
- pytest fixture를 통한 환경 전환
- 브라우저 상태 및 쿠키 관리
- 환경별 timeout 설정

### 3. 자동화된 테스트 시나리오
- 로그인 상태 확인 테스트
- 주식 투자 전략 페이지 테스트
- 코인 트렌드 전략 페이지 테스트
- 각 페이지별 핵심 기능 검증

### 4. Slack 알림 통합
- 테스트 성공/실패 결과 실시간 알림
- 환경별 구분된 메시지 전송
- 에러 상세 정보 포함
- 테스트 진행 상황 모니터링

### 5. CI/CD 및 Docker 지원
- Docker 컨테이너 환경에서 실행 가능
- GitHub Actions 연동
- Headless 모드 지원
- 스케줄링된 자동 테스트 실행

## 프로젝트 구조

```
playwright-web/
├── config/
│   └── config.py            # 환경별 설정 로더
├── src/
│   ├── pages/              # Page Object Model
│   │   ├── base_page.py    # 공통 기능 베이스 클래스
│   │   ├── home_page.py    # 홈/로그인 페이지
│   │   ├── stock_investment_page.py # 주식 투자 페이지
│   │   ├── stock_factor_strategy_page.py # 주식 팩터 전략 페이지
│   │   └── coin_trend_strategy_page.py # 코인 트렌드 전략 페이지
│   ├── tests/              # 테스트 케이스
│   │   ├── conftest.py     # pytest 설정 및 fixture
│   │   ├── test_home_pom.py # 로그인 상태 테스트
│   │   ├── test_stock_factor_strategy_pom.py # 주식 전략 테스트
│   │   └── test_coin_trend_strategy_pom.py # 코인 전략 테스트
│   └── utils/
│       └── slack_notifier.py # Slack 알림 모듈
├── .env                    # 환경 변수 (기본)
├── .env.stg                # Staging 환경 변수
├── .env.live               # Production 환경 변수
├── pytest.ini              # pytest 설정
├── Dockerfile              # Docker 이미지 빌드
├── entrypoint.sh           # Docker 진입점 스크립트
└── slack_notifier.py       # 독립 Slack 알림 모듈
```

## 워크플로우

### 1. 테스트 초기화
```
pytest 실행 → conftest.py의 fixture 로드 → 환경 설정 읽기 → 브라우저 컨텍스트 생성
```

### 2. 페이지 객체 생성
```
테스트 시작 → Page Object 인스턴스 생성 → BasePage 기능 상속
```

### 3. 테스트 실행
```
페이지 네비게이션 → UI 요소 상호작용 → 검증(assertion) → 결과 수집
```

### 4. 결과 처리
```
테스트 결과 집계 → Slack 메시지 포맷팅 → 알림 전송
```

## Page Object Model 구조

### BasePage (기본 클래스)
- `wait_for_loading()`: 페이지 로딩 대기
- `wait_for_page_load()`: DOM 로드 완료 대기
- `click_element()`: 요소 클릭
- `click_text()`: 텍스트로 요소 찾아 클릭
- `fill_input()`: 입력 필드 채우기
- `is_visible()`: 요소 가시성 확인
- `take_screenshot()`: 스크린샷 캡처

### 페이지별 클래스
각 페이지는 BasePage를 상속받아 페이지별 고유 기능 구현:
- **HomePage**: 로그인 상태 확인, 네비게이션
- **StockInvestmentPage**: 주식 투자 관련 기능
- **StockFactorStrategyPage**: 주식 팩터 전략 테스트
- **CoinTrendStrategyPage**: 코인 트렌드 전략 테스트

## 테스트 시나리오

### 1. 로그인 상태 확인 (test_home_pom.py)
```
홈페이지 접속 → 로그인 상태 검증 → 결과 Slack 알림
```

### 2. 주식 팩터 전략 테스트 (test_stock_factor_strategy_pom.py)
```
전략 페이지 이동 → 주요 요소 확인 → 기능 동작 검증 → 결과 Slack 알림
```

### 3. 코인 트렌드 전략 테스트 (test_coin_trend_strategy_pom.py)
```
전략 페이지 이동 → 주요 요소 확인 → 기능 동작 검증 → 결과 Slack 알림
```

## 기술 스택
- **Python 3.13+**
- **Playwright** - 브라우저 자동화
- **pytest** - 테스트 프레임워크
- **Docker** - 컨테이너화
- **GitHub Actions** - CI/CD 자동화
- **Slack Webhook** - 테스트 결과 알림

## 핵심 특징

### POM 패턴의 장점
- **유지보수성**: UI 변경 시 페이지 클래스만 수정
- **재사용성**: 공통 메서드를 여러 테스트에서 활용
- **가독성**: 테스트 코드가 비즈니스 로직에 집중
- **확장성**: 새로운 페이지 추가가 용이

### 안정성 향상
- 명시적 대기(explicit wait) 사용
- 로딩 상태 확인
- 에러 핸들링 및 재시도 로직
- 스크린샷 캡처 기능
