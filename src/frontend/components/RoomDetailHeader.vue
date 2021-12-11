<template>
  <div>
    <portal to="nav">
      <div class="d-none d-md-block">
        <portal-target name="nav--inner" />
      </div>
      <div class="d-md-none">
        <v-menu bottom offset-y>
          <template #activator="{ on, attrs }">
            <v-btn icon v-bind="attrs" v-on="on">
              <v-icon>mdi-menu</v-icon>
            </v-btn>
          </template>
          <v-card>
            <v-list nav>
              <portal-target name="nav--inner" />
            </v-list>
          </v-card>
        </v-menu>
      </div>
    </portal>
    <portal to="nav--inner">
      <div class="d-flex flex-md-row flex-column">
        <nuxt-link v-slot="{ navigate }" :to="roomInfoPath" custom>
          <v-btn text @click="navigate">
            房间信息
          </v-btn>
        </nuxt-link>
        <nuxt-link v-slot="{ navigate }" :to="roomConnectPath" custom>
          <v-btn text @click="navigate">
            连接设备
          </v-btn>
        </nuxt-link>
        <nuxt-link v-slot="{ navigate }" :to="roomCensorPath" custom>
          <v-btn text @click="navigate">
            弹幕审核
          </v-btn>
        </nuxt-link>
      </div>
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
    roomCensorPath () { return `/my-room/${this.roomId}/censor` },
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
