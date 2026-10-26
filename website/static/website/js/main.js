/**
 * AETHER - Modern Interactive UI Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
  initHeaderScroll();
  initMobileNav();
  initToastDismiss();
  initCardMouseFollow();
  initOrbMovement();
});

/* Sticky Header Scroll Effect */
function initHeaderScroll() {
  const header = document.querySelector('.site-header');
  if (!header) return;

  const handleScroll = () => {
    if (window.scrollY > 20) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  };

  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();
}

/* Mobile Navigation Toggle */
function initMobileNav() {
  const toggleBtn = document.getElementById('mobile-nav-toggle');
  const navMenu = document.getElementById('primary-nav-menu');

  if (!toggleBtn || !navMenu) return;

  toggleBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = navMenu.classList.toggle('open');
    toggleBtn.setAttribute('aria-expanded', isOpen);

    // Toggle icon animation
    const icon = toggleBtn.querySelector('svg');
    if (icon) {
      icon.style.transform = isOpen ? 'rotate(90deg)' : 'rotate(0deg)';
    }
  });

  // Close when clicking outside
  document.addEventListener('click', (e) => {
    if (navMenu.classList.contains('open') && !navMenu.contains(e.target) && !toggleBtn.contains(e.target)) {
      navMenu.classList.remove('open');
      toggleBtn.setAttribute('aria-expanded', 'false');
      const icon = toggleBtn.querySelector('svg');
      if (icon) icon.style.transform = 'rotate(0deg)';
    }
  });
}

/* Dismissible Toast Notifications */
function initToastDismiss() {
  const toasts = document.querySelectorAll('.toast-message');

  toasts.forEach((toast) => {
    const closeBtn = toast.querySelector('.toast-close-btn');

    const dismissToast = () => {
      toast.style.transform = 'translateX(60px) scale(0.9)';
      toast.style.opacity = '0';
      setTimeout(() => {
        if (toast.parentNode) {
          toast.remove();
        }
      }, 300);
    };

    if (closeBtn) {
      closeBtn.addEventListener('click', dismissToast);
    }

    // Auto-dismiss after 6.5 seconds
    setTimeout(dismissToast, 6500);
  });
}

/* Subtle Interactive Mouse Hover Highlight on Glass Cards */
function initCardMouseFollow() {
  const cards = document.querySelectorAll('.glass-card');

  cards.forEach((card) => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      card.style.setProperty('--mouse-x', `${x}px`);
      card.style.setProperty('--mouse-y', `${y}px`);
    });
  });
}

/* Dynamic Ambient Orb Drift on Cursor */
function initOrbMovement() {
  const orbs = document.querySelectorAll('.ambient-orb');
  if (orbs.length === 0 || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  let mouseX = 0;
  let mouseY = 0;
  let currentX = 0;
  let currentY = 0;

  window.addEventListener('mousemove', (e) => {
    mouseX = (e.clientX / window.innerWidth - 0.5) * 40;
    mouseY = (e.clientY / window.innerHeight - 0.5) * 40;
  }, { passive: true });

  const render = () => {
    currentX += (mouseX - currentX) * 0.05;
    currentY += (mouseY - currentY) * 0.05;

    orbs.forEach((orb, idx) => {
      const factor = (idx + 1) * 0.4;
      orb.style.transform = `translate(${currentX * factor}px, ${currentY * factor}px)`;
    });

    requestAnimationFrame(render);
  };

  requestAnimationFrame(render);
}
