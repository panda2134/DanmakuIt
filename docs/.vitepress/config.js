module.exports = {
  base: '/DanmakuIt/',
  title: '弹幕一下',
  description: '弹幕一下文档',
  lang: 'zh-CN',
  markdown: {
    lineNumbers: true
  },
  themeConfig: {
    repo: 'panda2134/DanmakuIt',
    docsDir: 'docs',
    docsBranch: 'docs',
    editLinks: 'true',
    editLinkText: '在 GitHub 上编辑此页',
    nav: [
      { text: 'Guide', link: '/guide/' },
      { text: 'Docs', link: '/documentation/' },
      { text: 'Development', link: '/development/' },
      { text: 'API', items: [
        { text: 'Pulsar接口', link: '/development/pulsar' },
        { text: '控制器', link: '/development/controller' },
        { text: '管理后端', link: '/development/dashboard' },
        { text: '前端', link: '/development/frontend' },
      ] }
    ]
  }
}