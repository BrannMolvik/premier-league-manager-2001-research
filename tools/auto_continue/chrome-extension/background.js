const REPO = "BrannMolvik/premier-league-manager-2001-research";
const MAIN_BRANCH = "main";
const RUNTIME_BRANCH = "agent-runtime";
const CHAT_URL = "https://chatgpt.com/";
const STALE_CHECK_ALARM = "fm2001-stale-check";
const STALE_CHECK_MINUTES = 3;
const DEFAULT_SAME_CHAT_FALLBACK_MINUTES = 30;
// Never stop an actively generating worker solely because GitHub is quiet.
// Explicit ChatGPT UI errors still use their existing immediate recovery path.
const ACTIVE_GENERATION_GRACE_MINUTES = 60;

const runtimeStateUrl = () =>
  `https://raw.githubusercontent.com/${REPO}/${RUNTIME_BRANCH}/research/AUTO_CONTINUE_STATE.json?ts=${Date.now()}`;

const handoffUrl = () =>
  `https://raw.githubusercontent.com/${REPO}/${MAIN_BRANCH}/research/HANDOFF_PROMPT.md?ts=${Date.now()}`;

const branchFeedUrl = (branch) =>
  `https://github.com/${REPO}/commits/${branch}.atom?ts=${Date.now()}`;

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
  const atom = await fetchText(branchFeedUrl(branch));
  const match = atom.match(/<updated>([^<]+)<\/updated>/i);
  if (!match) {
    throw new Error(`No <updated> timestamp in commit feed for ${branch}`);
  }
  const timestamp = Date.parse(match[1]);
  if (!Number.isFinite(timestamp)) {
    throw new Error(`Invalid commit-feed timestamp for ${branch}: ${match[1]}`);
  }
  return timestamp;
}

async function getLatestRepositoryActivity() {
  const [runtimeActivity, mainActivity] = await Promise.all([
    getBranchActivity(RUNTIME_BRANCH),
    getBranchActivity(MAIN_BRANCH)
  ]);
  return Math.max(runtimeActivity, mainActivity);
}

async function getSameChatRecoveryWindow() {
  const stored = await chrome.storage.local.get(["sameChatRecoveryWindow"]);
  return stored.sameChatRecoveryWindow || null;
}

async function beginSameChatRecoveryWindow(latestActivity) {
  const now = Date.now();
  const existing = await getSameChatRecoveryWindow();

  // A later repository heartbeat proves the previous recovery succeeded, so
  // a future stall starts a fresh fallback window. Otherwise keep the first
  // attempt time; repeated same-chat attempts must not postpone fallback.
  if (
    !existing ||
    Number(latestActivity || 0) > Number(existing.baselineActivity || 0)
  ) {
    const window = {
      startedAt: now,
      baselineActivity: Number(latestActivity || 0)
    };
    await chrome.storage.local.set({ sameChatRecoveryWindow: window });
    return window;
  }

  return existing;
}

async function clearSameChatRecoveryWindow() {
  await chrome.storage.local.remove("sameChatRecoveryWindow");
}

function shouldMonitor(state) {
  return (
    state &&
    state.enabled === true &&
    state.mode === "continuous" &&
    state.status === "working"
  );
}

// A new worker can start while the previous GitHub heartbeat is already stale.
// Detect its live Stop control before treating silence as a dead session. Otherwise
// the next three-minute alarm could interrupt a fresh worker after ~2-3 minutes.
// One uninterrupted generation gets at most a bounded grace period; real UI
// failures continue through the separate immediate error-recovery path.
async function deferStaleRecoveryForActiveGeneration(latestActivity) {
  const stored = await chrome.storage.local.get([
    "workerTabId",
    "activeGenerationGuard"
  ]);
  const tabId = stored.workerTabId;
  if (!tabId) {
    await chrome.storage.local.remove("activeGenerationGuard");
    return false;
  }

  let status;
  try {
    status = await chrome.tabs.sendMessage(tabId, {
      type: "fm2001-query-generation"
    });
  } catch (_error) {
    // A closed tab, unloaded content script, or unavailable ChatGPT page is
    // not evidence that a generation is live.
    await chrome.storage.local.remove("activeGenerationGuard");
    return false;
  }

  if (status?.generating !== true) {
    await chrome.storage.local.remove("activeGenerationGuard");
    return false;
  }

  const now = Date.now();
  const previous = stored.activeGenerationGuard;
  const guard = (
    previous &&
    previous.tabId === tabId &&
    Number(latestActivity) <= Number(previous.baselineActivity)
  )
    ? previous
    : { tabId, baselineActivity: Number(latestActivity), observedSince: now };

  await chrome.storage.local.set({ activeGenerationGuard: guard });
  if (now - Number(guard.observedSince) >= ACTIVE_GENERATION_GRACE_MINUTES * 60000) {
    console.warn(
      "FM2001 active generation exceeded quiet-period grace; allowing recovery",
      { tabId, minutes: ACTIVE_GENERATION_GRACE_MINUTES }
    );
    return false;
  }

  console.info(
    "FM2001 deferring stale recovery: worker response is still generating",
    { tabId, minutesObserved: Math.floor((now - guard.observedSince) / 60000) }
  );
  return true;
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

function buildNewChatRecoveryPrompt(reason, handoff, details = {}) {
  const detailText = Object.entries(details)
    .map(([key, value]) => `${key}: ${value}`)
    .join("\n");

  return `AUTO-RECOVERY: the previous FM2001 ChatGPT work session can no longer continue in its existing conversation.

The standing objective is to finish every remaining roadmap gate through Gate 17
and its Windows 11 release audit. The immediate active task is only the next
step; completing one response, subtask, or gate does not finish the assignment.

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

A new conversation was created because the previous conversation reached a true chat-length limit, no usable worker tab remained, or an in-place recovery produced no repository progress for the configured fallback interval. Do not restart already-persisted investigation.

Latest standard handoff follows:

${handoff}`;
}

function buildInPlaceRecoveryPrompt(reason, details = {}) {
  const detailText = Object.entries(details)
    .map(([key, value]) => `${key}: ${value}`)
    .join("\n");

  return `Continue the FM2001 work from the last successful GitHub checkpoint. The previous response appears to have stalled or been interrupted.

Recovery reason: ${reason}
${detailText ? `${detailText}\n` : ""}
The standing mission is to complete all remaining roadmap gates through Gate 17 and the verified Windows 11 release, not just the current subtask or response. Do not restart completed work. Check the current main HEAD and research/CURRENT_STATE.md, then continue the exact active task as the next step in that mission. Once that subtask is verified, continue the next source-backed step in the same session if feasible; checkpoint roughly every 10 minutes without treating a checkpoint as a stopping point. Advance through gates after their audits, without asking Daniel to say continue. If a genuine infrastructure failure prevents all productive work, record the precise blocker and next action instead of inventing work; only report the entire mission complete after Gate 17 passes.`;
}

async function savePendingRecovery(
  reason,
  state,
  tabId,
  details = {},
  existingGuard = null,
  options = {}
) {
  const guard = existingGuard || (await recoveryGuard(state));
  if (!guard) {
    return false;
  }

  await chrome.storage.local.set({ recoveryInFlightAt: guard.now });

  try {
    const inPlace = options.inPlace === true;
    const prompt = inPlace
      ? buildInPlaceRecoveryPrompt(reason, details)
      : buildNewChatRecoveryPrompt(
          reason,
          await fetchText(handoffUrl()),
          details
        );

    const recoveryRecord = {
      tabId,
      prompt,
      reason,
      inPlace,
      stopFirst: options.stopFirst === true,
      createdAt: guard.now,
      expiresAt: guard.now + 30 * 60 * 1000
    };

    await chrome.storage.local.set({
      pendingResume: recoveryRecord,
      workerTabId: tabId,
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

async function notifyRecoveryTab(tabId) {
  try {
    await chrome.tabs.sendMessage(tabId, {
      type: "fm2001-run-pending-resume"
    });
  } catch (_error) {
    // The content script may still be loading. It also checks pending state on load.
  }
}

async function recoverInPlace(tabId, reason, state, details = {}) {
  if (!tabId) {
    return false;
  }

  try {
    await chrome.tabs.get(tabId);
  } catch (_error) {
    return false;
  }

  const guard = await recoveryGuard(state);
  if (!guard) {
    return false;
  }

  const accepted = await savePendingRecovery(
    reason,
    state,
    tabId,
    details,
    guard,
    { inPlace: true, stopFirst: true }
  );

  if (accepted) {
    await notifyRecoveryTab(tabId);
  }
  return accepted;
}

async function triggerNewChatRecovery(reason, state, details = {}) {
  const guard = await recoveryGuard(state);
  if (!guard) {
    return false;
  }

  const tab = await chrome.tabs.create({ url: CHAT_URL, active: false });
  return savePendingRecovery(
    reason,
    state,
    tab.id,
    details,
    guard,
    { inPlace: false, stopFirst: false }
  );
}

async function recoverExistingWorker(reason, state, details = {}) {
  const stored = await chrome.storage.local.get(["workerTabId"]);
  const tabId = stored.workerTabId;
  if (!tabId) {
    return false;
  }

  const accepted = await recoverInPlace(tabId, reason, state, details);
  if (!accepted) {
    try {
      await chrome.tabs.get(tabId);
    } catch (_error) {
      await chrome.storage.local.remove("workerTabId");
    }
  }
  return accepted;
}

async function checkForStaleSession() {
  try {
    const state = await getRuntimeState();
    if (!shouldMonitor(state)) {
      return;
    }

    const latestActivity = await getLatestRepositoryActivity();
    if (!latestActivity) {
      return;
    }

    let sameChatWindow = await getSameChatRecoveryWindow();
    if (
      sameChatWindow &&
      latestActivity > Number(sameChatWindow.baselineActivity || 0)
    ) {
      await clearSameChatRecoveryWindow();
      sameChatWindow = null;
    }

    const staleAfterMinutes = Number(state.stale_after_minutes || 15);
    const staleMinutes = Math.floor((Date.now() - latestActivity) / 60000);
    if (staleMinutes < staleAfterMinutes) {
      // A new repository checkpoint resets the active-generation quiet window.
      await chrome.storage.local.remove("activeGenerationGuard");
      return;
    }

    // Repository silence alone must not cancel a ChatGPT response that is
    // visibly generating. This also protects a newly recovered worker whose
    // first checkpoint has not yet landed.
    if (await deferStaleRecoveryForActiveGeneration(latestActivity)) {
      return;
    }

    const details = {
      stale_minutes: staleMinutes,
      source: "chrome-extension-background-alarm"
    };

    if (sameChatWindow) {
      const fallbackMinutes = Number(
        state.same_chat_fallback_minutes ||
        DEFAULT_SAME_CHAT_FALLBACK_MINUTES
      );
      const fallbackAgeMinutes = Math.floor(
        (Date.now() - Number(sameChatWindow.startedAt || 0)) / 60000
      );

      if (fallbackAgeMinutes >= fallbackMinutes) {
        const opened = await triggerNewChatRecovery(
          "same-chat-recovery-no-progress",
          state,
          {
            ...details,
            same_chat_recovery_age_minutes: fallbackAgeMinutes,
            fallback_after_minutes: fallbackMinutes
          }
        );
        if (opened) {
          await clearSameChatRecoveryWindow();
        }
        return;
      }

      // The first same-chat recovery has not had its full grace period yet.
      // Do not keep retrying the same tab and accidentally reset the clock.
      return;
    }

    const reused = await recoverExistingWorker(
      "stale-repository-activity",
      state,
      details
    );

    if (reused) {
      await beginSameChatRecoveryWindow(latestActivity);
      return;
    }

    await triggerNewChatRecovery(
      "stale-repository-activity-no-worker-tab",
      state,
      details
    );
  } catch (error) {
    console.warn("FM2001 stale-session background check failed", error);
  }
}

function ensureStaleAlarm() {
  chrome.alarms.create(STALE_CHECK_ALARM, {
    periodInMinutes: STALE_CHECK_MINUTES
  });
}

chrome.runtime.onInstalled.addListener(async () => {
  await chrome.storage.local.remove([
    "pendingResume",
    "recoveryInFlightAt",
    "sameChatRecoveryWindow"
  ]);
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
        if (!shouldMonitor(state)) {
          sendResponse({ ok: false, reason: "runtime-not-working" });
          return;
        }

        const failureKind = message.failureKind || "transient";
        const reason = message.reason || "ChatGPT UI failure signal";
        const tabId = sender?.tab?.id;

        if (failureKind === "length") {
          const accepted = await triggerNewChatRecovery(reason, state, {
            page: sender?.tab?.url || "unknown",
            failure_kind: failureKind
          });
          sendResponse({ ok: accepted, action: "new-chat" });
          return;
        }

        const latestActivity = await getLatestRepositoryActivity();
        const accepted = await recoverInPlace(tabId, reason, state, {
          page: sender?.tab?.url || "unknown",
          failure_kind: failureKind
        });
        if (accepted) {
          await beginSameChatRecoveryWindow(latestActivity);
        }
        sendResponse({ ok: accepted, action: "in-place" });
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

        const latestActivity = await getLatestRepositoryActivity();
        const accepted = await recoverInPlace(
          tabId,
          message.reason || "local recovery request",
          state,
          message.details || {}
        );
        if (accepted) {
          await beginSameChatRecoveryWindow(latestActivity);
        }
        sendResponse({ ok: accepted });
      } catch (error) {
        console.warn("FM2001 local recovery failed", error);
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
        await chrome.storage.local.set({ workerTabId: sender.tab.id });
        await chrome.storage.local.remove("pendingResume");
      }
      sendResponse({ ok: true });
    })();
    return true;
  }

  return false;
});
