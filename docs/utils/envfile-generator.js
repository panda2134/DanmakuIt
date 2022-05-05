const fs = require('fs')
const os = require('os')
const path = require('path')
const { config } = require('process')

const filePath = path.resolve(__dirname)
const rootPath = path.join(filePath, '..', '..')
const envfiles = fs.readdirSync(rootPath).filter(filename => filename.endsWith('.env'))

const parsedConf = {}

for (const filename of envfiles) {
    console.log('⚙️', 'found envfile', filename)
    parsedConf[filename] = []
    const content = fs.readFileSync(path.join(rootPath, filename)).toString('utf-8').split('\n')
    for (const line of content) {
        const configItemName = line.split('=', 2)[0]
        const parts = line.split(/\:\:docs/, 2)
        const docMeta = parts[parts.length-1].trim().split(' ')
        const cmd = docMeta[0]
        const field = docMeta.slice(1).join(' ').trim()

        if (cmd.startsWith(':input')) {
            parsedConf[filename].push({ name: configItemName, type: 'input', field, value: '' })
        } else if (cmd.startsWith(':rand')) {
            const len = Number.parseInt(cmd.match(/\:rand\(([0-9]+)\)/)[1])
            parsedConf[filename].push({ name: configItemName, type: 'rand', field, len, value: '' })
        } else if (cmd.startsWith(':default')) {
            const defaultValue = cmd.match(/\:default\((.*)\)/)[1]
            parsedConf[filename].push({ name: configItemName, type: 'default', field, defaultValue, value: defaultValue })
        } else {
            console.warn(`Unknown markup: ${cmd}`)
        }
    }
}

fs.writeFileSync(path.join(__dirname, '..', 'envfile.json'), JSON.stringify(parsedConf))