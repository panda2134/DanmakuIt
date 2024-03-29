<template>
  <v-card>
    <v-card-title>
      基本信息
    </v-card-title>
    <v-card-text>
      <v-form id="basic-info-form" v-model="basicValid" @submit.prevent="submitBasicInfo">
        <v-text-field v-model="name" outlined label="房间名称" :rules="[v => v ? true : '不能为空']" />
        <v-checkbox v-model="danmakuEnabled" label="允许弹幕" />
        <label>
          用户弹幕颜色
        </label>
        <!--v-chip 不能放在label内，否则点击判定会出现故障！！！-->
        <v-text-field readonly single-line disabled class="elevation-0" rows="3">
          <template #prepend-inner>
            <div class="d-flex flex-wrap">
              <v-chip
                v-for="color in colors"
                :key="color"
                :color="color"
                class="mb-1 mr-2"
                dark
                close
                @click:close="removeColor(color)"
              >
                {{ color }}
              </v-chip>
            </div>
          </template>
          <template #append>
            <v-menu v-model="showColorDialog" max-width="398" left :close-on-content-click="false">
              <template #activator="{ on }">
                <v-btn icon v-on="on">
                  <v-icon>
                    mdi-plus
                  </v-icon>
                </v-btn>
              </template>
              <v-card>
                <v-card-title>
                  选择一种弹幕颜色
                </v-card-title>
                <v-card-text>
                  <v-color-picker show-swatches width="350" :value="newColor" @update:color="updateNewColor" />
                  <span v-show="!isNewColorValid" class="error--text">颜色重复。</span>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn text color="primary" :disabled="!isNewColorValid" @click="addColor">
                    添加
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-menu>
          </template>
        </v-text-field>
      </v-form>
    </v-card-text>
    <v-divider />
    <v-card-actions>
      <v-btn
        text
        :disabled="!basicValid"
        :loading="basicLoading"
        color="primary"
        form="basic-info-form"
        type="submit"
      >
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
    },
    initialColors: {
      type: Array,
      required: true
    }
  },
  data () {
    return {
      basicValid: true,
      basicLoading: false,
      name: this.initialName,
      danmakuEnabled: this.initialDanmakuEnabled,
      colors: Array.from(this.initialColors) as string[],
      newColor: '',
      showColorDialog: false
    }
  },
  computed: {
    isNewColorValid (): boolean {
      return !this.colors.includes(this.newColor)
    }
  },
  methods: {
    updateNewColor (color: { hex: string; }) {
      this.newColor = color.hex
    },
    addColor () {
      this.colors.push(this.newColor)
      this.showColorDialog = false
      this.newColor = ''
    },
    removeColor (color: string) {
      this.colors = this.colors.filter(x => x !== color)
    },
    async submitBasicInfo (): Promise<void> {
      const roomUpdate: RoomUpdate = {
        name: this.name,
        danmaku_enabled: this.danmakuEnabled,
        user_danmaku_colors: this.colors
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
