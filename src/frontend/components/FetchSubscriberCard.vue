<template>
  <v-card>
    <v-card-title>
      抓取关注者信息
    </v-card-title>
    <v-card-text>
      <!-- 对于新创建的房间，最好对现有关注者信息进行抓取。在此前，要先设置好AppID和AppSecret。 -->
      受微信平台策略限制，无法从公众号获得用户头像和昵称。如需展示用户头像和昵称，请部署并使用小程序。
    </v-card-text>
    <v-divider />
    <v-card-actions>
      <v-btn text disabled :loading="fetchingSubscribers" color="primary" @click="doFetchSubscribers">
        抓取
      </v-btn>
    </v-card-actions>
  </v-card>
</template>
<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  props: {
    roomId: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      fetchingSubscribers: false
    }
  },
  methods: {
    async doFetchSubscribers (): Promise<void> {
      try {
        this.fetchingSubscribers = true
        await this.$api['/room/{room_id}/fetch-subscribers'].post(this.roomId)
        this.$toast.success('已开始抓取')
      } catch (e) {
        this.$toast.error('请求错误：' + e)
        throw e
      } finally {
        this.fetchingSubscribers = false
      }
    }
  }
})
</script>
