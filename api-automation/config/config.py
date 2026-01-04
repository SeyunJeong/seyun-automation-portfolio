import os
import json
from pathlib import Path

# 환경 변수에서 ENVIRONMENT 가져오기
ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')

# 설정 파일 경로
CONFIG_FILE = Path(__file__).parent / 'config.json'

def load_config():
    """설정 파일 로드"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {CONFIG_FILE}")

def get_current_env_config():
    """현재 환경의 설정 반환"""
    config = load_config()
    if ENVIRONMENT not in config["environments"]:
        raise ValueError(f"환경 '{ENVIRONMENT}'가 설정 파일에 없습니다.")
    return config["environments"][ENVIRONMENT]

# Slack 설정
# Slack webhook URL은 config.json 또는 환경변수에서 설정하세요
# SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"