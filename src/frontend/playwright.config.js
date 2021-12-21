const { PlaywrightTestConfig } = require('@playwright/test')

const config = {
  webServer: {
    command: 'yarn build && yarn start',
    port: 3000,
    timeout: 120 * 1000,
    reuseExistingServer: !process.env.CI
  }
}

module.exports = config
