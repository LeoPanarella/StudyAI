# Stage 1: Build da aplicação React com Vite
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install --silent --no-audit --no-fund

COPY . .
RUN npm run build

# Stage 2: Servidor web de produção com Nginx
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
