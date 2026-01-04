# 환경변수 마이그레이션 계획 (간소화)

## 핵심 요약

**변경 필요**: `config/config.py` 1개 파일만
**다른 파일**: 수정 불필요 (함수명과 반환값만 같으면 됨)

## 작업 내용

### 1. requirements.txt
```txt
pydantic-settings>=2.0.0 추가
```

### 2. .env.example 생성
환경변수 예시 파일 생성 (실제 값 없음)

### 3. config/config.py 변경
- 내부 구현만 pydantic-settings로 변경
- **함수 인터페이스는 그대로 유지**:
  - `get_url()` → str 반환
  - `get_test_nickname()` → str 반환
  - `get_stock_account()` → str 반환
  - `get_coin_account()` → str 반환
  - `get_timeout()` → int 반환
  - `get_long_timeout()` → int 반환
  - `get_download_timeout()` → int 반환
  - `get_download_dir()` → str 반환
  - `get_stock_strategy(strategy_key)` → str 반환
  - `get_coin_strategy(strategy_key)` → str 반환
  - `ENVIRONMENT` → str ("live" 또는 "staging")

## 검증 방법

### 간단한 테스트
```bash
# 1. import 테스트
python -c "from config.config import *; print('OK')"

# 2. 함수 반환값 테스트
python -c "
from config.config import *
assert isinstance(get_url(), str)
assert isinstance(get_timeout(), int)
assert ENVIRONMENT in ['live', 'staging']
print('All tests passed')
"

# 3. 기존 테스트 실행
pytest src/tests/ -v
```

## 결론

- **수정 파일**: 1개 (`config/config.py`)
- **다른 파일**: 수정 불필요
- **검증**: 테스트만 실행하면 됨
- **위험도**: 매우 낮음 (함수 인터페이스만 유지하면 됨)

