# Frontend Web Dockerfile
# Team: DevOps

FROM node:20-alpine AS builder

WORKDIR /app

# Copy UI package
COPY packages/ui/package*.json ./
RUN npm ci

COPY packages/ui/ ./
RUN npm run build

# Production image
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY apps/web/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
