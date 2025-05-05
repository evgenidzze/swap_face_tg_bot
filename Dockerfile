FROM python:3.10.12

# Встановлення системних бібліотек, потрібних для OpenCV і збірки aiohttp
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    python3-dev \
    libssl-dev \
    libffi-dev \
 && rm -rf /var/lib/apt/lists/*

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо requirements і встановлюємо залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо увесь код проєкту
COPY . .

# Запускаємо додаток
CMD ["python3", "start_bot.py"]
