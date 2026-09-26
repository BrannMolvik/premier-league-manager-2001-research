const LENGTH_FAILURE_PATTERNS = [
  /conversation (?:is )?too long/i,
  /maximum (?:conversation )?length/i,
  /reached (?:the )?maximum length/i,
  /this conversation has reached.{0,80}limit/i,
  /start a new chat to continue/i
];

const TRANSIENT_FAILURE_PATTERNS = [
  /connection interrupted/i,
  /network error/i,
  /something went wrong/i,
  /response interrupted/i
];

const COMPOSER_SELECTORS = [
  "#prompt-textarea",
  "textarea[data-testid='prompt-textarea']",
  "div[data-testid='prompt-textarea'][contenteditable='true']",
  "div[contenteditable='true'][role='textbox']"
];

const SEND_SELECTORS = [
  "button[data-testid='send-button']",
  "button[aria-label='Send prompt']",
  "button[aria-label='Send message']",
  "button[aria-label^='Send']"
];

const STOP_SELECTORS = [
  "button[data-testid='stop-button']",
  "button[aria-label='Stop streaming']",
  "button[aria-label='Stop generating']"
];

const reportedFailures = new Set();
let resumeSubmitting = false;
let localRecoveryRequested = false;

function elementFromNode(node) {
  if (node?.nodeType === Node.ELEMENT_NODE) {
    return node;
  }
  return node?.parentElement || null;
}

function isConversationMessage(element) {
  return Boolean(element?.closest?.("[data-message-author-role]"));
}

function reportFailure(kind, text, pattern) {
  const signature = `${kind}:${pattern.source}:${text.slice(0, 180)}`;
  if (reportedFailures.has(signature)) {
    return;
  }
  reportedFailures.add(signature);

  chrome.runtime.sendMessage({
    type: "fm2001-ui-failure",
    failureKind: kind,
    reason: text.slice(0, 300)
  });
}

function detectFailureInNode(node) {
  const element = elementFromNode(node);
  if (!element || isConversationMessage(element)) {
    return;
  }

  const text = (element.innerText || element.textContent || "").trim();
  if (!text || text.length > 1000) {
    return;
  }

  for (const pattern of LENGTH_FAILURE_PATTERNS) {
    if (pattern.test(text)) {
      reportFailure("length", text, pattern);
      return;
    }
  }

  for (const pattern of TRANSIENT_FAILURE_PATTERNS) {
    if (pattern.test(text)) {
      reportFailure("transient", text, pattern);
      return;
    }
  }
}

const observer = new MutationObserver((mutations) => {
  for (const mutation of mutations) {
    for (const node of mutation.addedNodes) {
      detectFailureInNode(node);
    }
  }
});

if (document.documentElement) {
  observer.observe(document.documentElement, {
    childList: true,
    subtree: true
  });
}

function requestRecoveryFromUrl() {
  if (localRecoveryRequested) {
    return;
  }

  const params = new URLSearchParams(window.location.search);
  if (params.get("fm2001_auto_recover") !== "1") {
    return;
  }

  localRecoveryRequested = true;
  const reason = params.get("reason") || "legacy-local-watchdog";
  const staleMinutes = params.get("stale_minutes") || "unknown";

  chrome.runtime.sendMessage(
    {
      type: "fm2001-request-recovery",
      reason,
      details: {
        stale_minutes: staleMinutes,
        source: "legacy-watchdog-url"
      }
    },
    (response) => {
      if (response?.ok) {
        const cleanUrl = new URL(window.location.href);
        cleanUrl.searchParams.delete("fm2001_auto_recover");
        cleanUrl.searchParams.delete("reason");
        cleanUrl.searchParams.delete("stale_minutes");
        history.replaceState({}, "", cleanUrl.toString());
      }
    }
  );
}

function isVisible(element) {
  if (!element) {
    return false;
  }
  const rect = element.getBoundingClientRect();
  const style = window.getComputedStyle(element);
  return (
    rect.width > 0 &&
    rect.height > 0 &&
    style.visibility !== "hidden" &&
    style.display !== "none"
  );
}

function findFirstVisible(selectors) {
  for (const selector of selectors) {
    for (const element of document.querySelectorAll(selector)) {
      if (isVisible(element)) {
        return element;
      }
    }
  }
  return null;
}

function composerText(composer) {
  if (!composer) {
    return "";
  }
  if ("value" in composer) {
    return composer.value || "";
  }
  return composer.innerText || composer.textContent || "";
}

function setNativeTextValue(element, value) {
  const prototype =
    element instanceof HTMLTextAreaElement
      ? HTMLTextAreaElement.prototype
      : HTMLInputElement.prototype;
  const descriptor = Object.getOwnPropertyDescriptor(prototype, "value");
  descriptor?.set?.call(element, value);
}

function fillComposer(composer, prompt) {
  try {
    composer.focus({ preventScroll: true });
  } catch (_error) {
    try { composer.focus(); } catch (_ignored) {}
  }

  if (
    composer instanceof HTMLTextAreaElement ||
    composer instanceof HTMLInputElement
  ) {
    setNativeTextValue(composer, prompt);
    composer.dispatchEvent(new Event("input", { bubbles: true }));
    composer.dispatchEvent(new Event("change", { bubbles: true }));
    return composerText(composer).includes(prompt.slice(0, 40));
  }

  if (composer.isContentEditable) {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(composer);
    selection.removeAllRanges();
    selection.addRange(range);

    let inserted = false;
    try {
      inserted = document.execCommand("insertText", false, prompt);
    } catch (_error) {
      inserted = false;
    }

    if (!inserted || !composerText(composer).includes(prompt.slice(0, 40))) {
      composer.textContent = prompt;
    }

    composer.dispatchEvent(
      new InputEvent("input", {
        bubbles: true,
        inputType: "insertText",
        data: prompt
      })
    );

    return composerText(composer).includes(prompt.slice(0, 40));
  }

  return false;
}

async function requestPendingResume() {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage(
      { type: "fm2001-get-pending-resume" },
      (response) => resolve(response?.pending || null)
    );
  });
}

async function markResumeConsumed() {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage(
      { type: "fm2001-resume-consumed" },
      () => resolve()
    );
  });
}

function pressEnter(composer) {
  composer.dispatchEvent(
    new KeyboardEvent("keydown", {
      key: "Enter",
      code: "Enter",
      keyCode: 13,
      which: 13,
      bubbles: true,
      cancelable: true
    })
  );
  composer.dispatchEvent(
    new KeyboardEvent("keyup", {
      key: "Enter",
      code: "Enter",
      keyCode: 13,
      which: 13,
      bubbles: true,
      cancelable: true
    })
  );
}

async function waitForComposer(timeoutMs = 15000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const composer = findFirstVisible(COMPOSER_SELECTORS);
    if (composer) {
      return composer;
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  return null;
}

async function stopCurrentGenerationIfNeeded() {
  const stopButton = findFirstVisible(STOP_SELECTORS);
  if (!stopButton || stopButton.disabled) {
    return false;
  }

  stopButton.click();
  await new Promise((resolve) => setTimeout(resolve, 1200));
  return true;
}

async function submitPendingResume() {
  if (resumeSubmitting) {
    return;
  }

  const pending = await requestPendingResume();
  if (!pending?.prompt) {
    return;
  }

  resumeSubmitting = true;
  try {
    if (pending.stopFirst) {
      await stopCurrentGenerationIfNeeded();
    }

    const composer = await waitForComposer();
    if (!composer) {
      return;
    }

    const filled = fillComposer(composer, pending.prompt);
    if (!filled) {
      return;
    }

    await new Promise((resolve) => setTimeout(resolve, 700));

    const sendButton = findFirstVisible(SEND_SELECTORS);
    if (sendButton && !sendButton.disabled) {
      sendButton.click();
    } else {
      pressEnter(composer);
    }

    await new Promise((resolve) => setTimeout(resolve, 700));

    const currentText = composerText(composer).trim();
    if (!currentText || currentText.length < pending.prompt.length / 3) {
      await markResumeConsumed();
    }
  } finally {
    resumeSubmitting = false;
  }
}

chrome.runtime.onMessage.addListener((message) => {
  if (message?.type === "fm2001-run-pending-resume") {
    submitPendingResume();
  }
});

requestRecoveryFromUrl();

// Allow a newly created background recovery tab time to load its composer.
// Long-lived in-place recovery is event-driven by the background service worker.
const startupResumeInterval = setInterval(submitPendingResume, 2000);
setTimeout(() => clearInterval(startupResumeInterval), 2 * 60 * 1000);
submitPendingResume();
