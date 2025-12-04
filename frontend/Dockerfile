FROM node:lts-alpine AS build

WORKDIR /app

ARG VITE_BACKEND_URL
ENV VITE_BACKEND_URL=$VITE_BACKEND_URL

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

RUN rm -rf /usr/share/nginx/html/* \
 && mkdir -p /var/cache/nginx/client_temp /var/cache/nginx/proxy_temp /var/cache/nginx/fastcgi_temp \
               /var/cache/nginx/uwsgi_temp /var/cache/nginx/scgi_temp /var/run /var/log/nginx \
 && chgrp -R 0 /var/cache/nginx /var/run /var/log/nginx /etc/nginx/conf.d \
 && chmod -R g=u /var/cache/nginx /var/run /var/log/nginx /etc/nginx/conf.d

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]