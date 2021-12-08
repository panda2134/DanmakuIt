<template>
  <v-app>
    <site-app-bar />
    <v-main>
      <v-container fluid>
        <v-alert
          border="top"
          colored-border
          type="warning"
          elevation="2"
        >
          网站仍处于内测阶段，可能清空数据库，请谨慎使用。
        </v-alert>
        <Nuxt />
      </v-container>
    </v-main>
  </v-app>
</template>

<script lang="ts">
import Vue from 'vue'
import SiteAppBar from '~/components/SiteAppBar.vue'

export default Vue.extend({
  components: { SiteAppBar }
})
</script>
