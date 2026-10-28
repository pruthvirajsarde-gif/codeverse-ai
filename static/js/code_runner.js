/**
 * CodeVerse AI - C++ Code Execution, Copying, and File Management
 */

window.CodeRunner = (function() {
  'use strict';

  function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icon = type === 'success' ? '✓' : (type === 'error' ? '✕' : 'ℹ');
    toast.innerHTML = `<span style="color:var(--accent-cyan);font-weight:bold;">${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(8px)';
      toast.style.transition = 'all 0.25s ease';
      setTimeout(() => toast.remove(), 250);
    }, 3200);
  }

  function copyCode(btn, codeText) {
    if (!navigator.clipboard) {
      const textarea = document.createElement('textarea');
      textarea.value = codeText;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
    } else {
      navigator.clipboard.writeText(codeText);
    }

    const origHtml = btn.innerHTML;
    btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg> Copied!`;
    btn.style.color = 'var(--accent-neon-green)';
    btn.style.borderColor = 'var(--accent-neon-green)';

    showToast('C++ code snippet copied to clipboard', 'success');

    setTimeout(() => {
      btn.innerHTML = origHtml;
      btn.style.color = '';
      btn.style.borderColor = '';
    }, 2000);
  }

  function downloadCode(codeText, filename = 'main.cpp') {
    const blob = new Blob([codeText], { type: 'text/x-c++src;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast(`Downloaded ${filename}`, 'success');
  }

  function toggleCodeCollapse(btn, bodyWrapper) {
    bodyWrapper.classList.toggle('collapsed');
    const isCollapsed = bodyWrapper.classList.contains('collapsed');
    btn.innerHTML = isCollapsed
      ? `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg> Expand`
      : `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="18 15 12 9 6 15"></polyline></svg> Collapse`;
  }

  async function runCode(btn, codeText, outputPanel) {
    const origHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<div class="spinner-mini"></div> Compiling...`;

    outputPanel.classList.add('visible');
    outputPanel.innerHTML = `
      <div class="output-meta-row">
        <span class="output-status-tag info"><div class="spinner-mini"></div> Genuine C++ Compilation in progress...</span>
      </div>
      <div class="output-terminal" style="color:var(--text-muted);">Transmitting code to sandboxed C++ compiler...</div>
    `;

    try {
      const response = await fetch('/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: codeText, stdin: '' })
      });

      const res = await response.json();

      if (!res.configured) {
        // Required strictly by prompt:
        // "If code execution is not configured, show “Code execution is not configured yet” and explain how to enable it."
        outputPanel.innerHTML = `
          <div class="output-meta-row">
            <span class="output-status-tag info">⚠️ Configuration Notice</span>
          </div>
          <div class="output-terminal" style="color:var(--accent-amber);">
<strong>Code execution is not configured yet.</strong>

${res.error || res.message}

${res.instructions ? res.instructions : 'To enable genuine compilation, install MinGW-w64 or Clang on your machine and add g++ to PATH.'}
          </div>
        `;
        showToast('C++ execution environment not configured yet', 'info');
      } else if (res.compiled && res.success) {
        outputPanel.innerHTML = `
          <div class="output-meta-row">
            <span class="output-status-tag success">✓ Execution Successful (Exit Code: ${res.exit_code})</span>
            <span style="font-family:var(--font-code);font-size:0.75rem;color:var(--text-muted);">${res.execution_time_ms} ms</span>
          </div>
          <div class="output-terminal" style="color:var(--accent-neon-green);">${escapeHtml(res.output || '[Program executed successfully with no console output]')}</div>
        `;
        showToast('Program compiled and executed successfully!', 'success');
      } else if (!res.compiled) {
        outputPanel.innerHTML = `
          <div class="output-meta-row">
            <span class="output-status-tag error">✕ Compilation Error</span>
          </div>
          <div class="output-terminal" style="color:#f87171;">${escapeHtml(res.error || 'Compiler syntax or linkage error')}</div>
        `;
        showToast('Compilation error detected', 'error');
      } else {
        outputPanel.innerHTML = `
          <div class="output-meta-row">
            <span class="output-status-tag error">✕ Runtime Error (Exit Code: ${res.exit_code})</span>
            <span style="font-family:var(--font-code);font-size:0.75rem;color:var(--text-muted);">${res.execution_time_ms} ms</span>
          </div>
          <div class="output-terminal" style="color:#f87171;">${escapeHtml(res.error || res.output || 'Process terminated with non-zero exit code.')}</div>
        `;
        showToast('Program runtime error', 'error');
      }
    } catch (err) {
      outputPanel.innerHTML = `
        <div class="output-meta-row">
          <span class="output-status-tag error">✕ Network or Server Error</span>
        </div>
        <div class="output-terminal" style="color:#f87171;">Failed to connect to backend execution route: ${err.message}</div>
      `;
      showToast('Execution request failed', 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = origHtml;
    }
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  return {
    copyCode,
    downloadCode,
    toggleCodeCollapse,
    runCode,
    showToast
  };
})();
