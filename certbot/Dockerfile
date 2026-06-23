FROM certbot/certbot

# Install docker CLI so the container can signal the proxy via the Docker socket
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends docker.io curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/bin/sh", "-c"]
