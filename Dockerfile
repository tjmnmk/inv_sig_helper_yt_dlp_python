FROM alpine:3.21

RUN apk add --no-cache coreutils python3 py3-pip
RUN adduser -u 10001 -S appuser

COPY inv_sig_helper_yt_dlp_python /app
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

RUN pip3 install --break-system-packages -r /app/requirements.txt

WORKDIR /app
EXPOSE 12999

# Switch to non-privileged user
USER appuser

# Set the entrypoint to the binary name
ENTRYPOINT ["/app/entrypoint.sh"]