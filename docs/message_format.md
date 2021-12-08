弹幕接入点

/websocket/consumer/persistent/public/default/{room}/{subscription}

pulsar指pulsar容器，在Docker外部访问使用localhost

弹幕消息格式

```python
{
    'messageId': 'CBAQAiAAMAE=' # 仅用于ack
    'payload': 'AAAA', # 新弹幕, AAAB表示弹幕更新
    'properties':
    {
        'content': '{content}',
        'id': 'UMwXbJ7xE5xC4rJl8VZ8ZcUZ5n+qWs5I', # base64随机ID，几乎不可能碰撞
        'sender': 'user@wechat:{wx_openid}', # 管理员弹幕以admin:开头
        'permission': '1', # 字符串'1'表示审核通过，字符串'0'表示审核不通过
        'color': 'undefined', # 'undefined'由显示端决定, 或十六进制颜色码如'FFFFFF'
        'size': '16pt',
        'pos': 'rightleft', # 'top', 'bottom', 'rightleft'
    },
    'publishTime': '2021-11-21T10:56:25.798Z',
    'redeliveryCount': 0,
}
```

用户信息接入点

/websocket/consumer/persistent/public/default/user_{room}/{subscription}

用户信息消息格式

```python
{
    'messageId': 'CBAQAiAAMAE=' # 仅用于ack
    'payload': 'AAAC', # 表示为用户信息
    'properties':
    {
        'id': 'user@wechat:{wx_openid}', # 管理员以admin:开头
        'nickname': '微信昵称',
        'headimgurl': 'http://thirdwx.qlogo.cn/mmopen/{some_hash}' # 管理员为base64编码
    },
    'publishTime': '2021-11-21T10:56:25.798Z',
    'redeliveryCount': 0,
}
```

