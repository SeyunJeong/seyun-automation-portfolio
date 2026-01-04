#!/bin/bash
# Xvfb 및 테스트 환경 설정
mkdir -p "$XDG_RUNTIME_DIR"
chmod 0700 "$XDG_RUNTIME_DIR"
echo "Starting Xvfb..."
Xvfb :99 -screen 0 1920x1080x24 &
sleep 3
echo "Xvfb started, running tests..."

# 작업 디렉토리 이동
cd /app

# conftest.py 유무 확인
if [ -f "src/tests/conftest.py" ]; then
    echo "src/tests/conftest.py found. Global fixtures will be loaded."
else
    echo "Warning: src/tests/conftest.py not found!"
fi

# Python 모듈 경로 확인
python3 -c "import sys; print(sys.path)"

# 모든 테스트 실행 (실패해도 계속 진행)
python3 -m pytest src/tests --disable-warnings -vv -s