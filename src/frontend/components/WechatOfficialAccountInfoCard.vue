<template>
  <v-card outlined>
    <v-card-title>
      微信公众号
    </v-card-title>
    <v-card-text>
      <v-form v-model="wechatValid">
        <v-text-field
          :value="wechatCallbackURL"
          label="回调地址"
          messages="由平台自动生成，请填入微信公众号管理页面。暂时不支持设置消息加密。"
          outlined
          readonly
        >
          <template #append>
            <v-btn
              icon
              depressed
              color="grey darken-2"
              @click="copyText(wechatCallbackURL)"
            >
              <v-icon>mdi-clipboard</v-icon>
            </v-btn>
          </template>
        </v-text-field>
        <v-text-field
          :value="wechat_token"
          label="Token"
          messages="请填入微信公众号管理页面。"
          outlined
          readonly
        >
          <template #append>
            <v-btn
              icon
              depressed
              color="grey darken-2"
              @click="copyText(wechat_token)"
            >
              <v-icon>mdi-clipboard</v-icon>
            </v-btn>
          </template>
        </v-text-field>
        <v-text-field v-model="wechat_appid" outlined label="AppID" />
        <v-text-field v-model="wechat_appsecret" outlined label="AppSecret" />
      </v-form>
    </v-card-text>
    <v-divider />
    <v-card-actions>
      <v-btn :disabled="!wechatValid" :loading="wechatLoading" text color="primary" @click="submitWeChatInfo">
        提交
      </v-btn>
    </v-card-actions>
  </v-card>
</template>
<script lang="ts">
import Vue from 'vue'
import { RoomUpdate } from '~/openapi/models'

export default Vue.extend({
  props: {
    roomId: {
      type: String,
      required: true
    },
    initialWechatToken: {
      type: String,
      required: true
    },
    initialWechatAppid: {
      validator: x => (typeof x === 'string' || (x == null)),
      required: true
    },
    initialWechatAppSecret: {
      validator: x => (typeof x === 'string' || (x == null)),
      required: true
    }
  },
  data () {
    return {
      wechatValid: true,
      wechatLoading: false,
      wechat_appid: this.initialWechatAppid,
      wechat_appsecret: this.initialWechatAppSecret,
      wechat_token: this.initialWechatToken
    }
  },
  computed: {
    wechatCallbackURL (): string {
      return process.env.WECHAT_CALLBACK_URL_BASE + this.roomId
    }
  },
  methods: {
    async copyText (text: string) {
      if (!process.browser) { return }
      await navigator.clipboard.writeText(text)
      this.$toast.success('已复制到剪贴板')
    },
    async submitWeChatInfo () {
      const roomUpdate: RoomUpdate = {
        wechat_appid: this.wechat_appid as string|undefined,
        wechat_appsecret: this.wechat_appsecret as string|undefined
      }
      try {
        this.wechatLoading = true
        await this.$api['/room/{room_id}'].patch(roomUpdate, this.roomId)
        this.$toast.success('微信公众号配置更新成功')
        this.$emit('room-update')
      } catch (e) {
        this.$toast.error('请求错误：' + e)
        throw e
      } finally {
        this.wechatLoading = false
      }
    }
  }

})
</script>
