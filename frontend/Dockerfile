# ── Stage 1 : Build ──────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# ── Stage 2 : Serve ──────────────────────────────────────────────────────────
FROM nginx:alpine

# Copier le build dans le dossier servi par nginx
COPY --from=builder /app/dist /usr/share/nginx/html/AI-Taskforce

# Config nginx : SPA + base path /AI-Taskforce/
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
