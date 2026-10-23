// Test simulé du nœud réellement installé, sans accès réseau ni vrais identifiants.
// docker exec -i n8n-n8n-1 node < scripts/test-telegram-trigger.cjs
const assert = require('node:assert/strict');
const base = '/usr/local/lib/node_modules/n8n/node_modules/n8n-nodes-base/dist/nodes/Telegram/';
const {TelegramTrigger} = require(base + 'TelegramTrigger.node.js');
const functions = require(base + 'GenericFunctions.js');
const trigger = new TelegramTrigger();
let registration;
functions.getSecretToken = () => 'simulation-secret-only';
functions.apiRequest = async (method, endpoint, body) => {
  assert.equal(method, 'POST');
  assert.equal(endpoint, 'setWebhook');
  registration = body;
  return {ok: true};
};
function context(body, secret = 'simulation-secret-only') {
  const response = {statusCode: null, status(code) {this.statusCode = code; return this;}, json() {return this;}};
  return {
    response,
    getNode: () => ({id: 'simulation-trigger', typeVersion: 1.2}),
    getNodeWebhookUrl: () => 'https://example.invalid/webhook/simulation/webhook',
    getNodeParameter: key => key === 'updates' ? ['message', 'callback_query'] : {},
    getCredentials: async () => ({accessToken: 'simulation-only'}),
    getBodyData: () => body,
    getHeaderData: () => ({'x-telegram-bot-api-secret-token': secret}),
    getResponseObject: () => response,
    helpers: {returnJsonArray: values => values.map(json => ({json}))},
  };
}
async function main() {
  await trigger.webhookMethods.default.create.call(context({}));
  assert.equal(registration.drop_pending_updates, false);
  assert.deepEqual(registration.allowed_updates, ['message', 'callback_query']);
  assert.equal(registration.secret_token, 'simulation-secret-only');
  const callback = {update_id: 1, callback_query: {id: 'simulation', data: 'job:test',
    from: {id: 101}, message: {chat: {id: 101, type: 'private'}}}};
  const accepted = await trigger.webhook.call(context(callback));
  assert.deepEqual(accepted.workflowData[0][0].json, callback);
  const rejectedContext = context(callback, 'invalid-secret');
  const rejected = await trigger.webhook.call(rejectedContext);
  assert.equal(rejectedContext.response.statusCode, 403);
  assert.equal(rejected.noWebhookResponse, true);
  assert.equal(rejected.workflowData, undefined);
  console.log(JSON.stringify({simulated: true, nodeVersion: 1.2,
    preservesPendingUpdates: true, forwardsAuthenticatedCallbacksToWorkflow: true,
    rejectsInvalidSecret: true, realTelegramRequests: 0,
    requirement: 'Filter both user ID and private chat ID in the following IF node'}));
}
main().catch(error => {console.error(error.message); process.exitCode = 1;});
