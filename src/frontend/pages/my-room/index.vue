<template>
  <v-container>
    <h1 class="text-h4">
      我的房间
    </h1>
    <v-fab-transition>
      <v-speed-dial
        v-if="!deleteMode && roomList.length"
        v-model="fab"
        bottom
        right
        fixed
        dark
      >
        <template #activator>
          <v-btn v-model="fab" fab dark color="primary">
            <v-icon v-if="fab">
              mdi-close
            </v-icon>
            <v-icon v-else>
              mdi-menu
            </v-icon>
          </v-btn>
        </template>
        <v-btn fab dark small color="green" @click.stop="showAddRoomDialog=true">
          <v-icon>
            mdi-plus
          </v-icon>
        </v-btn>
        <v-btn
          v-show="roomList.length"
          fab
          dark
          small
          color="red"
          @click="deleteMode=true"
        >
          <v-icon>
            mdi-delete
          </v-icon>
        </v-btn>
      </v-speed-dial>
      <v-btn
        v-else-if="!roomList.length"
        fixed
        bottom
        right
        dark
        fab
        color="green"
        @click.stop="showAddRoomDialog=true"
      >
        <v-icon>mdi-plus</v-icon>
      </v-btn>
    </v-fab-transition>
    <v-fab-transition>
      <v-btn
        v-if="deleteMode"
        fixed
        bottom
        right
        dark
        fab
        color="red"
        @click="deleteMode=false"
      >
        <v-icon>mdi-chevron-left</v-icon>
      </v-btn>
    </v-fab-transition>
    <v-dialog v-model="showAddRoomDialog" max-width="300">
      <v-card>
        <v-card-title class="text-h5">
          新房间名称
        </v-card-title>
        <v-card-text>
          <v-text-field v-model="newRoomName" :rules="[value => (value && value.length) || '不能为空']" clearable />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text color="primary" @click="showAddRoomDialog=false">
            取消
          </v-btn>
          <v-btn text :disabled="!newRoomName" color="success darken-1" @click="onRoomCreation">
            创建
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <div class="mt-8">
      <v-row v-if="$fetchState.pending">
        <v-col v-for="i in 12" :key="i" cols="12" md="4" lg="3">
          <v-skeleton-loader elevation="2" type="article, actions" />
        </v-col>
      </v-row>
      <v-row v-else-if="roomList.length">
        <v-col v-for="room in roomList" :key="room.room_id" cols="12" md="4" lg="3">
          <v-card elevation="2">
            <v-card-title>{{ room.name }}</v-card-title>
            <v-card-subtitle>#{{ room.room_id }}</v-card-subtitle>
            <v-card-text>
              创建时间：{{ (new Date(room.creation_time + '+00:00')).toLocaleString() }}
            </v-card-text>
            <v-card-actions>
              <nuxt-link v-slot="{ navigate }" custom :to="`/my-room/${room.room_id}`">
                <v-btn color="primary" text @click="navigate">
                  管理
                </v-btn>
              </nuxt-link>
              <v-dialog v-model="showDeleteDialog[room.room_id]" max-width="300">
                <template #activator="{ on, attrs }">
                  <v-btn v-show="deleteMode" color="error" text v-bind="attrs" v-on="on">
                    删除
                  </v-btn>
                </template>
                <v-card>
                  <v-card-title class="text-h5">
                    删除“{{ room.name }}”？
                  </v-card-title>
                  <v-card-subtitle>
                    输入房间名称以确认。
                  </v-card-subtitle>
                  <v-card-text>
                    <v-text-field
                      v-model="deleteConfirm"
                      color="warning"
                      :rules="[value => value === room.name || '房间名称不匹配',]"
                    />
                  </v-card-text>
                  <v-card-actions>
                    <v-spacer />
                    <v-btn text color="primary" @click="showDeleteDialog[room.room_id]=false">
                      取消
                    </v-btn>
                    <v-btn
                      text
                      color="error"
                      :disabled="deleteConfirm !== room.name"
                      @click="onRoomDeletion(room.room_id)"
                    >
                      删除
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
      <v-responsive
        v-else
        min-height="60vh"
        class="d-flex align-center"
        content-class="d-flex flex-column justify-center align-center"
      >
        <v-img src="/empty_box.png" width="256px" />
        <h2 class="text--accent-1 mt-4 mb-3">
          什么都没有哦
        </h2>
        <span class="grey--text">
          点击右下角，创建一个新房间
        </span>
      </v-responsive>
    </div>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { components } from '~/openapi/openapi'

type Room = components['schemas']['Room']

interface RoomListPageData {
  roomList: Room[]
  fab: boolean
  deleteMode: boolean
  showAddRoomDialog: boolean
  newRoomName: string
  roomToDelete: Room | null
  deleteConfirm?: string
  showDeleteDialog: Record<string, boolean | undefined>
}

export default Vue.extend({
  data (): RoomListPageData {
    return {
      roomList: [],
      newRoomName: '新房间',
      fab: false,
      deleteMode: false,
      showAddRoomDialog: false,
      roomToDelete: null,
      deleteConfirm: '',
      showDeleteDialog: {}
    }
  },
  async fetch () {
    this.roomList.splice(0, this.roomList.length)
    this.roomList.push(...(await this.$api['/room/'].get()))
  },
  methods: {
    async onRoomCreation () {
      this.showAddRoomDialog = false // first, hide the dialog
      await this.$api['/room/'].post({ name: this.newRoomName })
      this.$toast.success('房间创建成功')
      this.$fetch()
    },
    async onRoomDeletion (roomId: string) {
      this.showDeleteDialog[roomId] = false
      this.deleteConfirm = ''
      await this.$api['/room/{room_id}'].delete(roomId)
      this.$toast.success('房间删除成功')
      this.$fetch()
    }
  }
})
</script>
