"""
GitHub Actions용 API 헬스 모니터링
테스트에서 생성한 타이밍 파일을 사용하는 버전
"""
import json
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
import subprocess
import time

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.slack_notifier import send_slack_message
from config.config import ENVIRONMENT

class GitHubHealthMonitor:
    def __init__(self):
        self.data_dir = Path("./data")
        self.data_dir.mkdir(exist_ok=True)
        self.results_file = self.data_dir / f"health_results_{ENVIRONMENT}.json"
        self.timing_file = Path("test_timings.json")
        
    def load_existing_data(self):
        """기존 데이터 로드"""
        if self.results_file.exists():
            try:
                with open(self.results_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"test_runs": []}
    
    def load_test_timings(self):
        """테스트에서 생성한 타이밍 파일 로드"""
        if self.timing_file.exists():
            try:
                with open(self.timing_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def run_tests_and_collect(self):
        """테스트 실행 및 타이밍 파일 활용"""
        print(f"🔍 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - API 헬스 체크 시작")
        
        # 기존 타이밍 파일 삭제 (새로운 측정을 위해)
        if self.timing_file.exists():
            self.timing_file.unlink()
        
        # pytest 실행 (간단한 옵션만 사용)
        total_start_time = time.time()
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/", f"--env={ENVIRONMENT}",
            "-v", "--tb=short", "--durations=10"  # 상위 10개만
        ], capture_output=True, text=True)
        total_execution_time = time.time() - total_start_time
        
        print(f"📊 pytest 실행 결과: {result.returncode} (총 소요시간: {total_execution_time:.2f}s)")
        
        # 타이밍 정보 로드
        test_timings = self.load_test_timings()
        print(f"⏱️ 타이밍 파일에서 {len(test_timings)}개 테스트 시간 정보 로드")
        
        # 결과 파싱 및 저장
        self.parse_and_save_with_timings(result, total_execution_time, test_timings)
        
        return result.returncode == 1

    def parse_and_save_with_timings(self, result, total_execution_time, test_timings):
        """타이밍 파일을 활용한 결과 파싱"""
        stdout_lines = result.stdout.split('\n')
        stderr_lines = result.stderr.split('\n') if result.stderr else []
        
        # 기존 데이터 로드
        existing_data = self.load_existing_data()
        
        run_info = {
            "timestamp": datetime.now().isoformat(),
            "environment": ENVIRONMENT,
            "total_execution_time": total_execution_time,
            "tests": []
        }
        
        print("🔍 pytest 출력에서 테스트 결과 파싱 중...")
        
        # 테스트 결과 파싱
        for line in stdout_lines:
            if "::" in line and (" PASSED" in line or " FAILED" in line):
                try:
                    # 테스트 이름 및 상태 추출
                    parts = line.split("::")
                    if len(parts) >= 2:
                        last_part = parts[-1]
                        if " PASSED" in last_part:
                            test_name = last_part.split(" PASSED")[0].strip()
                            status = "passed"
                        elif " FAILED" in last_part:
                            test_name = last_part.split(" FAILED")[0].strip()
                            status = "failed"
                        else:
                            continue
                        
                        # 타이밍 파일에서 실제 API 호출 시간 가져오기
                        duration = test_timings.get(test_name, 0.0)
                        
                        # 실패 사유 추출
                        failure_reason = None
                        if status == "failed":
                            failure_reason = self.extract_failure_reason_from_output(stdout_lines, stderr_lines, test_name)
                        
                        test_info = {
                            "name": test_name,
                            "status": status,
                            "duration": round(duration, 3),
                            "api_endpoint": self.extract_api_endpoint_from_test_name(test_name),
                            "failure_reason": failure_reason
                        }
                        
                        run_info["tests"].append(test_info)
                        print(f"  {'✅' if status == 'passed' else '❌'} {test_name} - {status} ({duration:.3f}s)")
                        
                except Exception as e:
                    print(f"  ⚠️ 파싱 오류: {line} - {e}")
                    continue
        
        # 저장 및 알림
        self.save_and_notify(existing_data, run_info)

    def save_and_notify(self, existing_data, run_info):
        """결과 저장 및 알림"""
        # 누적 데이터에 추가
        existing_data["test_runs"].append(run_info)
        
        # 7일 이상 된 데이터 정리
        cutoff_date = datetime.now() - timedelta(days=7)
        existing_data["test_runs"] = [
            run for run in existing_data["test_runs"]
            if datetime.fromisoformat(run["timestamp"]) > cutoff_date
        ]
        
        # 파일에 저장
        try:
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            print(f"✅ 결과 저장 완료: {len(run_info['tests'])}개 테스트")
        except Exception as e:
            print(f"❌ 결과 저장 실패: {e}")
            return
        
        # 즉시 Slack 알림
        self.send_immediate_slack_notification(run_info)

    def extract_failure_reason_from_output(self, stdout_lines, stderr_lines, test_name):
        """실패 사유 추출"""
        all_lines = stdout_lines + stderr_lines
        
        for line in all_lines:
            if test_name in line:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in ['timeout', '시간 초과', 'timed out']):
                    return "⏰ 타임아웃"
                elif any(keyword in line_lower for keyword in ['connection', '연결 실패', 'network']):
                    return "🌐 연결 실패"
                elif '401' in line:
                    return "🔐 인증 실패"
                elif '404' in line:
                    return "🔍 리소스 없음"
                elif '500' in line:
                    return "💥 서버 오류"
                elif 'assertionerror' in line_lower:
                    return "❌ 응답 오류"
        
        return "15초 내로 응답 오지 않음"

    def extract_api_endpoint_from_test_name(self, test_name):
        """테스트 이름에서 API 엔드포인트 추출"""
        endpoint_map = {
            # FastAPI2 엔드포인트
            "test_아이디어탭_관심그룹_토큰포함": "/api/v2/interest/groups",
            "test_아이디어탭_관심그룹_토큰미포함": "/api/v2/interest/groups",
            "test_아이디어탭_스토리_ID정상기입": "/api/v2/interest/stories",
            "test_아이디어탭_스토리_ID오기입": "/api/v2/interest/stories",
            "test_아이디어탭_종목정보_ID정상기입": "/api/v2/interest/price",
            "test_아이디어탭_종목정보_ID오기입": "/api/v2/interest/price",
            "test_아이디어탭_뉴스_ID정상기입": "/api/v2/interest/news",
            "test_아이디어탭_뉴스_페이지네이션": "/api/v2/interest/news",
            "test_아이디어탭_뉴스_ID오기입": "/api/v2/interest/news",

            # FastAPI1 엔드포인트
            "test_내투자탭_계좌정보_토큰포함": "/trade/get_accounts",
            "test_내투자탭_계좌정보_토큰미포함": "/trade/get_accounts",
            "test_전략탭_주식프라임전략_토큰포함": "/prime/stock_prime_strategies",
            "test_전략탭_주식프라임전략_토큰미포함": "/prime/stock_prime_strategies",
        }
        
        return endpoint_map.get(test_name, "Unknown")

    def send_immediate_slack_notification(self, run_info):
        """즉시 Slack 알림 전송"""
        passed = len([t for t in run_info["tests"] if t["status"] == "passed"])
        failed = len([t for t in run_info["tests"] if t["status"] == "failed"])
        total = len(run_info["tests"])
        
        current_time = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%m/%d %H:%M")
        
        if total == 0:
            message = f"API 헬스 체크 - {ENVIRONMENT} 환경 ({current_time})\n테스트 결과 없음"
            send_slack_message(message, "warning")
            return
        
        # 전체 소요시간 계산
        total_test_duration = sum(t.get("duration", 0) for t in run_info["tests"])
        total_execution_time = run_info.get("total_execution_time", 0)
        
        # 메시지 헤더
        if failed == 0:
            message = f"API 헬스 체크 - {ENVIRONMENT} 환경 ({current_time})\n"
            message += f"모든 테스트 성공: {passed}/{total}\n"
            message += f"총 실행시간: {total_execution_time:.2f}s, API 호출 시간: {total_test_duration:.3f}s\n\n"
            color = "good"
        else:
            message = f"API 헬스 체크 - {ENVIRONMENT} 환경 ({current_time})\n"
            message += f"성공: {passed}/{total}, 실패: {failed}개\n"
            message += f"총 실행시간: {total_execution_time:.2f}s, API 호출 시간: {total_test_duration:.3f}s\n\n"
            color = "danger"
        
        # 실패한 테스트 우선 정렬
        sorted_tests = sorted(run_info["tests"], key=lambda x: (x["status"] != "failed", x["name"]))
        
        # 테스트별 상세 정보
        message += "테스트 상세 결과:\n"
        for test in sorted_tests:
            test_result = "[Pass]" if test["status"] == "passed" else "[Fail]"
            api_endpoint = test.get("api_endpoint", "Unknown")
            
            if test["status"] == "passed":
                duration = test.get("duration", 0)
                message += f"{test_result} {test['name']} ({api_endpoint}) - {duration:.3f}s"
            else:
                message += f"{test_result} {test['name']} ({api_endpoint})"
            
            if test["status"] == "failed" and test.get("failure_reason"):
                message += f" | [{test['failure_reason']}]"
            
            message += "\n"
        
        send_slack_message(message, color)

def main():
    monitor = GitHubHealthMonitor()
    success = monitor.run_tests_and_collect()
    
    if success:
        print("✅ 헬스 체크 완료")
    else:
        print("⚠️ 헬스 체크 실패")
        
    return success

if __name__ == "__main__":
    main()