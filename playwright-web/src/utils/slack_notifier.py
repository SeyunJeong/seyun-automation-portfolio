import requests

# Slack 설정 (포트폴리오용 - 실제 사용 시 환경변수로 설정하세요)
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"

class SlackNotifier:
    """Slack 메시지 전송을 위한 클래스"""
    
    def __init__(self, webhook_url=SLACK_WEBHOOK_URL):
        """
        SlackNotifier 초기화
        
        Args:
            webhook_url: Slack 웹훅 URL (기본값: 환경 변수 또는 기본 URL)
        """
        self.webhook_url = webhook_url
    
    def send_message(self, message):
        """
        Slack 메시지 전송
        
        Args:
            message: 전송할 메시지
        """
        payload = {
            "text": message
        }
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error sending message to Slack: {e}")
            return False

def send_slack_message(message):
    payload = {
        "text": message
    }
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Slack: {e}")

# 저장 안하고 싶을 때
# git update-index --skip-worktree slack_notifier.py
# 저장 다시 하고 싶을 때
# git update-index --no-skip-worktree slack_notifier.py