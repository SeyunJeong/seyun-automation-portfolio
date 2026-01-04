"""
일일 리포트 생성 스크립트
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.slack_notifier import send_slack_message
from config.config import ENVIRONMENT

def generate_daily_report():
    """24시간 상세 리포트 생성"""
    data_file = Path(f"./data/health_results_{ENVIRONMENT}.json")
    
    if not data_file.exists():
        print("❌ 데이터 파일이 없습니다.")
        return
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # 지난 24시간 데이터 필터링
    yesterday = datetime.now() - timedelta(days=1)
    recent_runs = [
        run for run in data["test_runs"]
        if datetime.fromisoformat(run["timestamp"]) > yesterday
    ]
    
    if not recent_runs:
        message = f"❌ {ENVIRONMENT} 환경 - 최근 24시간 데이터가 없습니다."
        send_slack_message(message, "warning")
        return
    
    # 상세 통계 계산
    api_stats = defaultdict(lambda: {'total': 0, 'failed': 0, 'failures': defaultdict(int)})
    hourly_stats = defaultdict(lambda: {'total': 0, 'failed': 0})
    
    for run in recent_runs:
        # 시간대별 통계
        hour = datetime.fromisoformat(run["timestamp"]).hour
        
        for test in run["tests"]:
            endpoint = test["api_endpoint"]
            
            # API별 통계
            api_stats[endpoint]['total'] += 1
            hourly_stats[hour]['total'] += 1
            
            if test["status"] == "failed":
                api_stats[endpoint]['failed'] += 1
                hourly_stats[hour]['failed'] += 1
                
                reason = test.get("failure_reason", "❌ 테스트 실패")
                api_stats[endpoint]['failures'][reason] += 1
    
    # 실패율 계산 및 정렬
    failure_rates = []
    for endpoint, stats in api_stats.items():
        if stats['total'] > 0:
            failure_rate = (stats['failed'] / stats['total']) * 100
            failure_rates.append((endpoint, failure_rate, stats))
    
    failure_rates.sort(key=lambda x: x[1], reverse=True)
    
    # 전체 통계
    total_tests = sum(stats['total'] for stats in api_stats.values())
    total_failures = sum(stats['failed'] for stats in api_stats.values())
    overall_success_rate = ((total_tests - total_failures) / total_tests * 100) if total_tests > 0 else 0
    
    # 가장 불안정한 시간대 찾기
    worst_hour = None
    worst_failure_rate = 0
    for hour, stats in hourly_stats.items():
        if stats['total'] > 0:
            failure_rate = (stats['failed'] / stats['total']) * 100
            if failure_rate > worst_failure_rate:
                worst_failure_rate = failure_rate
                worst_hour = hour
    
    # 리포트 메시지 생성
    total_runs = len(recent_runs)
    report = f"""
📊 일일 API 헬스 리포트 - {ENVIRONMENT.upper()} 환경

🔍 24시간 종합 현황:
- 총 모니터링 횟수: {total_runs}회
- 전체 테스트 수: {total_tests}개
- 전체 성공률: {overall_success_rate:.1f}%
- 총 실패 수: {total_failures}개

🔥 API별 실패율 순위:
"""
    
    for i, (endpoint, failure_rate, stats) in enumerate(failure_rates[:5], 1):
        status_emoji = "🔴" if failure_rate > 50 else "🟡" if failure_rate > 20 else "🟢"
        report += f"\n{i}. {status_emoji} {endpoint}\n"
        report += f"   📈 실패율: {failure_rate:.1f}% ({stats['failed']}/{stats['total']})\n"
        
        # 주요 실패 원인
        if stats['failures']:
            main_failure = max(stats['failures'].items(), key=lambda x: x[1])
            report += f"   💥 주요 실패: {main_failure[0]} ({main_failure[1]}회)\n"
    
    # 시간대별 분석
    if worst_hour is not None:
        report += f"\n⏰ 가장 불안정한 시간대: {worst_hour}시 (실패율: {worst_failure_rate:.1f}%)\n"
    
    # 안정적인 API
    stable_apis = [item for item in failure_rates if item[1] == 0]
    if stable_apis:
        report += f"\n✅ 안정적인 API ({len(stable_apis)}개):\n"
        for endpoint, _, stats in stable_apis[:3]:
            report += f"• {endpoint} (성공: {stats['total']}/{stats['total']})\n"
    
    # 트렌드 분석
    if len(recent_runs) >= 10:
        # 최근 vs 이전 비교
        mid_point = len(recent_runs) // 2
        recent_half = recent_runs[mid_point:]
        earlier_half = recent_runs[:mid_point]
        
        recent_failures = sum(len([t for t in run["tests"] if t["status"] == "failed"]) for run in recent_half)
        earlier_failures = sum(len([t for t in run["tests"] if t["status"] == "failed"]) for run in earlier_half)
        
        if recent_failures > earlier_failures:
            report += f"\n📈 트렌드: 최근 실패 증가 ({recent_failures} vs {earlier_failures})"
        elif recent_failures < earlier_failures:
            report += f"\n📉 트렌드: 최근 실패 감소 ({recent_failures} vs {earlier_failures})"
    
    # 색상 결정
    if overall_success_rate >= 95:
        color = "good"
    elif overall_success_rate >= 80:
        color = "warning"
    else:
        color = "danger"
    
    # Slack 전송
    send_slack_message(report, color)
    
    print("✅ 일일 상세 리포트 생성 완료")

if __name__ == "__main__":
    generate_daily_report()