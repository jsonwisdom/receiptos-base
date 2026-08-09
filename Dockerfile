FROM alpine:3.19@sha256:51b67269f354137895d43f3b3d810bfacd3945438e94dc5ac55fdac340352f48
RUN apk add --no-cache python3 ca-certificates
WORKDIR /app
COPY run.py /app/run.py
ENTRYPOINT ["python3", "/app/run.py"]
