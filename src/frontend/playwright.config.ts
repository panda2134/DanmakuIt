import { PlaywrightTestConfig } from '@playwright/test';

const config: PlaywrightTestConfig = {
  webServer: {
    command: 'yarn build && yarn generate && yarn start',
    port: 3000,
    timeout: 600 * 1000,
    reuseExistingServer: !process.env.CI
  },
  reporter: process.env.CI ? 'github' : 'list',
  retries: 3,
  use: {
    trace: 'on',
    screenshot: 'on'
  }
}

export default config
