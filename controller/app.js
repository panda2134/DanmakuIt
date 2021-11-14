const Koa = require('koa');
const Router = require('@koa/router');
const Pulsar = require('pulsar-client');
const XMLParser = require('fast-xml-parser');
const { createHash } = require('crypto');
const { PassThrough } = require('stream');

const app = new Koa();
const router = new Router({
    prefix: '/api'
});

const produce = async ctx => {
    // Create a client
    const client = new Pulsar.Client({
        serviceUrl: 'pulsar://pulsar:6650',
      });
    
    // Create a producer
    const producer = await client.createProducer({
    topic: 'my-topic',
    });
    
    // Send messages
    const msg_list = [];
    for (let i = 0; i < 10; i += 1) {
    const msg = `my-message-${i}-${Math.random()}`;
    producer.send({
        data: Buffer.from(msg),
    });
    msg_list.push(`Sent message: ${msg}`);
    }
    await producer.flush();
    await producer.close();
    await client.close();
    ctx.body = msg_list;
}

const consume = async ctx => {
    // Create a client
    const client = new Pulsar.Client({
        serviceUrl: 'pulsar://pulsar:6650',
    });

    // Create a consumer
    const consumer = await client.subscribe({
        topic: 'my-topic',
        subscription: 'my-subscription',
        subscriptionType: 'Exclusive',
    });

    ctx.req.on('close', async () => {
        await consumer.close();
        await client.close();
    })

    // Receive messages
    const msg = await consumer.receive();
    consumer.acknowledge(msg);
    ctx.body = msg.getData().toString();
    
}

const token = 'token_placeholder'

const room_get = async ctx => {
    const query = ctx.query;
    const hash = createHash('sha1')
    hash.update([token, query.timestamp, query.nonce].sort().join(''));
    if (hash.digest('hex') === query.signature)
    {
        ctx.body = query.echostr;
        return;
    }
    ctx.body = '';
}

router
    .get('/', async ctx => {ctx.body = {message :'😂tes12t'}})
    .get('/produce', produce)
    .get('/consume', consume)
    .get('/room', room_get)



app.use(router.routes());
app.listen(8000);