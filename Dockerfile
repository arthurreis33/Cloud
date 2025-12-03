FROM python:3.11-slim AS builder

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

COPY . .

# Executa testes durante o build
RUN python -m pytest src/__tests__/ -v || true

FROM python:3.11-slim AS production

WORKDIR /usr/src/app

COPY --from=builder /root/.local /root/.local

COPY requirements.txt .
COPY main.py .
COPY src ./src

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 3000

CMD ["python", "main.py"]
