/**
 * CodeVerse AI - Application Coordinator, Storage, and UI Orchestrator
 */

window.AppController = (function() {
  'use strict';

  let conversations = [];
  let activeConversationId = null;

  function init() {
    loadSettings();
    loadConversations();
    setupSidebarEvents();
    setupModals();
    setupShortcuts();
    fetchSystemStatus();

    // Initialize child controllers
    window.ChatController.init();
    window.LearningLab.init();
  }

  // --------------------------------------------------------------------------
  // System Status
  // --------------------------------------------------------------------------
  async function fetchSystemStatus() {
    try {
      const resp = await fetch('/api/status');
      const data = await resp.json();

      // Topbar Badge
      const aiBadge = document.getElementById('badge-ai-mode');
      if (aiBadge) {
        if (data.ai.is_live_api) {
          aiBadge.innerHTML = `<span class="status-dot"></span> <span>${data.ai.model} (Live API)</span>`;
          aiBadge.style.color = 'var(--accent-cyan)';
        } else {
          aiBadge.innerHTML = `<span class="status-dot offline"></span> <span>Smart Offline C++ Engine</span>`;
          aiBadge.style.color = 'var(--accent-amber)';
        }
      }

      // Sidebar Footer Compiler status
      const compLabel = document.getElementById('compiler-status-label');
      const compDot = document.getElementById('compiler-status-dot');
      if (compLabel && compDot) {
        if (data.compiler.configured) {
          compDot.className = 'status-dot';
          compLabel.textContent = `Compiler: ${data.compiler.compiler_name || 'Active'}`;
        } else {
          compDot.className = 'status-dot offline';
          compLabel.textContent = 'Compiler: Not Configured';
        }
      }
    } catch (e) {
      console.warn('Status check warning:', e);
    }
  }

  // --------------------------------------------------------------------------
  // Conversation & LocalStorage Management
  // --------------------------------------------------------------------------
  function loadConversations() {
    try {
      const raw = localStorage.getItem('codeverse_conversations');
      conversations = raw ? JSON.parse(raw) : [];
    } catch (e) {
      conversations = [];
    }

    if (conversations.length === 0) {
      createNewConversation(false);
    } else {
      activeConversationId = conversations[0].id;
      renderConversationsList();
      window.ChatController.loadConversationMessages(conversations[0].messages);
      updateTopBarTitle(conversations[0].title);
    }
  }

  function saveConversationsToStorage() {
    try {
      localStorage.setItem('codeverse_conversations', JSON.stringify(conversations));
    } catch (e) {
      console.error('Failed to save to localStorage:', e);
    }
  }

  function createNewConversation(switchView = true) {
    const newId = `conv-${Date.now()}`;
    const newConv = {
      id: newId,
      title: 'New C++ Conversation',
      messages: [],
      createdAt: Date.now(),
      updatedAt: Date.now()
    };

    conversations.unshift(newConv);
    activeConversationId = newId;
    saveConversationsToStorage();
    renderConversationsList();

    if (switchView) {
      window.ChatController.clearCurrentChat();
      updateTopBarTitle(newConv.title);
      closeMobileSidebar();
    }
  }

  function saveActiveConversation(messages) {
    const active = conversations.find((c) => c.id === activeConversationId);
    if (!active) return;

    active.messages = messages;
    active.updatedAt = Date.now();

    // Auto-generate title from first user query if still default
    if (active.title === 'New C++ Conversation' && messages.length > 0) {
      const firstUser = messages.find((m) => m.role === 'user');
      if (firstUser) {
        let clean = firstUser.content.slice(0, 32).trim();
        if (firstUser.content.length > 32) clean += '...';
        active.title = clean;
        updateTopBarTitle(clean);
      }
    }

    saveConversationsToStorage();
    renderConversationsList();
  }

  function selectConversation(id) {
    if (id === activeConversationId) return;

    const conv = conversations.find((c) => c.id === id);
    if (!conv) return;

    activeConversationId = id;
    renderConversationsList();
    window.ChatController.loadConversationMessages(conv.messages);
    updateTopBarTitle(conv.title);
    closeMobileSidebar();
  }

  function renameConversation(id, event) {
    if (event) event.stopPropagation();
    const conv = conversations.find((c) => c.id === id);
    if (!conv) return;

    const newTitle = prompt('Enter new conversation title:', conv.title);
    if (newTitle && newTitle.trim()) {
      conv.title = newTitle.trim();
      saveConversationsToStorage();
      renderConversationsList();
      if (id === activeConversationId) {
        updateTopBarTitle(conv.title);
      }
      window.CodeRunner.showToast('Conversation renamed', 'success');
    }
  }

  function deleteConversation(id, event) {
    if (event) event.stopPropagation();

    if (!confirm('Are you sure you want to delete this conversation?')) return;

    conversations = conversations.filter((c) => c.id !== id);
    saveConversationsToStorage();

    if (conversations.length === 0) {
      createNewConversation(true);
    } else {
      if (activeConversationId === id) {
        selectConversation(conversations[0].id);
      } else {
        renderConversationsList();
      }
    }
    window.CodeRunner.showToast('Conversation deleted', 'info');
  }

  function renderConversationsList(filterQuery = '') {
    const listEl = document.getElementById('conversations-container');
    if (!listEl) return;

    const filtered = filterQuery
      ? conversations.filter((c) => c.title.toLowerCase().includes(filterQuery.toLowerCase()))
      : conversations;

    if (filtered.length === 0) {
      listEl.innerHTML = `<div style="padding:16px;font-size:0.8rem;color:var(--text-muted);text-align:center;">No conversations found</div>`;
      return;
    }

    listEl.innerHTML = filtered
      .map((conv) => {
        const isActive = conv.id === activeConversationId;
        return `
        <div class="conversation-item ${isActive ? 'active' : ''}" onclick="AppController.selectConversation('${conv.id}')">
          <div class="conversation-title-row">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink:0;">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <span style="overflow:hidden;text-overflow:ellipsis;">${escapeHtml(conv.title)}</span>
          </div>
          <div class="conversation-actions">
            <button class="btn-item-action" title="Rename conversation" onclick="AppController.renameConversation('${conv.id}', event)">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
            </button>
            <button class="btn-item-action delete" title="Delete conversation" onclick="AppController.deleteConversation('${conv.id}', event)">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
            </button>
          </div>
        </div>
      `;
      })
      .join('');
  }

  function updateTopBarTitle(title) {
    const titleEl = document.getElementById('current-chat-title-text');
    if (titleEl) titleEl.textContent = title;
  }

  function clearAllChats() {
    if (!confirm('Warning: This will permanently delete ALL saved chat conversations. Proceed?')) return;

    conversations = [];
    localStorage.removeItem('codeverse_conversations');
    createNewConversation(true);
    window.CodeRunner.showToast('All chat history cleared', 'info');
  }

  function exportCurrentChat(format = 'markdown') {
    const active = conversations.find((c) => c.id === activeConversationId);
    if (!active || !active.messages || active.messages.length === 0) {
      window.CodeRunner.showToast('No messages in this chat to export', 'error');
      return;
    }

    let output = '';
    const dateStr = new Date(active.createdAt).toLocaleDateString();

    if (format === 'markdown') {
      output += `# ${active.title}\n`;
      output += `*CodeVerse AI - C++ Programming Mentor Session (${dateStr})*\n\n---\n\n`;

      active.messages.forEach((m) => {
        const sender = m.role === 'user' ? '🧑 **User**' : '💻 **CodeVerse AI**';
        output += `### ${sender} (${m.timestamp})\n\n${m.content}\n\n---\n\n`;
      });
    } else {
      output += `=== ${active.title} ===\nDate: ${dateStr}\n\n`;
      active.messages.forEach((m) => {
        const sender = m.role === 'user' ? 'User' : 'CodeVerse AI';
        output += `[${m.timestamp}] ${sender}:\n${m.content}\n\n--------------------------------\n\n`;
      });
    }

    const filename = `${active.title.replace(/[^a-zA-Z0-9_-]/g, '_')}.${format === 'markdown' ? 'md' : 'txt'}`;
    const blob = new Blob([output], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    window.CodeRunner.showToast(`Exported chat as ${filename}`, 'success');
  }

  // --------------------------------------------------------------------------
  // Sidebar & Layout Events
  // --------------------------------------------------------------------------
  function setupSidebarEvents() {
    const btnNew = document.getElementById('btn-new-chat');
    if (btnNew) btnNew.addEventListener('click', () => createNewConversation(true));

    const searchInput = document.getElementById('search-conversations-input');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        renderConversationsList(e.target.value.trim());
      });
    }

    const btnCollapse = document.getElementById('btn-sidebar-collapse');
    const sidebar = document.getElementById('sidebar');
    if (btnCollapse && sidebar) {
      btnCollapse.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
      });
    }

    // Mobile Hamburger
    const btnMobile = document.getElementById('btn-mobile-sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    if (btnMobile && sidebar) {
      btnMobile.addEventListener('click', () => {
        const isOpen = sidebar.classList.toggle('mobile-open');
        if (backdrop) backdrop.classList.toggle('active', isOpen);
      });
    }

    if (backdrop && sidebar) {
      backdrop.addEventListener('click', () => {
        closeMobileSidebar();
      });
    }

    // Export button
    const btnExport = document.getElementById('btn-export-chat');
    if (btnExport) {
      btnExport.addEventListener('click', () => exportCurrentChat('markdown'));
    }
  }

  function closeMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    if (sidebar) sidebar.classList.remove('mobile-open');
    if (backdrop) backdrop.classList.remove('active');
  }

  // --------------------------------------------------------------------------
  // Modals & Navigation
  // --------------------------------------------------------------------------
  function setupModals() {
    // Learning Lab open trigger
    const labTriggers = document.querySelectorAll('.trigger-open-lab');
    labTriggers.forEach((btn) => {
      btn.addEventListener('click', () => {
        const tab = btn.dataset.tab || 'concepts';
        window.LearningLab.openLab(tab);
        closeMobileSidebar();
      });
    });

    const btnCloseLab = document.getElementById('btn-close-lab');
    if (btnCloseLab) btnCloseLab.addEventListener('click', () => window.LearningLab.closeLab());

    // About Modal
    setupSimpleModal('btn-open-about', 'modal-about', 'btn-close-about');

    // Roadmap Modal
    setupSimpleModal('btn-open-roadmap', 'modal-roadmap', 'btn-close-roadmap');

    // Settings Modal
    setupSimpleModal('btn-open-settings', 'modal-settings', 'btn-close-settings');

    // Shortcuts Modal
    setupSimpleModal('btn-open-shortcuts', 'modal-shortcuts', 'btn-close-shortcuts');

    // Bookmarks / Saved answers drawer
    const btnBookmarks = document.getElementById('btn-open-favorites');
    const drawerFavorites = document.getElementById('drawer-favorites');
    const btnCloseFav = document.getElementById('btn-close-favorites');

    if (btnBookmarks && drawerFavorites) {
      btnBookmarks.addEventListener('click', () => {
        renderFavoritesDrawer();
        drawerFavorites.classList.add('open');
        closeMobileSidebar();
      });
    }
    if (btnCloseFav && drawerFavorites) {
      btnCloseFav.addEventListener('click', () => drawerFavorites.classList.remove('open'));
    }

    // Clear all chats trigger
    const btnClearAll = document.getElementById('btn-clear-all-chats');
    if (btnClearAll) btnClearAll.addEventListener('click', clearAllChats);

    // Theme selector
    const themeSelect = document.getElementById('theme-select');
    if (themeSelect) {
      themeSelect.value = localStorage.getItem('codeverse_theme') || 'midnight';
      themeSelect.addEventListener('change', (e) => {
        setTheme(e.target.value);
      });
    }

    // Reduced motion checkbox
    const motionCheckbox = document.getElementById('reduced-motion-toggle');
    if (motionCheckbox) {
      motionCheckbox.checked = document.body.classList.contains('reduced-motion');
      motionCheckbox.addEventListener('change', (e) => {
        setReducedMotion(e.target.checked);
      });
    }
  }

  function setupSimpleModal(triggerId, modalId, closeId) {
    const trigger = document.getElementById(triggerId);
    const modal = document.getElementById(modalId);
    const closeBtn = document.getElementById(closeId);

    if (trigger && modal) {
      trigger.addEventListener('click', () => {
        modal.classList.add('open');
        closeMobileSidebar();
      });
    }
    if (closeBtn && modal) {
      closeBtn.addEventListener('click', () => modal.classList.remove('open'));
    }
    if (modal) {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.remove('open');
      });
    }
  }

  function renderFavoritesDrawer() {
    const container = document.getElementById('favorites-list-container');
    if (!container) return;

    const saved = JSON.parse(localStorage.getItem('codeverse_favorites') || '[]');
    if (saved.length === 0) {
      container.innerHTML = `<div style="text-align:center;padding:30px;color:var(--text-muted);">No bookmarked answers yet. Bookmark answers by clicking "Save" in any response!</div>`;
      return;
    }

    container.innerHTML = saved
      .map(
        (item) => `
      <div style="background:rgba(16,26,50,0.6);border:1px solid var(--border-subtle);border-radius:10px;padding:14px;margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:0.75rem;color:var(--accent-cyan);">
          <span>★ Saved Answer</span>
          <span>${item.timestamp || ''}</span>
        </div>
        <div style="font-size:0.85rem;color:var(--text-secondary);max-height:120px;overflow:hidden;text-overflow:ellipsis;margin-bottom:10px;">
          ${escapeHtml(item.content.slice(0, 200))}...
        </div>
        <button class="btn-topbar-action" style="font-size:0.75rem;width:100%;justify-content:center;" onclick="AppController.copyFavorite('${item.id}')">
          Copy Content
        </button>
      </div>
    `
      )
      .join('');
  }

  function copyFavorite(favId) {
    const saved = JSON.parse(localStorage.getItem('codeverse_favorites') || '[]');
    const target = saved.find((s) => String(s.id) === String(favId));
    if (target) {
      navigator.clipboard.writeText(target.content);
      window.CodeRunner.showToast('Favorite response copied to clipboard!', 'success');
    }
  }

  // --------------------------------------------------------------------------
  // Settings & Themes
  // --------------------------------------------------------------------------
  function loadSettings() {
    const theme = localStorage.getItem('codeverse_theme') || 'midnight';
    setTheme(theme);

    const reducedMotion = localStorage.getItem('codeverse_reduced_motion') === 'true';
    setReducedMotion(reducedMotion);
  }

  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('codeverse_theme', theme);
  }

  function setReducedMotion(enable) {
    if (enable) {
      document.body.classList.add('reduced-motion');
      localStorage.setItem('codeverse_reduced_motion', 'true');
    } else {
      document.body.classList.remove('reduced-motion');
      localStorage.setItem('codeverse_reduced_motion', 'false');
    }
  }

  // --------------------------------------------------------------------------
  // Keyboard Shortcuts
  // --------------------------------------------------------------------------
  function setupShortcuts() {
    window.addEventListener('keydown', (e) => {
      // Ctrl+N: New Chat
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        createNewConversation(true);
      }
      // Ctrl+K: Focus search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const search = document.getElementById('search-conversations-input');
        if (search) search.focus();
      }
      // Esc: Close open modals & drawers
      if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.open').forEach((m) => m.classList.remove('open'));
        const drawer = document.getElementById('drawer-favorites');
        if (drawer) drawer.classList.remove('open');
        closeMobileSidebar();
      }
    });
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Start initialization on DOM ready
  document.addEventListener('DOMContentLoaded', init);

  return {
    selectConversation,
    renameConversation,
    deleteConversation,
    saveActiveConversation,
    copyFavorite
  };
})();
