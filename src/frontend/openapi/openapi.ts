/**
 * This file was auto-generated by openapi-typescript.
 * Do not make direct changes to the file.
 */

export interface paths {
  "/user/social-login/github/login": {
    get: operations["login_github_user_social_login_github_login_get"];
  };
  "/user/social-login/github/auth": {
    get: operations["auth_github_user_social_login_github_auth_get"];
  };
  "/user/social-login/gitlab/login": {
    get: operations["login_gitlab_user_social_login_gitlab_login_get"];
  };
  "/user/social-login/gitlab3rd/login": {
    get: operations["login_gitlab_3rd_party_user_social_login_gitlab3rd_login_get"];
  };
  "/user/social-login/gitlab/auth": {
    get: operations["auth_gitlab_user_social_login_gitlab_auth_get"];
  };
  "/user/social-login/gitlab3rd/auth": {
    get: operations["auth_gitlab_3rd_party_user_social_login_gitlab3rd_auth_get"];
  };
  "/user/social-login/wechat": {
    get: operations["connect_to_wechat_user_social_login_wechat_get"];
  };
  "/user/me": {
    get: operations["user_information_user_me_get"];
  };
  "/room/": {
    get: operations["list_room_room__get"];
    post: operations["create_room_room__post"];
  };
  "/room/{room_id}": {
    get: operations["get_room_room__room_id__get"];
    delete: operations["delete_room_room__room_id__delete"];
    /** uid, room_id and creation_time cannot be altered */
    patch: operations["modify_room_room__room_id__patch"];
  };
  "/room/{room_id}/client-login": {
    /** Set `room_passcode` in HTTP Bearer; `pulsar_jwt` is then used for pulsar connection */
    get: operations["client_login_room_room__room_id__client_login_get"];
  };
  "/room/{room_id}/mpcode": {
    /** Get WeChat MiniProgram code for sending danmaku. Set `room_passcode` in HTTP Bearer;This is provided for clients so that they can fetch the QR code without JWT. */
    get: operations["get_room_mpcode_room__room_id__mpcode_get"];
  };
  "/room/{room_id}/qrcode": {
    /** Set `room_passcode` in HTTP Bearer;This is provided for clients so that they can fetch the QR code without JWT. */
    get: operations["get_room_qrcode_room__room_id__qrcode_get"];
  };
  "/room/{room_id}/fetch-subscribers": {
    /** Fetch the user information of all subscribers.Returns room_id in JSON when the fetch process starts. */
    post: operations["fetch_subscribers_of_room_room__room_id__fetch_subscribers_post"];
  };
  "/room/{room_id}/danmaku-admin": {
    /** Send a danmaku message from admin. Sender in danmaku will always be overwritten to admin. */
    post: operations["danmaku_admin_send_room__room_id__danmaku_admin_post"];
  };
  "/room/{room_id}/danmaku-update": {
    /** Update a danmaku message. */
    post: operations["danmaku_update_room__room_id__danmaku_update_post"];
  };
  "/room/{room_id}/consumers": {
    /** Get the online consumers of a room. */
    get: operations["online_consumers_room__room_id__consumers_get"];
  };
}

export interface components {
  schemas: {
    ConsumerDetail: {
      address?: string;
      consumerName?: string;
      availablePermits?: number;
      blockedConsumerOnUnackedMsgs?: boolean;
      clientVersion?: string;
      connectedSince?: string;
      msgRateOut?: number;
      msgRateRedeliver?: number;
      msgThroughputOut?: number;
      unackedMessages?: number;
    };
    DanmakuMessage: {
      color: string;
      content: string;
      id: string;
      permission: string;
      pos: string;
      sender: string;
      size: string;
    };
    HTTPValidationError: {
      detail?: components["schemas"]["ValidationError"][];
    };
    OnlineSubscription: {
      subscription_name: string;
      consumers: components["schemas"]["ConsumerDetail"][];
    };
    Room: {
      name: string;
      uid: string;
      danmaku_enabled?: boolean;
      room_id: string;
      room_passcode: string;
      creation_time: string;
      remote_censor?: boolean;
      keyword_blacklist?: string[];
      pulsar_jwt: string;
      wechat_token: string;
      wechat_encrypted?: boolean;
      wechat_encryption_key?: string;
      wechat_appid?: string;
      wechat_appsecret?: string;
      wechat_access_token?: string;
      user_danmaku_colors?: string[];
    };
    RoomIdModel: {
      room_id: string;
    };
    RoomNameModel: {
      name: string;
    };
    RoomQRCodeResponse: {
      ticket: string;
      expire_seconds: number;
      url: string;
    };
    RoomUpdate: {
      name?: string;
      danmaku_enabled?: boolean;
      remote_censor?: boolean;
      keyword_blacklist?: string[];
      wechat_token?: string;
      wechat_encrypted?: boolean;
      wechat_encryption_key?: string;
      wechat_appid?: string;
      wechat_appsecret?: string;
      user_danmaku_colors?: string[];
    };
    RoomWeChatMpCodeResponse: {
      image_dataurl: string;
    };
    User: {
      username: string;
      avatar?: string;
      uid: string;
    };
    ValidationError: {
      loc: string[];
      msg: string;
      type: string;
    };
  };
}

export interface operations {
  login_github_user_social_login_github_login_get: {
    responses: {
      /** Successful Response */
      200: {
        content: {
          "application/json": unknown;
        };
      };
    };
  };
  auth_github_user_social_login_github_auth_get: {
    responses: {
      /** redirect to frontend */
      307: {
        content: {
          "application/json": unknown;
        };
      };
    };
  };
  login_gitlab_user_social_login_gitlab_login_get: {
    responses: {
      /** Successful Response */
      200: {
        content: {
          "application/json": unknown;
        };
      };
    };
  };
  login_gitlab_3rd_party_user_social_login_gitlab3rd_login_get: {
    responses: {
      /** Successful Response */
      200: {
        content: {
          "application/json": unknown;
        };
      };
    };
  };
  auth_gitlab_user_social_login_gitlab_auth_get: {
    responses: {
      /** redirect to frontend */
      307: {
        content: {
          "application/json": unknown;
        };
      };
    };
  };
  auth_gitlab_3rd_party_user_social_login_gitlab3rd_auth_get: {
    responses: {
      /** redirect to frontend */
      307: {
        content: {
          "application/json": unknown;
        };
      };
    };
  };
  connect_to_wechat_user_social_login_wechat_get: {
    parameters: {
      query: {
        code: string;
      };
    };
    responses: {
      /** redirect to frontend */
      307: {
        content: {
          "application/json": unknown;
        };
      };
      /** Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  user_information_user_me_get: {
    responses: {
      /** Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["User"];
        };
      };
    };
  };
  list_room_room__get: {
    responses: {
      /** last 100 created rooms */
      200: {
        content: {
          "application/json": components["schemas"]["Room"][];
        };
      };
    };
  };
  create_room_room__post: {
    responses: {
      /** Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["Room"];
        };
      };
      /** Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["RoomNameModel"];
      };
    };
  };
  get_room_room__room_id__get: {
    parameters: {
      path: {
        room_id: string;
      };
    };
    responses: {
      /** Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["Room"];
        };
      };
      /** Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  delete_room_room__room_id__delete: {
    parameters: {
      path: {
        room_id: string;
      };
    };
    responses: {
      /** Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["RoomIdModel"];
        };
      };
      /** Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** uid, room_id and creation_time cannot be altered */
  modify_room_room__room_id__patch: {
    parameters: {
      path: {
        room_id: string;
      };
    };
    responses: {
      /** Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["Room"];
        };
      };
      /** Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["RoomUpdate"];
      };
    };
  };
  /** Set `room_passcode` in HTTP Bearer; `pulsar_jwt` is then used for pulsar connection */
  client_login_room_room__room_id__client_login_get: {
    parameters: {
      path: {
        room_id: string;
      };
    };
    responses: {
      /** Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["Room"];
        };
      };
      /** Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Get WeChat MiniProgram code for sending danmaku. Set `room_passcode` in HTTP Bearer;This is provided for clients so that they can fetch the QR code without JWT. */
  get_room_mpcode_room__room_id__mpcode_get: {
    parameters: {
      path: {
        room_id: string;
      };
    };
    responses: {
      /** respond with a JSON containing dataurl for MP Code. */
      200: {
        content: {
          "application/json": components["schemas"]["RoomWeChatMpCodeResponse"];
        };
      };
      /** Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Set `room_passcode` in HTTP Bearer;This is provided for clients so that they can fetch the QR code without JWT. */
  get_room_qrcode_room__room_id__qrcode_get: {
    parameters: {
      path: {
        room_id: string;
      };
    };
    responses: {
      /** Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["RoomQRCodeResponse"];
        };
      };
      /** Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Fetch the user information of all subscribers.Returns room_id in JSON when the fetch process starts. */
  fetch_subscribers_of_room_room__room_id__fetch_subscribers_post: {
    parameters: {
      path: {
        room_id: string;
      };
    };
    responses: {
      /** Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["RoomIdModel"];
        };
      };
      /** Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Send a danmaku message from admin. Sender in danmaku will always be overwritten to admin. */
  danmaku_admin_send_room__room_id__danmaku_admin_post: {
    parameters: {
      path: {
        room_id: string;
      };
    };
    responses: {
      /** Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["DanmakuMessage"];
        };
      };
      /** Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["DanmakuMessage"];
      };
    };
  };
  /** Update a danmaku message. */
  danmaku_update_room__room_id__danmaku_update_post: {
    parameters: {
      path: {
        room_id: string;
      };
    };
    responses: {
      /** Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["DanmakuMessage"];
        };
      };
      /** Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["DanmakuMessage"];
      };
    };
  };
  /** Get the online consumers of a room. */
  online_consumers_room__room_id__consumers_get: {
    parameters: {
      path: {
        room_id: string;
      };
    };
    responses: {
      /** Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["OnlineSubscription"][];
        };
      };
      /** Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
}

export interface external {}
