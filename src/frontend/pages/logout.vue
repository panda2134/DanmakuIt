<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  beforeMount () {
    localStorage.removeItem('token')
    this.$axios.setToken(false)
    this.$router.push('/')
    this.$toast.success('退出登录成功', { y: 'top' })
  }
})
</script>
