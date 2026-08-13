(() => {
  const initialTargetId = window.location.hash.slice(1);
  const initialTarget = initialTargetId ? document.getElementById(initialTargetId) : null;
  if (initialTarget) {
    document.documentElement.style.scrollBehavior = 'auto';
    const navigationOffset = 68;
    const targetTop = initialTarget.getBoundingClientRect().top + window.scrollY - navigationOffset;
    window.scrollTo(0, targetTop);
    requestAnimationFrame(() => document.documentElement.style.removeProperty('scroll-behavior'));
  }

  const revealElements = [...document.querySelectorAll('.reveal')];

  if ('IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.08, rootMargin: '0px 0px -8% 0px' },
    );
    revealElements.forEach((element) => revealObserver.observe(element));
  } else {
    revealElements.forEach((element) => element.classList.add('visible'));
  }

  const siteNavigation = document.querySelector('[data-site-navigation]');
  const menuButton = document.querySelector('[data-menu-toggle]');
  const mobileNavigation = document.querySelector('[data-mobile-navigation]');

  const setMenuOpen = (isOpen) => {
    if (!menuButton || !mobileNavigation) return;
    menuButton.setAttribute('aria-expanded', String(isOpen));
    menuButton.setAttribute('aria-label', isOpen ? 'Close navigation' : 'Open navigation');
    mobileNavigation.hidden = !isOpen;
  };

  menuButton?.addEventListener('click', () => {
    setMenuOpen(menuButton.getAttribute('aria-expanded') !== 'true');
  });

  mobileNavigation?.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => setMenuOpen(false));
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    setMenuOpen(false);
    menuButton?.focus();
  });

  const updateNavigationSurface = () => {
    siteNavigation?.classList.toggle('is-scrolled', window.scrollY > 12);
  };
  updateNavigationSurface();
  window.addEventListener('scroll', updateNavigationSurface, { passive: true });

  const sections = [...document.querySelectorAll('[data-nav-section]')];
  const sectionLinks = [...document.querySelectorAll('[data-section-link]')];
  const sectionToNavigationItem = {
    gate: 'product',
    behavior: 'product',
    evidence: 'product',
  };

  const setActiveSection = (sectionId) => {
    const navigationId = sectionToNavigationItem[sectionId] || sectionId;
    sectionLinks.forEach((link) => {
      if (link.dataset.sectionLink === navigationId) {
        link.setAttribute('aria-current', 'location');
      } else {
        link.removeAttribute('aria-current');
      }
    });
  };

  if (sections.length && sectionLinks.length && 'IntersectionObserver' in window) {
    setActiveSection(sections[0].id);
    const sectionObserver = new IntersectionObserver(
      (entries) => {
        const activeEntry = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => Math.abs(a.boundingClientRect.top) - Math.abs(b.boundingClientRect.top))[0];
        if (activeEntry) setActiveSection(activeEntry.target.id);
      },
      { rootMargin: '-28% 0px -58% 0px', threshold: 0 },
    );
    sections.forEach((section) => sectionObserver.observe(section));
  }
})();
