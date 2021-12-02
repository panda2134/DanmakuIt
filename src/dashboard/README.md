# 管理面板

“弹幕一下”平台的管理面板RESTful API.

## Dependencies

```shell
$ pip install poetry
$ poetry install # run with python 3.9
```

## 登录

目前实现了通过微信扫码/GitHub/GitLab/TsinghuaGit进行的社交网络登录；在扫码后，会根据从微信获取的UnionID等信息，
建立本地账户，并且签发相应的 Json Web Token.

## 房间管理

目前实现了房间的增加、列表、修改、删除等功能。和实时弹幕相关的功能由Apache Pulsar提供。

## 登录

Click for a login test.

- <a target="_self" href="/user/social-login/github/login">GitHub</a>
- <a target="_self" href="/user/social-login/gitlab/login">GitLab</a>
- <a target="_self" href="/user/social-login/gitlab3rd/login">GitLabTsinghua</a> &lt; - 推荐用这个