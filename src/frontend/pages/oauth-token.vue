<template>
  <v-container class="d-flex flex-column justify-center align-center" style="height: 100vh">
    <v-card :color="error ? 'error' : 'secondary'" dark width="300">
      <v-card-title>{{ error ? '凭据错误，请重新登录' : '存储凭据中' }}</v-card-title>
      <v-card-text v-show="!error">
        <v-progress-linear color="white" class="my-1" indeterminate />
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  layout: 'fullpage',
  data () {
    return {
      error: false
    }
  },
  mounted () {
    const token = this.$route.query.token
    if (typeof token !== 'string' || !token.length) {
      this.error = true
      setTimeout(() => { this.$router.push('/') }, 1000)
    } else {
      localStorage.setItem('token', token)
      // eslint-disable-next-line no-console
      console.log('Token:', token)
      this.$router.push('/')
    }
  }
})
</script>
