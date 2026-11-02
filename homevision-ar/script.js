document.addEventListener('DOMContentLoaded', () => {
  // Theme Toggle Logic
  const themeToggle = document.getElementById('themeToggle');
  const body = document.body;

  themeToggle.addEventListener('click', () => {
    if (body.classList.contains('dark-theme')) {
      body.classList.replace('dark-theme', 'light-theme');
      themeToggle.innerHTML = `
        <!-- Moon icon outline SVG -->
        <svg class="theme-icon moon-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
        </svg>
      `;
    } else {
      body.classList.replace('light-theme', 'dark-theme');
      themeToggle.innerHTML = `
        <!-- Sun icon outline SVG -->
        <svg class="theme-icon sun-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="5"></circle>
          <line x1="12" y1="1" x2="12" y2="3"></line>
          <line x1="12" y1="21" x2="12" y2="23"></line>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
          <line x1="1" y1="12" x2="3" y2="12"></line>
          <line x1="21" y1="12" x2="23" y2="12"></line>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        </svg>
      `;
    }
  });

  // Navigation Active State Highlights
  const navLinks = document.querySelectorAll('.nav-link');
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      navLinks.forEach(item => item.classList.remove('active'));
      link.classList.add('active');
    });
  });

  // Camera Toolbar Button Interaction
  const toolbarButtons = document.querySelectorAll('.toolbar-btn');
  toolbarButtons.forEach(button => {
    button.addEventListener('click', () => {
      // Toggle active states
      const isActive = button.classList.contains('active');
      toolbarButtons.forEach(btn => btn.classList.remove('active'));
      if (!isActive) {
        button.classList.add('active');
        console.log(`Camera action activated: ${button.dataset.action}`);
      }
    });
  });

  // Get Started Button Hover Micro-interactions
  const startBtn = document.querySelector('.cta-start-btn');
  startBtn.addEventListener('click', () => {
    alert('Initializing HomeVision AR Spatial Core... Connecting Cliffside Modern Living Area config.');
  });
});
