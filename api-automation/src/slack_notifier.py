import requests
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from config.config import get_current_env_config, ENVIRONMENT

def send_slack_message(message, color="good"):
    """Slack으로 메시지 전송"""
    try:
        # 먼저 환경변수에서 직접 확인
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
        # 환경변수에 없으면 config에서 가져오기
        if not webhook_url:
            config = get_current_env_config()
            webhook_url = config.get('slack_webhook_url')
        
        print(f"🔍 웹훅 URL 확인: {webhook_url[:30]}..." if webhook_url else "❌ 웹훅 URL 없음")
        
        if not webhook_url or webhook_url == "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK":
            print("⚠️ Slack 웹훅 URL이 설정되지 않았습니다.")
            return False
        
        current_time = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%m/%d %H:%M")
        
        payload = {
            "text": f"API 테스트 알림 - {ENVIRONMENT.upper()} 환경",
            "username": "API Test Bot",
            "icon_emoji": ":robot_face:",
            "attachments": [{
                "color": color,
                "text": message,
                "fields": [{
                    "title": "환경",
                    "value": ENVIRONMENT.upper(),
                    "short": True
                }, {
                    "title": "시간", 
                    "value": current_time,
                    "short": True
                }]
            }]
        }
        
        print(f"📤 Slack 전송 시도: {webhook_url[:30]}...")
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Slack 메시지 전송 성공")
            return True
        else:
            print(f"❌ Slack 메시지 전송 실패: {response.status_code}")
            print(f"📄 응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Slack 메시지 전송 중 오류: {str(e)}")
        return False

def test_slack_connection():
    """Slack 연결 테스트"""
    message = f"🧪 Slack 연결 테스트 - {ENVIRONMENT} 환경"
    return send_slack_message(message, "warning")