<template>
  <div id="danmakuWall" class="d-flex flex-column justify-space-between" style="height: 100vh">
    <v-row justify-lg="spaces-between" justify="end" class="flex-grow-0">
      <v-col xl="8" cols="12">
        <h1 class="display-3">
          {{ room.name }}
        </h1>
      </v-col>
      <v-col cols="4">
        <img width="100px" height="100px" src="~assets/qr.svg" alt="QR Placeholder" class="float-end">
      </v-col>
    </v-row>
    <div ref="danmakuBox" class="flex-grow-1 overflow-y-hidden d-flex flex-column justify-end">
      <transition-group name="danmaku-box--inner">
        <v-sheet
          v-for="danmaku in danmakuList"
          :key="danmaku.id"
          elevation="4"
          height="190"
          class="mt-8 d-flex flex-column justify-space-between pa-8"
          color="grey lighten-3"
          light
          tile
        >
          <h3 class="danmaku--user">{{ danmaku.sender }}</h3>
          <div class="danmaku--content">{{ danmaku.content }}</div>
        </v-sheet>
      </transition-group>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import { components } from '~/openapi/api'
import { throttle } from 'throttle-debounce'

type Room = components['schemas']['Room']
interface Danmaku {
  color: string;
  content: string;
  id: string;
  permission: '0' | '1';
  pos: 'rightleft' | 'top' | 'bottom',
  sender: string;
  size: string;
}

const danmakuItemOuterHeight = 190 + 48
function getEmptyDanmaku (): Danmaku {
  return {
    color: 'black',
    content: '微信发送消息上墙吧！',
    id: Math.random().toString(),
    permission: '1',
    pos: 'rightleft',
    sender: '神秘人',
    size: '16pt'
  }
}
function getRandomDanmaku (): Danmaku {
  return {
    color: 'black',
    content: Math.random().toString(),
    id: Math.random().toString(),
    permission: '1',
    pos: 'rightleft',
    sender: '神秘人',
    size: '16pt'
  }
}

export default Vue.extend({
  layout: 'fullpage',
  data () {
    // TODO: replace with API call
    const room: Room = {
      name: '软件学院2021“下一栈”学生节',
      uid: 'gitlab3rd:panda2134',
      danmaku_enabled: true,
      room_id: '8888888888',
      room_passcode: 'Adhere',
      creation_time: Date().toString(),
      pulsar_jwt: '123123',
      wechat_token: '123123'
    }
    const danmakuList: Danmaku[] = []
    return {
      room,
      danmakuList,
      availableSlotCount: 1
    }
  },
  head: {
    title: '弹幕墙'
  },
  mounted () {
    this.updateAvailableSlotCount()
    window.addEventListener('resize', throttle(300, this.updateAvailableSlotCount.bind(this)))
    setInterval(() => {
      const newDanmaku = getRandomDanmaku()
      this.danmakuList.splice(0, 1)
      this.danmakuList.push(newDanmaku)
    }, 1500)
  },
  methods: {
    updateAvailableSlotCount () {
      if (!this.$refs.danmakuBox) {
        return
      }
      const danmakuBox = (this.$refs.danmakuBox as HTMLDivElement)
      console.log(danmakuBox.clientHeight, danmakuItemOuterHeight)
      const newCount = (danmakuBox.clientHeight / danmakuItemOuterHeight) | 0
      if (this.availableSlotCount < newCount) {
        this.danmakuList.splice(0, 0,
          ...Array.from(Array(newCount - this.availableSlotCount), getEmptyDanmaku))
      } else if (this.availableSlotCount > newCount) {
        this.danmakuList.slice(newCount - this.availableSlotCount)
      }
      this.availableSlotCount = newCount
    }
  }
})
</script>

<style lang="scss" scoped>
@import '~vuetify/src/styles/main.sass';

$danmaku-transition-time: 0.6s;

#danmakuWall {
  background-image: url("/bg.png");
  background-attachment: fixed;
  background-size: cover;
  padding: 64px 53px;
  h1.display-3 {
    font-family: "ZCOOLKuaiLe", sans-serif !important;
    color: var(--v-secondary-base);
    font-weight: normal;
  }
  .danmaku--user, .danmaku--content {
    font-size: 48px;
  }
  .danmaku--user {
    color: map-get($indigo, 'lighten-1');
  }
  .danmaku--content {
    font-family: "ZCOOLKuaiLe", sans-serif !important;
  }
  .danmaku-box--inner-enter-active {
    transition: all $danmaku-transition-time;
  }
  .danmaku-box--inner-leave-active {
    transition: all $danmaku-transition-time ease-out;
  }
  .danmaku-box--inner-enter, .danmaku-box--inner-leave-to {
    opacity: 0;
  }
  .danmaku-box--inner-leave-to {
    transform: translateY(-256px);
  }
  .danmaku-box--inner-enter {
    transform: translateY(256px);
  }
  .danmaku-box--inner-move {
    transition: all $danmaku-transition-time;
  }
}
</style>
