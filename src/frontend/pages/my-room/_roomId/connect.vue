<template>
  <v-container>
    <room-detail-header :room-id="room.room_id" :room-name="room.name" />
    <consumer-info-card class="mb-5" :room-id="room.room_id" :passcode="room.room_passcode" />
    <connected-client-list-card class="mb-5" :room-id="room.room_id" />
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { Room } from '~/openapi/models'
import ConsumerInfoCard from '~/components/ConsumerInfoCard.vue'

export default Vue.extend({
  components: { ConsumerInfoCard },
  async asyncData ({ $api, params }) {
    const room = await $api['/room/{room_id}'].get(params.roomId)
    return { room }
  },
  data: () => ({ room: null } as {room: Room | null})
})
</script>
