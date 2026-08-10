document.addEventListener("DOMContentLoaded", () => {
  const statusBadge = document.getElementById("statusBadge");
  const taskPrompt = document.getElementById("taskPrompt");
  const dispatchBtn = document.getElementById("dispatchBtn");
  const logBox = document.getElementById("logBox");

  function log(msg) {
    const time = new Date().toLocaleTimeString();
    logBox.innerText += `\n[${time}] ${msg}`;
    logBox.scrollTop = logBox.scrollHeight;
  }

  // Check initial connection status
  chrome.runtime.sendMessage({ type: "GET_STATUS" }, (response) => {
    if (response && response.status === "connected") {
      updateStatus("connected");
    } else {
      updateStatus("disconnected");
    }
  });

  // Listen for status updates
  chrome.runtime.onMessage.addListener((msg) => {
    if (msg.type === "STATUS_UPDATE") {
      updateStatus(msg.status);
    }
  });

  function updateStatus(status) {
    if (status === "connected") {
      statusBadge.innerText = "Active";
      statusBadge.className = "badge badge-connected";
      log("Connected to Hermes Agent Gateway!");
    } else {
      statusBadge.innerText = "Offline";
      statusBadge.className = "badge badge-disconnected";
      log("Disconnected from Gateway. Ensure hermes dashboard --tui is running.");
    }
  }

  dispatchBtn.addEventListener("click", () => {
    const prompt = taskPrompt.value.trim();
    if (!prompt) return;

    log(`Dispatching prompt: "${prompt.slice(0, 30)}..."`);
    chrome.runtime.sendMessage({ type: "SUBMIT_TASK", prompt }, (res) => {
      if (res && res.success) {
        log("Task dispatched successfully!");
        taskPrompt.value = "";
      } else {
        log(`Error: ${res ? res.message : "Failed to dispatch"}`);
      }
    });
  });
});
