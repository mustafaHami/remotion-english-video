FROM node:22-bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv ffmpeg ca-certificates libnss3 libdbus-1-3 libatk1.0-0 libgbm1 libasound2 libxrandr2 libxkbcommon0 libxfixes3 libxcomposite1 libxdamage1 libatk-bridge2.0-0 libpango-1.0-0 libcairo2 libcups2 && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" PYTHON=python TZ=Europe/Paris RENDER_CONCURRENCY=2 PUBLISH_ENABLED=false
WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY package.json package-lock.json ./
RUN npm ci && npx remotion browser ensure
COPY --chown=node:node . .
RUN mkdir -p output .runtime && chown -R node:node /app /opt/venv
USER node
CMD ["npm", "run", "verify"]
