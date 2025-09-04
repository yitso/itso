FROM node:20.19.4-alpine AS  node20-builder
WORKDIR /fe
COPY package.json package-lock.json ./
RUN npm install -g npm@11.5.2 && npm ci
COPY frontend frontend
COPY vite.config.js .
RUN npm run build

FROM python:3.9.20-alpine AS py3-dep
RUN apk update && apk add --no-cache git build-base python3-dev libffi-dev openssl-dev linux-headers
WORKDIR /py
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/install -r requirements.txt && \
    rm -rf /root/.cache

# runtime image
FROM python:3.9.20-alpine
WORKDIR /app
ENV FORCE_BUILD=0
COPY --from=py3-dep /install /usr/local/lib/python3.9/site-packages
COPY . .
COPY --from=node20-builder /fe/static/itso/dist ./static/itso/dist
EXPOSE 8000
ENTRYPOINT ["python3", "main.py", "--host", "0.0.0.0"]