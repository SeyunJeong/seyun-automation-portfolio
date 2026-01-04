# Stock Data Validation & Automation

## 프로젝트 개요
Google Sheets와 Stock API를 연동하여 한국/미국 주식 데이터를 자동으로 수집하고 검증하는 시스템입니다.

## 주요 기능

### 1. 데이터 수집 자동화
- Google Sheets에서 종목 코드 읽기
- Stock API를 통한 실시간 주식 데이터 조회
- 배치 처리 (50개 종목씩) 방식으로 효율적 수집
- API 호출 간격 조절로 Rate Limit 방지

### 2. 체크포인트 시스템
- 진행 상태를 JSON 파일로 저장
- GitHub Actions 환경 변수 연동
- 중단 시 마지막 위치부터 재시작 가능
- 대량 데이터 처리 시 안정성 보장

### 3. Google Sheets 연동
- Google Service Account 인증
- Sheets API를 통한 자동 데이터 업데이트
- 종목별 주가 정보 실시간 반영
- 배치 단위 쓰기로 성능 최적화

### 4. 데이터 처리 및 검증
- Stock API 응답 데이터 파싱
- 캐시 기능으로 중복 API 호출 방지
- 데이터 정규화 및 포맷팅
- 에러 핸들링 및 로깅

## 프로젝트 구조

```
data-validation/
├── KRPortfolioChecker-main/     # 한국 주식 검증
│   ├── config/
│   │   ├── config.py            # 설정 관리
│   │   └── service-account-key.json # Google 인증 키
│   ├── modules/
│   │   ├── google_sheets.py     # Google Sheets 연동
│   │   ├── stock_api.py         # 한국 주식 API 클라이언트
│   │   └── data_processing.py   # 데이터 처리 로직
│   ├── main.py                  # 메인 실행 스크립트
│   └── checkpoint.json          # 진행 상태 저장
│
└── USPortfolioChecker-main/     # 미국 주식 검증
    ├── config/
    │   ├── config.py            # 설정 관리
    │   └── service-account-key.json # Google 인증 키
    ├── modules/
    │   ├── google_sheets.py     # Google Sheets 연동
    │   ├── stock_data_api.py    # 미국 주식 API 클라이언트
    │   └── data_processing.py   # 데이터 처리 로직
    ├── main.py                  # 메인 실행 스크립트
    └── checkpoint.json          # 진행 상태 저장
```

## 워크플로우

### 한국 주식 데이터 수집 (KRPortfolioChecker)
```
1. Google Sheets에서 종목 코드 읽기
2. 50개씩 배치로 분할
3. Stock API 호출 (한국 주식)
4. 데이터 처리 및 정규화
5. Google Sheets에 업데이트
6. 체크포인트 저장
7. 다음 배치로 이동 (sleep 1초)
```

### 미국 주식 데이터 수집 (USPortfolioChecker)
```
1. Google Sheets에서 종목 코드 읽기
2. 50개씩 배치로 분할
3. Stock Data API 호출 (미국 주식)
4. 데이터 처리 및 정규화
5. Google Sheets에 업데이트
6. 체크포인트 저장
7. 다음 배치로 이동 (sleep 1초)
```

## 주요 모듈

### 1. Google Sheets 모듈
- `GoogleSheets` 클래스로 Sheets API 추상화
- `read_column()`: 종목 코드 읽기
- `write_columns()`: 주가 데이터 쓰기
- Service Account 인증 방식 사용

### 2. Stock API 모듈
- `StockAPI` (한국): 한국 주식 데이터 조회
- `StockDataAPI` (미국): 미국 주식 데이터 조회
- API 키 기반 인증
- 응답 데이터 파싱 및 정규화

### 3. Data Processing 모듈
- `prepare_data()`: 배치 데이터 준비 및 처리
- 캐시 기능 지원
- 데이터 검증 및 포맷팅
- 에러 핸들링

### 4. Checkpoint 시스템
- `load_checkpoint()`: 마지막 처리 위치 로드
- `save_checkpoint()`: 현재 진행 상태 저장
- GitHub Actions 환경 변수 연동
- 로컬 파일 시스템 백업

## 기술 스택
- **Python 3.x**
- **Google Sheets API** - 스프레드시트 연동
- **Google Service Account** - 인증
- **Stock API** - 주식 데이터 조회
- **JSON** - 데이터 저장 및 설정
- **GitHub Actions** (선택) - 자동화 실행
