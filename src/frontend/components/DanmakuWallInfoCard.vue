<template>
  <v-card outlined>
    <v-card-title>
      弹幕墙信息
    </v-card-title>
    <v-card-text>
      <v-text-field :value="danmakuWallURL" readonly label="弹幕墙链接" outlined>
        <template #append>
          <nuxt-link v-slot="{ navigate }" :to="danmakuWallPath" custom>
            <v-btn
              icon
              depressed
              color="grey darken-2"
              @click="navigate"
            >
              <v-icon>mdi-open-in-new</v-icon>
            </v-btn>
          </nuxt-link>
        </template>
      </v-text-field>
      <v-text-field
        :value="passcode"
        label="房间密码"
        messages="请在登录弹幕墙时输入。"
        outlined
        readonly
      >
        <template #append>
          <v-btn
            icon
            depressed
            color="grey darken-2"
            @click="copyText(passcode)"
          >
            <v-icon>mdi-clipboard</v-icon>
          </v-btn>
        </template>
      </v-text-field>
    </v-card-text>
  </v-card>
</template>
<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  props: {
    roomId: {
      type: String,
      required: true
    },
    passcode: {
      type: String,
      required: true
    }
  },
  computed: {
    danmakuWallPath () {
      return '/wall/' + this.roomId + '?code=' + encodeURIComponent(this.passcode)
    },
    danmakuWallURL (): string {
      return location.origin + this.danmakuWallPath
    }
  },
  methods: {
    async copyText (text: string) {
      if (!process.browser) { return }
      await navigator.clipboard.writeText(text)
      this.$toast.success('已复制到剪贴板')
    }
  }
})
</script>
