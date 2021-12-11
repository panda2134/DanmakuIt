import colors from 'vuetify/es5/util/colors'
import zhHans from 'vuetify/lib/locale/zh-Hans'

export default {
  // Disable server-side rendering: https://go.nuxtjs.dev/ssr-mode
  ssr: false,

  // Target: https://go.nuxtjs.dev/config-target
  target: 'static',

  // Environs
  env: {
    GITHUB_SHA: process.env.GITHUB_SHA,
    TEST_TOKEN: process.env.TEST_TOKEN || '',
    WECHAT_CALLBACK_URL_BASE: process.env.WECHAT_CALLBACK_URL_BASE || 'https://danmakuit.panda2134.site/port/',
    ROOM_PASSCODE_LEN: process.env.ROOM_PASSCODE_LEN || '6'
  },

  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    titleTemplate: '%s - 弹幕一下',
    title: '弹幕一下',
    htmlAttrs: {
      lang: 'zh-cn'
    },
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: '' },
      { name: 'format-detection', content: 'telephone=no' },
      { name: 'msapplication-TileColor', content: '#2b5797' },
      { name: 'theme-color', content: '#aaaaaa' } // android task menu
    ],
    link: [
      { rel: 'preconnect', href: 'https://cdn.jsdelivr.net' },
      { rel: 'preconnect', href: 'https://fonts.googleapis.cnpmjs.org' },
      { rel: 'preconnect', href: 'https://fonts.gstatic.cnpmjs.org' },
      { rel: 'stylesheet', href: 'https://fonts.googleapis.cnpmjs.org/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap' },
      { rel: 'stylesheet', href: 'https://fonts.googleapis.cnpmjs.org/css2?family=ZCOOL+KuaiLe&display=swap' },
      { rel: 'stylesheet', href: 'https://fonts.googleapis.cnpmjs.org/css2?family=Noto+Sans+SC:wght@100;300;400;500;700;900&family=Noto+Serif+SC:wght@200;300;400;500;600;700;900&display=swap' },
      { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' },
      { rel: 'icon', type: 'image/png', sizes: '32x32', href: '/favicon-32x32.png' },
      { rel: 'icon', type: 'image/png', sizes: '16x16', href: '/favicon-16x16.png' },
      { rel: 'manifest', href: '/site.webmanifest' },
      { rel: 'mask-icon', href: '/safari-pinned-tab.svg', color: '#1e88e5' },
      { rel: 'icon', type: 'image/png', href: '/favicon.ico' }
    ]
  },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [
    '~/assets/global.scss'
  ],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [
    '~/plugins/http.ts',
    '~/plugins/snackbar.ts'
  ],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    // https://go.nuxtjs.dev/typescript
    '@nuxt/typescript-build',
    // https://go.nuxtjs.dev/vuetify
    '@nuxtjs/vuetify'
  ],

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    // https://go.nuxtjs.dev/axios
    '@nuxtjs/axios',
    'portal-vue/nuxt'
  ],

  // Axios module configuration: https://go.nuxtjs.dev/config-axios
  axios: {},

  publicRuntimeConfig: {
    axios: {
      browserBaseURL: process.env.BROWSER_BASE_URL || 'https://danmakuit.panda2134.site/api/v1/'
    }
  },

  // Vuetify module configuration: https://go.nuxtjs.dev/config-vuetify
  vuetify: {
    lang: {
      locales: { zhHans },
      current: 'zhHans'
    },
    treeShake: {
      components: ['VSnackbar', 'VBtn', 'VIcon']
    },
    customVariables: ['~/assets/variables.scss'],
    theme: {
      themes: {
        light: {
          primary: colors.blue.darken1,
          secondary: colors.orange.darken2,
          accent: colors.pink.base,
          error: colors.red.base,
          warning: colors.deepOrange.base,
          info: colors.cyan.base,
          success: colors.green.base
        }
      },
      options: {
        customProperties: true
      }
    }
  },

  // Build Configuration: https://go.nuxtjs.dev/config-build
  build: {
  }
}
