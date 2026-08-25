/* AI私邮 落地页前端逻辑：问卷校验 + 人群预填 + 提交处理 */
(function () {
  "use strict";

  var form = document.getElementById("diagnosis-form");
  var goal = document.getElementById("goal");
  var examField = document.getElementById("exam-field");
  var examType = document.getElementById("exam_type");
  var email = document.getElementById("email");
  var emailError = document.getElementById("email-error");
  var successBox = document.getElementById("form-success");
  var submitBtn = form.querySelector('button[type="submit"]');

  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  /* 1. 人群卡片点击 → 预填 goal 并滚到问卷 */
  document.querySelectorAll(".audience-card").forEach(function (card) {
    card.addEventListener("click", function () {
      var g = card.getAttribute("data-goal");
      if (g && goal) {
        goal.value = g;
        toggleExamField();
      }
    });
  });

  /* 2. 目标=考试时显示 exam_type 必填 */
  function toggleExamField() {
    if (!examField || !goal) return;
    var isExam = goal.value === "考试";
    examField.hidden = !isExam;
    if (!isExam) {
      examType.value = "";
      examType.removeAttribute("required");
    } else {
      examType.setAttribute("required", "required");
    }
  }
  if (goal) goal.addEventListener("change", toggleExamField);

  /* 3. 邮箱实时校验提示 */
  function validateEmail() {
    var v = email.value.trim();
    if (!v) {
      emailError.textContent = "";
      return true;
    }
    var ok = EMAIL_RE.test(v);
    emailError.textContent = ok ? "" : "请输入正确的邮箱地址（如 name@example.com）";
    emailError.classList.toggle("error-msg", !ok);
    return ok;
  }
  if (email) email.addEventListener("blur", validateEmail);
  if (email) email.addEventListener("input", validateEmail);

  /* 4. 提交：真实 POST 到后端 /api/diagnosis（P2-3b 后端，2026-08-26 接入） */
  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    emailError.textContent = "";
    emailError.classList.remove("error-msg");

    var payload = {
      goal: goal.value,
      exam_type: goal.value === "考试" ? examType.value : "",
      level: document.getElementById("level").value,
      hours: document.getElementById("hours").value,
      scenario: document.getElementById("scenario").value.trim(),
      email: email.value.trim(),
      ts: new Date().toISOString()
    };

    var ok = true;
    ["goal", "level", "hours"].forEach(function (id) {
      var el = document.getElementById(id);
      if (!el.value) { el.focus(); ok = false; }
    });
    if (goal.value === "考试" && !examType.value) { examType.focus(); ok = false; }
    if (!EMAIL_RE.test(payload.email)) { email.focus(); ok = false; }

    if (!ok) {
      if (emailError) { emailError.textContent = "请补全必填项，并检查邮箱格式。"; emailError.classList.add("error-msg"); }
      return;
    }

    if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = "正在寄出…"; }

    fetch("/api/diagnosis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
      .then(function (resp) { return resp.json().then(function (d) { return { ok: resp.ok, d: d }; }); })
      .then(function (r) {
        if (r.ok && r.d.ok) {
          form.hidden = true;
          successBox.hidden = false;
          try { successBox.scrollIntoView({ behavior: "smooth", block: "center" }); } catch (e) {}
        } else {
          throw new Error((r.d && r.d.error) || "服务器返回异常");
        }
      })
      .catch(function (err) {
        if (emailError) {
          emailError.textContent = "发送失败：" + err.message + "（请确认服务已启动，或稍后重试）";
          emailError.classList.add("error-msg");
        }
      })
      .finally(function () {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = "免费领取诊断报告"; }
      });
  });
})();
