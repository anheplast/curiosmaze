# Multi-stage Dockerfile para Frontend Vue.js + Vite
# frontend/Dockerfile

# =============================================================================
# ETAPA 1: Construcción (Build Stage)
# =============================================================================
FROM node:18-alpine AS builder

# Configurar variables de entorno para el build
ENV NODE_ENV=production \
    PNPM_HOME="/pnpm" \
    PATH="$PNPM_HOME:$PATH"

# Instalar pnpm (opcional, puedes usar npm si prefieres)
RUN corepack enable

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci --only=production --silent

# Copiar el código fuente
COPY . .

# Construir la aplicación para producción
RUN npm run build

# =============================================================================
# ETAPA 2: Desarrollo (Development Stage)
# =============================================================================
FROM node:18-alpine AS development

# Configurar variables de entorno
ENV NODE_ENV=development

# Instalar pnpm
RUN corepack enable

# Crear directorio de trabajo
WORKDIR /app

# Crear usuario no-root para seguridad
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Copiar archivos de configuración
COPY package*.json ./

# Instalar todas las dependencias (incluidas las de desarrollo)
RUN npm install

# Copiar el código fuente
COPY . .

# Cambiar propiedad de archivos al usuario nodejs
RUN chown -R nextjs:nodejs /app
USER nextjs

# Exponer puerto de desarrollo
EXPOSE 5173

# Comando por defecto para desarrollo
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

# =============================================================================
# ETAPA 3: Producción con Nginx (Production Stage)
# =============================================================================
FROM nginx:alpine AS production

# Instalar dependencias adicionales si son necesarias
RUN apk --no-cache add curl

# Crear directorio para logs personalizados
RUN mkdir -p /var/log/nginx

# Copiar los archivos construidos desde la etapa builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Crear configuración de nginx optimizada para Vue.js SPA
RUN echo 'server {\n\
    listen 80;\n\
    listen [::]:80;\n\
    \n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    \n\
    # Configuración para Vue Router (SPA)\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
    \n\
    # Cachear archivos estáticos\n\
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {\n\
        expires 1y;\n\
        add_header Cache-Control "public, immutable";\n\
        add_header Access-Control-Allow-Origin "*";\n\
    }\n\
    \n\
    # Configuración de seguridad\n\
    add_header X-Frame-Options "SAMEORIGIN" always;\n\
    add_header X-Content-Type-Options "nosniff" always;\n\
    add_header X-XSS-Protection "1; mode=block" always;\n\
    \n\
    # Compresión gzip\n\
    gzip on;\n\
    gzip_vary on;\n\
    gzip_min_length 1024;\n\
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;\n\
    \n\
    # Health check endpoint\n\
    location /health {\n\
        access_log off;\n\
        return 200 "healthy\n";\n\
        add_header Content-Type text/plain;\n\
    }\n\
}' > /etc/nginx/conf.d/default.conf

# Crear script de salud para Docker health check
RUN echo '#!/bin/sh\n\
curl -f http://localhost/health || exit 1' > /health-check.sh && \
    chmod +x /health-check.sh

# Exponer puerto
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["/health-check.sh"]

# Comando por defecto
CMD ["nginx", "-g", "daemon off;"]