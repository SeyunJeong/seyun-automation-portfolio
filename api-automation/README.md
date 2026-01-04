# API Automation & Health Monitoring

## 프로젝트 개요
API 엔드포인트의 헬스 체크를 자동화하고, 테스트 결과를 실시간으로 Slack에 알림하는 모니터링 시스템입니다.

## 주요 기능

### 1. API 헬스 체크 자동화
- pytest 기반의 API 테스트 자동 실행
- 다중 환경 지원 (dev, stg, live)
- 각 API 엔드포인트별 응답 시간 측정
- 테스트 결과 및 타이밍 데이터 JSON 파일로 저장

### 2. 실시간 모니터링
- 테스트 성공/실패 여부 실시간 수집
- API 응답 시간 추적 및 분석
- 7일간의 히스토리 데이터 관리
- 실패 원인 자동 분류 (타임아웃, 연결 실패, 인증 오류 등)

### 3. Slack 알림 시스템
- 테스트 완료 즉시 Slack 채널로 결과 전송
- 성공/실패 상태별 색상 구분 (good/danger)
- 각 테스트별 상세 정보 제공:
  - API 엔드포인트
  - 응답 시간
  - 실패 원인 (실패 시)

### 4. GitHub Actions 통합
- 스케줄링된 자동 실행 (Cron)
- GitHub 환경 변수를 통한 체크포인트 관리
- CI/CD 파이프라인에 통합 가능

## 프로젝트 구조

```
api-automation/
├── config/
│   └── config.json          # 환경별 설정 (API URL, Slack webhook 등)
├── src/
│   ├── api_client.py        # API 요청 클라이언트
│   ├── slack_notifier.py    # Slack 알림 전송 모듈
│   ├── test_schemas.py      # 응답 스키마 검증
│   └── token_manager.py     # OAuth 토큰 관리
├── tests/
│   ├── test_fastapi2_apis.py # FastAPI2 서버 테스트
│   └── test_fastapi1_apis.py # FastAPI1 서버 테스트
├── data/
│   └── health_results_*.json # 테스트 결과 히스토리
├── github_health_monitor.py  # 메인 모니터링 스크립트
├── run_full_test.py         # 로컬 전체 테스트 실행
└── test_timings.json        # API 응답 시간 데이터
```

## 워크플로우

### 1. 테스트 실행
```
pytest 실행 → 각 API 엔드포인트 테스트 → 응답 시간 측정
```

### 2. 결과 수집 및 분석
```
테스트 결과 파싱 → 타이밍 데이터 로드 → 실패 원인 분석
```

### 3. 데이터 저장
```
기존 히스토리 로드 → 새 결과 추가 → 7일 이상 데이터 정리 → JSON 파일 저장
```

### 4. 알림 전송
```
결과 포맷팅 → Slack 메시지 생성 → Webhook으로 전송
```

## 모니터링 대상 API

### FastAPI v2 엔드포인트
- `/api/v2/interest/groups` - 관심 그룹 조회
- `/api/v2/interest/stories` - 스토리 조회
- `/api/v2/interest/price` - 종목 정보 조회
- `/api/v2/interest/news` - 뉴스 조회 및 페이지네이션

### FastAPI v1 엔드포인트
- `/trade/get_accounts` - 계좌 정보 조회
- `/prime/stock_prime_strategies` - 주식 프라임 전략 조회

## 기술 스택
- **Python 3.9+**
- **pytest** - 테스트 프레임워크
- **requests** - HTTP 통신
- **jsonschema** - JSON 스키마 검증
- **GitHub Actions** - CI/CD 자동화
- **Slack Webhook** - 실시간 알림
