FROM node:16-alpine AS buildStage
WORKDIR /workspace/
COPY src/frontend/yarn.lock .
COPY src/frontend/package.json .
RUN yarn config set registry https://registry.npmmirror.com
RUN yarn
COPY src/frontend .
RUN yarn build && yarn generate

FROM nginx:alpine
RUN rm -rf /etc/nginx/conf.d/
COPY conf/nginx/danmakuit.conf /etc/nginx/conf.d/
COPY --from=buildStage /workspace/dist/ /var/www/html/