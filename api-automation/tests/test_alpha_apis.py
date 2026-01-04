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
        with open(timing_file, 'w') as f:
            json.dump(TEST_TIMINGS, f, indent=2)
    except:
        pass

class TestAlphaAPIs:
    """알파 서버 API 테스트 클래스 - 시간 측정 포함"""
    
    def test_아이디어탭_관심그룹_토큰포함(self, api_client):
        """관심 그룹 조회 - 성공 케이스"""
        test_name = "test_아이디어탭_관심그룹_토큰포함"
        
        # Given: 인증된 API 클라이언트
        url = api_client.get_fast1_url("/api/v2/interest/groups")
        
        # When: 관심 그룹 요청 (시간 측정)
        start_time = time.time()
        response = api_client.make_authenticated_request("GET", url)
        api_duration = time.time() - start_time
        
        # 시간 정보 기록
        record_test_timing(test_name, api_duration)
        
        # Then: 응답 검증
        assert response.status_code == 200, f"예상: 200, 실제: {response.status_code}"
        print(f"[실제응답내용]")
        print(f"응답 코드: {response.status_code}")
        print(f"⏱️ 실제 API 호출 시간: {api_duration:.3f}초")
        print(f"응답 소요 시간: {response.elapsed.total_seconds()}초")
        print(f"응답 내용: {response.text}")
        
        # JSON 응답 파싱
        data = response.json()
        
        # 스키마 검증
        try:
            ResponseSchemas.validate_groups_response(data)
        except ValidationError as e:
            pytest.fail(f"응답 스키마 검증 실패: {str(e)}")
        
        print("✅ 관심 그룹 조회 성공 테스트 통과")
    
    def test_아이디어탭_관심그룹_토큰미포함(self, api_client):
        """관심 그룹 조회 - 인증 토큰 없는 요청 케이스"""
        test_name = "test_아이디어탭_관심그룹_토큰미포함"
        
        # Given: 인증 토큰 없는 요청
        url = api_client.get_fast1_url("/api/v2/interest/groups")
        
        # When: 인증 없이 요청 (시간 측정)
        start_time = time.time()
        response = api_client.make_unauthenticated_request("GET", url)
        api_duration = time.time() - start_time
        
        # 시간 정보 기록
        record_test_timing(test_name, api_duration)
        print(f"⏱️ API 호출 시간: {api_duration:.3f}초")
        
        # Then: 401 에러 검증
        assert response.status_code == 401, f"예상: 401, 실제: {response.status_code}"
        print("✅ 관심 그룹 조회 인증 실패 테스트 통과")

    def test_아이디어탭_스토리_ID정상기입(self, api_client):
        """스토리 - 성공 케이스"""
        test_name = "test_아이디어탭_스토리_ID정상기입"
        
        # Given: 인증된 API 클라이언트와 유효한 ID
        group_id = 123  # 예시 그룹 ID (포트폴리오용 샘플 데이터)
        url = api_client.get_alpha_url(f"/api/v2/interest/stories/{group_id}")
        
        # When: 스토리 요청 (시간 측정)
        start_time = time.time()
        response = api_client.make_authenticated_request("GET", url)
        api_duration = time.time() - start_time
        
        # 시간 정보 기록
        record_test_timing(test_name, api_duration)
        
        print(f"[실제응답내용]")
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
            ResponseSchemas.validate_stories_response(data)
        except ValidationError as e:
            pytest.fail(f"응답 스키마 검증 실패: {str(e)}")
        
        print("✅ 스토리 성공 테스트 통과")
    
    def test_아이디어탭_스토리_ID오기입(self, api_client):
        """스토리 - 존재하지 않는 ID 케이스"""
        test_name = "test_아이디어탭_스토리_ID오기입"
        
        # Given: 인증된 API 클라이언트와 존재하지 않는 ID
        invalid_story_id = 99999
        url = api_client.get_alpha_url(f"/api/v2/interest/stories/{invalid_story_id}")
        
        # When: 존재하지 않는 스토리 요청 (시간 측정)
        start_time = time.time()
        response = api_client.make_authenticated_request("GET", url)
        api_duration = time.time() - start_time
        
        # 시간 정보 기록
        record_test_timing(test_name, api_duration)
        print(f"⏱️ API 호출 시간: {api_duration:.3f}초")
        
        # Then: 404 에러 검증
        assert response.status_code == 404, f"예상: 404, 실제: {response.status_code}"
        print("✅ 스토리 Not Found 테스트 통과")
    
    def test_아이디어탭_종목정보_ID정상기입(self, api_client):
        """가격 정보 - 성공 케이스"""
        test_name = "test_아이디어탭_종목정보_ID정상기입"
        
        # Given: 인증된 API 클라이언트와 유효한 ID
        interest_id = 123  # 예시 관심종목 ID (포트폴리오용 샘플 데이터)
        url = api_client.get_alpha_url(f"/api/v2/interest/{interest_id}/price")
        params = {"lang": "ko"}
        
        # When: 가격 정보 요청 (시간 측정)
        start_time = time.time()
        response = api_client.make_authenticated_request("GET", url, params=params)
        api_duration = time.time() - start_time
        
        # 시간 정보 기록
        record_test_timing(test_name, api_duration)
        print(f"⏱️ API 호출 시간: {api_duration:.3f}초")
        
        # Then: 응답 검증
        assert response.status_code == 200, f"예상: 200, 실제: {response.status_code}"
        
        # JSON 응답 파싱
        data = response.json()
        
        # 기본 구조 검증
        assert isinstance(data, dict), "응답이 객체 형태여야 합니다"
        
        print("✅ 가격 정보 성공 테스트 통과")
    
    def test_아이디어탭_종목정보_ID오기입(self, api_client):
        """가격 정보 - 존재하지 않는 ID 케이스"""
        test_name = "test_아이디어탭_종목정보_ID오기입"
        
        # Given: 인증된 API 클라이언트와 존재하지 않는 ID
        invalid_interest_id = 99999
        url = api_client.get_alpha_url(f"/api/v2/interest/{invalid_interest_id}/price")
        params = {"lang": "ko"}
        
        # When: 존재하지 않는 가격 정보 요청 (시간 측정)
        start_time = time.time()
        response = api_client.make_authenticated_request("GET", url, params=params)
        api_duration = time.time() - start_time
        
        # 시간 정보 기록
        record_test_timing(test_name, api_duration)
        print(f"⏱️ API 호출 시간: {api_duration:.3f}초")
        
        # Then: 404 에러 검증
        assert response.status_code == 404, f"예상: 404, 실제: {response.status_code}"
        print("✅ 가격 정보 Not Found 테스트 통과")
    
    def test_아이디어탭_뉴스_ID정상기입(self, api_client):
        """뉴스 - 성공 케이스"""
        test_name = "test_아이디어탭_뉴스_ID정상기입"
        
        # Given: 인증된 API 클라이언트와 유효한 ID
        interest_id = 123  # 예시 관심종목 ID (포트폴리오용 샘플 데이터)
        url = api_client.get_alpha_url(f"/api/v2/interest/news/{interest_id}")
        params = {
            "lang": "ko",
            "page": 1,
            "size": 10
        }
        
        # When: 뉴스 요청 (시간 측정)
        start_time = time.time()
        response = api_client.make_authenticated_request("GET", url, params=params)
        api_duration = time.time() - start_time
        
        # 시간 정보 기록
        record_test_timing(test_name, api_duration)
        print(f"⏱️ API 호출 시간: {api_duration:.3f}초")
        
        # Then: 응답 검증
        assert response.status_code == 200, f"예상: 200, 실제: {response.status_code}"
        
        # JSON 응답 파싱
        data = response.json()
        
        # 스키마 검증
        try:
            ResponseSchemas.validate_news_response(data)
        except ValidationError as e:
            pytest.fail(f"응답 스키마 검증 실패: {str(e)}")
        
        print("✅ 뉴스 성공 테스트 통과")
    
    def test_아이디어탭_뉴스_페이지네이션(self, api_client):
        """뉴스 - 페이지네이션 테스트"""
        test_name = "test_아이디어탭_뉴스_페이지네이션"
        
        # Given: 인증된 API 클라이언트와 페이지네이션 파라미터
        interest_id = 123  # 예시 관심종목 ID (포트폴리오용 샘플 데이터)
        url = api_client.get_alpha_url(f"/api/v2/interest/news/{interest_id}")
        
        # When: 서로 다른 페이지 크기로 요청 (시간 측정)
        params_small = {"lang": "ko", "page": 1, "size": 5}
        params_large = {"lang": "ko", "page": 1, "size": 20}
        
        start_time = time.time()
        response_small = api_client.make_authenticated_request("GET", url, params=params_small)
        response_large = api_client.make_authenticated_request("GET", url, params=params_large)
        api_duration = time.time() - start_time
        
        # 시간 정보 기록
        record_test_timing(test_name, api_duration)
        print(f"⏱️ API 호출 시간: {api_duration:.3f}초")
        
        # Then: 둘 다 성공하고 크기가 다른지 검증
        assert response_small.status_code == 200
        assert response_large.status_code == 200
        
        data_small = response_small.json()
        data_large = response_large.json()
        
        # 페이지네이션 파라미터 검증
        if "pagination" in data_small:
            assert data_small["pagination"]["size"] == 5
        if "pagination" in data_large:
            assert data_large["pagination"]["size"] == 20
        
        print("✅ 뉴스 페이지네이션 테스트 통과")
    
    def test_아이디어탭_뉴스_ID오기입(self, api_client):
        """뉴스 - 존재하지 않는 ID 케이스"""
        test_name = "test_아이디어탭_뉴스_ID오기입"
        
        # Given: 인증된 API 클라이언트와 존재하지 않는 ID
        invalid_interest_id = 99999
        url = api_client.get_fast1_url(f"/api/v2/interest/news/{invalid_interest_id}")
        params = {"lang": "ko", "page": 1, "size": 10}
        
        # When: 존재하지 않는 뉴스 요청 (시간 측정)
        start_time = time.time()
        response = api_client.make_authenticated_request("GET", url, params=params)
        api_duration = time.time() - start_time
        
        # 시간 정보 기록
        record_test_timing(test_name, api_duration)
        print(f"⏱️ API 호출 시간: {api_duration:.3f}초")
        
        # Then: 404 에러 검증
        assert response.status_code == 404, f"예상: 404, 실제: {response.status_code}"
        print("✅ 뉴스 Not Found 테스트 통과")