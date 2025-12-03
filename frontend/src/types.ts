export enum ViewState {
  USER_CENTER = 'USER_CENTER',
  BOT_SETTINGS = 'BOT_SETTINGS',
  CLOUD_ORGANIZE = 'CLOUD_ORGANIZE',
  EMBY_INTEGRATION = 'EMBY_INTEGRATION',
  STRM_GENERATION = 'STRM_GENERATION',
  LOGS = 'LOGS',
}

export interface ClassificationRule {
  id: string;
  name: string;
  targetCid: string;
  conditions: {
    genre_ids?: string;
    origin_country?: string;
    original_language?: string;
    release_year?: string;
    [key: string]: any;
  };
}

export interface AppConfig {
  telegram: {
    botToken: string;
    adminUserId: string;
    whitelistMode: boolean;
    notificationChannelId: string;
  };
  cloud115: {
    loginMethod: string;
    loginApp: string;
    cookies: string;
    appId: string;
    userAgent: string;
    downloadPath: string;
    downloadDirName: string;
    autoDeleteMsg: boolean;
    qps: number;
  };
  cloud123: {
    enabled: boolean;
    clientId: string;
    clientSecret: string;
    qps: number;
  };
  openList: {
    enabled: boolean;
    url: string;
    mountPath: string;
    username?: string;
    password?: string;
  };
  proxy: {
    enabled: boolean;
    type: 'http' | 'socks5';
    host: string;
    port: string;
  };
  tmdb: {
    apiKey: string;
    language: string;
    includeAdult: boolean;
  };
  emby: {
    enabled: boolean;
    serverUrl: string;
    apiKey: string;
    refreshAfterOrganize: boolean;
    notifications: {
      enabled: boolean;
      forwardToTelegram: boolean;
      includePosters: boolean;
      playbackReportingFreq: string;
    };
    posterGeneration: {
      enabled: boolean;
      template: string;
      overlayDirName: boolean;
      sortOrder: string;
      cronSchedule: string;
    };
  };
  strm: {
    enabled: boolean;
    outputDir: string;
    sourceCid115: string;
    urlPrefix115: string;
    sourceDir123: string;
    urlPrefix123: string;
    sourcePathOpenList: string;
    urlPrefixOpenList: string;
    webdav?: {
      enabled: boolean;
      port: string;
      username: string;
      password: string;
      readOnly: boolean;
    };
  };
  organize: {
    enabled: boolean;
    sourceCid: string;
    sourceDirName: string;
    targetCid: string;
    targetDirName: string;
    ai: {
      enabled: boolean;
      provider: string;
      baseUrl: string;
      apiKey: string;
      model: string;
    };
    rename: {
      enabled: boolean;
      movieTemplate: string;
      seriesTemplate: string;
      addTmdbIdToFolder: boolean;
    };
    movieRules: ClassificationRule[];
    tvRules: ClassificationRule[];
  };
  twoFactorSecret?: string;
  user?: {
    password?: string;
  };
}
