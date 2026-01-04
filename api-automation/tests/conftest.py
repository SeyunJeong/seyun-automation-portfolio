import pytest
import sys
import os
from pathlib import Path
from src.slack_notifier import send_slack_message
from config.config import ENVIRONMENT

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config import get_current_env_config, ENVIRONMENT
from src.api_client import APIClient

def pytest_addoption(parser):
    """pytest 명령줄 옵션 추가"""
    parser.addoption(
        "--env", 
        action="store", 
        default="dev",
        help="테스트 환경 선택: dev, staging, live"
    )

@pytest.fixture(scope="session")
def config(request):
    """설정 파일 로드 및 환경 설정"""
    env = request.config.getoption("--env")
    
    # 환경 변수 설정
    os.environ['ENVIRONMENT'] = env
    
    # 설정 반환
    return get_current_env_config()

@pytest.fixture(scope="session")
def api_client(config):
    """API 클라이언트 인스턴스 생성 및 토큰 발급"""
    client = APIClient(config)
    # 세션 시작 시 토큰 자동 발급
    client.refresh_access_token()
    return client

@pytest.fixture(scope="session", autouse=True)
def test_environment_info(config):
    """테스트 환경 정보 출력"""
    print(f"\n🌐 테스트 환경: {ENVIRONMENT}")
    print(f"📍 Fast1 URL: {config['fast1_base_url']}")
    print(f"📍 Fast2 URL: {config['fast2_base_url']}")

import pytest
from src.slack_notifier import send_slack_message
from config.config import ENVIRONMENT

class TestResultCollector:
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            # 실패 이유 추출 (타임아웃 우선 처리)
            failure_reason = None
            if report.failed and report.longrepr:
                failure_text = str(report.longrepr)
                
                # 타임아웃 에러 우선 검사
                if "요청 시간 초과" in failure_text:
                    for line in failure_text.split('\n'):
                        if "요청 시간 초과" in line:
                            failure_reason = line.strip()
                            break
                
                # 연결 에러 검사
                elif "ConnectionError" in failure_text or "HTTPSConnectionPool" in failure_text:
                    failure_reason = "🌐 서버 연결 실패"
                
                # AssertionError 검사
                elif "AssertionError" in failure_text:
                    for line in failure_text.split('\n'):
                        if 'assert' in line and ('예상:' in line or '실제:' in line):
                            failure_reason = line.strip()
                            break
                
                # 기타 에러 검사
                else:
                    for line in failure_text.split('\n'):
                        if any(keyword in line for keyword in ['Error:', 'Exception:', 'Failed:']):
                            failure_reason = line.strip()
                            break
            
            self.results.append({
                'name': report.nodeid.split("::")[-1],
                'status': 'PASS' if report.passed else 'FAIL' if report.failed else 'SKIP',
                'duration': getattr(report, 'duration', 0),
                'failure_reason': failure_reason
            })

    def pytest_sessionstart(self, session):
        from datetime import datetime
        self.start_time = datetime.now()

    def pytest_sessionfinish(self, session):
        print("✅ conftest.py: 세션 완료 처리")


@pytest.fixture(scope="session", autouse=True)
def test_result_collector():
    collector = TestResultCollector()
    return collector

def pytest_configure(config):
    config.pluginmanager.register(TestResultCollector(), "test_result_collector")