<template>
  <v-container>
    <room-detail-header :room-id="room.room_id" :room-name="room.name" />
    <basic-info-card
      class="mb-5"
      :room-id="room.room_id"
      :initial-name="room.name"
      :initial-danmaku-enabled="room.danmaku_enabled"
      @room-update="$fetch"
    />
    <wechat-official-account-info-card
      class="mb-5"
      :room-id="room.room_id"
      :initial-wechat-appid="room.wechat_appid"
      :initial-wechat-app-secret="room.wechat_appsecret"
      :initial-wechat-token="room.wechat_token"
      @room-update="$fetch"
    />
    <fetch-subscriber-card :room-id="room.room_id" />
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { Room, RoomUpdate } from '~/openapi/models'
import RoomDetailHeader from '~/components/RoomDetailHeader.vue'
import BasicInfoCard from '~/components/BasicInfoCard.vue'
import WechatOfficialAccountInfoCard from '~/components/WechatOfficialAccountInfoCard.vue'

interface RoomPageData {
  room?: Room | null;
  roomUpdate?: RoomUpdate | null;
  basicValid: boolean;
  basicLoading: boolean;
  wechatValid: boolean;
  wechatLoading: boolean;
}

export default Vue.extend({
  components: { BasicInfoCard, RoomDetailHeader, WechatOfficialAccountInfoCard },
  async asyncData (ctx): Promise<{room: Room, roomUpdate: RoomUpdate}> {
    const room = await ctx.$api['/room/{room_id}'].get(ctx.params.roomId)
    const roomUpdate = Object.assign({}, room)
    return {
      room,
      roomUpdate
    }
  },
  data: () => ({
    room: null,
    roomUpdate: null,
    basicValid: true,
    basicLoading: false,
    wechatValid: true,
    wechatLoading: false
  } as RoomPageData),
  async fetch () {
    this.room = await this.$api['/room/{room_id}'].get(this.$route.params.roomId)
    Object.assign(this.roomUpdate, this.room)
  }
})
</script>
