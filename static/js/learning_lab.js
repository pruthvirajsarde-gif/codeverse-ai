/**
 * CodeVerse AI - Special C++ Learning Lab (8 Specialized Developer Tools)
 */

window.LearningLab = (function() {
  'use strict';

  let conceptsData = [];
  let quizQuestions = [];
  let currentQuizIndex = 0;
  let quizScore = 0;

  function init() {
    setupTabSwitching();
    setupToolForms();
    loadConcepts();
    loadDailyChallenge();
    loadCheatSheet();
    loadViva();
  }

  function setupTabSwitching() {
    const tabBtns = document.querySelectorAll('.lab-tab-btn');
    const panes = document.querySelectorAll('.lab-tab-pane');

    tabBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        const target = btn.dataset.tab;
        tabBtns.forEach((b) => b.classList.remove('active'));
        panes.forEach((p) => p.classList.remove('active'));

        btn.classList.add('active');
        const targetPane = document.getElementById(`lab-pane-${target}`);
        if (targetPane) targetPane.classList.add('active');

        if (target === 'quiz' && quizQuestions.length === 0) {
          loadQuiz();
        }
      });
    });
  }

  function openLab(tabName = 'concepts') {
    const modal = document.getElementById('modal-learning-lab');
    if (!modal) return;
    modal.classList.add('open');

    // Activate specific tab
    const tabBtn = document.querySelector(`.lab-tab-btn[data-tab="${tabName}"]`);
    if (tabBtn) tabBtn.click();
  }

  function closeLab() {
    const modal = document.getElementById('modal-learning-lab');
    if (modal) modal.classList.remove('open');
  }

  function setupToolForms() {
    // Code Generator
    const btnGen = document.getElementById('btn-generate-code');
    if (btnGen) {
      btnGen.addEventListener('click', () => {
        const desc = document.getElementById('gen-problem-desc').value.trim();
        const std = document.getElementById('gen-std-select').value;
        const paradigm = document.getElementById('gen-paradigm-select').value;

        if (!desc) {
          window.CodeRunner.showToast('Please provide a problem description', 'error');
          return;
        }

        const prompt = `Generate a complete, modern C++ (${std}) program using the ${paradigm} paradigm for the following requirement:\n\n"${desc}"\n\nPlease include full headers, compilation instructions, time complexity, and a step-by-step breakdown.`;
        closeLab();
        window.ChatController.sendCustomPrompt(prompt);
      });
    }

    // Output Predictor
    const btnPredict = document.getElementById('btn-predict-output');
    if (btnPredict) {
      btnPredict.addEventListener('click', () => {
        const code = document.getElementById('predict-code-input').value.trim();
        if (!code) {
          window.CodeRunner.showToast('Please paste a C++ code snippet', 'error');
          return;
        }

        const prompt = `Predict the exact step-by-step output of the following C++ code. Provide a dry-run variable trace table and explain any subtleties:\n\n\`\`\`cpp\n${code}\n\`\`\``;
        closeLab();
        window.ChatController.sendCustomPrompt(prompt);
      });
    }

    // Debugging Assistant
    const btnDebug = document.getElementById('btn-debug-code');
    if (btnDebug) {
      btnDebug.addEventListener('click', () => {
        const code = document.getElementById('debug-code-input').value.trim();
        const errorLog = document.getElementById('debug-error-input').value.trim();

        if (!code) {
          window.CodeRunner.showToast('Please paste your C++ code', 'error');
          return;
        }

        let prompt = `Please debug this C++ code and provide a corrected, working version with explanation of root causes:\n\n\`\`\`cpp\n${code}\n\`\`\``;
        if (errorLog) {
          prompt += `\n\nCompiler / Runtime error message observed:\n\`\`\`text\n${errorLog}\n\`\`\``;
        }

        closeLab();
        window.ChatController.sendCustomPrompt(prompt);
      });
    }

    // Concept level filter buttons
    document.querySelectorAll('.btn-level-filter').forEach((btn) => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.btn-level-filter').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        filterConcepts(btn.dataset.level);
      });
    });
  }

  // 1. Concept Explorer
  async function loadConcepts() {
    const container = document.getElementById('concepts-grid-container');
    if (!container) return;

    try {
      const resp = await fetch('/api/learning-lab/concepts');
      const data = await resp.json();
      conceptsData = data.concepts || [];
      renderConcepts(conceptsData);
    } catch (e) {
      container.innerHTML = `<div style="color:var(--accent-danger);">Failed to load concepts: ${e.message}</div>`;
    }
  }

  function filterConcepts(level) {
    if (!level || level === 'all') {
      renderConcepts(conceptsData);
    } else {
      const filtered = conceptsData.filter((c) => c.level.toLowerCase() === level.toLowerCase());
      renderConcepts(filtered);
    }
  }

  function renderConcepts(list) {
    const container = document.getElementById('concepts-grid-container');
    if (!container) return;

    container.innerHTML = list.map((item) => `
      <div class="concept-item-card">
        <div style="display:flex;align-items:center;justify-content:space-between;">
          <span class="concept-level-badge ${item.level.toLowerCase()}">${item.level}</span>
          <span style="font-size:0.75rem;color:var(--text-muted);">${item.category}</span>
        </div>
        <h4 style="font-family:var(--font-main);font-size:1.05rem;color:var(--text-primary);margin:0;">${item.title}</h4>
        <p style="font-size:0.82rem;color:var(--text-secondary);flex:1;line-height:1.5;">${item.summary}</p>
        <div style="display:flex;gap:6px;flex-wrap:wrap;">
          ${item.tags.map((t) => `<span style="font-family:var(--font-code);font-size:0.7rem;background:rgba(56,189,248,0.1);color:var(--accent-cyan);padding:2px 6px;border-radius:4px;">${t}</span>`).join('')}
        </div>
        <button class="btn-topbar-action" style="width:100%;justify-content:center;margin-top:4px;" onclick="LearningLab.explainConceptInChat('${item.title}')">
          Explain in Chat →
        </button>
      </div>
    `).join('');
  }

  function explainConceptInChat(title) {
    closeLab();
    window.ChatController.sendCustomPrompt(`Explain "${title}" in C++ with beginner-friendly logic, a modern code example, output prediction, and common mistakes.`);
  }

  // 5. Quiz Mode
  async function loadQuiz() {
    try {
      const resp = await fetch('/api/learning-lab/quiz');
      const data = await resp.json();
      quizQuestions = data.questions || [];
      currentQuizIndex = 0;
      quizScore = 0;
      renderQuizQuestion();
    } catch (e) {
      const container = document.getElementById('quiz-view-container');
      if (container) container.innerHTML = `<div style="color:var(--accent-danger);">Failed to load quiz questions: ${e.message}</div>`;
    }
  }

  function renderQuizQuestion() {
    const container = document.getElementById('quiz-view-container');
    if (!container) return;

    if (currentQuizIndex >= quizQuestions.length) {
      container.innerHTML = `
        <div class="quiz-card" style="text-align:center;padding:36px;">
          <h3 style="font-family:var(--font-main);font-size:1.8rem;background:var(--grad-primary);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:12px;">Quiz Complete!</h3>
          <p style="font-size:1.1rem;color:var(--text-primary);margin-bottom:20px;">Your Final Score: <strong>${quizScore} / ${quizQuestions.length}</strong> (${Math.round((quizScore / quizQuestions.length) * 100)}%)</p>
          <button class="btn-lab-submit" onclick="LearningLab.restartQuiz()">Restart C++ Quiz</button>
        </div>
      `;
      return;
    }

    const q = quizQuestions[currentQuizIndex];
    container.innerHTML = `
      <div class="quiz-header-bar">
        <span>Question ${currentQuizIndex + 1} of ${quizQuestions.length}</span>
        <span class="quiz-score-badge">Score: ${quizScore}</span>
      </div>
      <div class="quiz-card">
        <div style="font-size:0.75rem;color:var(--accent-cyan);margin-bottom:8px;font-family:var(--font-code);">${q.category} • ${q.difficulty}</div>
        <div class="quiz-question-text">${escapeHtml(q.question)}</div>
        <div class="quiz-options-list">
          ${q.options.map((opt, i) => `
            <button class="quiz-option-btn" onclick="LearningLab.submitQuizAnswer(${i}, this)">
              <span style="font-family:var(--font-code);font-weight:bold;color:var(--accent-cyan);width:20px;">${String.fromCharCode(65 + i)}.</span>
              <span>${escapeHtml(opt)}</span>
            </button>
          `).join('')}
        </div>
        <div class="quiz-feedback-box" id="quiz-feedback"></div>
        <div style="margin-top:20px;display:flex;justify-content:flex-end;">
          <button class="btn-lab-submit" id="btn-next-quiz" style="display:none;" onclick="LearningLab.nextQuestion()">Next Question →</button>
        </div>
      </div>
    `;
  }

  function submitQuizAnswer(chosenIdx, btn) {
    const q = quizQuestions[currentQuizIndex];
    const buttons = document.querySelectorAll('.quiz-option-btn');
    buttons.forEach((b) => (b.disabled = true));

    const feedbackBox = document.getElementById('quiz-feedback');
    const nextBtn = document.getElementById('btn-next-quiz');

    if (chosenIdx === q.correct) {
      btn.classList.add('selected-correct');
      quizScore++;
      feedbackBox.style.display = 'block';
      feedbackBox.style.borderLeftColor = 'var(--accent-neon-green)';
      feedbackBox.innerHTML = `<strong>✓ Correct!</strong><br>${escapeHtml(q.explanation)}`;
    } else {
      btn.classList.add('selected-wrong');
      buttons[q.correct].classList.add('selected-correct');
      feedbackBox.style.display = 'block';
      feedbackBox.style.borderLeftColor = 'var(--accent-danger)';
      feedbackBox.innerHTML = `<strong>✕ Incorrect.</strong><br>${escapeHtml(q.explanation)}`;
    }

    if (nextBtn) nextBtn.style.display = 'inline-flex';
  }

  function nextQuestion() {
    currentQuizIndex++;
    renderQuizQuestion();
  }

  function restartQuiz() {
    currentQuizIndex = 0;
    quizScore = 0;
    renderQuizQuestion();
  }

  // 6. Daily Challenge
  async function loadDailyChallenge() {
    const container = document.getElementById('challenge-container');
    if (!container) return;

    try {
      const resp = await fetch('/api/learning-lab/challenge');
      const data = await resp.json();
      const ch = data.challenge;
      if (!ch) return;

      container.innerHTML = `
        <div class="quiz-card">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
            <h3 style="font-family:var(--font-main);font-size:1.3rem;color:var(--text-primary);margin:0;">${ch.title}</h3>
            <span class="concept-level-badge intermediate">${ch.difficulty}</span>
          </div>
          <p style="color:var(--text-secondary);font-size:0.92rem;margin-bottom:16px;">${ch.description}</p>
          
          <h4 style="color:var(--accent-cyan);margin-bottom:8px;font-size:0.95rem;">Starter Code:</h4>
          <div style="margin-bottom:16px;">
            <pre><code class="language-cpp">${escapeHtml(ch.starter_code)}</code></pre>
          </div>

          <details style="margin-bottom:16px;background:rgba(16,26,50,0.5);border-radius:6px;padding:10px 14px;border:1px solid var(--border-subtle);">
            <summary style="cursor:pointer;color:var(--accent-amber);font-weight:600;">💡 View Hints</summary>
            <ul style="margin:10px 0 0 20px;font-size:0.85rem;color:var(--text-secondary);">
              ${ch.hints.map((h) => `<li>${h}</li>`).join('')}
            </ul>
          </details>

          <button class="btn-lab-submit" onclick="LearningLab.solveChallengeInChat('${ch.title}')">Solve Challenge with AI Mentor →</button>
        </div>
      `;

      if (window.Prism) {
        container.querySelectorAll('pre code').forEach((el) => window.Prism.highlightElement(el));
      }
    } catch (e) {
      container.innerHTML = `<div style="color:var(--accent-danger);">Failed to load daily challenge.</div>`;
    }
  }

  function solveChallengeInChat(title) {
    closeLab();
    window.ChatController.sendCustomPrompt(`I am tackling the Daily C++ Challenge: "${title}". Can you give me an optimized C++ solution with both iterative and recursive approaches, along with space-time complexity analysis?`);
  }

  // 7. Cheat Sheet
  async function loadCheatSheet() {
    const container = document.getElementById('cheatsheet-container');
    if (!container) return;

    try {
      const resp = await fetch('/api/learning-lab/cheatsheet');
      const data = await resp.json();
      const cs = data.cheatsheet;

      container.innerHTML = `
        <h4 style="color:var(--accent-cyan);margin-bottom:12px;">⚡ STL Sequence & Associative Containers</h4>
        <div style="overflow-x:auto;margin-bottom:24px;">
          <table>
            <thead>
              <tr><th>Container</th><th>Internal Data Structure</th><th>Element Access</th><th>Insertion / Deletion</th><th>Header</th></tr>
            </thead>
            <tbody>
              ${cs.stl_containers.map((c) => `
                <tr>
                  <td><code>${c.container}</code></td>
                  <td>${c.underlying}</td>
                  <td>${c.access}</td>
                  <td>${c.insert_back}</td>
                  <td><code>${c.header}</code></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>

        <h4 style="color:var(--accent-cyan);margin-bottom:12px;">⚡ Modern C++ Core Keywords</h4>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin-bottom:24px;">
          ${cs.keywords.map((k) => `
            <div style="background:rgba(16,26,50,0.6);border:1px solid var(--border-subtle);border-radius:8px;padding:14px;">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
                <code style="color:var(--accent-cyan);font-weight:bold;">${k.keyword}</code>
                <span style="font-size:0.7rem;color:var(--text-muted);">${k.standard}</span>
              </div>
              <p style="font-size:0.82rem;color:var(--text-secondary);margin:0;">${k.desc}</p>
            </div>
          `).join('')}
        </div>
      `;
    } catch (e) {
      container.innerHTML = `<div style="color:var(--accent-danger);">Failed to load cheat sheet.</div>`;
    }
  }

  // 8. Viva Preparation
  async function loadViva() {
    const container = document.getElementById('viva-container');
    if (!container) return;

    try {
      const resp = await fetch('/api/learning-lab/viva');
      const data = await resp.json();
      const vivaList = data.viva || [];

      container.innerHTML = `
        <div style="margin-bottom:16px;">
          <p style="font-size:0.9rem;color:var(--text-secondary);">Frequently asked questions for engineering university practical evaluations, lab assessments, and technical viva examinations.</p>
        </div>
        ${vivaList.map((item, idx) => `
          <div class="viva-item-accordion" id="viva-acc-${idx}">
            <div class="viva-q-header" onclick="LearningLab.toggleVivaAccordion(${idx})">
              <span><strong>Q${idx + 1}.</strong> ${escapeHtml(item.q)}</span>
              <span style="color:var(--accent-cyan);font-size:1.2rem;">+</span>
            </div>
            <div class="viva-answer-content">
              ${escapeHtml(item.a).replace(/\n/g, '<br>')}
              <div style="margin-top:12px;">
                <button class="btn-topbar-action" style="font-size:0.75rem;" onclick="LearningLab.deepDiveViva('${escapeHtml(item.q)}')">Deep Dive in Chat →</button>
              </div>
            </div>
          </div>
        `).join('')}
      `;
    } catch (e) {
      container.innerHTML = `<div style="color:var(--accent-danger);">Failed to load viva questions.</div>`;
    }
  }

  function toggleVivaAccordion(idx) {
    const el = document.getElementById(`viva-acc-${idx}`);
    if (el) el.classList.toggle('open');
  }

  function deepDiveViva(question) {
    closeLab();
    window.ChatController.sendCustomPrompt(`Explain the viva question in detail with code and diagrams if applicable: "${question}"`);
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  return {
    init,
    openLab,
    closeLab,
    explainConceptInChat,
    submitQuizAnswer,
    nextQuestion,
    restartQuiz,
    solveChallengeInChat,
    toggleVivaAccordion,
    deepDiveViva
  };
})();
