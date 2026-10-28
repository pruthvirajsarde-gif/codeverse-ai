/**
 * CodeVerse AI - Core Chat Controller & Streaming Engine
 */

window.ChatController = (function() {
  'use strict';

  let currentMessages = [];
  let isGenerating = false;
  let activeAbortController = null;
  let rotatingStatusInterval = null;

  const ROTATING_MESSAGES = [
    'Parsing AST & Syntax Trees...',
    'Consulting ISO C++ Standard...',
    'Checking pointer safety & RAII...',
    'Analyzing algorithmic complexity...',
    'Synthesizing modern C++ solution...',
    'Optimizing cache locality...'
  ];

  function init() {
    setupEventListeners();
    setupTextareaAutoResize();
  }

  function setupEventListeners() {
    const chatInput = document.getElementById('chat-input');
    const btnSend = document.getElementById('btn-send');
    const btnStop = document.getElementById('btn-stop');
    const btnClearInput = document.getElementById('btn-clear-input');

    if (chatInput) {
      chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          if (!btnSend.disabled && !isGenerating) {
            sendMessage();
          }
        }
      });

      chatInput.addEventListener('input', () => {
        updateComposerState();
      });
    }

    if (btnSend) {
      btnSend.addEventListener('click', () => {
        if (!btnSend.disabled && !isGenerating) {
          sendMessage();
        }
      });
    }

    if (btnStop) {
      btnStop.addEventListener('click', stopGeneration);
    }

    if (btnClearInput) {
      btnClearInput.addEventListener('click', () => {
        if (chatInput) {
          chatInput.value = '';
          updateComposerState();
          chatInput.focus();
        }
      });
    }

    // Attach Suggestion Card Triggers
    document.querySelectorAll('.suggestion-card').forEach((card) => {
      card.addEventListener('click', () => {
        const type = card.dataset.type;
        handleSuggestionClick(type);
      });
    });

    // Attach Prompt Chip Triggers
    document.querySelectorAll('.prompt-chip').forEach((chip) => {
      chip.addEventListener('click', () => {
        const prompt = chip.dataset.prompt || chip.textContent.trim();
        sendCustomPrompt(prompt);
      });
    });
  }

  function setupTextareaAutoResize() {
    const textarea = document.getElementById('chat-input');
    if (!textarea) return;

    textarea.addEventListener('input', function() {
      this.style.height = 'auto';
      this.style.height = `${Math.min(this.scrollHeight, 180)}px`;
    });
  }

  function updateComposerState() {
    const input = document.getElementById('chat-input');
    const btnSend = document.getElementById('btn-send');
    const counter = document.getElementById('char-counter');

    if (!input || !btnSend) return;

    const len = input.value.trim().length;
    btnSend.disabled = len === 0 || isGenerating;

    if (counter) {
      counter.textContent = `${input.value.length} / 4000`;
      if (input.value.length > 3800) {
        counter.style.color = 'var(--accent-danger)';
      } else {
        counter.style.color = 'var(--text-muted)';
      }
    }
  }

  function handleSuggestionClick(type) {
    const input = document.getElementById('chat-input');
    if (type === 'learn') {
      sendCustomPrompt('Give detailed theory of C++ core concepts, memory models, OOP, templates, and STL with memory diagrams.');
    } else if (type === 'generate') {
      sendCustomPrompt('Give complete compilable C++ code demonstrating RAII and smart pointers with a step-by-step code walkthrough.');
    } else if (type === 'debug') {
      if (input) {
        input.value = 'Please debug this C++ code and explain the error:\n\n```cpp\n#include <iostream>\n\nint main() {\n    int* p = nullptr;\n    *p = 42;\n    return 0;\n}\n```';
        updateComposerState();
        input.focus();
      }
    } else if (type === 'predict') {
      if (input) {
        input.value = 'Predict the step-by-step output of this C++ program:\n\n```cpp\n#include <iostream>\n\nvoid modify(int& a, int* b) {\n    a += 10;\n    *b *= 2;\n}\n\nint main() {\n    int x = 5, y = 20;\n    modify(x, &y);\n    std::cout << x << " " << y << std::endl;\n    return 0;\n}\n```';
        updateComposerState();
        input.focus();
      }
    }
  }

  function sendCustomPrompt(promptText) {
    const input = document.getElementById('chat-input');
    if (input) {
      input.value = promptText;
      updateComposerState();
      sendMessage();
    }
  }

  async function sendMessage() {
    const input = document.getElementById('chat-input');
    if (!input) return;

    const messageText = input.value.trim();
    if (!messageText || isGenerating) return;

    // Reset input
    input.value = '';
    input.style.height = 'auto';
    updateComposerState();

    // Transition view from welcome hero if it's the first message
    hideWelcomeHero();

    // Add user message to state & UI
    const userMsg = {
      role: 'user',
      content: messageText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    currentMessages.push(userMsg);
    renderMessage(userMsg, currentMessages.length - 1);

    // Save state into active conversation in window.AppController
    if (window.AppController && window.AppController.saveActiveConversation) {
      window.AppController.saveActiveConversation(currentMessages);
    }

    // Scroll to bottom
    scrollToBottom();

    // Begin AI streaming
    await startStreamGeneration();
  }

  function hideWelcomeHero() {
    const hero = document.getElementById('chat-welcome');
    const messagesList = document.getElementById('messages-list');
    if (hero) hero.style.display = 'none';
    if (messagesList) messagesList.style.display = 'flex';
  }

  function showWelcomeHero() {
    const hero = document.getElementById('chat-welcome');
    const messagesList = document.getElementById('messages-list');
    if (hero) hero.style.display = 'flex';
    if (messagesList) {
      messagesList.style.display = 'none';
      messagesList.innerHTML = '';
    }
  }

  function startRotatingStatus() {
    const statusEl = document.getElementById('composer-rotating-status');
    const textEl = document.getElementById('rotating-status-text');
    if (!statusEl || !textEl) return;

    statusEl.classList.add('visible');
    let idx = 0;
    textEl.textContent = ROTATING_MESSAGES[0];

    rotatingStatusInterval = setInterval(() => {
      idx = (idx + 1) % ROTATING_MESSAGES.length;
      textEl.textContent = ROTATING_MESSAGES[idx];
    }, 2200);
  }

  function stopRotatingStatus() {
    const statusEl = document.getElementById('composer-rotating-status');
    if (statusEl) statusEl.classList.remove('visible');
    if (rotatingStatusInterval) {
      clearInterval(rotatingStatusInterval);
      rotatingStatusInterval = null;
    }
  }

  async function startStreamGeneration() {
    isGenerating = true;
    updateComposerControls(true);
    startRotatingStatus();

    activeAbortController = new AbortController();

    // Prepare assistant message slot
    const botMsg = {
      role: 'assistant',
      content: '',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isStreaming: true
    };
    currentMessages.push(botMsg);
    const botMsgIndex = currentMessages.length - 1;
    const bubbleEl = renderMessage(botMsg, botMsgIndex);

    scrollToBottom();

    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: currentMessages.slice(0, -1).map((m) => ({
            role: m.role,
            content: m.content
          }))
        }),
        signal: activeAbortController.signal
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // keep trailing incomplete chunk

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data: ')) {
            const jsonStr = trimmed.slice(6);
            try {
              const parsed = JSON.parse(jsonStr);
              if (parsed.chunk) {
                botMsg.content += parsed.chunk;
                updateBubbleContent(bubbleEl, botMsg.content, true);
                scrollToBottom();
              }
              if (parsed.done) {
                break;
              }
            } catch (err) {
              // Ignore non-json chunks
            }
          }
        }
      }

      botMsg.isStreaming = false;
      updateBubbleContent(bubbleEl, botMsg.content, false);
    } catch (err) {
      if (err.name === 'AbortError') {
        botMsg.content += '\n\n*(Generation stopped by user)*';
      } else {
        botMsg.content += `\n\n> ⚠️ **Error generating response:** ${err.message}. Please verify server connection or check terminal.`;
      }
      botMsg.isStreaming = false;
      updateBubbleContent(bubbleEl, botMsg.content, false);
    } finally {
      isGenerating = false;
      activeAbortController = null;
      updateComposerControls(false);
      stopRotatingStatus();

      // Persist full updated chat state
      if (window.AppController && window.AppController.saveActiveConversation) {
        window.AppController.saveActiveConversation(currentMessages);
      }
    }
  }

  function stopGeneration() {
    if (activeAbortController) {
      activeAbortController.abort();
      window.CodeRunner.showToast('Generation cancelled', 'info');
    }
  }

  function updateComposerControls(streaming) {
    const btnSend = document.getElementById('btn-send');
    const btnStop = document.getElementById('btn-stop');

    if (streaming) {
      if (btnSend) btnSend.style.display = 'none';
      if (btnStop) btnStop.classList.add('visible');
    } else {
      if (btnSend) btnSend.style.display = 'flex';
      if (btnStop) btnStop.classList.remove('visible');
      updateComposerState();
    }
  }

  function renderMessage(msg, index) {
    const list = document.getElementById('messages-list');
    if (!list) return null;

    const row = document.createElement('div');
    row.className = `message-row ${msg.role === 'user' ? 'user' : 'bot'}`;
    row.dataset.index = index;

    const avatar = document.createElement('div');
    avatar.className = `msg-avatar ${msg.role === 'user' ? 'user-avatar' : 'bot-avatar'}`;
    if (msg.role === 'user') {
      avatar.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`;
    } else {
      avatar.innerHTML = `<img src="/static/assets/logo.svg" alt="CodeVerse AI" />`;
    }

    const bubbleContainer = document.createElement('div');
    bubbleContainer.className = 'msg-bubble-container';

    const metaRow = document.createElement('div');
    metaRow.className = 'msg-meta-row';
    const authorName = msg.role === 'user' ? 'You' : 'CodeVerse AI';
    metaRow.innerHTML = `<span><strong>${authorName}</strong></span> <span>•</span> <span>${msg.timestamp}</span>`;

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';

    bubbleContainer.appendChild(metaRow);
    bubbleContainer.appendChild(bubble);

    // If bot message, create action toolbar
    if (msg.role === 'assistant') {
      const actionsToolbar = document.createElement('div');
      actionsToolbar.className = 'msg-actions-toolbar';
      actionsToolbar.innerHTML = `
        <button class="btn-msg-action" title="Copy response markdown" onclick="ChatController.copyMessageText(${index})">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg> Copy
        </button>
        <button class="btn-msg-action" title="Bookmark answer" onclick="ChatController.toggleBookmark(${index}, this)">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg> Save
        </button>
        <button class="btn-msg-action" title="Helpful" onclick="ChatController.voteResponse(${index}, 'up', this)">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg>
        </button>
        <button class="btn-msg-action" title="Unhelpful" onclick="ChatController.voteResponse(${index}, 'down', this)">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3"></path></svg>
        </button>
        <button class="btn-msg-action" title="Regenerate answer" onclick="ChatController.regenerateResponse(${index})">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6"></path><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg> Retry
        </button>
      `;
      bubbleContainer.appendChild(actionsToolbar);
    } else {
      // User message actions
      const actionsToolbar = document.createElement('div');
      actionsToolbar.className = 'msg-actions-toolbar';
      actionsToolbar.innerHTML = `
        <button class="btn-msg-action" title="Edit and resend" onclick="ChatController.editUserMessage(${index})">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg> Edit
        </button>
      `;
      bubbleContainer.appendChild(actionsToolbar);
    }

    row.appendChild(avatar);
    row.appendChild(bubbleContainer);
    list.appendChild(row);

    updateBubbleContent(bubble, msg.content, msg.isStreaming);
    return bubble;
  }

  function updateBubbleContent(bubble, rawContent, isStreaming = false) {
    if (!bubble) return;

    if (!rawContent) {
      bubble.innerHTML = `<span class="skeleton-shimmer" style="display:inline-block;width:140px;height:18px;"></span> <span class="typing-cursor"></span>`;
      return;
    }

    // Render markdown using Marked
    let html = '';
    if (window.marked) {
      try {
        html = window.marked.parse(rawContent);
      } catch (e) {
        html = escapeHtml(rawContent).replace(/\n/g, '<br>');
      }
    } else {
      html = escapeHtml(rawContent).replace(/\n/g, '<br>');
    }

    if (isStreaming) {
      html += `<span class="typing-cursor"></span>`;
    }

    bubble.innerHTML = html;

    // Enhance standard <pre><code> blocks into our professional C++ panels
    enhanceCodeBlocks(bubble);
  }

  function enhanceCodeBlocks(container) {
    const preBlocks = container.querySelectorAll('pre');

    preBlocks.forEach((pre) => {
      if (pre.closest('.code-block-wrapper')) return; // already enhanced

      const codeEl = pre.querySelector('code');
      const codeText = codeEl ? codeEl.textContent : pre.textContent;

      // Extract language class (default to cpp)
      let lang = 'cpp';
      if (codeEl) {
        const classes = codeEl.className.split(' ');
        for (const c of classes) {
          if (c.startsWith('language-')) {
            lang = c.replace('language-', '');
            break;
          }
        }
      }

      // Create wrapper
      const wrapper = document.createElement('div');
      wrapper.className = 'code-block-wrapper';

      const headerBar = document.createElement('div');
      headerBar.className = 'code-header-bar';
      headerBar.innerHTML = `
        <div class="code-lang-label">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
          <span>${lang === 'cpp' || lang === 'c++' ? 'C++' : lang.toUpperCase()}</span>
        </div>
        <div class="code-header-actions">
          <button class="btn-code-action btn-copy-code" title="Copy code">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg> Copy
          </button>
          <button class="btn-code-action btn-download-code" title="Download .cpp file">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg> Download
          </button>
          <button class="btn-code-action btn-collapse-code" title="Toggle expand/collapse">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="18 15 12 9 6 15"></polyline></svg> Collapse
          </button>
          <button class="btn-code-action btn-run-code" title="Compile & Run C++">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> Run Code
          </button>
        </div>
      `;

      const bodyWrapper = document.createElement('div');
      bodyWrapper.className = 'code-body-wrapper';

      const outputPanel = document.createElement('div');
      outputPanel.className = 'code-output-panel';

      // Insert wrapper into DOM
      pre.parentNode.insertBefore(wrapper, pre);
      bodyWrapper.appendChild(pre);
      wrapper.appendChild(headerBar);
      wrapper.appendChild(bodyWrapper);
      wrapper.appendChild(outputPanel);

      // Apply Prism Syntax Highlighting
      if (window.Prism && codeEl) {
        codeEl.className = `language-${lang}`;
        window.Prism.highlightElement(codeEl);
      }

      // Attach button events
      const btnCopy = headerBar.querySelector('.btn-copy-code');
      btnCopy.addEventListener('click', () => window.CodeRunner.copyCode(btnCopy, codeText));

      const btnDownload = headerBar.querySelector('.btn-download-code');
      btnDownload.addEventListener('click', () => window.CodeRunner.downloadCode(codeText, 'solution.cpp'));

      const btnCollapse = headerBar.querySelector('.btn-collapse-code');
      btnCollapse.addEventListener('click', () => window.CodeRunner.toggleCodeCollapse(btnCollapse, bodyWrapper));

      const btnRun = headerBar.querySelector('.btn-run-code');
      btnRun.addEventListener('click', () => window.CodeRunner.runCode(btnRun, codeText, outputPanel));
    });
  }

  function scrollToBottom() {
    const scrollArea = document.querySelector('.chat-scroll-area');
    if (scrollArea) {
      scrollArea.scrollTop = scrollArea.scrollHeight;
    }
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Action methods
  function copyMessageText(index) {
    const msg = currentMessages[index];
    if (msg) {
      navigator.clipboard.writeText(msg.content);
      window.CodeRunner.showToast('Response markdown copied to clipboard', 'success');
    }
  }

  function toggleBookmark(index, btn) {
    const msg = currentMessages[index];
    if (!msg) return;

    msg.bookmarked = !msg.bookmarked;
    btn.classList.toggle('active', msg.bookmarked);

    let saved = JSON.parse(localStorage.getItem('codeverse_favorites') || '[]');
    if (msg.bookmarked) {
      saved.push({
        id: Date.now(),
        content: msg.content,
        timestamp: msg.timestamp
      });
      window.CodeRunner.showToast('Answer saved to Favourites!', 'success');
    } else {
      saved = saved.filter((s) => s.content !== msg.content);
      window.CodeRunner.showToast('Removed from Favourites', 'info');
    }
    localStorage.setItem('codeverse_favorites', JSON.stringify(saved));
  }

  function voteResponse(index, type, btn) {
    const msg = currentMessages[index];
    if (!msg) return;

    msg.vote = type;
    btn.parentNode.querySelectorAll('button').forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    window.CodeRunner.showToast(`Feedback noted: ${type === 'up' ? 'Helpful' : 'Needs improvement'}`, 'info');
  }

  function editUserMessage(index) {
    const msg = currentMessages[index];
    if (!msg) return;

    const input = document.getElementById('chat-input');
    if (input) {
      input.value = msg.content;
      updateComposerState();
      input.focus();

      // Trim messages up to this point
      currentMessages = currentMessages.slice(0, index);
      refreshMessagesUI();
    }
  }

  async function regenerateResponse(botIndex) {
    if (isGenerating) return;

    // Find preceding user query
    let userMsgIdx = -1;
    for (let i = botIndex - 1; i >= 0; i--) {
      if (currentMessages[i].role === 'user') {
        userMsgIdx = i;
        break;
      }
    }

    if (userMsgIdx === -1) return;

    // Trim messages to user query and re-stream
    currentMessages = currentMessages.slice(0, userMsgIdx + 1);
    refreshMessagesUI();
    scrollToBottom();
    await startStreamGeneration();
  }

  function refreshMessagesUI() {
    const list = document.getElementById('messages-list');
    if (!list) return;

    list.innerHTML = '';
    if (currentMessages.length === 0) {
      showWelcomeHero();
    } else {
      hideWelcomeHero();
      currentMessages.forEach((m, idx) => renderMessage(m, idx));
    }
  }

  function loadConversationMessages(messages) {
    currentMessages = messages || [];
    refreshMessagesUI();
  }

  function getCurrentMessages() {
    return currentMessages;
  }

  function clearCurrentChat() {
    currentMessages = [];
    refreshMessagesUI();
    showWelcomeHero();
  }

  return {
    init,
    sendMessage,
    sendCustomPrompt,
    stopGeneration,
    copyMessageText,
    toggleBookmark,
    voteResponse,
    editUserMessage,
    regenerateResponse,
    loadConversationMessages,
    getCurrentMessages,
    clearCurrentChat
  };
})();
