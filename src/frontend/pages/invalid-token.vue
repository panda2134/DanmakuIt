<script>
import Vue from 'vue'

export default Vue.extend({
  layout: 'fullpage',
  mounted () {
    this.$toast.error('未登录或凭据过期，请重新登录！')
    this.$router.push('/')
  }
})
</script>
