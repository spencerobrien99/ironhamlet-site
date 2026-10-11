// IronHamlet marketing site: navigation toggle and demo-request form.
// No third-party scripts. The form endpoint is public by design (it identifies
// a form, not an account) and carries no credentials.
(function () {
  "use strict";

  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  var year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());

  var form = document.getElementById("demo-form");
  if (!form) return;

  var status = document.getElementById("form-status");
  var submit = form.querySelector("button[type=submit]");
  var started = Date.now();

  function setStatus(msg, kind) {
    status.textContent = msg;
    status.className = "form-status" + (kind ? " " + kind : "");
  }

  function mailtoFallback(data) {
    var to = form.getAttribute("data-mailto");
    if (!to) return false;
    var lines = [
      "Name: " + (data.get("name") || ""),
      "Organization: " + (data.get("organization") || ""),
      "Role: " + (data.get("role") || ""),
      "Email: " + (data.get("email") || ""),
      "Interest: " + (data.get("interest") || ""),
      "Team size: " + (data.get("team_size") || ""),
      "",
      data.get("message") || ""
    ];
    var subject = "IronHamlet demo request - " + (data.get("organization") || data.get("name") || "");
    window.location.href = "mailto:" + to + "?subject=" + encodeURIComponent(subject) +
      "&body=" + encodeURIComponent(lines.join("\n"));
    setStatus("Your email application should open with the request filled in. Send it to complete your request.", "ok");
    return true;
  }

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    if (!form.reportValidity()) return;

    var data = new FormData(form);
    // Spam protection: honeypot field must stay empty, and humans take longer than 3 s.
    if (data.get("_gotcha") || Date.now() - started < 3000) {
      setStatus("Thank you. Your request has been received.", "ok");
      form.reset();
      return;
    }

    var endpoint = form.getAttribute("data-endpoint");
    if (!endpoint) {
      if (!mailtoFallback(data)) setStatus("The request form is temporarily unavailable. Please try again later.", "err");
      return;
    }

    submit.disabled = true;
    setStatus("Sending...", "");
    fetch(endpoint, { method: "POST", body: data, headers: { Accept: "application/json" } })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        form.reset();
        setStatus("Thank you. Your request has been received. We will reply by email.", "ok");
      })
      .catch(function () {
        if (!mailtoFallback(data)) setStatus("Your request could not be sent. Please try again in a few minutes.", "err");
      })
      .finally(function () { submit.disabled = false; });
  });
})();
