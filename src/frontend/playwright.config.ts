import { PlaywrightTestConfig } from '@playwright/test'

const config: PlaywrightTestConfig = {
  webServer: {
    command: 'yarn start',
    port: 3000,
    timeout: 30 * 1000,
    reuseExistingServer: !process.env.CI
  },
  reporter: process.env.CI ? 'github' : 'list',
  retries: process.env.CI ? 3 : 0,
  use: {
    trace: 'on',
    screenshot: 'on'
  }
}

export default config
