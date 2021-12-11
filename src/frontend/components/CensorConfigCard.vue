<template>
  <v-card>
    <v-card-title>
      审核管理
    </v-card-title>
    <v-card-text>
      <v-form id="censor-config-form" v-model="valid" @submit.prevent="submit">
        <v-checkbox
          v-model="autoCensor"
          label="自动审核"
        />
        <div style="margin-top: -16px" class="mb-6">
          自动审核需站长在配置文件中正确填写API Token后方可启用，目前接入的是百度智能审核。关闭后，所有弹幕都需要人工审核。
        </div>
        <label>
          关键词黑名单
        </label>
        <v-text-field
          v-model="newKeywordInput"
          single-line
          :rules="[x => !keywords.includes(x) || '重复的屏蔽词']"
          placeholder="填入屏蔽词, 回车确认添加"
          @keydown.enter.prevent="addKeyword"
          @blur.prevent="addKeyword"
        >
          <template #prepend-inner>
            <v-chip-group>
              <v-chip
                v-for="kwd in keywords"
                :key="kwd"
                close
                @click:close="removeKeyword(kwd)"
              >
                {{ kwd }}
              </v-chip>
            </v-chip-group>
          </template>
        </v-text-field>
      </v-form>
    </v-card-text>
    <v-divider />
    <v-card-actions>
      <v-btn
        text
        :disabled="!valid"
        :loading="loading"
        color="primary"
        type="submit"
        form="censor-config-form"
      >
        提交
      </v-btn>
    </v-card-actions>
  </v-card>
</template>
<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  props: {
    roomId: {
      type: String,
      required: true
    },
    initialAutoCensor: {
      type: Boolean,
      required: true
    },
    initialKeywords: {
      validator (val) {
        if (!Array.isArray(val)) { return false }
        for (const x of val) {
          if (typeof x !== 'string') {
            return false
          }
        }
        return true
      },
      required: true
    }
  },
  data () {
    return {
      valid: true,
      loading: false,
      autoCensor: this.initialAutoCensor,
      keywords: this.initialKeywords as string[],
      newKeywordInput: ''
    }
  },
  methods: {
    removeKeyword (kwd: string) {
      this.keywords = this.keywords.filter(x => x !== kwd)
    },
    addKeyword () {
      if (!this.newKeywordInput.length || this.keywords.includes(this.newKeywordInput)) {
        return
      }
      this.keywords.push(this.newKeywordInput)
      this.newKeywordInput = ''
    },
    async submit (): Promise<void> {
      try {
        this.loading = true
        await this.$api['/room/{room_id}'].patch({
          remote_censor: this.autoCensor,
          keyword_blacklist: this.keywords
        }, this.roomId)
        this.$toast.success('审核配置更新成功')
        this.$emit('room-update')
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
