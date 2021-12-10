<template>
  <v-app-bar elevation="4" color="primary" dark app>
    <nuxt-link v-slot="{ navigate }" custom to="/">
      <v-app-bar-nav-icon @click="navigate">
        <v-img srcset="/icon.webp 412w, /icon.png 412w" src="/icon.webp" contain :max-width="32" :max-height="32" />
      </v-app-bar-nav-icon>
    </nuxt-link>
    <v-toolbar-title>
      弹幕一下
    </v-toolbar-title>
    <v-spacer />
    <portal-target name="nav" />
    <v-menu bottom offset-y>
      <template #activator="{ on, attrs }">
        <v-btn icon v-bind="attrs" v-on="on">
          <v-icon>mdi-account</v-icon>
        </v-btn>
      </template>
      <v-card>
        <v-list nav>
          <v-list-item>
            <v-list-item-avatar>
              <v-img
                :src="user.avatar"
                :alt="user.username"
              >
                <template #placeholder>
                  <v-progress-circular indeterminate color="primary" />
                </template>
              </v-img>
            </v-list-item-avatar>
            <v-list-item-content>
              <v-list-item-title class="text-h6">
                {{ user.username }}
              </v-list-item-title>
              <v-list-item-subtitle>{{ user.uid }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list>
        <v-divider />
        <v-list nav dense>
          <nuxt-link v-slot="{ navigate }" to="/my-room" custom>
            <v-list-item @click="navigate">
              <v-list-item-icon>
                <v-icon>mdi-format-list-bulleted-type</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                我的房间
              </v-list-item-content>
            </v-list-item>
          </nuxt-link>
          <nuxt-link v-slot="{ navigate }" to="/logout" custom>
            <v-list-item @click="navigate">
              <v-list-item-icon>
                <v-icon>mdi-logout</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                退出登录
              </v-list-item-content>
            </v-list-item>
          </nuxt-link>
        </v-list>
      </v-card>
    </v-menu>
  </v-app-bar>
</template>
<script lang="ts">
import Vue from 'vue'
import { components } from '~/openapi/openapi'

export default Vue.extend({
  data (): { user: components['schemas']['User'] } {
    return {
      user: {
        uid: '',
        username: '',
        avatar: ''
      }
    }
  },
  async fetch () {
    this.user = await this.$api['/user/me'].get()
  }
})
</script>
