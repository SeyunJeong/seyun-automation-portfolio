import pytest
import os
import json
from datetime import datetime
from src.slack_notifier import send_slack_message

def load_slack_webhook_from_config():
    """config/config.json 파일에서 설정을 읽어와 슬랙 웹훅 URL을 환경 변수로 등록합니다."""
    try:
        with open('config/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        env_config = config['environments']['dev']
        os.environ['SLACK_WEBHOOK_URL'] = env_config.get('slack_webhook_url')
        print("✅ config.json에서 설정 로드 완료")
        return True
    except (FileNotFoundError, KeyError) as e:
        print(f"❌ config.json 파일 처리 중 오류 발생: {e}")
        return False

class InMemoryReport:
    """pytest 테스트 결과를 파일에 쓰지 않고 메모리에 저장하는 간단한 플러그인."""
    def __init__(self):
        self.tests = []
        self.summary = {}

    def pytest_runtest_logreport(self, report):
        """각 테스트가 끝날 때마다 호출되어 결과를 저장합니다."""
        if report.when == 'call':
            self.tests.append({
                'name': report.nodeid.split('::')[-1], # 테스트 함수 이름만 추출
                'outcome': report.outcome,
                'duration': report.duration
            })

    def pytest_sessionfinish(self, session):
        """모든 테스트가 끝난 후 요약 정보를 저장합니다."""
        self.summary = {
            'total': session.testscollected,
            'passed': session.testsfailed,
            'failed': session.testscollected - session.testsfailed,
        }

def run_local_test():
    """로컬에서 전체 API 테스트를 실행하고, 결과를 파일 저장 없이 슬랙으로 전송합니다."""
    if not load_slack_webhook_from_config():
        print("⚠️ 슬랙 웹훅 URL을 로드할 수 없어 알림 전송이 불가합니다.")

    start_time = datetime.now()
    print(f"🔍 {start_time.strftime('%Y-%m-%d %H:%M:%S')} - API 헬스 체크 시작")

    # --- 1. 테스트 실행 (메모리 내 리포트 플러그인 사용) ---
    in_memory_report = InMemoryReport()
    # JSON 리포트 관련 인자들을 모두 제거하여 에러를 해결했습니다.
    exit_code = pytest.main(['-v'], plugins=[in_memory_report])
    print(f"📊 pytest 실행 결과: {exit_code}")

    # --- 2. 슬랙 메시지 포맷팅 (메모리에서 직접 데이터 사용) ---
    print("🔍 테스트 결과 정리 중...")
    summary = in_memory_report.summary
    total_tests = summary.get('total', 0)
    # Pytest의 testsfailed는 실패한 테스트의 수를 의미합니다.
    failed_count = summary.get('passed',0) 
    passed_count = summary.get('failed', 0)
    
    # 전체 실행 시간 계산
    total_duration = sum(test['duration'] for test in in_memory_report.tests)

    message_parts = [
        f"--- *로컬 API 테스트 결과* ---",
        f"결과: *{'✅ 테스트 통과' if failed_count == 0 else '❌ 일부 테스트 실패'}*",
        f"- *전체*: {total_tests}개",
        f"- *성공*: {passed_count}개",
        f"- *실패*: {failed_count}개",
        f"- *실행시간*: {total_duration:.2f}초",
        "\n*상세 결과 (호출 시간):*"
    ]

    for test in in_memory_report.tests:
        icon = '✅' if test['outcome'] == 'passed' else '❌'
        message_parts.append(f"  {icon} {test['name']} - {test['outcome']} ({test['duration']:.2f}s)")
    
    final_message = "\n".join(message_parts)
    print("\n--- 전송할 메시지 ---")
    print(final_message)
    print("---------------------\n")

    # --- 3. 슬랙 알림 전송 ---
    send_slack_message(final_message)
    print("✅ 슬랙 알림 전송 완료!")

if __name__ == "__main__":
    run_local_test()