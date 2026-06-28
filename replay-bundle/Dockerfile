FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY . /app
RUN chmod +x replay.sh self_test.py receipt_anchor.py verify.py
CMD ["./replay.sh"]
