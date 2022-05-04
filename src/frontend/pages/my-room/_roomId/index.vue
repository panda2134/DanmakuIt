<template>
  <v-container>
    <room-detail-header :room-id="room.room_id" :room-name="room.name" />
    <v-alert
      v-if="showNoAppSecretError"
      type="error"
      dense
      elevation="1"
    >
      尚未设置微信公众号AppID/AppSecret，公众号二维码显示功能将不会工作。
    </v-alert>
    <basic-info-card
      class="mb-5"
      :room-id="room.room_id"
      :initial-name="room.name"
      :initial-danmaku-enabled="room.danmaku_enabled"
      :initial-colors="room.user_danmaku_colors"
      @room-update="$fetch"
    />
    <wechat-official-account-info-card
      class="mb-5"
      :room-id="room.room_id"
      :wechat-token="room.wechat_token"
      :initial-wechat-appid="room.wechat_appid"
      :initial-wechat-app-secret="room.wechat_appsecret"
      @room-update="$fetch"
    />
    <fetch-subscriber-card :room-id="room.room_id" class="mb-5" />
    <censor-config-card
      :room-id="room.room_id"
      :initial-auto-censor="room.remote_censor"
      :initial-keywords="room.keyword_blacklist"
      @room-update="$fetch"
    />
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
  },
  computed: {
    showNoAppSecretError () {
      return !(this.room?.wechat_appid && this.room?.wechat_appsecret)
    }
  }
})
</script>
