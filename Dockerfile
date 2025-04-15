FROM python:3.12.3

# Встановлення необхідних бібліотек для CUDA
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libx11-6 \
    && apt-get clean

# Встановлення NVIDIA підтримки (необхідно для GPU)
RUN apt-get update && apt-get install -y \
    nvidia-cuda-toolkit \
    && apt-get clean

WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Command to run the application
CMD ["python3", "main.py"]
