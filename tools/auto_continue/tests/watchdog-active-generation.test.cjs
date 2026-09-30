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
  let activeGeneration = generating;
  let createdTabs = 0;
  let resumeMessages = 0;
  let onMessage;
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
    alarms: { create() {}, onAlarm: { addListener() {} } },
    runtime: {
      onInstalled: { addListener() {} },
      onStartup: { addListener() {} },
      onMessage: { addListener(fn) { onMessage = fn; } }
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
            same_chat_fallback_minutes: 30
          };
        }
      };
    }
    if (url.includes("/commits/")) {
      return {
        ok: true,
        async text() {
          return "<feed><updated>" + new Date(activity).toISOString() + "</updated></feed>";
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
    async sendUiFailure() {
      return new Promise(resolve => {
        onMessage(
          {
            type: "fm2001-ui-failure",
            failureKind: "transient",
            reason: "network error"
          },
          { tab: { id: 9, url: "https://chatgpt.com/c/example" } },
          resolve
        );
      });
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
  h.store.activeGenerationGuard.observedSince -= 61 * 60000;
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
