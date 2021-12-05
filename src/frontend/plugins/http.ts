import { Context, Plugin } from '@nuxt/types'
import { paths } from '~/openapi/openapi'

type APIGetType<Q extends paths[keyof paths]> = Q extends Record<'get', any> ? {
  get: (...args: any[]) => Promise<Q['get']['responses'] extends {200: any} ?
          Q['get']['responses'][200]['content']['application/json'] : void>;
} : {};

type APIDeleteType<Q extends paths[keyof paths]> = Q extends Record<'delete', any> ? {
  delete: (...args: any[]) => Promise<Q['delete']['responses'] extends {200: any} ?
      Q['delete']['responses'][200]['content']['application/json'] : void>;
} : {};

type APIPatchType<Q extends paths[keyof paths]> = Q extends Record<'patch', any> ? {
  patch: (postBody: Q['patch']['requestBody']['content']['application/json'], ...args: any[]) =>
    Promise<Q['patch']['responses'] extends {200: any} ?
      Q['patch']['responses'][200]['content']['application/json'] : void>;
} : {};

type APIPostType<Q extends paths[keyof paths]> = Q extends Record<'post', any> ? {
  post: (postBody: Q['post']['requestBody']['content']['application/json'], ...args: any[]) =>
    Promise<Q['post']['responses'] extends {200: any} ?
    Q['post']['responses'][200]['content']['application/json'] : void>;
} : {};

type APIType = {
  [urlPath in (keyof paths)]: APIGetType<paths[urlPath]> & APIDeleteType<paths[urlPath]>
                            & APIPatchType<paths[urlPath]> & APIPostType<paths[urlPath]>;
}

function getAPI ({ $axios }: Context): APIType {
  return {
    '/user/me': {
      get: () => $axios.$get('/user/me')
    },
    '/user/social-login/github/auth': {
      get: () => { throw new Error('Not implemented') }
    },
    '/user/social-login/github/login': {
      // eslint-disable-next-line require-await
      async get () { location.href = '/user/social-login/github/login' }
    },
    '/user/social-login/gitlab/auth': {
      get: () => { throw new Error('Not implemented') }
    },
    '/user/social-login/gitlab/login': {
      get () { location.href = '/user/social-login/gitlab/login'; return Promise.resolve() }
    },
    '/user/social-login/gitlab3rd/auth': {
      get: () => { throw new Error('Not implemented') }
    },
    '/user/social-login/gitlab3rd/login': {
      get () { location.href = '/user/social-login/gitlab3rd/login'; return Promise.resolve() }
    },
    '/user/social-login/wechat': {
      get: () => { throw new Error('Not implemented') }
    },
    '/room/{room_id}/client-login': {
      get: (roomId: string, roomPasscode: string) => $axios.$get(`/room/${roomId}/client-login`, {
        headers: { Authorization: `Bearer ${roomPasscode}` }
      })
    },
    '/room/{room_id}': {
      get: (roomId: string) => $axios.$get(`/room/${roomId}`),
      delete: (roomId: string) => $axios.$delete(`/room/${roomId}`),
      patch: (postBody, roomId: string) => $axios.$patch(`/room/${roomId}`, postBody)
    },
    '/room/': {
      get: () => $axios.$get('/room/'),
      post: roomCreation => $axios.$post('/room/', roomCreation)
    }
  }
}

declare module 'vue/types/vue' {
  interface Vue {
    $api: APIType
  }
}

declare module '@nuxt/types' {
  interface NuxtAppOptions {
    $api: APIType
  }
  interface Context {
    $api: APIType
  }
}

const myPlugin: Plugin = (context, inject) => {
  const api = getAPI(context)
  context.$api = api
  inject('api', api)
}

export default myPlugin
