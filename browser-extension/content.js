/**
 * Hermes Autonomous Browser Agent - Content Script DOM Execution Engine
 * Executes element clicking, form filling, text extraction, and page scrolling
 * directly inside active web pages without losing user session cookies.
 */

console.log("[Hermes Extension] Content script initialized on:", window.location.href);

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "dom_action") {
    const { action, selector, value } = request;
    console.log(`[Hermes Extension] Executing DOM action: ${action}`, { selector, value });

    try {
      let result = null;
      switch (action) {
        case "click":
          result = clickElement(selector);
          break;
        case "type":
          result = typeInput(selector, value);
          break;
        case "extract":
          result = extractPageText();
          break;
        case "scroll":
          result = scrollPage(value);
          break;
        case "highlight":
          result = highlightElement(selector);
          break;
        default:
          result = { success: false, error: `Unknown action: ${action}` };
      }
      sendResponse(result);
    } catch (e) {
      sendResponse({ success: false, error: e.toString() });
    }
  }
  return true;
});

function clickElement(selector) {
  const el = document.querySelector(selector);
  if (!el) return { success: false, error: `Element not found: ${selector}` };
  highlightElement(selector);
  el.click();
  return { success: true, message: `Clicked element ${selector}` };
}

function typeInput(selector, value) {
  const el = document.querySelector(selector);
  if (!el) return { success: false, error: `Input element not found: ${selector}` };
  highlightElement(selector);
  el.value = value;
  el.dispatchEvent(new Event("input", { bubbles: true }));
  el.dispatchEvent(new Event("change", { bubbles: true }));
  return { success: true, message: `Typed value into ${selector}` };
}

function extractPageText() {
  const title = document.title;
  const bodyText = document.body.innerText.slice(0, 5000);
  return { success: true, title, bodyText, url: window.location.href };
}

function scrollPage(direction) {
  const distance = direction === "up" ? -500 : 500;
  window.scrollBy({ top: distance, behavior: "smooth" });
  return { success: true, message: `Scrolled page ${direction}` };
}

function highlightElement(selector) {
  const el = document.querySelector(selector);
  if (!el) return { success: false };
  const origBorder = el.style.border;
  el.style.border = "2px solid #3b82f6";
  setTimeout(() => {
    el.style.border = origBorder;
  }, 1500);
  return { success: true };
}
