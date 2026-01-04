import pytest
import sys
import time
import json
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.test_schemas import ResponseSchemas
from jsonschema import ValidationError

# 글로벌 변수로 테스트 시간 정보 저장
TEST_TIMINGS = {}

def record_test_timing(test_name, duration):
    """테스트 시간 정보 기록"""
    TEST_TIMINGS[test_name] = duration
    # 파일에도 저장
    timing_file = Path("test_timings.json")
    try:
        # 기존 파일이 있으면 로드해서 추가
        existing_timings = {}
        if timing_file.exists():
            with open(timing_file, 'r') as f:
                existing_timings = json.load(f)
        
        existing_timings[test_name] = duration
        
        with open(timing_file, 'w') as f:
            json.dump(existing_timings, f, indent=2)
    except:
        pass

EXPECTED_STRATEGY_NAMES = {
    "Strategy A - Multi Factor",
    "Strategy B - All Weather Active",
    "Strategy C - Long Short Active",
    "Strategy D - Monthly Dividend",
    "Strategy E - Global All Weather",
    "Strategy F - Index Long Short",
    "Strategy G - Sector Active"
}

class TestFastAPI1:
    """FastAPI1 서버 API 테스트 클래스"""
    
    def test_내투자탭_계좌정보_토큰포함(self, api_client):
        """내 투자 탭 - 성공 케이스"""
        test_name = "test_내투자탭_계좌정보_토큰포함"
        
        # Given: 인증된 API 클라이언트
        url = api_client.get_fastapi1_url("/trade/get_accounts")
        
        # When: 계정 정보 요청 (시간 측정)
        start_time = time.time()
        response = api_client.make_authenticated_request("POST", url)
        api_duration = time.time() - start_time
        
        # 시간 정보 기록
        record_test_timing(test_name, api_duration)
        
        print(f"\n[실제 응답 확인]")
        print(f"응답 코드: {response.status_code}")
        print(f"⏱️ 실제 API 호출 시간: {api_duration:.3f}초")
        print(f"응답 소요 시간: {response.elapsed.total_seconds()}초")
        print(f"응답 내용: {response.text}")
        
        # Then: 응답 검증
        assert response.status_code == 200, f"예상: 200, 실제: {response.status_code}"
        
        # JSON 응답 파싱
        data = response.json()
        
        # 스키마 검증
        try:
            ResponseSchemas.validate_accounts_response(data)
        except ValidationError as e:
            pytest.fail(f"응답 스키마 검증 실패: {str(e)}")
        
        print("✅ 내 투자 탭 성공 테스트 통과")
    
    def test_내투자탭_계좌정보_토큰미포함(self, api_client):
        """내 투자 탭 - 인증 토큰 없는 요청 케이스"""
        test_name = "test_내투자탭_계좌정보_토큰미포함"
        
        # Given: 인증 토큰 없는 요청
        url = api_client.get_fastapi1_url("/trade/get_accounts")
        
        # When: 인증 없이 요청 (시간 측정)
        start_time = time.time()
        response = api_client.make_unauthenticated_request("POST", url)
        api_duration = time.time() - start_time
        
        # 시간 정보 기록
        record_test_timing(test_name, api_duration)
        print(f"⏱️ API 호출 시간: {api_duration:.3f}초")
        
        # Then: 400 에러 검증
        assert response.status_code == 400, f"예상: 400, 실제: {response.status_code}"
        
        print("✅ 내 투자 탭 인증 실패 테스트 통과")

    def test_전략탭_주식프라임전략_토큰포함(self, api_client):
        """전략 탭 - 성공 케이스 (이름 목록 검증)"""
        test_name = "test_전략탭_주식프라임전략_토큰포함"
        
        # Given: 인증된 API 클라이언트
        # 이 URL은 주식 전략만 반환하므로, 검증 대상도 주식 전략 목록이어야 합니다.
        url = api_client.get_fastapi1_url("/prime/stock_prime_strategies")
        
        # When: 전략 정보 요청 (시간 측정)
        start_time = time.time()
        response = api_client.make_authenticated_request("POST", url)
        api_duration = time.time() - start_time
        
        # 시간 정보 기록
        record_test_timing(test_name, api_duration)
        print(f"⏱️ API 호출 시간: {api_duration:.3f}초")

        # Then: 응답 검증
        assert response.status_code == 200, f"예상: 200, 실제: {response.status_code}"
        
        strategies_list = response.json()
        
        # --- 이름 목록 비교 검증 로직 ---
        
        # 1. 실제 응답에서 'strategy_name'만 모두 추출하여 set으로 만듭니다.
        extracted_names = {strategy['strategy_name'] for strategy in strategies_list}
        
        # 2. 예상 이름 목록과 실제 응답의 이름 목록이 정확히 일치하는지 검증합니다.
        assert extracted_names == EXPECTED_STRATEGY_NAMES, "전략 이름 목록이 예상과 다릅니다."
        
        print("✅ 전략 탭 이름 목록 검증 테스트 통과")
        
    
    def test_전략탭_주식프라임전략_토큰미포함(self, api_client):
        """전략 탭 - 인증 토큰 없는 요청 케이스"""
        test_name = "test_전략탭_주식프라임전략_토큰미포함"
        
        # Given: 인증 토큰 없는 요청
        url = api_client.get_fastapi1_url("/prime/stock_prime_strategies")
        
        # When: 인증 없이 요청 (시간 측정)
        start_time = time.time()
        response = api_client.make_unauthenticated_request("POST", url)
        api_duration = time.time() - start_time
        
        # 시간 정보 기록
        record_test_timing(test_name, api_duration)
        print(f"⏱️ API 호출 시간: {api_duration:.3f}초")
        
        # Then: 401 에러 검증
        assert response.status_code == 200, f"예상: 200, 실제: {response.status_code}"
        
        print("✅ 전략 탭 인증 실패 테스트 통과")

    
    # def test_get_notice_success(self, api_client):
    #     """공지사항 - 성공 케이스"""
    #     # Given: 인증된 API 클라이언트
    #     url = api_client.get_fastapi1_url("/admin/notice")
        
    #     # When: 공지사항 요청
    #     response = api_client.make_authenticated_request("GET", url)
        
    #     # Then: 응답 검증
    #     assert response.status_code == 200, f"예상: 200, 실제: {response.status_code}"
        
    #     # JSON 응답 파싱
    #     data = response.json()
        
    #     # 스키마 검증
    #     try:
    #         ResponseSchemas.validate_notice_response(data)
    #     except ValidationError as e:
    #         pytest.fail(f"응답 스키마 검증 실패: {str(e)}")
        
    #     print("✅ 공지사항 성공 테스트 통과")
    
    # def test_get_notice_unauthorized(self, api_client):
    #     """공지사항 - 인증 실패 케이스"""
    #     # Given: 인증 토큰 없는 요청
    #     url = api_client.get_fastapi1_url("/admin/notice")
        
    #     # When: 인증 없이 요청
    #     response = api_client.make_unauthenticated_request("GET", url)
        
    #     # Then: 401 에러 검증
    #     assert response.status_code == 401, f"예상: 401, 실제: {response.status_code}"
        
    #     print("✅ 공지사항 인증 실패 테스트 통과")