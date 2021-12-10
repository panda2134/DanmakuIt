import { nanoid } from 'nanoid'
import ReconnectingWebSocket from 'reconnecting-websocket'

const dummyHandler = () => {}

export interface Danmaku {
  color: string;
  content: string;
  id: string;
  permission: '0' | '1';
  pos: 'rightleft' | 'top' | 'bottom',
  sender: string;
  size: string;
}

export interface PulsarEvent<T> {
  messageId: string;
  payload: string; // AAAA = new danmaku / AAAB = danmaku update, respectively
  properties: T;
  publishTime: string; // Time in ISO8601
  redeliveryCount: number;
}

export interface UserInfo {
  headimgurl: string;
  id: string;
  nickname: string;
}

function setWebSocketKeepAlive (ws?: WebSocket | ReconnectingWebSocket) {
  const keepAlive = () => {
    if (!ws) {
      throw new Error('WebSocket is still null!')
    } else {
      ws.send(JSON.stringify({ type: 'isEndOfTopic' }))
    }
  }
  keepAlive()
  return setInterval(keepAlive, 1000)
}

export class DanmakuUserInfoCacheClient {
  private readonly wsUserInfo: ReconnectingWebSocket
  private userInfoMap: Map<string, UserInfo>
  private keepAliveTimer?: ReturnType<typeof setInterval>
  constructor (public readonly roomId: string, public readonly pulsarJWT: string) {
    this.userInfoMap = new Map<string, UserInfo>()
    const url = 'wss://danmakuit.panda2134.site/websocket/' +
      `reader/persistent/public/default/user_${this.roomId}` +
      `?messageId=earliest&token=${this.pulsarJWT}`
    this.wsUserInfo = new ReconnectingWebSocket(url)
    this.wsUserInfo.onopen = () => {
      this.keepAliveTimer = setWebSocketKeepAlive(this.wsUserInfo)
    }
    this.wsUserInfo.onclose = () => {
      if (this.keepAliveTimer) {
        clearInterval(this.keepAliveTimer)
      }
    }
    this.wsUserInfo.onmessage = (msg) => {
      const pulsarData = JSON.parse(msg.data)
      if (pulsarData.messageId) {
        // we've met a userinfo event
        this.wsUserInfo.send(JSON.stringify({ messageId: pulsarData.messageId })) // ACK
        this.handleUserInfo(pulsarData)
      }
    }
  }

  public close () {
    this.wsUserInfo.close()
    if (this.keepAliveTimer) {
      clearInterval(this.keepAliveTimer)
    }
  }

  private handleUserInfo (ev: PulsarEvent<UserInfo>) {
    this.userInfoMap.set(ev.properties.id, ev.properties)
  }

  public getUserInfo (id: string) {
    return this.userInfoMap.get(id)
  }
}

export class DanmakuWallClient {
  private wsDanmaku?: WebSocket
  private retryHandle?: ReturnType<typeof setInterval>
  private keepAliveHandle?: ReturnType<typeof setInterval>
  constructor (public readonly roomId: string, public readonly pulsarJWT: string,
               public onDanmaku: (o: PulsarEvent<Danmaku>) => void = dummyHandler,
               public onConnected: () => void = dummyHandler,
               public onDisconnect: () => void = dummyHandler,
               public onConnectionFail: (ev: Event) => void = dummyHandler,
               public readonly subscriptionNamePrefix: 'DanmakuWall' | 'Censor' = 'DanmakuWall') {
    this.initWebSocket()
  }

  private initWebSocket () {
    if (this.wsDanmaku) {
      this.wsDanmaku.close()
    }
    const subscriptionName = this.subscriptionNamePrefix + '~' + nanoid()
    this.wsDanmaku = new WebSocket('wss://danmakuit.panda2134.site/websocket/' +
      `consumer/persistent/public/default/${this.roomId}/${subscriptionName}?token=${this.pulsarJWT}`)
    this.wsDanmaku.onmessage = (msg) => {
      const pulsarData = JSON.parse(msg.data)
      if (pulsarData.messageId) {
        // we've met a danmaku event
        this.wsDanmaku!.send(JSON.stringify({ messageId: pulsarData.messageId })) // ACK
        this.onDanmaku(pulsarData)
      }
    }
    const closeHandler = () => {
      if (this.retryHandle) { clearInterval(this.retryHandle) }
      this.onDisconnect()
      this.wsDanmaku!.removeEventListener('close', closeHandler)
      this.retryHandle = setInterval(() => {
        this.initWebSocket()
      }, 5000)
    }
    const errorHandler = (ev: Event) => {
      closeHandler()
      this.onConnectionFail(ev)
    }
    this.wsDanmaku!.onerror = errorHandler
    this.wsDanmaku!.onopen = () => {
      if (this.retryHandle) {
        clearInterval(this.retryHandle)
      }
      this.wsDanmaku!.removeEventListener('error', errorHandler)
      this.keepAliveHandle = setWebSocketKeepAlive(this.wsDanmaku)
      this.wsDanmaku!.addEventListener('close', closeHandler)
      this.onConnected()
    }
  }

  public close () {
    this.wsDanmaku!.close()
    if (this.keepAliveHandle) { clearInterval(this.keepAliveHandle) }
    if (this.retryHandle) { clearInterval(this.retryHandle) }
  }
}
