# Build context must be the llm-hub/ directory (parent of gui/) so registry.tsv is included.
#   docker build -f gui/Dockerfile -t llm-hub .
FROM node:22-alpine
WORKDIR /app

# zero runtime dependencies — just copy the app + registry
COPY gui/package.json ./package.json
COPY gui/server.js ./server.js
COPY gui/lib ./lib
COPY gui/public ./public
COPY registry.tsv ./registry.tsv

# Provider keys live ENCRYPTED in secrets/keys.enc and are decrypted at runtime
# with the private PEM (mounted, never baked into the image).
ENV PORT=7878 \
    DATA_DIR=/app/data \
    SECRETS_ENC=/app/secrets/keys.enc \
    LLMHUB_PEM=/app/secrets/llmhub_private.pem
EXPOSE 7878
VOLUME ["/app/data", "/app/secrets"]

# basic healthcheck against the public endpoint
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:7878/api/health || exit 1

CMD ["node", "server.js"]
