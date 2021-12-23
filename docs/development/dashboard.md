# 管理后端文档

REST API 文档可见[Redoc](https://redocly.github.io/redoc/?url=https://panda2134.github.io/DanmakuIt/openapi.json).

在搭建好开发环境后，也可以在 `http://localhost:8000/api/v1/docs` 访问到带有调试界面的管理后端文档。

## 密钥生成

### 房间密码

房间密码生成采用完全随机的 32 Byte，经过哈希后替换人眼难以辨认的字符得到；这是为了方便登录客户端时输入密码。

### 微信接入 token

微信接入 token 的生成基于确定性的算法，从房间号码派生得到。对房间号加盐后哈希，再替换人眼难辨认的字符，即可生成微信接入 token.

可参考[代码中的实现](https://github.com/panda2134/DanmakuIt/blob/86c62edfa22061985ad2a2dd39e55cafa7a77418/src/dashboard/app/routers/room/__init__.py#L38)。

## 后台任务

后台任务都定义在 `worker.py` 中。

### 刷新微信公众号的 Access Token

任务名称为 `refresh_wechat_access_token_all`, `refresh_wechat_access_token_room`.

根据微信接口要求，管理后端会定期刷新所有房间对应公众号的 Access Token；目前的两次刷新之间时间间隔为 `max(ex / 2, ex - 1e3)`，其中 `ex` 为单个 Access Token 的有效期。

### 与控制器的同步

任务名称为 `resume_controller`.

在创建或修改房间时，均会通过控制器的 REST API 进行同步。
当所有服务重启时，管理后端会把数据库中房间状态向控制器进行一次同步，此后这些信息缓存在控制器的内存中。
