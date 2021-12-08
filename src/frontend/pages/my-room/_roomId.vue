<template>
  <v-container>
    <portal to="nav">
      <v-btn text dark>
        房间信息
      </v-btn>
      <v-btn text dark>
        连接设备
      </v-btn>
      <v-btn text dark>
        弹幕审核
      </v-btn>
    </portal>
    <div v-if="$fetchState.pending">
      <v-skeleton-loader type="text" />
      <v-skeleton-loader type="article, paragraph@20" />
    </div>
    <div v-else>
      <v-breadcrumbs divider="/" :items="breadcrumbs" />
      <v-card outlined>
        <v-card-title>
          基本信息
        </v-card-title>
        <v-card-text>
          <v-form v-model="basicValid">
            <v-text-field v-model="roomUpdate.name" label="房间名称" :rules="[v => v ? true : '不能为空']" />
            <v-checkbox v-model="roomUpdate.danmaku_enabled" label="允许弹幕" />
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-btn :disabled="!basicValid" :loading="basicLoading" color="primary" @click="submitBasicInfo">
            提交
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { components } from '~/openapi/openapi'

type Room = components['schemas']['Room']
type RoomUpdate = components['schemas']['RoomUpdate']

interface RoomPageData {
  room: Room;
  roomUpdate: RoomUpdate;
  basicValid: boolean;
  basicLoading: boolean;
}

export default Vue.extend({
  data (): RoomPageData {
    return {
      room: {
        creation_time: '',
        name: '',
        pulsar_jwt: '',
        room_id: '',
        room_passcode: '',
        uid: '',
        wechat_token: '',
        danmaku_enabled: false,
        remote_censor: true,
        keyword_blacklist: [],
        wechat_encrypted: false,
        wechat_encryption_key: ''
      },
      roomUpdate: {
        name: '',
        danmaku_enabled: false
      },
      basicValid: true,
      basicLoading: false
    }
  },
  async fetch () {
    this.room = await this.$api['/room/{room_id}'].get(this.$route.params.roomId)
    Object.assign(this.roomUpdate, this.room)
  },
  computed: {
    breadcrumbs (): any[] {
      return [
        {
          link: true,
          text: '我的房间',
          to: '/my-room',
          exact: true
        },
        {
          text: this.room.name
        }
      ]
    }
  },
  methods: {
    async submitBasicInfo () {
      const roomUpdate: RoomUpdate = {
        name: this.roomUpdate.name,
        danmaku_enabled: this.roomUpdate.danmaku_enabled
      }
      this.basicLoading = true
      try {
        await this.$api['/room/{room_id}'].patch(roomUpdate, this.room.room_id)
        this.$toast.success('基本信息更新成功')
        this.$fetch()
      } catch (e) {
        this.$toast.error('请求错误：' + e)
      } finally {
        this.basicLoading = false
      }
    }
  }
})
</script>
