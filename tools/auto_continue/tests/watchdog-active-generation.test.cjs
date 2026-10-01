"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(
  path.join(__dirname, "../chrome-extension/background.js"), "utf8"
);

function harness({ generating = false, staleMinutes = 20, initialStorage = {} } = {}) {
  const now = Date.now();
  let activity = now - staleMinutes * 60 * 1000;
  let unrelatedMainActivity = now;
  let activeGeneration = generating;
  let createdTabs = 0;
  let resumeMessages = 0;
  let onMessage;
  let onActionClick;
  const badges = new Map();
  const store = { workerTabId: 9, ...initialStorage };
  const chrome = {
    storage: {
      local: {
        async get(keys) {
          const requested = Array.isArray(keys) ? keys : [keys];
          return Object.fromEntries(requested.map(key => [key, store[key]]));
        },
        async set(values) { Object.assign(store, values); },
        async remove(keys) {
          for (const key of (Array.isArray(keys) ? keys : [keys])) delete store[key];
        }
      }
    },
    tabs: {
      async get(id) {
        if (id !== store.workerTabId) throw Error("Tab missing");
        return { id };
      },
      async sendMessage(id, message) {
        assert.equal(id, store.workerTabId);
        if (message.type === "fm2001-query-generation") {
          return { generating: activeGeneration };
        }
        if (message.type === "fm2001-run-pending-resume") {
          resumeMessages++;
          return {};
        }
        throw Error("Unexpected message " + message.type);
      },
      async create() {
        createdTabs++;
        return { id: 10 };
      }
    },
    action: {
      onClicked: { addListener(fn) { onActionClick = fn; } },
      async setBadgeText({ tabId, text }) { badges.set(tabId, text); }
    },
    alarms: { create() {}, onAlarm: { addListener() {} } },
    runtime: {
      onInstalled: { addListener() {} },
      onStartup: { addListener() {} },
      onMessage: { addListener(fn) { onMessage = fn; } },
      getURL(path) {return "chrome-extension://extension-id/" + path;}
    }
  };
  const fetch = async url => {
    if (url.includes("/research/AUTO_CONTINUE_STATE.json")) {
      return {
        ok: true,
        async json() {
          return {
            enabled: true,
            mode: "continuous",
            status: "working",
            stale_after_minutes: 15,
            recovery_cooldown_minutes: 20,
            max_recoveries_per_hour: 3,
            active_generation_grace_minutes: 10,
            same_chat_fallback_minutes: 20
          };
        }
      };
    }
    if (url.includes("/commits/")) {
      return {
        ok: true,
        async text() {
          return "<feed><updated>" + new Date(url.includes("/commits/main.atom") ? unrelatedMainActivity : activity).toISOString() + "</updated></feed>";
        }
      };
    }
    return { ok: true, async text() { return "Standard handoff"; } };
  };
  const context = vm.createContext({ chrome, fetch, console, Date });
  vm.runInContext(source, context, { filename: "background.js" });
  return {
    store,
    async check() { return vm.runInContext("checkForStaleSession()", context); },
    setGenerating(value) { activeGeneration = value; },
    setHeartbeatAge(minutes) { activity = Date.now() - minutes * 60000; },
    setUnrelatedMainHeartbeatAge(minutes) { unrelatedMainActivity = Date.now() - minutes * 60000; },
    async sendUiFailure(tabId = 9, failureKind = "transient", reason = "network error") {
      return new Promise(resolve => {
        onMessage(
          {
            type: "fm2001-ui-failure",
            failureKind,
            reason
          },
          { tab: { id: tabId, url: "https://chatgpt.com/c/example" } },
          resolve
        );
      });
    },
    async clickAction(tab = { id: 9, url: "https://chatgpt.com/c/fm2001" }) {
      return onActionClick(tab);
    },
    badge(tabId) { return badges.get(tabId); },
    async diagnostic() { return new Promise(resolve => onMessage({type:"fm2001-diagnostics"},{tab:{id:9}},resolve)); },
    async startNow(url = "chrome-extension://extension-id/diagnostics.html") {
      return new Promise(resolve => onMessage({type:"fm2001-start-now"},{url},resolve));
    },
    newChatPrompt() {
      return vm.runInContext(
        'buildNewChatRecoveryPrompt("conversation-length-limit", "Standard handoff")',
        context
      );
    },
    get createdTabs() { return createdTabs; },
    get resumeMessages() { return resumeMessages; }
  };
}

test("stale heartbeat does not stop a newly active ChatGPT generation", async () => {
  const h = harness({ generating: true });
  await h.check();
  assert.ok(h.store.activeGenerationGuard);
  assert.equal(h.store.pendingResume, undefined);
  assert.equal(h.resumeMessages, 0);
  assert.equal(h.createdTabs, 0);
});

test("stale heartbeat recovers a stopped worker", async () => {
  const h = harness({ generating: false });
  await h.check();
  assert.equal(h.store.pendingResume.inPlace, true);
  assert.equal(h.store.pendingResume.stopFirst, true);
  assert.equal(h.resumeMessages, 1);
  assert.equal(h.createdTabs, 0);
});

test("active-generation grace is finite: a prolonged silent worker can recover", async () => {
  const h = harness({ generating: true });
  await h.check();
  h.store.activeGenerationGuard.observedSince -= 11 * 60000;
  await h.check();
  assert.equal(h.store.pendingResume.inPlace, true);
  assert.equal(h.resumeMessages, 1);
});

test("a new heartbeat resets the quiet-generation window", async () => {
  const h = harness({ generating: true });
  await h.check();
  assert.ok(h.store.activeGenerationGuard);
  h.setHeartbeatAge(3);
  await h.check();
  assert.equal(h.store.activeGenerationGuard, undefined);
  h.setHeartbeatAge(20);
  await h.check();
  assert.ok(h.store.activeGenerationGuard);
  assert.equal(h.store.pendingResume, undefined);
});

test("active generation blocks same-chat fallback escalation", async () => {
  const h = harness({
    generating: true,
    initialStorage: {
      sameChatRecoveryWindow: {
        startedAt: Date.now() - 35 * 60000,
        baselineActivity: Date.now() - 20 * 60000
      }
    }
  });
  await h.check();
  assert.equal(h.createdTabs, 0);
  assert.equal(h.store.pendingResume, undefined);
});

test("explicit transient UI errors still recover immediately", async () => {
  const h = harness({ generating: true });
  const result = await h.sendUiFailure();
  assert.equal(result.ok, true);
  assert.equal(result.action, "in-place");
  assert.equal(h.store.pendingResume.stopFirst, true);
  assert.equal(h.resumeMessages, 1);
});

test("both recovery paths preserve the entire Gate-17 mission", async () => {
  const h = harness({ generating: false });
  await h.check();
  const inPlace = h.store.pendingResume.prompt;
  const fresh = h.newChatPrompt();
  assert.match(inPlace, /Gate 17/);
  assert.match(inPlace, /not just the current subtask/i);
  assert.match(fresh, /Gate 17/);
  assert.match(fresh, /immediate active task is only the next/i);
});

test("error in unrelated ChatGPT tab cannot hijack FM2001 worker", async () => {
  const h = harness();
  const ignored = await h.sendUiFailure(22);
  assert.equal(ignored.ok, false);
  assert.equal(ignored.reason, "unregistered-worker-tab");
  assert.equal(h.store.workerTabId, 9);
  assert.equal(h.store.pendingResume, undefined);
  assert.equal(h.createdTabs, 0);
});

test("toolbar click explicitly registers selected FM2001 worker", async () => {
  const h = harness();
  await h.clickAction({ id: 22, url: "https://chatgpt.com/c/fm2001" });
  assert.equal(h.store.workerTabId, 22);
  assert.equal(h.badge(22), "FM");
  const ignored = await h.sendUiFailure(9);
  assert.equal(ignored.reason, "unregistered-worker-tab");
  const accepted = await h.sendUiFailure(22);
  assert.equal(accepted.ok, true);
  assert.equal(h.store.pendingResume.tabId, 22);
});

test("toolbar action cannot register a non-ChatGPT tab", async () => {
  const h = harness();
  await h.clickAction({ id: 34, url: "https://github.com/" });
  assert.equal(h.store.workerTabId, 9);
});

test("recent unrelated main commits cannot hide a stale worker",async()=>{
  const h=harness({generating:false,staleMinutes:45});
  h.setUnrelatedMainHeartbeatAge(0);
  await h.check();
  assert.equal(h.store.pendingResume.inPlace,true);
});
test("diagnostics are read-only and use worker heartbeat",async()=>{
  const h=harness({generating:true,staleMinutes:45});
  const result=await h.diagnostic();
  assert.equal(result.ok,true);
  assert.equal(result.report.workerTabId,9);
  assert.equal(result.report.workerStaleMinutes>=44,true);
  assert.equal(h.store.pendingResume,undefined);
});

test("manual start requests recovery immediately without stale delay",async()=>{
  const h=harness({generating:false,staleMinutes:0});
  const result=await h.startNow();
  assert.equal(result.ok,true);
  assert.equal(result.reason,"manual-recovery-requested");
  assert.equal(h.store.pendingResume.inPlace,true);
  assert.equal(h.store.pendingResume.stopFirst,false);
  assert.equal(h.resumeMessages,1);
});
test("manual start never interrupts an actively generating response",async()=>{
  const h=harness({generating:true,staleMinutes:30});
  const result=await h.startNow();
  assert.equal(result.reason,"already-running");
  assert.equal(h.store.pendingResume,undefined);
  assert.equal(h.resumeMessages,0);
});
test("manual start requires the extension options page",async()=>{
  const h=harness({generating:false});
  const result=await h.startNow("https://unrelated.example/");
  assert.equal(result.ok,false);
  assert.equal(result.reason,"invalid-sender");
});
test("manual duplicate clicks respect the throttle and do not stack prompts",async()=>{
  const h=harness({generating:false});
  const first=await h.startNow();
  const next=await h.startNow();
  assert.equal(first.ok,true);
  assert.equal(next.reason,"manual-throttle");
  assert.equal(h.resumeMessages,1);
});
test("unregistered worker cannot be started manually",async()=>{
  const h=harness({initialStorage:{workerTabId:null}});
  const result=await h.startNow();
  assert.equal(result.reason,"no-worker-tab");
  assert.equal(h.createdTabs,0);
});


test("sandbox/CAAS failure opens a fresh worker chat immediately", async()=>{
  const h=harness({generating:false,staleMinutes:0});
  const result=await h.sendUiFailure(
    9,
    "sandbox",
    "Analysis errored: caas.internal.errors.ClientError"
  );
  assert.equal(result.ok,true);
  assert.equal(result.action,"new-chat");
  assert.equal(result.failure_kind,"sandbox");
  assert.equal(h.createdTabs,1);
  assert.equal(h.store.pendingResume.inPlace,false);
  assert.equal(h.store.pendingResume.stopFirst,false);
});


test("assistant Analysis errored fragments are sandbox failures while quoted ClientError text stays inert", ()=>{
  const source=fs.readFileSync(path.join(extensionDir,"content.js"),"utf8");
  assert.match(source,/function isAssistantSandboxErrorFragment\(role, text\)/);
  assert.match(source,/role !== "assistant"/);
  assert.match(source,/normalized\.length <= 240/);
  assert.match(source,/\^analysis errored\\b/i);
  assert.match(source,/if \(isAssistantSandboxErrorFragment\(messageRole, text\)\)/);
  assert.doesNotMatch(source,/if \(!element \|\| isConversationMessage\(element\)\)/);
});
