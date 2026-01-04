"""
리프레시 토큰 유효성 검사 모듈
GitHub Actions에서 사용하여 테스트 실행 전 토큰 유효성 확인
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.token_manager import refresh_google_token
from src.slack_notifier import send_slack_message
from config.config import ENVIRONMENT, get_current_env_config

def check_token_validity():
    """
    현재 환경에 맞는 리프레시 토큰의 유효성을 검사하고 결과를 반환합니다.
    
    Returns:
        bool: 토큰이 유효하면 True, 아니면 False
    """
    try:
        # 현재 환경 설정 가져오기
        config = get_current_env_config()
        current_refresh_token = config.get("google_refresh_token")
        
        print(f"현재 환경: {ENVIRONMENT}")
        print(f"리프레시 토큰 확인 중...")
        
        # Google OAuth2 토큰 갱신 시도
        tokens = refresh_google_token(current_refresh_token)
        access_token = tokens.get("access_token") if tokens else None
        
        if not access_token:
            message = f"🚨 {ENVIRONMENT} 환경의 Google 리프레시 토큰이 만료되었습니다. 자동화 테스트를 중단합니다. ❌"
            print(message)
            send_slack_message(message)
            return False
        else:
            message = f"🔑 {ENVIRONMENT} 환경의 Google 액세스 토큰 갱신 성공. 자동화 테스트를 진행합니다. ✅"
            print(message)
            send_slack_message(message)
            return True
            
    except Exception as e:
        message = f"🚨 {ENVIRONMENT} 환경 토큰 검증 중 오류 발생: {str(e)}"
        print(message)
        send_slack_message(message)
        return False

def main():
    """
    토큰 유효성을 확인하고 그 결과에 따라 스크립트 종료 코드를 반환합니다.
    GitHub Actions 워크플로우에서 이 종료 코드를 기반으로 다음 단계를 결정합니다.
    """
    # 환경 변수에서 ENVIRONMENT 확인
    if not os.getenv('ENVIRONMENT'):
        print("⚠️ ENVIRONMENT 환경 변수가 설정되지 않았습니다. 기본값 'dev'를 사용합니다.")
        os.environ['ENVIRONMENT'] = 'dev'
    
    is_valid = check_token_validity()
    
    # 토큰이 유효하지 않으면 종료 코드 1을 반환하여 워크플로우를 중단시킵니다.
    if not is_valid:
        sys.exit(1)
    
    # 토큰이 유효하면 종료 코드 0을 반환하여 워크플로우를 계속 진행합니다.
    sys.exit(0)

if __name__ == '__main__':
    main()