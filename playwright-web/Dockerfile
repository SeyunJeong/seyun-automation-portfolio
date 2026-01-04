# ✅ Playwright 공식 Python 이미지 사용 (최신 버전)
FROM mcr.microsoft.com/playwright/python:v1.36.0-focal

# ✅ 환경 변수 설정
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# ✅ 작업 디렉토리 설정
WORKDIR /app

# ✅ 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    xvfb \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon-x11-0 \
    libgbm1 \
    libpango-1.0-0 \
    libasound2 \
    libwayland-client0 \
    libwayland-cursor0 \
    libwayland-egl1 \
    libgdk-pixbuf2.0-0 \
    dbus-x11 \
    x11-utils \
    x11-xserver-utils \
    build-essential \
    libyaml-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ✅ Python 패키지 설치
COPY requirements.txt /app/
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# ✅ 디렉토리 생성 및 권한 설정
RUN mkdir -p /app/session-data /app/screenshots /app/downloads /app/src/utils /app/src/pages /app/src/tests && \
    chmod -R 755 /app/session-data /app/screenshots /app/downloads

# ✅ 프로젝트 파일 복사
COPY . /app/

# ✅ Playwright 브라우저 설치
RUN python3 -m playwright install --with-deps chromium

# ✅ 환경 변수 설정
ENV DISPLAY=:99
ENV XDG_RUNTIME_DIR=/tmp/runtime-root
ENV PYTHONPATH=/app

# ✅ 시작 스크립트 설정
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# ✅ 엔트리포인트 설정
ENTRYPOINT ["/app/entrypoint.sh"]