FROM python:3.12.3

WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Command to run the application
CMD ["python3", "main.py"]
