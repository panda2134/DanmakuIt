<template>
  <v-card>
    <v-card-title>
      弹幕审核
      <v-spacer />
      <v-icon large :color="connected ? 'success' : 'error'">
        mdi-circle-small
      </v-icon>
      <span class="text-caption">{{ connected ? '已连接' : '连接中' }}</span>
    </v-card-title>
    <v-card-text>
      <v-data-table
        :headers="headers"
        :items="danmakuList"
        sort-by="time"
        sort-desc
        item-key="id"
      >
        <template v-slot:item.id="{ item }">
          {{ item.id.substr(0, 8) + '...' }}
        </template>
        <template v-slot:item.time="{ item }">
          {{ item.time.toLocaleString() }}
        </template>
        <template v-slot:item.avatar="{ item }">
          <v-avatar tile size="36">
            <v-img :src="item.avatar" />
          </v-avatar>
        </template>
        <template v-slot:item.pass="{ item }">
          <v-simple-checkbox :ripple="false" :value="item.pass" @click="toggleCensor(item)" />
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import copy from 'fast-copy'
import { DanmakuWallClient, DanmakuUserInfoCacheClient, PulsarEvent, Danmaku } from '~/websocket/DanmakuWallClient'

interface CensorItem {
  id: string;
  avatar: string;
  username: string;
  content: string;
  pass: boolean;
  time: Date;
  originalData: Danmaku;
}

interface CensorData {
  wsDanmaku: DanmakuWallClient | null;
  wsUserInfo: DanmakuUserInfoCacheClient | null;
  connected: boolean;
  danmakuList: CensorItem[];
  headers: {
    text: string;
    value: string;
    align?: string;
    sortable?: boolean
  }[]
}

export default Vue.extend({
  name: 'DanmakuCensor',
  props: {
    roomId: {
      type: String,
      required: true
    }
  },
  data (): CensorData {
    return {
      wsDanmaku: null,
      wsUserInfo: null,
      connected: false,
      danmakuList: [],
      headers: [{ text: '#id', value: 'id' }, { text: '时间', value: 'time', sortable: true },
        { text: '头像', value: 'avatar' },
        { text: '发送人', value: 'username' }, { text: '内容', value: 'content' },
        { text: '审核通过', value: 'pass' }]
    }
  },
  async fetch () {
    const room = await this.$api['/room/{room_id}'].get(this.roomId)
    this.wsDanmaku = new DanmakuWallClient(
      this.roomId, room.pulsar_jwt,
      (ev) => { this.handleDanmaku(ev) },
      () => { this.connected = true },
      () => { this.connected = false },
      () => {
        this.$toast.error('无法连接到弹幕服务器，重试中...')
        this.connected = false
      },
      'Censor'
    )
    this.wsUserInfo = new DanmakuUserInfoCacheClient(this.roomId, room.pulsar_jwt)
  },
  methods: {
    handleDanmaku (ev: PulsarEvent<Danmaku>) {
      if (ev.payload === 'AAAB') {
        return // update danmaku
      }
      const danmaku = ev.properties
      const userInfo = this.wsUserInfo?.getUserInfo(danmaku.sender)
      if (!danmaku.id) {
        return
      }
      this.danmakuList.push({
        id: danmaku.id,
        time: new Date(ev.publishTime),
        avatar: danmaku.sender === 'admin' ? '/admin.png' : (userInfo?.headimgurl ?? ''),
        username: danmaku.sender === 'admin' ? '管理员' : (userInfo?.nickname ?? danmaku.sender),
        content: danmaku.content,
        pass: danmaku.permission === '1',
        originalData: danmaku
      })
    },
    async toggleCensor (item: CensorItem) {
      try {
        const newPass = !item.pass
        const danmakuAltered = Object.assign(copy(item.originalData), { permission: newPass ? '1' : '0' })
        await this.$api['/room/{room_id}/danmaku-update'].post(danmakuAltered, this.roomId)
        item.pass = newPass
        this.$toast.success('修改弹幕成功')
      } catch (e) {
        this.$toast.error('修改弹幕失败：' + e)
        throw e
      }
    }
  }
})
</script>

<style scoped>

</style>