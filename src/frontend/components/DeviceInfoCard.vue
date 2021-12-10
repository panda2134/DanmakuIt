<template>
  <v-card>
    <v-card-title>
      设备连接信息
    </v-card-title>
    <v-card-text>
      <v-text-field :value="danmakuWallURL" readonly label="弹幕墙链接" outlined>
        <template #append>
          <v-btn
            icon
            depressed
            color="grey darken-2"
            @click="openDanmakuWall"
          >
            <v-icon>mdi-open-in-new</v-icon>
          </v-btn>
        </template>
      </v-text-field>
      <v-text-field
        :value="roomId"
        label="房间号"
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
      <v-text-field
        :value="passcode"
        label="房间密码"
        messages="请在登录时输入。"
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
    },
    openDanmakuWall () {
      window.open(this.danmakuWallURL, '_blank')
    }
  }
})
</script>
