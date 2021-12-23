# Pulsar 消息格式

## 用户元信息推送

此为 WebSocket 接口。

**接口路径**: `/websocket/reader/persistent/public/default/user_{room}?messageId=earliest&token=YOUR_PULSAR_TOKEN`

推送下行数据中properties字段类型为UserProperties，描述用户信息元数据，如下：

- `id` 用户标识符，与弹幕显示元数据对应
- `nickname` 用户微信昵称
- `headimgurl` 用户头像URL

## 弹幕接入点

此为 WebSocket 接口。

**接口路径**: 

- Consumer（实时弹幕）
    - `/websocket/consumer/persistent/public/default/{room}/{subscription}`
- Reader（历史弹幕）
    - `/websocket/reader/persistent/public/default/{room}?messageId=earliest&token=YOUR_PULSAR_TOKEN`

### 格式样例

```javascript
{
    'messageId': 'CBAQAiAAMAE=' // 仅用于ack
    'payload': 'AAAA', // 新弹幕, AAAB表示弹幕更新
    'properties':
    {
        'content': '{content}',
        'id': 'UMwXbJ7xE5xC4rJl8VZ8ZcUZ5n+qWs5I', // base64随机ID，几乎不可能碰撞
        'sender': 'user_{wx_openid}', // 管理员弹幕以admin_开头
        'permission': '1', // 字符串'1'表示审核通过，字符串'0'表示审核不通过
        'color': 'undefined', // 'undefined'由显示端决定, 或十六进制颜色码如'FFFFFF'
        'size': '16pt',
        'pos': 'rightleft', // 'top', 'bottom', 'rightleft'
    },
    'publishTime': '2021-11-21T10:56:25.798Z',
    'redeliveryCount': 0,
}
```

### 弹幕投放的实现逻辑

- 如果权限字段是"0"，且为弹幕更新请求（AAAB）,立刻撤下对应弹幕
- 如果权限字段是"1"，不论请求类型是AAAA还是AAAB，都使得消息体中弹幕上屏

## WebSocket API 鉴权细节

- 客户端/前端通过 dashboard 的 `client-login` 接口，以房间号和密码换取 Pulsar 的 JWT;
- 以上述 JWT 连接 Pulsar; WebSocket 的 JWT 通过 query 参数 `token` 传递