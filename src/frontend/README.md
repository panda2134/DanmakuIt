# frontend

DanmakuIt平台前端代码。

## 构建

本项目采用 Nuxt.js 和 Vuetify 2.

```bash
# install dependencies
$ yarn install

# serve with hot reload at localhost:3000
$ yarn dev

# build for production and launch server
$ yarn build
$ yarn start

# generate static project
$ yarn generate
```

如果你对Dashboard API进行了修改，需要重新生成 OpenAPI 类型，再实现新API.
为此，首先在 Dashboard 服务器的 `/openapi.json` 处取得新 spec 文件，放入本项目的 `openapi` 目录下进行覆盖。
然后生成类型：

```shell
$ yarn openapi
```

最后，修改 `plugins/http.ts`，实现新的 API 接口。返回值类型会自动根据 spec 文件进行推断。

## 测试

TODO: e2e test & unit test
