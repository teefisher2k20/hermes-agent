/**
 * Hermes Autonomous Browser Agent - Service Worker Background Script
 * Maintains WebSocket connection to Hermes Agent Gateway (ws://127.0.0.1:9119/api/ws)
 * and relays DOM automation commands to active content scripts.
 */

const GATEWAY_WS_URL = "ws://127.0.0.1:9119/api/ws";
let ws = null;
let isConnected = false;

function connectGateway() {
  try {
    ws = new WebSocket(GATEWAY_WS_URL);

    ws.onopen = () => {
      isConnected = true;
      console.log("[Hermes Extension] Connected to Hermes Gateway WS");
      chrome.storage.local.set({ status: "connected" });
      broadcastStatus("connected");
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        console.log("[Hermes Extension] Received WS message:", msg);
        handleGatewayMessage(msg);
      } catch (err) {
        console.error("[Hermes Extension] Invalid JSON message from gateway", err);
      }
    };

    ws.onclose = () => {
      isConnected = false;
      console.log("[Hermes Extension] Gateway WS disconnected. Retrying in 5s...");
      chrome.storage.local.set({ status: "disconnected" });
      broadcastStatus("disconnected");
      setTimeout(connectGateway, 5000);
    };

    ws.onerror = (err) => {
      console.error("[Hermes Extension] Gateway WS Error:", err);
    };
  } catch (e) {
    console.error("[Hermes Extension] Failed to establish WS connection:", e);
    setTimeout(connectGateway, 5000);
  }
}

async function handleGatewayMessage(msg) {
  if (msg.type === "dom_action") {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.id) {
      chrome.tabs.sendMessage(tab.id, msg, (response) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({
            type: "dom_action_result",
            actionId: msg.actionId,
            result: response
          }));
        }
      });
    }
  }
}

function broadcastStatus(status) {
  chrome.runtime.sendMessage({ type: "STATUS_UPDATE", status });
}

// Handle extension popup messages
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "SUBMIT_TASK") {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: "user_task_prompt",
        prompt: request.prompt,
        timestamp: new Date().toISOString()
      }));
      sendResponse({ success: true, message: "Task dispatched to Hermes Agent!" });
    } else {
      sendResponse({ success: false, message: "Gateway not connected (ws://127.0.0.1:9119)" });
    }
  } else if (request.type === "GET_STATUS") {
    sendResponse({ status: isConnected ? "connected" : "disconnected" });
  }
  return true;
});

connectGateway();
