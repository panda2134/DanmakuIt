import{_ as e,c as a,o as r,a as t}from"./app.28e7ae63.js";var o="/DanmakuIt/assets/services.f55ea672.png";const m='{"title":"\u5F00\u59CB\u5F00\u53D1","description":"","frontmatter":{},"headers":[{"level":2,"title":"\u5F00\u59CB\u5F00\u53D1","slug":"\u5F00\u59CB\u5F00\u53D1"},{"level":2,"title":"\u63A5\u53E3\u8BBE\u8BA1","slug":"\u63A5\u53E3\u8BBE\u8BA1"},{"level":2,"title":"\u6D4B\u8BD5","slug":"\u6D4B\u8BD5"},{"level":2,"title":"\u5BA2\u6237\u7AEF","slug":"\u5BA2\u6237\u7AEF"}],"relativePath":"development/index.md","lastUpdated":1640269512291}',l={},s=t(`<p>\u5F39\u5E55\u4E00\u4E0B\u662F\u4E00\u4E2A\u5F00\u6E90\u9879\u76EE\u3002\u5728\u4F60\u4F7F\u7528\u7684\u540C\u65F6\uFF0C\u6211\u4EEC\u975E\u5E38\u6B22\u8FCE\u4F60\u4E3A\u4EA7\u54C1\u6DFB\u52A0\u65B0\u7684\u529F\u80FD\u3002</p><p>\u5982\u679C\u4F60\u6709\u8FD9\u65B9\u9762\u7684\u6253\u7B97\uFF0C\u6211\u4EEC\u5EFA\u8BAE\u5148\u5728 issue \u5185\u548C\u7BA1\u7406\u5458\u8FDB\u884C\u8BA8\u8BBA\uFF0C\u518D\u63D0\u4EA4 Pull Request\u3002\u6211\u4EEC\u4F1A\u91CD\u89C6\u4F60\u63D0\u51FA\u7684\u610F\u89C1\u6216\u5EFA\u8BAE\u3002</p><h2 id="\u5F00\u59CB\u5F00\u53D1" tabindex="-1">\u5F00\u59CB\u5F00\u53D1 <a class="header-anchor" href="#\u5F00\u59CB\u5F00\u53D1" aria-hidden="true">#</a></h2><div class="language-shell line-numbers-mode"><pre><code><span class="token function">git</span> clone --recursive https://github.com/panda2134/DanmakuIt.git
</code></pre><div class="line-numbers-wrapper"><span class="line-number">1</span><br></div></div><p>\u8FD9\u5C06\u4F1A\u4E0B\u8F7D\u5F39\u5E55\u4E00\u4E0B\u7684\u5B8C\u6574\u6E90\u4EE3\u7801\u3002\u4EE3\u7801\u4F4D\u4E8E<code>src</code>\u76EE\u5F55\uFF0C\u7531\u4EE5\u4E0B\u90E8\u5206\u7EC4\u6210\uFF1A</p><ul><li><code>frontend</code>: \u7BA1\u7406\u6240\u7528\u524D\u7AEF\uFF0C\u8D1F\u8D23\u589E\u5220\u623F\u95F4\u3001\u914D\u7F6E\u623F\u95F4\u7B49\u529F\u80FD\uFF0C\u91C7\u7528 <a href="https://nuxtjs.org/" target="_blank" rel="noopener noreferrer">Nuxt.js 2</a> \u7F16\u5199\uFF1B</li><li><code>dashboard</code>: \u7BA1\u7406\u524D\u7AEF\u5BF9\u5E94\u7684 REST API \u63A5\u53E3\uFF0C\u91C7\u7528 <a href="https://fastapi.tiangolo.com/" target="_blank" rel="noopener noreferrer">FastAPI</a> \u5B9E\u73B0\uFF1B</li><li><code>controller</code>: \u8D1F\u8D23\u5FAE\u4FE1\u5F39\u5E55\u53D1\u9001\u8BF7\u6C42\u548C\u670D\u52A1\u5668\u5185\u90E8\u4E0E Pulsar \u901A\u4FE1\u76F8\u5173\u8BF7\u6C42\uFF0C\u91C7\u7528 <a href="https://sanicframework.org/" target="_blank" rel="noopener noreferrer">sanic</a> \u5B9E\u73B0\uFF1B</li><li><code>tagger</code>: \u8D1F\u8D23\u5BF9\u8BC4\u8BBA\u8FDB\u884C\u5BA1\u6838\u7684 Pulsar Client\uFF1B</li><li><code>client</code>: \u684C\u9762\u5BA2\u6237\u7AEF\u3002</li></ul><p>\u5728\u5F00\u59CB\u5F00\u53D1\u524D\uFF0C\u4F60\u9700\u8981\u914D\u7F6E\u4E00\u4E0B\u5F00\u53D1\u73AF\u5883\u3002\u6211\u4EEC\u63A8\u8350\u7684\u914D\u7F6E\u4E3A\uFF1A</p><ul><li>Python 3.9.x</li><li>Node.js 16.x, \u5E76\u91C7\u7528 <code>yarn</code> \u5305\u7BA1\u7406\u5668</li><li>Docker \u4E0E <code>docker-compose</code>\uFF0C\u6216\u8005 Podman \u4E0E <code>podman-compose</code></li><li>Qt 6.2.2</li></ul><p>\u4E0B\u56FE\u5C55\u793A\u4E86\u5404\u4E2A\u670D\u52A1\u7684\u4EA4\u4E92\u6D41\u7A0B\u3002</p><p><img src="`+o+'" alt="services"></p><h2 id="\u63A5\u53E3\u8BBE\u8BA1" tabindex="-1">\u63A5\u53E3\u8BBE\u8BA1 <a class="header-anchor" href="#\u63A5\u53E3\u8BBE\u8BA1" aria-hidden="true">#</a></h2><h2 id="\u6D4B\u8BD5" tabindex="-1">\u6D4B\u8BD5 <a class="header-anchor" href="#\u6D4B\u8BD5" aria-hidden="true">#</a></h2><h2 id="\u5BA2\u6237\u7AEF" tabindex="-1">\u5BA2\u6237\u7AEF <a class="header-anchor" href="#\u5BA2\u6237\u7AEF" aria-hidden="true">#</a></h2>',13),n=[s];function i(d,c,p,h,u,_){return r(),a("div",null,n)}var g=e(l,[["render",i]]);export{m as __pageData,g as default};
