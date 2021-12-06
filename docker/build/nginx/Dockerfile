FROM node:17-alpline AS buildStage
WORKDIR /workspace/
COPY ../../../src/frontend/yarn.lock .
COPY ../../../src/frontend/package.json .
RUN yarn
COPY ../../../src/frontend .
RUN yarn build && yarn generate

FROM nginx:alpine
RUN rm -rf /etc/nginx/conf.d/*
COPY ./danmakuit.conf /etc/nginx/conf.d/
COPY --from=buildStage /workspace/dist/ /var/www/html/