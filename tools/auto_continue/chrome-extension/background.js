const REPO = "BrannMolvik/premier-league-manager-2001-research";
const MAIN_BRANCH = "main";
const RUNTIME_BRANCH = "agent-runtime";
const CHAT_URL = "https://chatgpt.com/";
const STALE_CHECK_ALARM = "fm2001-stale-check";
const STALE_CHECK_MINUTES = 3;

const runtimeStateUrl = () =>
  `https://raw.githubusercontent.com/${REPO}/${RUNTIME_BRANCH}/research/AUTO_CONTINUE_STATE.json?ts=${Date.now()}`;

const handoffUrl = () =>
  `https://raw.githubusercontent.com/${REPO}/${MAIN_BRANCH}/research/HANDOFF_PROMPT.md?ts=${Date.now()}`;

async function fetchJson(url) {
  const response = await fetch(url, {
    cache: "no-store",
    headers: { Accept: "application/vnd.github+json" }
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status} for ${url}`);
  }
  return response.json();
}

async function fetchText(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status} for ${url}`);
  }
  return response.text();
}

async function getRuntimeState() {
  return fetchJson(runtimeStateUrl());
}

async function getBranchActivity(branch) {
  const data = await fetchJson(
    `https://api.github.com/repos/${REPO}/branches/${branch}?ts=${Date.now()}`
  );
  const dateText =
    data?.commit?.commit?.committer?.date ||
    data?.commit?.commit?.author?.date ||
    null;
  return dateText ? Date.parse(dateText) : 0;
}

function shouldMonitor(state) {
  return (
    state &&
    state.enabled === true &&
    state.mode === "continuous" &&
    state.status === "working"
  );
}

async function recoveryGuard(state) {
  const now = Date.now();
  const stored = await chrome.storage.local.get([
    "lastRecoveryAt",
    "recoveryHistory",
    "recoveryInFlightAt"
  ]);

  const cooldownMinutes = Number(state.recovery_cooldown_minutes || 20);
  const maxPerHour = Number(state.max_recoveries_per_hour || 3);

  if (
    stored.recoveryInFlightAt &&
    now - stored.recoveryInFlightAt < 5 * 60 * 1000
  ) {
    return null;
  }

  if (
    stored.lastRecoveryAt &&
    now - stored.lastRecoveryAt < cooldownMinutes * 60 * 1000
  ) {
    return null;
  }

  const history = (stored.recoveryHistory || []).filter(
    (timestamp) => now - timestamp < 60 * 60 * 1000
  );

  if (history.length >= maxPerHour) {
    return null;
  }

  return { now, history };
}

function buildRecoveryPrompt(reason, handoff, details = {}) {
  const detailText = Object.entries(details)
    .map(([key, value]) => `${key}: ${value}`)
    .join("\n");

  return `AUTO-RECOVERY: the previous FM2001 ChatGPT work session was still marked as working but stopped progressing.

Recovery reason: ${reason}
${detailText ? `${detailText}\n` : ""}
Do not ask Daniel to reconstruct the previous chat. GitHub is canonical.

Before substantive work:
1. Check the current main HEAD.
2. Read research/CURRENT_STATE.md and research/CONTINUATION_INSTRUCTIONS.md.
3. Read research/AUTO_CONTINUE.md.
4. Read research/AUTO_CONTINUE_STATE.json from the agent-runtime branch.
5. Mark the runtime state as mode=continuous and status=working, increment recovery_generation, and record the latest main HEAD.
6. Continue the exact current task from the repository and checkpoint at the normal persistence boundaries.

If the old chat merely hit its length limit, treat this as a normal handoff, not as a reason to restart the investigation.

Latest standard handoff follows:

${handoff}`;
}

async function savePendingRecovery(
  reason,
  state,
  tabId,
  details = {},
  existingGuard = null
) {
  const guard = existingGuard || (await recoveryGuard(state));
  if (!guard) {
    return false;
  }

  await chrome.storage.local.set({ recoveryInFlightAt: guard.now });

  try {
    const handoff = await fetchText(handoffUrl());
    const prompt = buildRecoveryPrompt(reason, handoff, details);
    const recoveryRecord = {
      tabId,
      prompt,
      reason,
      createdAt: guard.now,
      expiresAt: guard.now + 30 * 60 * 1000
    };

    await chrome.storage.local.set({
      pendingResume: recoveryRecord,
      lastRecoveryAt: guard.now,
      recoveryHistory: [...guard.history, guard.now],
      recoveryInFlightAt: 0
    });

    return true;
  } catch (error) {
    await chrome.storage.local.set({ recoveryInFlightAt: 0 });
    console.warn("FM2001 auto-continue recovery preparation failed", error);
    return false;
  }
}

async function triggerRecovery(reason, state, details = {}) {
  const guard = await recoveryGuard(state);
  if (!guard) {
    return false;
  }

  const tab = await chrome.tabs.create({ url: CHAT_URL, active: false });
  return savePendingRecovery(reason, state, tab.id, details, guard);
}


async function checkForStaleSession() {
  try {
    const state = await getRuntimeState();
    if (!shouldMonitor(state)) {
      return;
    }

    const [runtimeActivity, mainActivity] = await Promise.all([
      getBranchActivity(RUNTIME_BRANCH),
      getBranchActivity(MAIN_BRANCH)
    ]);
    const latestActivity = Math.max(runtimeActivity, mainActivity);
    if (!latestActivity) {
      return;
    }

    const staleAfterMinutes = Number(state.stale_after_minutes || 15);
    const staleMinutes = Math.floor((Date.now() - latestActivity) / 60000);
    if (staleMinutes < staleAfterMinutes) {
      return;
    }

    await triggerRecovery("stale-repository-activity", state, {
      stale_minutes: staleMinutes,
      source: "chrome-extension-background-alarm"
    });
  } catch (error) {
    console.warn("FM2001 stale-session background check failed", error);
  }
}

function ensureStaleAlarm() {
  chrome.alarms.create(STALE_CHECK_ALARM, {
    periodInMinutes: STALE_CHECK_MINUTES
  });
}

chrome.runtime.onInstalled.addListener(() => {
  ensureStaleAlarm();
});

chrome.runtime.onStartup.addListener(() => {
  ensureStaleAlarm();
});

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === STALE_CHECK_ALARM) {
    checkForStaleSession();
  }
});

ensureStaleAlarm();

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === "fm2001-ui-failure") {
    (async () => {
      try {
        const state = await getRuntimeState();
        if (
          shouldMonitor(state) &&
          state.auto_new_chat_on_ui_failure !== false
        ) {
          await triggerRecovery(
            message.reason || "ChatGPT UI failure signal",
            state,
            { page: sender?.tab?.url || "unknown" }
          );
        }
        sendResponse({ ok: true });
      } catch (error) {
        console.warn("FM2001 UI-failure recovery failed", error);
        sendResponse({ ok: false, error: String(error) });
      }
    })();
    return true;
  }

  if (message?.type === "fm2001-request-recovery") {
    (async () => {
      try {
        const state = await getRuntimeState();
        if (!shouldMonitor(state)) {
          sendResponse({ ok: false, reason: "runtime-not-working" });
          return;
        }

        const tabId = sender?.tab?.id;
        if (!tabId) {
          sendResponse({ ok: false, reason: "missing-tab" });
          return;
        }

        const accepted = await savePendingRecovery(
          message.reason || "local watchdog recovery request",
          state,
          tabId,
          message.details || {}
        );
        sendResponse({ ok: accepted });
      } catch (error) {
        console.warn("FM2001 local-watchdog recovery failed", error);
        sendResponse({ ok: false, error: String(error) });
      }
    })();
    return true;
  }

  if (message?.type === "fm2001-get-pending-resume") {
    (async () => {
      const stored = await chrome.storage.local.get(["pendingResume"]);
      const pending = stored.pendingResume || null;
      const tabId = sender?.tab?.id;

      if (!pending) {
        sendResponse({ pending: null });
        return;
      }

      if (pending.expiresAt && Date.now() > pending.expiresAt) {
        await chrome.storage.local.remove("pendingResume");
        sendResponse({ pending: null });
        return;
      }

      if (pending.tabId !== tabId) {
        sendResponse({ pending: null });
        return;
      }

      sendResponse({ pending });
    })();
    return true;
  }

  if (message?.type === "fm2001-resume-consumed") {
    (async () => {
      const stored = await chrome.storage.local.get(["pendingResume"]);
      if (
        stored.pendingResume &&
        stored.pendingResume.tabId === sender?.tab?.id
      ) {
        await chrome.storage.local.remove("pendingResume");
      }
      sendResponse({ ok: true });
    })();
    return true;
  }

  return false;
});
