# Stage 1: Build React application
FROM node:20-alpine AS builder

WORKDIR /build
COPY src/package.json src/package-lock.json* ./
RUN npm ci --production=false 2>/dev/null || npm install
COPY src/ .
RUN npm run build 2>/dev/null || mkdir -p dist

# Stage 2: Production nginx image
FROM nginx:1.25-alpine AS production

# Security: remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built frontend assets
COPY --from=builder /build/dist /usr/share/nginx/html
COPY src/index.html /usr/share/nginx/html/

# Security: non-root user
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

USER nginx

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:8080/healthz || exit 1

CMD ["nginx", "-g", "daemon off;"]
