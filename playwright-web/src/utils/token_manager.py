import requests
import urllib3
# SSL 인증서 검증 비활성화 및 경고 억제
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import sys

def refresh_google_token(refresh_token):
    """
    리프레시 토큰을 사용하여 새 액세스 토큰을 획득하는 함수
    """
    CLIENT_ID = 'YOUR-CLIENT-ID.apps.googleusercontent.com'
    CLIENT_SECRET = 'YOUR-CLIENT-SECRET'
    
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    
    try:
        # 검증 없이 요청 (테스트 환경에서만 사용)
        token_response = requests.post(token_url, data=token_data, verify=False)
        
        if token_response.status_code != 200:
            print(f"오류: 액세스 토큰을 갱신하지 못했습니다. 서버 응답: {token_response.text}", file=sys.stderr)
            return None
        
        return token_response.json()
    
    except Exception as e:
        print(f"오류 발생: {str(e)}", file=sys.stderr)
        return None