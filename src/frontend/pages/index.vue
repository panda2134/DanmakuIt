<template>
  <div>
    <v-container class="d-flex flex-column justify-center align-center" style="height: 100vh">
      <header class="d-flex flex-row align-center my-8">
        <!--suppress CheckImageSize -->
        <img src="../assets/icon.png" height="160" width="160" alt="icon">
        <h1 class="ml-12">
          弹幕一下
        </h1>
      </header>
      <div class="d-flex flex-row">
        <v-dialog max-width="400">
          <template #activator="{ on, attrs }">
            <v-btn
              depressed
              rounded
              color="secondary"
              class="mx-2"
              v-bind="attrs"
              v-on="on"
            >
              注册登录
            </v-btn>
          </template>
          <v-card>
            <v-card-title>登录</v-card-title>
            <v-card-text>
              <v-btn depressed class="mr-2 my-1" color="secondary" @click="$api['/user/social-login/github/login'].get()">
                <v-icon>mdi-github</v-icon>
                采用GitHub登录
              </v-btn>
              <v-btn depressed class="mr-2 my-1" color="secondary" @click="$api['/user/social-login/gitlab/login'].get()">
                <v-icon>mdi-gitlab</v-icon>
                采用GitLab登录
              </v-btn>
              <v-btn depressed class="mr-2 my-1" color="secondary" @click="$api['/user/social-login/gitlab3rd/login'].get(S)">
                <v-icon>mdi-gitlab</v-icon>
                采用校内GitLab登录
              </v-btn>
            </v-card-text>
          </v-card>
        </v-dialog>
        <v-btn rounded outlined color="secondary" class="mx-2">
          管理房间
        </v-btn>
      </div>
    </v-container>
    <v-footer fixed>
      &copy; {{ new Date().getFullYear() }}, DanmakuIt Team. Licensed under GPLv3. Commit {{ commitSHA }}.
    </v-footer>
  </div>
</template>

<script>
export default {
  layout: 'fullpage',
  data () {
    return {
      commitSHA: process.env.NUXT_ENV_GIT_SHA || '#dev#'
    }
  }
}
</script>

<style lang="scss" scoped>
h1 {
  font-size: 72px;
  font-family: "ZCOOLKuaiLe", sans-serif;
  font-weight: 400;
  color: var(--v-primary-base);
}
</style>
