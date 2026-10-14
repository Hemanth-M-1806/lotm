# ==============================================================================
# Stage 1: Build React Production Bundle
# ==============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package manifests first for efficient layer caching
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies deterministically
RUN npm ci

# Copy frontend source and configuration files
COPY frontend/index.html ./
COPY frontend/vite.config.ts ./
COPY frontend/tsconfig*.json ./
COPY frontend/.oxlintrc.json ./
COPY frontend/public ./public
COPY frontend/src ./src

# Build production bundle
RUN npm run build

# ==============================================================================
# Stage 2: Serve with Pinned Nginx
# ==============================================================================
FROM nginx:1.27-alpine AS runner

LABEL maintainer="LOTM Tarot Development Team" \
      version="0.1.0" \
      description="Production web server for LOTM Tarot Victorian Backlund frontend"

# Remove default static files
RUN rm -rf /usr/share/nginx/html/*

# Copy built distribution files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Healthcheck
HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q --spider http://127.0.0.1/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
