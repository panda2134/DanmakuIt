<template>
  <v-card>
    <v-card-title>
      已连接设备
      <v-spacer />
      <v-btn :loading="$fetchState.pending" icon @click="$fetch">
        <v-icon>mdi-refresh</v-icon>
      </v-btn>
    </v-card-title>
    <v-card-text>
      <v-row v-if="detailedConsumers.length">
        <v-col v-for="c in detailedConsumers" :key="c.id" cols="12" lg="3">
          <v-card outlined>
            <v-list>
              <v-list-item>
                <v-icon large color="success lighten-1">
                  mdi-circle-small
                </v-icon>
                <v-list-item-avatar tile>
                  <v-icon v-if="c.type === 'DanmakuWall'" large>
                    mdi-projector-screen
                  </v-icon>
                  <v-icon v-else-if="c.type === 'Censor'" large>
                    mdi-account-lock
                  </v-icon>
                  <v-icon v-else large>
                    mdi-laptop
                  </v-icon>
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title>{{ getDeviceTypeString(c.type) }}</v-list-item-title>
                  <v-list-item-subtitle>{{ c.id }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card>
        </v-col>
      </v-row>
      <span v-else>
        暂无在线设备。
      </span>
    </v-card-text>
  </v-card>
</template>
<script lang="ts">
import Vue from 'vue'
import { components } from '~/openapi/openapi'

type OnlineSubscription = components['schemas']['OnlineSubscription']

// from https://stackoverflow.com/questions/41253310/typescript-retrieve-element-type-information-from-array-type
type ArrayElement<ArrayType extends readonly unknown[]> =
  ArrayType extends readonly (infer ElementType)[] ? ElementType : never;

interface ConsumerData {
  type: string;
  id: string;
  detail: ArrayElement<OnlineSubscription['consumers']>;
}

export default Vue.extend({
  props: {
    roomId: {
      type: String,
      required: true
    }
  },
  data: () => ({
    subscriptions: [] as OnlineSubscription[],
    refreshHandle: null as (null | ReturnType<typeof setTimeout>)
  }),
  async fetch () {
    this.subscriptions = await this.$api['/room/{room_id}/consumers'].get(this.roomId)
  },
  computed: {
    detailedConsumers (): ConsumerData[] {
      const ret: ConsumerData[] = []
      for (const subscription of this.subscriptions) {
        const split = subscription.subscription_name.split('~', 2)
        subscription.consumers.forEach((x) => {
          ret.push({
            type: split[0],
            id: (split[0] === 'DanmakuWall' || split[0] === 'Censor') ? split[1] : split[0],
            detail: x
          })
        })
      }
      return ret
    }
  },
  mounted () {
    this.$fetch()
    this.refreshHandle = setInterval(() => { this.$fetch() }, 5000)
  },
  beforeDestroy () {
    if (this.refreshHandle) {
      clearInterval(this.refreshHandle)
    }
  },
  methods: {
    getDeviceTypeString (type: string): string {
      switch (type) {
        case 'DanmakuWall':
          return '弹幕墙'
        case 'Censor':
          return '审核员'
        default:
          return '客户端'
      }
    }
  }
})
</script>
