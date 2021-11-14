const Koa = require('koa');
const Router = require('@koa/router');
const Pulsar = require('pulsar-client');

const getRawBody = require('raw-body');
const XMLParser = require('fast-xml-parser');
const { createHash } = require('crypto');

const app = new Koa();
const router = new Router({
    prefix: '/api'
});

const token = 'token_placeholder'

router.get('/', async ctx => { ctx.body = { message: '😂tes12t' } })
    .get('/consume', async ctx => {
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

    })
    .get('/room/:id/port', async ctx => {
        const query = ctx.query;
        const hash = createHash('sha1')
        hash.update([token, query.timestamp, query.nonce].sort().join(''));
        if (hash.digest('hex') !== query.signature) {
            return;
        }
        ctx.body = query.echostr;
    })
    .post('/room/:id/port', async ctx => {
        const rawBody = await getRawBody(ctx.req, 'utf8');
        const msg = XMLParser.parse(rawBody).xml;
        if (msg.MsgType !== 'text')
        {
            return;
        }

        // Create a client
        const client = new Pulsar.Client({
            serviceUrl: 'pulsar://pulsar:6650',
        });

        // Create a producer
        const producer = await client.createProducer({
            topic: 'my-topic',
        });

        // Send messages
        producer.send({
            data: Buffer.from(msg.Content),
        });
        await producer.flush();
        await producer.close();
        await client.close();
        ctx.body = 'success';
    })



app.use(router.routes());
app.listen(8000);