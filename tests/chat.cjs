const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');

function load(file, imports = {}) {
  const code = ts.transpileModule(fs.readFileSync(file, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, esModuleInterop: true },
  }).outputText;
  const module = { exports: {} };
  new Function('require', 'module', 'exports', code)(name => imports[name] || require(name), module, module.exports);
  return module.exports;
}
const analysis = load('src/app/api/chat/analysis.ts');
const rows = [{ region: 'East', revenue: 10 }, { region: 'East', revenue: 20 }, { region: 'West', revenue: null }];

test('profile computes real statistics and excludes missing values', () => {
  const result = analysis.queryDataset(rows, { operation: 'profile' });
  assert.equal(result.rows, 3);
  assert.deepEqual(result.columns[1], { name: 'revenue', missing: 1, unique: 2, examples: ['10', '20'], min: 10, max: 20, sum: 30, mean: 15 });
});
test('grouped aggregates preserve missing-only groups and reject text calculations', () => {
  assert.deepEqual(analysis.queryDataset(rows, { operation: 'sum', column: 'revenue', group_by: 'region' }).results,
    [{ group: 'East', value: 30 }, { group: 'West', value: null }]);
  assert.throws(() => analysis.queryDataset(rows, { operation: 'sum', column: 'region' }), /numeric/);
  assert.equal(analysis.queryDataset([], { operation: 'count' }).results[0].value, 0);
});

function routeWith(create) {
  class MockGroq { chat = { completions: { create } }; }
  return load('src/app/api/chat/route.ts', {
    'groq-sdk': MockGroq, './analysis': analysis,
    'next/server': { NextResponse: { json: (body, init) => ({ body, status: init?.status || 200 }) } },
  });
}
const request = { json: async () => ({ api_key: 'test-only', user_message: 'Summarize this', dataset_records: rows }) };
test('five tool rounds are followed by a forced written answer with actual query results', async () => {
  const calls = [];
  const route = routeWith(async options => {
    calls.push(options.tool_choice);
    if (options.tool_choice === 'none') {
      const results = options.messages.filter(message => message.role === 'tool');
      assert.equal(results.length, 5);
      assert.equal(JSON.parse(results[0].content).data.rows, 3);
      return { choices: [{ message: { content: 'There are 3 records, with revenue totaling 30.' } }] };
    }
    return { choices: [{ message: { role: 'assistant', content: null, tool_calls: [{ id: `call-${calls.length}`, type: 'function', function: { name: 'run_query', arguments: '{"operation":"profile"}' } }] } }] };
  });
  const result = await route.POST(request);
  assert.equal(result.status, 200);
  assert.match(result.body.response, /3 records/);
  assert.equal(result.body.telemetry.iterations, 6);
  assert.deepEqual(calls, ['auto', 'auto', 'auto', 'auto', 'auto', 'none']);
});
test('empty model output retries once and returns an explicit error if still empty', async () => {
  let calls = 0;
  const route = routeWith(async () => { calls++; return { choices: [{ message: { content: '' } }] }; });
  const result = await route.POST(request);
  assert.equal(calls, 2);
  assert.equal(result.status, 502);
  assert.match(result.body.detail, /no written answer/);
});
test('a normal written answer returns without an unnecessary final call', async () => {
  let calls = 0;
  const route = routeWith(async () => { calls++; return { choices: [{ message: { content: 'Your dataset has three records.' } }] }; });
  const result = await route.POST(request);
  assert.equal(calls, 1);
  assert.equal(result.status, 200);
  assert.match(result.body.response, /three records/);
});
