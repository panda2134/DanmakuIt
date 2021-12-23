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

## 关于 Favicon

为什么 `/static` 下面这么多看上去一样的图标？能不能删掉一些？

不能，这些图标是用来兼容不同平台的。
请看[这篇文章](https://stackoverflow.com/questions/48956465/favicon-standard-2021-svg-ico-png-and-dimensions) 。

## 测试


[![e2e tests](https://github.com/panda2134/DanmakuIt/actions/workflows/e2e.yml/badge.svg?branch=master)](https://github.com/panda2134/DanmakuIt/actions/workflows/e2e.yml)

采用 GitHub Actions 自动运行端到端测试。你也可以本地执行现有测例：

```shell
yarn test:e2e  # 读取 ./test/e2e/ 文件夹下的所有测试用例
```

其中的一些例子是回归测试，因此不要轻易删除已有测例。
