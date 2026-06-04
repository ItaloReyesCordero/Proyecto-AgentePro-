# Frontend de PRODUCCIÓN: construye el sitio y lo sirve con nginx.
# (El Dockerfile.dev es solo para desarrollo con Vite + hot reload.)

# --- Etapa 1: build ---
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build

# --- Etapa 2: servir estático con nginx ---
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
