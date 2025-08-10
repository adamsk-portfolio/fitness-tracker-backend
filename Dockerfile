FROM python:3.12-slim
WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
 && pip install gunicorn

COPY backend/ /app/backend
COPY migrations/ /app/migrations/

EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "backend.app:create_app()"]
