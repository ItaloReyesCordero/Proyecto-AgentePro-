# Frontend de PRODUCCIÓN: construye el sitio y lo sirve con nginx.
# (El Dockerfile.dev es solo para desarrollo con Vite + hot reload.)

# --- Etapa 1: build ---
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build

# --- Etapa 2: servir estático con nginx (imagen NO-ROOT) ---
# nginx-unprivileged corre como usuario 101 (no root) y escucha en el puerto 8080
# (puerto no privilegiado, >1024) sin necesidad de capacidades extra. El proxy
# (Caddy) apunta a frontend:8080 (ver Caddyfile).
FROM nginxinc/nginx-unprivileged:1.27-alpine
# El nginx.conf ya escucha en 8080 (ver frontend/nginx.conf).
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
# La imagen unprivileged ya define USER 101 y un CMD que arranca nginx en primer
# plano; no hace falta volver a declararlos.
