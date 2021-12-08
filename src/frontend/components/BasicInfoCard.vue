<template>
  <v-card outlined>
    <v-card-title>
      基本信息
    </v-card-title>
    <v-card-text>
      <v-form v-model="basicValid">
        <v-text-field v-model="name" outlined label="房间名称" :rules="[v => v ? true : '不能为空']" />
        <v-checkbox v-model="danmaku_enabled" label="允许弹幕" />
      </v-form>
    </v-card-text>
    <v-divider />
    <v-card-actions>
      <v-btn text :disabled="!basicValid" :loading="basicLoading" color="primary" @click="submitBasicInfo">
        提交
      </v-btn>
    </v-card-actions>
  </v-card>
</template>
<script lang="ts">
import Vue from 'vue'
import { RoomUpdate } from '~/openapi/models'

export default Vue.extend({
  props: {
    roomId: {
      type: String,
      required: true
    },
    initialName: {
      type: String,
      required: true
    },
    initialDanmakuEnabled: {
      type: Boolean,
      required: true
    }
  },
  data () {
    return {
      basicValid: true,
      basicLoading: false,
      name: this.initialName,
      danmaku_enabled: this.initialDanmakuEnabled
    }
  },
  methods: {
    async submitBasicInfo (): Promise<void> {
      const roomUpdate: RoomUpdate = {
        name: this.name,
        danmaku_enabled: this.danmaku_enabled
      }
      try {
        this.basicLoading = true
        await this.$api['/room/{room_id}'].patch(roomUpdate, this.roomId)
        this.$toast.success('基本信息更新成功')
        this.$emit('room-update')
      } catch (e) {
        this.$toast.error('请求错误：' + e)
        throw e
      } finally {
        this.basicLoading = false
      }
    }
  }
})
</script>
