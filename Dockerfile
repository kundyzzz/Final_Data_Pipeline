FROM apache/airflow:2.10.5-python3.11
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libdbus-1-3 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2 \
    libatspi2.0-0 libgtk-3-0 fonts-liberation && \
    rm -rf /var/lib/apt/lists/*
USER airflow
RUN pip install --no-cache-dir 'pandas==2.2.3' 'playwright==1.51.0' 'pytest==8.3.5' && \
    python -m playwright install chromium
