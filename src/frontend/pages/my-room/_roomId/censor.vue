<template>
  <v-container>
    <room-detail-header :room-id="room.room_id" :room-name="room.name" page-name="弹幕审核" />
    <admin-danmaku-card :room-id="room.room_id" class="mb-5" />
    <danmaku-censor :room-id="room.room_id" />
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { Room } from '~/openapi/models'

export default Vue.extend({
  async asyncData ({ $api, params }) {
    const room = await $api['/room/{room_id}'].get(params.roomId)
    return { room }
  },
  data: () => ({ room: null } as {room: Room | null})
})
</script>
