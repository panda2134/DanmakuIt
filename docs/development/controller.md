---
title: 控制器API
---


# 控制器 API

## Delete room

### 基本信息

**Path：** /room/{room}

**Method：** DELETE

**接口描述：**


### 请求参数

**Headers**

| 参数名称     | 参数值                            | 是否必须 | 示例 | 备注 |
| ------------ | --------------------------------- | -------- | ---- | ---- |
| Content-Type | application/x-www-form-urlencoded | 是       |      |      |
| **路径参数** |                                   |          |      |      |

| 参数名称 | 示例 | 备注         |
| -------- | ---- | ------------ |
| room     |      | 房间号字符串 |

## Fetch & push users

### 基本信息

**Path：** /feed/{room}

**Method：** POST

**接口描述：**


### 请求参数

**Headers**

| 参数名称     | 参数值                            | 是否必须 | 示例 | 备注 |
| ------------ | --------------------------------- | -------- | ---- | ---- |
| Content-Type | application/x-www-form-urlencoded | 是       |      |      |
| **路径参数** |                                   |          |      |      |

| 参数名称 | 示例 | 备注         |
| -------- | ---- | ------------ |
| room     |      | 房间号字符串 |

## Get consumers

### 基本信息

**Path：** /room/{room}/consumers

**Method：** GET

**接口描述：**

<p>每个Consumer的值列表格式可见&nbsp;<a href="https://yapi.panda2134.site/project/24/interface/api/255">https://yapi.panda2134.site/project/24/interface/api/255</a>&nbsp;中的 consumers 值列表</p>


### 请求参数

**路径参数**

| 参数名称 | 示例      | 备注         |
| -------- | --------- | ------------ |
| room     | 123456789 | 房间号字符串 |

### 返回数据

```javascript
{
"consumer1": [{}],
"consumer2": [{}]
}
```

## Register room

### 基本信息

**Path：** /room/{room}

**Method：** POST

**接口描述：**

<p>返回 text/plain 的纯文本 pulsar token</p>


### 请求参数

**Headers**

| 参数名称     | 参数值                            | 是否必须 | 示例 | 备注 |
| ------------ | --------------------------------- | -------- | ---- | ---- |
| Content-Type | application/x-www-form-urlencoded | 是       |      |      |
| **路径参数** |                                   |          |      |      |

| 参数名称 | 示例 | 备注         |
| -------- | ---- | ------------ |
| room     |      | 房间号字符串 |

## Replace WeChat AccessToken

### 基本信息

**Path：** /token/{room}

**Method：** PUT

**接口描述：**

<p>用于dashboard向controller同步设置</p>


### 请求参数

**Headers**

| 参数名称     | 参数值                            | 是否必须 | 示例 | 备注 |
| ------------ | --------------------------------- | -------- | ---- | ---- |
| Content-Type | application/x-www-form-urlencoded | 是       |      |      |
| **路径参数** |                                   |          |      |      |

| 参数名称 | 示例 | 备注         |
| -------- | ---- | ------------ |
| room     |      | 房间号字符串 |

## Replace room settings

### 基本信息

**Path：** /setting/{room}

**Method：** PUT

**接口描述：**

<p>用于dashboard向controller同步设置</p>


### 请求参数

**Headers**

| 参数名称     | 参数值                            | 是否必须 | 示例 | 备注 |
| ------------ | --------------------------------- | -------- | ---- | ---- |
| Content-Type | application/x-www-form-urlencoded | 是       |      |      |
| **路径参数** |                                   |          |      |      |

| 参数名称 | 示例 | 备注         |
| -------- | ---- | ------------ |
| room     |      | 房间号字符串 |

## Send / Update danmaku

### 基本信息

**Path：** /danmaku-alter/{room}

**Method：** POST

**接口描述：**


### 请求参数

**Headers**

| 参数名称     | 参数值                            | 是否必须 | 示例 | 备注 |
| ------------ | --------------------------------- | -------- | ---- | ---- |
| Content-Type | application/x-www-form-urlencoded | 是       |      |      |
| **路径参数** |                                   |          |      |      |

| 参数名称  | 示例 | 备注         |
| --------- | ---- | ------------ |
| room      |      | 房间号字符串 |
| **Query** |      |              |

| 参数名称 | 是否必须 | 示例   | 备注                                                         |
| -------- | -------- | ------ | ------------------------------------------------------------ |
| type     | 否       | update | update或者send，分别表示这是更新或发送弹幕请求；没有时默认update |

## Send danmaku

### 基本信息

**Path：** /port/{room}

**Method：** POST

**接口描述：**

<p>同微信公众号“基础消息能力”接口</p>


### 请求参数

**路径参数**

| 参数名称 | 示例 | 备注         |
| -------- | ---- | ------------ |
| room     |      | 房间号字符串 |
| **Body** |      |              |

<table>
  <thead class="ant-table-thead">
    <tr>
      <th key=name>名称</th><th key=type>类型</th><th key=required>是否必须</th><th key=default>默认值</th><th key=desc>备注</th><th key=sub>其他信息</th>
    </tr>
  </thead><tbody className="ant-table-tbody"><tr key=0><td key=0><span style="padding-left: 0px"><span style="color: #8c8a8a"></span> </span></td><td key=1><span></span></td><td key=2>非必须</td><td key=3></td><td key=4><span style="white-space: pre-wrap"></span></td><td key=5></td></tr>
               </tbody>
              </table>


### 返回数据

```javascript
<xml>
        <ToUserName><![CDATA[{from_user}]]></ToUserName>
        <FromUserName><![CDATA[{developer_account}]]></FromUserName>
        <CreateTime>{int(time())}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{reply_message}]]></Content>
</xml>
```

## WeChat Official Account Auth

### 基本信息

**Path：** /port/{room}

**Method：** GET

**接口描述：**

<p>同微信公众号“验证成为开发者”文档所叙述</p>


### 请求参数

**路径参数**

| 参数名称  | 示例 | 备注         |
| --------- | ---- | ------------ |
| room      |      | 房间号字符串 |
| **Query** |      |              |

| 参数名称  | 是否必须 | 示例 | 备注                   |
| --------- | -------- | ---- | ---------------------- |
| timestamp | 是       |      | 时间戳                 |
| nonce     | 是       |      | nonce随机数            |
| signature | 是       |      | 微信签名               |
| echostr   | 是       |      | 验证成功时的回显字符串 |

### 返回数据

```javascript
{echostr}
```