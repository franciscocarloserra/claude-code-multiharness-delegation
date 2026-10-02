import type { Register } from 'claude-code'

const CONNECTOR = '/home/usuario/projects/know-how/claude-mods/claude-code-multiharness-delegation/bridge/connector.py'
const PREFIX = 'multiharness-delegation:'
const TIMEOUT_MS = 600_000

export const register: Register = (on) => {
  on('tool.call', { tool: 'Agent' }, async ($, e, next) => {
    if (e.tool !== 'Agent' || !e.subagent_type?.startsWith(PREFIX)) return next(e)
    const harness = e.subagent_type.slice(PREFIX.length)
    const t0 = Date.now()
    const r = await $.process.run(['python3', CONNECTOR, harness, '--name', e.name ?? 'default'], { stdin: e.prompt, timeoutMs: TIMEOUT_MS })
    return {
      result: {
        status: 'completed', agentId: `bridge-${harness}-${e.name ?? 'default'}`, agentType: e.subagent_type, prompt: e.prompt,
        content: [{ type: 'text', text: r.stdout.trim() || r.stderr.trim() || '(empty)' }],
        totalToolUseCount: 0, totalDurationMs: Date.now() - t0, totalTokens: 0,
        usage: { input_tokens: 0, output_tokens: 0, cache_creation_input_tokens: null, cache_read_input_tokens: null, server_tool_use: null, service_tier: null, cache_creation: null },
      },
    }
  })
}
