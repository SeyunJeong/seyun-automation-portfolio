import requests
import json
import pytest
from typing import Dict, Any, Optional
from .token_manager import refresh_google_token

class APIClient:
    """API 요청을 관리하는 중앙 클래스"""
    
    def __init__(self, config: Dict[str, str]):
        """
        API 클라이언트 초기화
        
        Args:
            config: 환경별 설정 정보 (base_url, google_refresh_token 포함)
        """
        self.fastapi1_base_url = config["fastapi1_base_url"]
        self.fastapi2_base_url = config["fastapi2_base_url"]
        self.google_refresh_token = config["google_refresh_token"]
        self.access_token = None
        self.session = requests.Session()
        
        # 공통 헤더 설정
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'API-Test-Suite/1.0',
            'Sns-type': 'google',
            'Client-type': 'api-client'
        })
    
    def refresh_access_token(self) -> str:
        """
        Google OAuth2 리프레시 토큰을 사용하여 새 액세스 토큰 발급
        
        Returns:
            발급받은 액세스 토큰
            
        Raises:
            Exception: 토큰 발급 실패 시
        """
        try:
            token_data = refresh_google_token(self.google_refresh_token)
            
            if not token_data:
                raise Exception("토큰 갱신 함수에서 None 반환")
            
            self.access_token = token_data.get("access_token")
            
            if not self.access_token:
                raise Exception("응답에서 access_token을 찾을 수 없습니다.")
            
            # 세션 헤더에 Authorization 추가
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
            
            print(f"✅ Google 액세스 토큰 발급 성공")
            return self.access_token
            
        except Exception as e:
            raise Exception(f"토큰 발급 실패: {str(e)}")
    
    def make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        모든 API 요청을 실행하는 핵심 메서드
        """
        kwargs.setdefault('timeout', 15)

        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except requests.exceptions.Timeout:
            # 타임아웃 에러 메시지 개선
            timeout_val = kwargs.get('timeout', 15)
            pytest.fail(f"⏰ 요청 시간 초과 ({timeout_val}초): {method} {url}", pytrace=False)
        except requests.exceptions.ConnectionError:
            # 연결 에러 메시지 개선  
            pytest.fail(f"🌐 서버 연결 실패: {method} {url}", pytrace=False)
        except requests.exceptions.RequestException as e:
            # 기타 요청 에러
            pytest.fail(f"❌ API 요청 실패: {e}", pytrace=False)
    
    def get_fastapi1_url(self, endpoint: str) -> str:
        """FastAPI1 서버 전체 URL 생성"""
        return f"{self.fastapi1_base_url}{endpoint}"

    def get_fastapi2_url(self, endpoint: str) -> str:
        """FastAPI2 서버 전체 URL 생성"""
        return f"{self.fastapi2_base_url}{endpoint}"
    
    def make_authenticated_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        인증이 필요한 API 요청 실행
        토큰이 만료된 경우 자동으로 갱신 시도
        
        Args:
            method: HTTP 메서드
            url: 요청 URL
            **kwargs: requests 라이브러리 추가 인자
            
        Returns:
            응답 객체
        """
        response = self.make_request(method, url, **kwargs)
        
        # 401 에러 시 토큰 갱신 후 재시도
        if response.status_code == 401:
            print("🔄 토큰 만료, 갱신 후 재시도...")
            self.refresh_access_token()
            response = self.make_request(method, url, **kwargs)
        
        return response
    
    def make_unauthenticated_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        인증 없이 API 요청 실행 (실패 테스트용)
        
        Args:
            method: HTTP 메서드
            url: 요청 URL
            **kwargs: requests 라이브러리 추가 인자
            
        Returns:
            응답 객체
        """
        # 임시로 Authorization 헤더 제거
        temp_auth = None
        if 'Authorization' in self.session.headers:
            temp_auth = self.session.headers.pop('Authorization')
        
        try:
            response = self.make_request(method, url, **kwargs)
            return response
        finally:
            # Authorization 헤더 복원
            if temp_auth:
                self.session.headers['Authorization'] = temp_auth