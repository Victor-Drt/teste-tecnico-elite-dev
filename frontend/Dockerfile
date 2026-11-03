
# Dependências compartilhadas
FROM node:22-alpine AS base

WORKDIR /app

COPY package*.json ./
RUN npm ci

# Desenvolvimento local
FROM base AS development

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Build de produção
FROM base AS builder

COPY . .

ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# Servidor de produção
FROM nginx:alpine AS production

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/templates/default.conf.template

ENV NGINX_ENVSUBST_FILTER=^PORT$

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
