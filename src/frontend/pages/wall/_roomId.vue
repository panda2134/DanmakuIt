<!--suppress JSUnusedGlobalSymbols -->
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
          <v-otp-input
            v-model="passcodeInput"
            :plain="passcodeLength > 8"
            :length="passcodeLength"
            autofocus
            @finish="$fetch"
          />
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
        <div>
          <v-img :src="qrCodePath" width="150px" height="150px" class="float-end">
            <template #placeholder>
              <img width="150px" height="150px" src="~assets/qr.svg" alt="QR Placeholder">
            </template>
          </v-img>
        </div>
        <div>
          <v-img :src="mpCode" width="150px" height="150px" class="float-end">
            <template #placeholder>
              <img width="150px" height="150px" src="~assets/qr.svg" alt="MP Placeholder">
            </template>
          </v-img>
        </div>
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
          <v-list-item three-line>
            <v-list-item-avatar tile size="100">
              <v-img eager :src="getUserInfo(danmaku.sender).headimgurl" />
            </v-list-item-avatar>
            <v-list-item-content>
              <h3 class="danmaku--user">
                {{ getUserInfo(danmaku.sender).nickname }}
              </h3>
              <div class="danmaku--content">
                {{ danmaku.content }}
              </div>
            </v-list-item-content>
          </v-list-item>
        </v-sheet>
      </transition-group>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import { throttle } from 'throttle-debounce'
import { components } from '~/openapi/openapi'
import {
  Danmaku,
  PulsarEvent,
  DanmakuWallClient,
  DanmakuUserInfoCacheClient,
  UserInfo
} from '~/websocket/DanmakuWallClient'

type Room = components['schemas']['Room']

interface WallData {
  room: Room;
  danmakuList: Danmaku[];
  availableSlotCount: number;
  wsDanmaku: DanmakuWallClient | null;
  userInfoCache: DanmakuUserInfoCacheClient | null;
  retryHandle: ReturnType<typeof setInterval>;
  passcodeInput: string;
  showPasscodeDialog: boolean;
  qrCodeTicket: string;
  mpCode: string;
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

// noinspection JSUnusedGlobalSymbols
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
      wsDanmaku: null,
      userInfoCache: null,
      retryHandle: setInterval(() => {}, 1e10), // noop
      passcodeInput: '',
      showPasscodeDialog: false,
      qrCodeTicket: '',
      mpCode: ''
    }
  },
  async fetch () {
    const roomId = this.$route.params.roomId
    const roomPasscode = this.passcodeInput || this.$route.query.code
    try {
      // eslint-disable-next-line camelcase
      this.room = await this.$api['/room/{room_id}/client-login'].get(roomId, roomPasscode)
      try {
        this.qrCodeTicket = (await this.$api['/room/{room_id}/qrcode'].get(roomId, roomPasscode)).ticket
      } catch (e) {
        this.$toast.error('获取二维码失败，可能是AppId/AppSecret填写错误')
      }
      try {
        this.mpCode = (await this.$api['/room/{room_id}/mpcode'].get(roomId, roomPasscode)).image_dataurl
      } catch (e) {
        this.$toast.error('获取小程序码失败，可能是AppId/AppSecret填写错误')
      }

      // @ts-ignore
      await new Promise<void>((resolve, reject) => {
        this.wsDanmaku = new DanmakuWallClient(
          this.room.room_id,
          this.room.pulsar_jwt,
          this.handleDanmaku.bind(this),
          () => {
            this.$toast('连接成功', { color: 'green' })
            this.userInfoCache = new DanmakuUserInfoCacheClient(this.room.room_id, this.room.pulsar_jwt)
            resolve()
          },
          () => {
            this.$toast('与服务器连接断开，重试中...', { color: 'red' })
          },
          (ev) => {
            this.$toast('与服务器连接断开，重试中...', { color: 'red' })
            reject(ev)
          }
        )
      })
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
    handleDanmaku (danmakuEvent: PulsarEvent<Danmaku>) {
      if (danmakuEvent.properties.permission === '1') {
        this.danmakuList.splice(0, 1)
        this.danmakuList.push(danmakuEvent.properties)
      } else if (danmakuEvent.payload === UpdateDanmaku && danmakuEvent.properties.permission === '0') {
        // take off this danmaku
        this.danmakuList = this.danmakuList.map(danmaku =>
          danmaku.id !== danmakuEvent.properties.id ? danmaku : getEmptyDanmaku())
      }
    },
    getUserInfo (id: string): UserInfo {
      const anonymousUser = {
        id: 'anonymous',
        nickname: '神秘人',
        headimgurl: '/anonymous.png'
      }
      const adminUser = {
        id: 'admin',
        nickname: '管理员',
        headimgurl: '/admin.png'
      }
      const localCache = [anonymousUser, adminUser]
      if (this.userInfoCache == null) {
        return anonymousUser
      }
      const userInfo = this.userInfoCache.getUserInfo(id)

      return userInfo || localCache.find(x => x.id === id) || anonymousUser
    }
  }
})
</script>

<style lang="scss" scoped>
/* @import '~vuetify/src/styles/main.sass'; */

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
    /* color: map-get($indigo, 'lighten-1'); */
    color: #5c6bc0; /* hardcode to reduce bundle size */
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
