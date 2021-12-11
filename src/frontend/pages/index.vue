<template>
  <div>
    <v-container class="d-flex flex-column justify-center align-center" style="height: 100vh">
      <header class="d-flex flex-md-row flex-column justify-center align-center my-8">
        <!--suppress CheckImageSize -->
        <img srcset="/icon.webp 412w, /icon.png 412w" src="/icon.png" height="160" width="160" alt="icon">
        <h1 class="ml-md-12">
          弹幕一下
        </h1>
      </header>
      <div class="d-flex flex-row">
        <v-dialog max-width="400">
          <template #activator="{ on, attrs }">
            <v-btn
              depressed
              rounded
              color="primary"
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
              <v-btn depressed class="mr-2 my-1" color="primary" @click="$api['/user/social-login/github/login'].get()">
                <v-icon>mdi-github</v-icon>
                采用GitHub登录
              </v-btn>
              <v-btn depressed class="mr-2 my-1" color="primary" @click="$api['/user/social-login/gitlab/login'].get()">
                <v-icon>mdi-gitlab</v-icon>
                采用GitLab登录
              </v-btn>
              <v-btn depressed class="mr-2 my-1" color="primary" @click="$api['/user/social-login/gitlab3rd/login'].get(S)">
                <v-icon>mdi-gitlab</v-icon>
                采用校内GitLab登录
              </v-btn>
              <v-btn v-if="!commitSHA" depressed class="mr-2 my-1" color="secondary" @click="loadTestToken">
                [测试用]点击载入测试Token
              </v-btn>
            </v-card-text>
          </v-card>
        </v-dialog>
        <nuxt-link v-slot="{ navigate }" to="/my-room" custom>
          <v-btn rounded outlined color="primary" class="mx-2" @click="navigate">
            管理房间
          </v-btn>
        </nuxt-link>
      </div>
    </v-container>
    <v-footer fixed>
      &copy; {{ new Date().getFullYear() }}, DanmakuIt Team. Licensed under GPLv3.
      <span v-if="commitSHA">
        Commit <a :href="commitURL" target="_blank">{{ shortSHA }}</a>.
      </span>
      <span v-else class="light-blue--text text-uppercase">
        Development environment.
      </span>
    </v-footer>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  layout: 'fullpage',
  data () {
    return {
      commitSHA: process.env.GITHUB_SHA || ''
    }
  },
  computed: {
    shortSHA (): string {
      return (this.commitSHA).slice(0, 8)
    },
    commitURL (): string {
      return `https://github.com/panda2134/DanmakuIt/commit/${this.commitSHA}`
    }
  },
  methods: {
    loadTestToken () {
      if (process.env.TEST_TOKEN) {
        this.$axios.setToken(process.env.TEST_TOKEN, 'Bearer')
        localStorage.setItem('token', process.env.TEST_TOKEN)
        this.$toast.success('已经载入测试Token')
      } else {
        this.$toast.error('测试Token未找到')
      }
    }
  }
})
</script>

<style lang="scss" scoped>
h1 {
  font-size: 72px;
  font-family: "ZCOOL KuaiLe", cursive;
  font-weight: 400;
  color: var(--v-secondary-base);
}
</style>
