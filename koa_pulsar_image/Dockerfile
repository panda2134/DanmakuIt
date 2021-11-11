FROM node:latest AS build

WORKDIR /build/

COPY package.json .

# libpulsarnossl.so is symlink to libpulsarnossl.so.2.8.1
# node-pulsar-client deployment only need libpulsar.so.2.8.1
RUN wget https://dlcdn.apache.org/pulsar/pulsar-2.8.1/DEB/apache-pulsar-client-dev.deb \
    && wget https://dlcdn.apache.org/pulsar/pulsar-2.8.1/DEB/apache-pulsar-client.deb \
    && apt install ./apache-pulsar-client*.deb \
    && rm ./apache-pulsar-client*.deb \
    && npm install --only=production --registry=https://registry.npmmirror.com \
    && rm -rf /root/.npm \
    && cp /usr/lib/libpulsar.so.2.8.1 . \
    && apt remove -y apache-pulsar-client

FROM node:slim AS deploy

WORKDIR /workspace/
COPY --from=build /build/libpulsar.so.2.8.1 /usr/lib
COPY --from=build /build/node_modules /workspace/node_modules