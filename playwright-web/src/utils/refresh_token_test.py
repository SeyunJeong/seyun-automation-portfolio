"""
리프레시 토큰 유효성 검사 모듈
GitHub Actions에서 사용하여 테스트 실행 전 토큰 유효성 확인
"""
import sys
import os
# 상대 경로로 import 수정
from .token_manager import refresh_google_token
from .slack_notifier import send_slack_message
from config.config import ENVIRONMENT

# 환경별 리프레시 토큰 설정 (포트폴리오용 - 실제 사용 시 환경변수로 설정하세요)
REFRESH_TOKENS = {
    "live": "YOUR-GOOGLE-REFRESH-TOKEN-LIVE",
    "staging": "YOUR-GOOGLE-REFRESH-TOKEN-STAGING"
}

def check_token_validity():
    """
    현재 환경에 맞는 리프레시 토큰의 유효성을 검사하고 결과를 반환합니다.
    
    Returns:
        bool: 토큰이 유효하면 True, 아니면 False
    """
    # 현재 환경에 맞는 토큰 선택
    current_refresh_token = REFRESH_TOKENS.get(ENVIRONMENT)
    
    print(f"현재 환경: {ENVIRONMENT}")
    print(f"리프레시 토큰 확인 중: {current_refresh_token}")
    
    tokens = refresh_google_token(current_refresh_token)
    access_token = tokens.get("access_token") if tokens else None
    
    if not access_token:
        message = f"🚨 {ENVIRONMENT} 환경의 리프레시 토큰이 만료되었습니다. 자동화 테스트를 중단합니다. ❌"
        print(message)
        send_slack_message(message)
        return False
    else:
        message = f"🔑 {ENVIRONMENT} 환경의 구글 엑세스 토큰 갱신 성공. 자동화 테스트를 진행합니다."
        print(message)
        send_slack_message(message)
        return True

def main():
    """
    토큰 유효성을 확인하고 그 결과에 따라 스크립트 종료 코드를 반환합니다.
    GitHub Actions 워크플로우에서 이 종료 코드를 기반으로 다음 단계를 결정합니다.
    """
    is_valid = check_token_validity()
    
    # 토큰이 유효하지 않으면 종료 코드 1을 반환하여 워크플로우를 중단시킵니다.
    if not is_valid:
        sys.exit(1)
    
    # 토큰이 유효하면 종료 코드 0을 반환하여 워크플로우를 계속 진행합니다.
    sys.exit(0)

if __name__ == '__main__':
    main() 
