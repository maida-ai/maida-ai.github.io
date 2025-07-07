// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        // Only remove .active if this link isn't already active
        if (!this.classList.contains('active')) {
            document.querySelectorAll('.nav-links a').forEach(link => link.classList.remove('active'));
        }
        const target = document.querySelector(this.getAttribute('href'));
        if (!target) return;
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
});

// Intersection Observer for animations
if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all elements with animation classes
    document.querySelectorAll('.fade-in, .slide-in').forEach(element => {
        observer.observe(element);
    });
}

// Navbar scroll effect
const navbar = document.querySelector('.navbar');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll <= 0) {
        navbar.classList.remove('scroll-up');
        return;
    }

    if (currentScroll > lastScroll && !navbar.classList.contains('scroll-down')) {
        navbar.classList.remove('scroll-up');
        navbar.classList.add('scroll-down');
    } else if (currentScroll < lastScroll && navbar.classList.contains('scroll-down')) {
        navbar.classList.remove('scroll-down');
        navbar.classList.add('scroll-up');
    }
    lastScroll = currentScroll;
});

// Mobile menu functionality
const mobileMenuButton = document.querySelector('.mobile-menu');
const navLinks = document.querySelector('.nav-links');

mobileMenuButton.addEventListener('click', () => {
    const expanded = navLinks.classList.toggle('active');
    document.body.classList.toggle('menu-open');
    mobileMenuButton.setAttribute('aria-expanded', expanded.toString());
});

// Close mobile menu when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.navbar')) {
        navLinks.classList.remove('active');
        document.body.classList.remove('menu-open');
    }
});

// Close mobile menu when clicking a link
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
        navLinks.classList.remove('active');
        document.body.classList.remove('menu-open');
    });
});

// Active section highlighting
const sections = document.querySelectorAll('section[id]');
const navItems = document.querySelectorAll('.nav-links a');

const sectionObserverOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.4
};

const sectionObserver = new IntersectionObserver((entries) => {
    // Get all intersecting entries
    const visible = entries.filter(entry => entry.isIntersecting);
    if (visible.length > 0) {
        // Find the one closest to the top (smallest boundingClientRect.top)
        const topSection = visible.reduce((prev, curr) => {
            return prev.boundingClientRect.top < curr.boundingClientRect.top ? prev : curr;
        });
        const id = topSection.target.getAttribute('id');
        navItems.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${id}`) {
                link.classList.add('active');
            }
        });
    }
}, sectionObserverOptions);

sections.forEach(section => {
    sectionObserver.observe(section);
});

// Theme toggle for light mode
if (localStorage.getItem('prefersLight') === 'true') {
  document.documentElement.classList.add('theme-light');
}

const themeSwitch = document.querySelector('#theme-switch');
if (themeSwitch) {
  themeSwitch.addEventListener('click', () => {
    const root = document.documentElement;
    const usingLight = root.classList.toggle('theme-light');
    localStorage.setItem('prefersLight', usingLight);
  });
}
