FROM registry.cn-hangzhou.aliyuncs.com/acs/node:20-alpine as build-stage

WORKDIR /app

COPY package*.json ./

RUN npm install --registry=https://registry.npmmirror.com

COPY . .

RUN npm run build

FROM registry.cn-hangzhou.aliyuncs.com/acs/nginx:alpine as production-stage

COPY --from=build-stage /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]