<template>
  <div id="danmakuWall" class="d-flex flex-column justify-space-between" style="height: 100vh">
    <v-dialog v-model="showPasscodeDialog" max-width="600" persistent>
      <v-card>
        <v-card-title>
          输入房间密码
        </v-card-title>
        <v-card-subtitle>
          {{ passcodeLength }} 位字母数字组合
        </v-card-subtitle>
        <v-card-text>
          <v-otp-input v-model="passcodeInput" :plain="passcodeLength > 8" :length="passcodeLength" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text color="primary" @click="$fetch">
            登录
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-row justify-lg="space-between" justify="end" class="flex-grow-0">
      <v-col xl="8" cols="12">
        <h1 class="display-3">
          {{ room.name }}
        </h1>
      </v-col>
      <v-col xl="4" cols="12">
        <v-img :src="qrCodePath" width="100px" height="100px" class="float-end">
          <template #placeholder>
            <img width="100px" height="100px" src="~assets/qr.svg" alt="QR Placeholder">
          </template>
        </v-img>
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
          <h3 class="danmaku--user">
            {{ danmaku.sender }}
          </h3>
          <div class="danmaku--content">
            {{ danmaku.content }}
          </div>
        </v-sheet>
      </transition-group>
    </div>
  </div>
</template>

<script lang="ts">
import { nanoid } from 'nanoid'
import Vue from 'vue'
import { throttle } from 'throttle-debounce'
import { components } from '~/openapi/openapi'

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

interface WallData {
  room: Room;
  danmakuList: Danmaku[];
  availableSlotCount: number;
  ws: WebSocket | null;
  retryHandle: ReturnType<typeof setInterval>;
  passcodeInput: string;
  showPasscodeDialog: boolean;
  qrCodeTicket: string;
}
interface DanmakuEvent {
  messageId: string;
  payload: 'AAAA' | 'AAAB'; // new danmaku / danmaku update, respectively
  properties: Danmaku;
  publishTime: string; // Time in ISO8601
  redeliveryCount: number;
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const NewDanmaku = 'AAAA'
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const UpdateDanmaku = 'AAAB'

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
export default Vue.extend({
  layout: 'fullpage',
  data (): WallData {
    const emptyRoom: Room = {
      name: '加载中',
      uid: 'uid',
      danmaku_enabled: true,
      room_id: '8888888888',
      room_passcode: 'QWERTY',
      creation_time: Date().toString(),
      pulsar_jwt: 'placeholder',
      wechat_token: 'placeholder'
    }
    return {
      room: emptyRoom,
      danmakuList: [],
      availableSlotCount: 0,
      ws: null,
      retryHandle: setInterval(() => {}, 1e10), // noop
      passcodeInput: '',
      showPasscodeDialog: false,
      qrCodeTicket: ''
    }
  },
  async fetch () {
    const roomId = this.$route.params.roomId
    const roomPasscode = this.passcodeInput || this.$route.query.code
    try {
      // eslint-disable-next-line camelcase
      this.room = await this.$api['/room/{room_id}/client-login'].get(roomId, roomPasscode)
      this.qrCodeTicket = (await this.$api['/room/{room_id}/qrcode'].get(roomId, roomPasscode)).ticket
      // @ts-ignore
      await this.initWebSocket()
      this.showPasscodeDialog = false
    } catch (e) {
      // failed to do a "client login", ask the user to type passcode
      this.$toast.error('客户端登录失败')
      this.showPasscodeDialog = true
    }
  },
  head: {
    title: '弹幕墙'
  },
  computed: {
    passcodeLength () { return parseInt(process.env.ROOM_PASSCODE_LEN || '6') },
    qrCodePath (): string { return `https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=${this.qrCodeTicket}` }
  },
  mounted () {
    this.updateAvailableSlotCount()
    window.addEventListener('resize', throttle(300, this.updateAvailableSlotCount.bind(this)))
  },
  methods: {
    initWebSocket () {
      if (this.ws) {
        this.ws.close()
      }
      const subscriptionName = 'DanmakuWall' + '~' + nanoid()
      // eslint-disable-next-line camelcase
      this.ws = new WebSocket(`wss://danmakuit.panda2134.site/websocket/consumer/persistent/public/default/${this.room.room_id}/${subscriptionName}?token=${this.room.pulsar_jwt}`)
      this.ws.onmessage = (msg) => {
        const pulsarData = JSON.parse(msg.data)
        if (pulsarData.messageId) {
          // we've met a danmaku event
          this.ws!.send(JSON.stringify({ messageId: pulsarData.messageId })) // ACK
          this.handleDanmaku(pulsarData)
        }
      }

      return new Promise<void>((resolve, reject) => {
        const closeHandler = () => {
          clearInterval(this.retryHandle)
          this.$toast('与服务器连接断开，重试中...', { color: 'red' })
          this.ws!.removeEventListener('close', closeHandler)
          this.retryHandle = setInterval(() => {
            this.initWebSocket()
          }, 5000)
        }
        const errorHandler = (ev: Event) => {
          closeHandler()
          reject(ev)
        }
        this.ws!.onerror = errorHandler
        this.ws!.onopen = () => {
          clearInterval(this.retryHandle)
          this.$toast('连接成功', { color: 'green' })
          this.ws!.removeEventListener('error', errorHandler)
          this.setWebSocketKeepAlive()
          this.ws!.addEventListener('close', closeHandler)
          resolve()
        }
      })
    },
    updateAvailableSlotCount () {
      if (!this.$refs.danmakuBox) {
        return
      }
      const danmakuBox = (this.$refs.danmakuBox as HTMLDivElement)
      const newCount = Math.max((danmakuBox.clientHeight / danmakuItemOuterHeight) | 0, 2)
      if (this.availableSlotCount < newCount) {
        this.danmakuList.splice(0, 0,
          ...Array.from(Array(newCount - this.availableSlotCount), getEmptyDanmaku))
      } else if (this.availableSlotCount > newCount) {
        this.danmakuList.slice(-newCount)
      }
      this.availableSlotCount = newCount
    },
    setWebSocketKeepAlive () {
      const keepAlive = () => {
        if (!this.ws) {
          throw new Error('WebSocket is still null!')
        } else {
          this.ws.send(JSON.stringify({ type: 'isEndOfTopic' }))
        }
      }
      keepAlive()
      setInterval(keepAlive, 1000)
    },
    handleDanmaku (danmakuEvent: DanmakuEvent) {
      if (danmakuEvent.properties.permission === '1') {
        this.danmakuList.splice(0, 1)
        this.danmakuList.push(danmakuEvent.properties)
      } else if (danmakuEvent.payload === UpdateDanmaku && danmakuEvent.properties.permission === '0') {
        // take off this danmaku
        this.danmakuList = this.danmakuList.map(danmaku =>
          danmaku.id !== danmakuEvent.properties.id ? danmaku : getEmptyDanmaku())
      }
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
    font-family: "ZCOOL KuaiLe", sans-serif !important;
    color: var(--v-primary-base);
    font-weight: normal;
  }
  .danmaku--user, .danmaku--content {
    font-size: 48px;
  }
  .danmaku--user {
    color: map-get($indigo, 'lighten-1');
  }
  .danmaku--content {
    font-family: "ZCOOL KuaiLe", sans-serif !important;
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
