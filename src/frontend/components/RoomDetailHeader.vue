<template>
  <div>
    <portal to="nav">
      <nuxt-link v-slot="{ navigate }" :to="roomInfoPath" custom>
        <v-btn text dark @click="navigate">
          房间信息
        </v-btn>
      </nuxt-link>
      <nuxt-link v-slot="{ navigate }" :to="roomConnectPath" custom>
        <v-btn text dark @click="navigate">
          连接设备
        </v-btn>
      </nuxt-link>
      <v-btn text dark>
        弹幕审核
      </v-btn>
    </portal>
    <v-breadcrumbs divider="/" :items="breadcrumbs" />
  </div>
</template>
<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  props: {
    roomId: {
      type: String,
      required: true
    },
    roomName: {
      type: String,
      required: true
    }
  },
  computed: {
    roomInfoPath () { return `/my-room/${this.roomId}` },
    roomConnectPath () { return `/my-room/${this.roomId}/connect` },
    breadcrumbs (): any[] {
      return [
        {
          link: true,
          text: '我的房间',
          to: '/my-room',
          exact: true
        },
        {
          text: this.roomName
        }
      ]
    }
  }
})
</script>
