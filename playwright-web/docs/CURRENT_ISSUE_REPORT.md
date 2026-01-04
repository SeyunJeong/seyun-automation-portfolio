# 현재 문제 상황 보고서

## 📋 진행 상황

### 완료된 작업
1. ✅ 가상환경 생성 (`venv`)
2. ✅ `requirements.txt`에 `pydantic-settings>=2.0.0` 추가
3. ✅ `.env.live`, `.env.stg` 파일 생성
4. ✅ `config/config.py`를 pydantic-settings로 변경 시도
5. ✅ 기본값 제거 (필수 필드로 설정)

### 현재 코드 상태
- `config/config.py`: pydantic-settings 클래스 구조로 변경 완료
- 함수 인터페이스: 11개 함수 모두 유지 (하위 호환성)
- `.env.live`, `.env.stg`: 환경별 파일 생성 완료

## 🐛 발생한 문제

### 문제 1: ENVIRONMENT 상수 초기화 실패
**증상**:
```python
# 모듈 로드 시점에 ENVIRONMENT 상수 초기화 시도
ENVIRONMENT = get_common_settings().environment  # ❌ 에러 발생
```

**에러 메시지**:
```
pydantic_core._pydantic_core.ValidationError: 4 validation errors for CommonSettings
timeout
  Field required [type=missing, input_value={'environment': 'staging'}, input_value=dict]
long_timeout
  Field required [type=missing, ...]
download_timeout
  Field required [type=missing, ...]
download_dir
  Field required [type=missing, ...]
```

**원인 분석**:
1. 모듈 로드 시점에 `ENVIRONMENT = get_common_settings().environment` 실행
2. `get_common_settings()` 내부에서 `load_dotenv(env_file, override=True)` 호출
3. `load_dotenv`는 정상 작동 (환경변수 로드 확인됨)
4. 하지만 `CommonSettings()` 생성 시점에 pydantic-settings가 환경변수를 읽지 못함
5. `input_value={'environment': 'staging'}`만 보이고 나머지 필드(timeout 등)는 없음

### 문제 2: pydantic-settings가 환경변수를 읽지 못함
**확인 사항**:
- ✅ `load_dotenv('.env.stg', override=True)` 호출 후 `os.getenv('TIMEOUT')` → `'30000'` 정상
- ✅ 단독 테스트에서 `TestSettings()` 생성 성공
- ❌ `get_common_settings()` 내부에서 `CommonSettings()` 생성 실패

**가설**:
- `load_dotenv`는 `os.environ`을 업데이트하지만, pydantic-settings가 읽는 시점의 문제일 수 있음
- 또는 `get_common_settings()` 내부의 로직 순서 문제

## 🔍 시도한 해결책

### 시도 1: 프록시 객체로 ENVIRONMENT 제공
```python
class _EnvironmentProxy:
    def __str__(self):
        return _get_environment_value()
    def __eq__(self, other):
        return _get_environment_value() == other
```
**결과**: ❌ 여전히 모듈 로드 시점 초기화 문제 발생

### 시도 2: 모듈 로드 시점에 환경 파일 로드
```python
# 모듈 최상단
load_dotenv(".env.live", override=False)
```
**결과**: ❌ staging 환경에서 live 값이 로드됨

### 시도 3: get_common_settings() 내부에서 load_dotenv 호출
```python
def get_common_settings():
    env = os.getenv("ENVIRONMENT", "live")
    env_file = f".env.{env}"
    load_dotenv(env_file, override=True)  # ✅ 여기서는 정상 작동
    return CommonSettings()  # ❌ 여기서 실패
```
**결과**: ❌ `load_dotenv`는 성공하지만 `CommonSettings()` 생성 실패

## 💡 현재 상황 요약

### 정상 작동하는 부분
1. ✅ `load_dotenv('.env.stg', override=True)` → 환경변수 정상 로드
2. ✅ 단독 테스트에서 `TestSettings()` 생성 성공
3. ✅ Live 환경에서 기본 동작 (환경변수 없을 때)

### 문제가 있는 부분
1. ❌ `get_common_settings()` 내부에서 `CommonSettings()` 생성 실패
2. ❌ ENVIRONMENT 상수 모듈 로드 시점 초기화 실패
3. ❌ Staging 환경에서 테스트 시 필수 필드 누락 에러

## 🤔 의문점

1. **왜 `load_dotenv`는 성공하는데 `CommonSettings()`는 실패할까?**
   - `os.getenv('TIMEOUT')` → 정상
   - `CommonSettings()` → 필수 필드 누락

2. **pydantic-settings가 환경변수를 읽는 시점은?**
   - `BaseSettings` 생성 시점에 `os.environ`을 읽는지 확인 필요

3. **`get_common_settings()` 내부에서 `load_dotenv` 후 바로 `CommonSettings()` 생성하는데 왜 실패할까?**
   - 타이밍 문제? 캐싱 문제?

## 🎯 다음 단계 제안

1. **디버깅**: `get_common_settings()` 내부에서 환경변수 상태 확인
2. **대안 검토**: pydantic-settings의 `env_file` 파라미터 사용 방법 재확인
3. **간단한 해결책**: ENVIRONMENT 상수를 함수로 제공하거나, 모듈 로드 시점 초기화 포기

