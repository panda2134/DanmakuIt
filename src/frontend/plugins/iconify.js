import Vue from 'vue'
import { Icon } from '@iconify/vue2/dist/offline'

Vue.use({
  install (vue) {
    vue.component('VIconify', Icon)
  }
})
