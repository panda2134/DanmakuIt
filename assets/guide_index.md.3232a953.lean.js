import{r as _,e as y,f as A,g as T,c,b as i,F as b,h as m,u as I,a as h,J as S,o as r,t as k,w as E,v as w}from"./app.8babe835.js";const x="modulepreload",f={},D="/DanmakuIt/",L=function(t,p){return!p||p.length===0?t():Promise.all(p.map(a=>{if(a=`${D}${a}`,a in f)return;f[a]=!0;const s=a.endsWith(".css"),l=s?'[rel="stylesheet"]':"";if(document.querySelector(`link[href="${a}"]${l}`))return;const n=document.createElement("link");if(n.rel=s?"stylesheet":x,s||(n.as="script",n.crossOrigin=""),n.href=a,document.head.appendChild(n),s)return new Promise((e,o)=>{n.addEventListener("load",e),n.addEventListener("error",o)})})).then(()=>t())};var v="/DanmakuIt/icon.png",R="/DanmakuIt/icon.webp",G="/DanmakuIt/assets/baidu-censor1.e319e471.png",P="/DanmakuIt/assets/running.22feb44e.png",N={"api.env":[{name:"BAIDU_CLIENT_ID",type:"input",field:"\u767E\u5EA6\u4E91\u6587\u672C\u5BA1\u6838 API Key",value:""},{name:"BAIDU_CLIENT_SECRET",type:"input",field:"\u767E\u5EA6\u4E91\u6587\u672C\u5BA1\u6838 Secret Key",value:""}],"site.env":[{name:"MONGO_INITDB_ROOT_USERNAME",type:"default",field:"MongoDB \u6570\u636E\u5E93\u540D\u79F0",defaultValue:"danmakuit",value:"danmakuit"},{name:"MONGO_INITDB_ROOT_PASSWORD",type:"rand",field:"MongoDB \u6570\u636E\u5E93\u5BC6\u7801",len:32,value:""},{name:"WEB_ORIGIN",type:"input",field:"\u7F51\u7AD9\u5916\u90E8\u8BBF\u95EE\u57DF\u540D\u548C\u534F\u8BAE\uFF08\u8981\u6C42https\uFF09",value:""},{name:"SESSION_SECRET",type:"rand",field:"\u4F1A\u8BDD\u5BC6\u94A5",len:32,value:""},{name:"JWT_SECRET",type:"rand",field:"JWT\u5BC6\u94A5",len:64,value:""},{name:"GITHUB_APPID",type:"input",field:"GitHub App ID",value:""},{name:"GITHUB_SECRET",type:"input",field:"GitHub App Secret",value:""},{name:"GITLAB_APPID",type:"input",field:"GitLab App ID",value:""},{name:"GITLAB_SECRET",type:"input",field:"GitLab App Secret",value:""},{name:"GITLAB_3RD_BASEURL",type:"input",field:"\u81EA\u6258\u7BA1 GitLab \u5B9E\u4F8B\u5730\u5740",value:""},{name:"GITLAB_3RD_APPID",type:"input",field:"\u81EA\u6258\u7BA1 GitLab \u5B9E\u4F8B App ID",value:""},{name:"GITLAB_3RD_APPSECRET",type:"input",field:"\u81EA\u6258\u7BA1 GitLab \u5B9E\u4F8B App Secret",value:""},{name:"ALLOW_REGISTRATION",type:"input",field:"\u662F\u5426\u5141\u8BB8\u6CE8\u518C\uFF0C1\u4E3A\u5141\u8BB8\uFF0C0\u4E3A\u4E0D\u5141\u8BB8",value:""}],"token.env":[{name:"WECHAT_TOKEN_LEN",type:"default",field:"\u5FAE\u4FE1\u516C\u4F17\u53F7\u9A8C\u8BC1\u6240\u7528\u7684token\u957F\u5EA6",defaultValue:"12",value:"12"},{name:"WECHAT_TOKEN_SALT",type:"rand",field:"\u7528\u4E8E\u5185\u90E8\u751F\u6210Token\u7684\u76D0\u503C",len:32,value:""}]};const C=R+" 200w, "+v+" 200w",O=h("",41),B={class:"tip custom-block"},H=i("p",{class:"custom-block-title"},"\u914D\u7F6E\u751F\u6210\u5DE5\u5177",-1),U={action:"",style:{margin:"1rem 0"}},V={style:{"margin-bottom":"0.5rem"}},W={style:{display:"flex","margin-bottom":"0.3rem"}},j=["for"],$=["onUpdate:modelValue","name"],q=h("",17),z='{"title":"\u65B0\u624B\u6307\u5357","description":"","frontmatter":{},"headers":[{"level":2,"title":"\u90E8\u7F72","slug":"\u90E8\u7F72"},{"level":3,"title":"\u51C6\u5907\u5DE5\u4F5C","slug":"\u51C6\u5907\u5DE5\u4F5C"},{"level":3,"title":"\u5B89\u88C5\u6240\u9700\u8F6F\u4EF6","slug":"\u5B89\u88C5\u6240\u9700\u8F6F\u4EF6"},{"level":3,"title":"\u5B89\u88C5 caddy","slug":"\u5B89\u88C5-caddy"},{"level":3,"title":"\u914D\u7F6E\u81EA\u52A8\u5BA1\u6838","slug":"\u914D\u7F6E\u81EA\u52A8\u5BA1\u6838"},{"level":3,"title":"\u914D\u7F6E OAuth","slug":"\u914D\u7F6E-oauth"},{"level":3,"title":"\u4E0B\u8F7D\u548C\u914D\u7F6E\u5F39\u5E55\u4E00\u4E0B","slug":"\u4E0B\u8F7D\u548C\u914D\u7F6E\u5F39\u5E55\u4E00\u4E0B"},{"level":2,"title":"\u8FDB\u4E00\u6B65\u4E86\u89E3","slug":"\u8FDB\u4E00\u6B65\u4E86\u89E3"},{"level":3,"title":"\u9047\u5230\u95EE\u9898\uFF1F","slug":"\u9047\u5230\u95EE\u9898\uFF1F"},{"level":3,"title":"\u53C2\u4E0E\u5F00\u53D1","slug":"\u53C2\u4E0E\u5F00\u53D1"}],"relativePath":"guide/index.md","lastUpdated":1640278705514}',K={},F=Object.assign(K,{setup(g){const t=_(N),p=y(()=>Object.keys(t.value));A(()=>{for(const[s,l]of Object.entries(t.value))for(const n of l)if(n.type==="rand"){const e=new Uint8Array(n.len/2);crypto.getRandomValues(e),n.value=T(e)}});const a=async()=>{const s=new S;for(const[e,o]of Object.entries(t.value)){const d=["# Generated with DanmakuIt Envfile Generator"];for(const u of o)d.push(`${u.name}=${u.value}`);s.file(e,d.join(`
`))}const l=await s.generateAsync({type:"blob"}),{saveAs:n}=await L(()=>import("./index.ccd2a8df.js").then(function(e){return e.i}),[]);n(l,"envfile.zip")};return(s,l)=>(r(),c("div",null,[O,i("div",B,[H,(r(!0),c(b,null,m(I(p),n=>(r(),c("form",U,[i("h4",V,k(n),1),(r(!0),c(b,null,m(t.value[n],e=>(r(),c("div",W,[i("label",{for:e.name,style:{"margin-right":"0.5rem","flex-grow":"0"}},k(e.field),9,j),E(i("input",{"onUpdate:modelValue":o=>e.value=o,name:e.name,style:{"flex-grow":"1"}},null,8,$),[[w,e.value]])]))),256))]))),256)),i("button",{onClick:a,style:{"margin-bottom":"1em"}},"\u4E0B\u8F7D\u914D\u7F6E")]),q]))}});export{z as __pageData,F as default};
