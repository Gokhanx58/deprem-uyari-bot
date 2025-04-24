FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir requests beautifulsoup4

RUN chmod +x start.sh

CMD ["./start.sh"]
