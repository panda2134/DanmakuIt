<template>
  <v-container>
    <room-detail-header :room-id="room.room_id" :room-name="room.name" page-name="连接设备" />
    <device-info-card class="mb-5" :room-id="room.room_id" :passcode="room.room_passcode" />
    <connected-device-list-card class="mb-5" :room-id="room.room_id" />
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { Room } from '~/openapi/models'
import DeviceInfoCard from '~/components/DeviceInfoCard.vue'
import ConnectedDeviceListCard from '~/components/ConnectedDeviceListCard.vue'

export default Vue.extend({
  components: { DeviceInfoCard, ConnectedDeviceListCard },
  async asyncData ({ $api, params }) {
    const room = await $api['/room/{room_id}'].get(params.roomId)
    return { room }
  },
  data: () => ({ room: null } as {room: Room | null})
})
</script>
