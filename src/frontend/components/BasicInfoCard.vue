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
          <v-text-field readonly single-line disabled class="elevation-0" rows="3">
            <template #prepend-inner>
              <div class="d-flex flex-wrap">
                <v-chip
                  v-for="color in colors"
                  :key="color"
                  :color="color"
                  class="mb-1 mr-2"
                  dark
                >
                  {{ color }}
                </v-chip>
              </div>
            </template>
            <template #append>
              <v-menu v-model="showColorDialog" max-width="398" left>
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
                    <v-color-picker v-model="newColor" show-swatches width="350" />
                    <span v-show="!isNewColorValid" class="error--text">颜色重复。</span>
                  </v-card-text>
                  <v-card-actions>
                    <v-spacer />
                    <!--                    <v-btn text @click="showColorDialog=false">-->
                    <!--                      取消-->
                    <!--                    </v-btn>-->
                    <v-btn text color="primary" :disabled="!isNewColorValid" @click="addColor">
                      添加
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-menu>
            </template>
          </v-text-field>
        </label>
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
      colors: this.initialColors as string[],
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
    addColor () {
      this.colors.push(this.newColor)
      this.showColorDialog = false
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
