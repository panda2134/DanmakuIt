<template>
  <v-card>
    <v-card-title>
      发送弹幕
    </v-card-title>
    <v-card-subtitle>
      弹幕将显示为以管理员身份发送。
    </v-card-subtitle>
    <v-card-text>
      <v-form id="admin-danmaku-form" v-model="valid" @submit.prevent="submit">
        <v-text-field
          v-model="danmakuContent"
          clearable
          label="弹幕内容"
          :rules="[x => x && x.length || '不能为空']"
        />
        <v-radio-group v-model="danmakuType" label="弹幕类型" mandatory row>
          <v-radio label="滚动" value="rightleft" />
          <v-radio label="顶部" value="top" />
          <v-radio label="底部" value="bottom" />
        </v-radio-group>
        <div class="d-flex">
          <label class="mr-1">
            弹幕颜色
          </label>
          <v-menu max-width="398" offset-x>
            <template #activator="{ on, attrs }">
              <div class="v-color-picker__color" v-bind="attrs" v-on="on">
                <div :style="{ backgroundColor: danmakuColor }" />
              </div>
            </template>
            <v-color-picker v-model="danmakuColor" show-swatches />
          </v-menu>
        </div>
        <v-row class="mt-2">
          <v-col cols="12" md="3">
            <div class="d-flex">
              <label class="pt-1">字体大小</label>
              <v-slider v-model="fontSize" min="12" max="72" thumb-label />
            </div>
          </v-col>
        </v-row>
      </v-form>
    </v-card-text>
    <v-divider />
    <v-card-actions>
      <v-btn
        text
        :loading="loading"
        :disabled="!valid"
        color="primary"
        type="submit"
        form="admin-danmaku-form"
      >
        <v-icon small>
          mdi-send
        </v-icon>
        发送
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import { nanoid } from 'nanoid'

type DanmakuType = 'rightleft' | 'top' | 'bottom'

export default Vue.extend({
  props: {
    roomId: {
      required: true,
      type: String
    }
  },
  data: () => ({
    valid: true,
    danmakuContent: '',
    danmakuType: 'rightleft' as DanmakuType,
    danmakuColor: '#f57c00',
    fontSize: 16,
    loading: false
  }),
  methods: {
    async submit () {
      try {
        this.loading = true
        await this.$api['/room/{room_id}/danmaku-admin'].post(
          {
            color: this.danmakuColor,
            size: this.fontSize + 'pt',
            id: nanoid(),
            permission: '1',
            pos: this.danmakuType,
            sender: 'admin',
            content: this.danmakuContent
          }
          , this.roomId)
        this.$toast.success('发送成功')
      } catch (e) {
        this.$toast.error('请求错误：' + e)
        throw e
      } finally {
        this.loading = false
      }
    }
  }
})
</script>

<style scoped>

</style>
