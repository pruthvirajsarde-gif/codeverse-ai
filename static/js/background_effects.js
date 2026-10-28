/**
 * CodeVerse AI - Futuristic Background Matrix & Floating C++ Tokens
 */

(function() {
  'use strict';

  const canvas = document.getElementById('canvas-matrix');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let width = (canvas.width = window.innerWidth);
  let height = (canvas.height = window.innerHeight);

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  // C++ Programming Matrix Symbols
  const symbols = [
    '{', '}', ';', '::', '->', '0', '1', '++', '--',
    '#include', 'template', '<T>', 'std::cout', 'std::cin',
    'nullptr', 'auto&&', 'constexpr', 'virtual', 'override',
    '&', '*', '~', 'public:', 'private:', 'throw', 'catch',
    'std::vector', 'std::unique_ptr', 'std::move', 'sizeof'
  ];

  const fontSize = 14;
  const columns = Math.floor(width / (fontSize * 1.8));
  const drops = Array(columns).fill(1).map(() => Math.floor(Math.random() * -50));

  function drawMatrix() {
    if (document.body.classList.contains('reduced-motion')) return;

    // Semi-transparent fade
    ctx.fillStyle = 'rgba(7, 10, 19, 0.08)';
    ctx.fillRect(0, 0, width, height);

    ctx.font = `${fontSize}px 'Fira Code', monospace`;

    for (let i = 0; i < drops.length; i++) {
      const text = symbols[Math.floor(Math.random() * symbols.length)];
      const x = i * (fontSize * 1.8);
      const y = drops[i] * fontSize;

      // Electric cyan / blue / subtle purple color variation
      const randColor = Math.random();
      if (randColor > 0.85) {
        ctx.fillStyle = '#00f2fe'; // Bright cyan
      } else if (randColor > 0.65) {
        ctx.fillStyle = '#3b82f6'; // Electric blue
      } else if (randColor > 0.45) {
        ctx.fillStyle = '#a855f7'; // Purple
      } else {
        ctx.fillStyle = 'rgba(56, 189, 248, 0.28)'; // Dim blue
      }

      ctx.fillText(text, x, y);

      if (y > height && Math.random() > 0.985) {
        drops[i] = 0;
      }
      drops[i]++;
    }
  }

  let animationInterval = setInterval(drawMatrix, 45);

  // Floating C++ Code Tokens
  const tokenContainer = document.querySelector('.floating-tokens-container');
  const tokenList = [
    '#include <iostream>',
    'std::vector<int> numbers;',
    'auto ptr = std::make_unique<Node>();',
    'template <typename T> class Stack;',
    'virtual void execute() override;',
    'std::cout << "CodeVerse" << std::endl;',
    'constexpr int MAX_NODES = 1024;',
    'int* p = &data;',
    'delete[] buffer;',
    'std::move(resource);',
    'noexcept;'
  ];

  function spawnFloatingToken() {
    if (!tokenContainer || document.body.classList.contains('reduced-motion')) return;

    const tokenEl = document.createElement('div');
    tokenEl.className = 'floating-token';
    tokenEl.textContent = tokenList[Math.floor(Math.random() * tokenList.length)];
    tokenEl.style.left = `${Math.random() * 85 + 5}%`;
    const duration = Math.random() * 14 + 18; // 18s - 32s
    tokenEl.style.animationDuration = `${duration}s`;
    tokenEl.style.fontSize = `${Math.random() * 0.2 + 0.72}rem`;

    tokenContainer.appendChild(tokenEl);

    setTimeout(() => {
      tokenEl.remove();
    }, duration * 1000);
  }

  // Spawn initial tokens
  for (let i = 0; i < 7; i++) {
    setTimeout(spawnFloatingToken, i * 2500);
  }
  setInterval(spawnFloatingToken, 4500);
})();
