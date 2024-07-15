FROM python:3.11.8-bookworm

WORKDIR /app

# Copy the requirements.txt first for better cache on later pushes
COPY ./requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# Copy the main application
COPY . .

# Run the application
CMD ["python3", "store.py"]
# CMD ["gunicorn", "src.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--reload"]


