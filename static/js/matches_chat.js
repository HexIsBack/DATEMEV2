/**
 * DateMe — matches_chat.js
 * Handles chat auto-scroll and the report modal.
 */

document.addEventListener("DOMContentLoaded", function () {

  /* ── Auto-scroll chat to latest message ── */
  const chatBody = document.getElementById("chatBody");
  if (chatBody) {
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  /* ── Report modal ── */
  const modal        = document.getElementById("reportModal");
  const submitBtn    = document.getElementById("submitReport");
  const reasonInput  = document.getElementById("reasonInput");

  function openReport() {
    if (modal) modal.classList.add("show");
  }

  function closeReport() {
    if (modal) modal.classList.remove("show");
  }

  function selectReason(btn, val) {
    document.querySelectorAll(".reason-btn").forEach(function (b) {
      b.classList.remove("selected");
    });
    btn.classList.add("selected");
    if (reasonInput) reasonInput.value = val;
    if (submitBtn)   submitBtn.disabled = false;
  }

  /* Close modal when clicking the dark overlay */
  if (modal) {
    modal.addEventListener("click", function (e) {
      if (e.target === modal) closeReport();
    });
  }

  /* Expose to inline onclick handlers in the template */
  window.openReport   = openReport;
  window.closeReport  = closeReport;
  window.selectReason = selectReason;

});
