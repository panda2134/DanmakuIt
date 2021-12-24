# 控制器数据
## 数据项目
### 房间存在性
控制器接收到弹幕Post请求后，首先会根据path中的房间号由加盐Hash计算token并验证query中的token参数进行身份认证，提供一定的安全性。
但由于房间可被注销，而注销后token仍可被验证通过，我们还需要验证房间的存在性。
### 房间可用性
房间管理员可关闭弹幕，因此我们还需要验证房间的可用性。
### 用户数据存在性
控制器接收到弹幕Post请求后，若弹幕发送者的用户数据（头像、昵称）缺失，需要从微信服务器拉取，为了避免重复拉取，需要验证用户数据的存在性。
### 微信Access Token
控制器从微信服务器拉取用户数据时需要微信Access Token，因此每个房间都需要可以配置和保存微信Access Token。
## 数据存储方案
控制器允许多实例、多worker分布式运行，且上述数据项目显然要求有基本的一致性，不可能使用纯粹的单进程内存数据存储。
考虑到上述数据项目的读取频率极高（每条弹幕的处理都需要读取房间存在性、房间可用性和用户数据存在性），每次都读取中心数据库（即使是Redis）可能开销也较高，因此采用消息队列分发日志同步单进程内存数据的方式。
暂时没有实现为主从模式，从而不能在出错时保持一致性，更没有实现分布式共识算法在一致性的基础上保证高可用。

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
