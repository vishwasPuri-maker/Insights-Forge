import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import landingCss from './landing.css?raw';
import landingMarkup from './landingMarkup.html?raw';

/**
 * DecisionIQ marketing landing page.
 *
 * The original design was authored as a standalone HTML file (see
 * reference/decisioniq_landing (1).html). To preserve the exact visual design,
 * its CSS and body markup are imported verbatim and its vanilla-JS behaviours
 * (scroll animations, count-ups, parallax) are ported into the effect below,
 * scoped to this component and cleaned up on unmount.
 *
 * Any CTA marked with data-login-cta navigates to the existing login screen.
 * This is a UI/routing-only screen — it touches no data/API layer.
 */
export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;

    // Load the marketing fonts used by the design (DM Sans + Inter).
    const fontLink = document.createElement('link');
    fontLink.rel = 'stylesheet';
    fontLink.href =
      'https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=Inter:wght@400;500;600&display=swap';
    document.head.appendChild(fontLink);

    // Expose the inline nav scroll helper used by the markup's onclick handlers.
    const w = window as unknown as { scrollToSection?: (id: string) => void };
    const prevScrollToSection = w.scrollToSection;
    w.scrollToSection = (id: string) => {
      const el = root.querySelector<HTMLElement>(`#${CSS.escape(id)}`);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    const cleanups: Array<() => void> = [];

    // --- Count-up numbers ---
    const countUp = (el: HTMLElement) => {
      const target = parseFloat(el.dataset.target || '');
      if (isNaN(target)) return;
      const dec = parseInt(el.dataset.dec || '0');
      const pre = el.dataset.pre || '';
      const suf = el.dataset.suf || '';
      const dur = 1100;
      const t0 = performance.now();
      const fmt = (v: number) => {
        let s = dec > 0 ? v.toFixed(dec) : Math.round(v).toString();
        if (dec === 0 && Math.abs(target) >= 1000) s = Math.round(v).toLocaleString('en-US');
        return pre + s + suf;
      };
      const step = (now: number) => {
        let p = Math.min(1, (now - t0) / dur);
        p = 1 - Math.pow(1 - p, 3);
        el.textContent = fmt(target * p);
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };

    // --- Sector blocks: activation + count-up ---
    const activeObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const block = entry.target as HTMLElement;
          if (entry.isIntersecting && entry.intersectionRatio >= 0.5) {
            if (!block.classList.contains('is-active')) {
              block.classList.add('is-active');
              block
                .querySelectorAll<HTMLElement>('.dash-kpi-value[data-target]')
                .forEach(countUp);
            }
          } else if (entry.intersectionRatio < 0.25) {
            block.classList.remove('is-active');
          }
        });
      },
      { threshold: [0, 0.25, 0.5, 0.75] },
    );
    root.querySelectorAll('.sector-block[data-animate]').forEach((b) => activeObserver.observe(b));
    cleanups.push(() => activeObserver.disconnect());

    // --- Dimming scrim as the next panel slides over the current one ---
    const panels = Array.from(root.querySelectorAll<HTMLElement>('.sector-block'));
    let ticking = false;
    const updateScrim = () => {
      const vh = window.innerHeight;
      for (let i = 0; i < panels.length - 1; i++) {
        const nextTop = panels[i + 1].getBoundingClientRect().top;
        let prog = 1 - nextTop / vh;
        prog = Math.max(0, Math.min(1, prog));
        panels[i].style.setProperty('--cover', prog.toFixed(3));
      }
      if (panels.length) panels[panels.length - 1].style.setProperty('--cover', '0');
      ticking = false;
    };
    const onScroll = () => {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(updateScrim);
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    updateScrim();
    cleanups.push(() => {
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onScroll);
    });
    if (!('IntersectionObserver' in window)) {
      panels.forEach((b) => b.classList.add('is-active'));
    }

    // --- Step cards animation ---
    const observerOptions: IntersectionObserverInit = {
      root: null,
      rootMargin: '0px',
      threshold: 0.15,
    };
    const stepObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
          setTimeout(() => entry.target.classList.add('visible'), index * 150);
        }
      });
    }, observerOptions);
    root.querySelectorAll('.step-card[data-animate-step]').forEach((c) => stepObserver.observe(c));
    cleanups.push(() => stepObserver.disconnect());

    // --- Feature cards animation ---
    const featureObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
          setTimeout(() => entry.target.classList.add('visible'), index * 150);
        }
      });
    }, observerOptions);
    root
      .querySelectorAll('.feature-card[data-animate-feature]')
      .forEach((c) => featureObserver.observe(c));
    cleanups.push(() => featureObserver.disconnect());

    // --- Parallax hero cards on mouse move ---
    const heroRight = root.querySelector<HTMLElement>('.hero-right');
    let onMouseMove: ((e: MouseEvent) => void) | null = null;
    if (heroRight) {
      onMouseMove = (e: MouseEvent) => {
        const x = (window.innerWidth / 2 - e.clientX) / 50;
        const y = (window.innerHeight / 2 - e.clientY) / 50;
        heroRight.querySelectorAll<HTMLElement>('.dashboard-card').forEach((card, i) => {
          const factor = (i + 1) * 0.5;
          card.style.transform = `translate(${x * factor}px, ${y * factor}px)`;
        });
      };
      document.addEventListener('mousemove', onMouseMove);
      cleanups.push(() => onMouseMove && document.removeEventListener('mousemove', onMouseMove));
    }

    // --- Nav shadow on scroll ---
    const nav = root.querySelector<HTMLElement>('.nav-capsule');
    const onNavScroll = () => {
      if (!nav) return;
      nav.style.boxShadow =
        window.pageYOffset > 100
          ? '0 4px 20px rgba(32,32,32,0.08)'
          : '0 1px 3px rgba(32,32,32,0.04), 0 4px 12px rgba(32,32,32,0.03)';
    };
    window.addEventListener('scroll', onNavScroll);
    cleanups.push(() => window.removeEventListener('scroll', onNavScroll));

    return () => {
      cleanups.forEach((fn) => fn());
      document.head.removeChild(fontLink);
      if (prevScrollToSection) w.scrollToSection = prevScrollToSection;
      else delete w.scrollToSection;
    };
  }, []);

  // Route any CTA marked data-login-cta to the login screen.
  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const target = (e.target as HTMLElement).closest('[data-login-cta]');
    if (target) {
      e.preventDefault();
      navigate('/login');
    }
  };

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: landingCss }} />
      <div
        ref={rootRef}
        onClick={handleClick}
        dangerouslySetInnerHTML={{ __html: landingMarkup }}
      />
    </>
  );
};

export default LandingPage;
