FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p qr_codes exports

EXPOSE 5000

CMD ["gunicorn", "app:app"]
