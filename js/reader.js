/**
 * AMINA Experience — Interactive E-Reader Engine
 * Manages full manuscript rendering, table of contents drawer,
 * theme switching, font size scaling, reading progress tracking
 */

(function (global) {
  'use strict';

  class ReaderEngine {
    constructor() {
      this.container = null;
      this.bookData = null;
      this.currentSectionType = 'chapter'; // 'chapter' | 'preambule' | 'guide'
      this.currentChapterIndex = 0; // 0 to 10
      this.currentTheme = 'night';
      this.currentFontSize = 17;
      this.isDrawerOpen = false;
    }

    init(container) {
      this.container = container;
      this.bookData = (typeof window !== 'undefined' && window.AMINA_BOOK) || null;
      if (!this.bookData) {
        console.warn('[AminaReader] No book data found');
        return;
      }

      // Restore preferences from AminaState
      const prefs = window.AminaState ? window.AminaState.getPreferences() : {};
      if (prefs.theme) this.currentTheme = prefs.theme;
      if (prefs.fontSize) this.currentFontSize = prefs.fontSize;
      if (prefs.lastChapter) this.currentChapterIndex = Math.max(0, Math.min(10, prefs.lastChapter - 1));

      this._renderBaseLayout();
      this._bindEvents();
      this.setTheme(this.currentTheme);
      this.setFontSize(this.currentFontSize);
      this.openChapter(this.currentChapterIndex + 1);
    }

    _renderBaseLayout() {
      this.container.innerHTML = `
        <div class="reader-screen theme-${this.currentTheme}" id="reader-screen-wrap">
          <!-- Reading Progress Bar -->
          <div class="reader-progress-bar-wrap">
            <div class="reader-progress-bar-fill" id="reader-progress-fill"></div>
          </div>

          <!-- Reader Toolbar -->
          <header class="reader-toolbar">
            <div class="toolbar-left">
              <button class="toolbar-btn" id="btn-open-drawer" aria-label="Sommaire du roman">
                <svg viewBox="0 0 24 24">
                  <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
                </svg>
                <span>Sommaire</span>
              </button>
            </div>

            <div class="toolbar-right">
              <!-- Font Size Sizer -->
              <div class="font-size-group">
                <button class="font-size-btn" id="btn-font-dec" aria-label="Réduire la police">A-</button>
                <span class="font-size-indicator" id="font-size-val">${this.currentFontSize}</span>
                <button class="font-size-btn" id="btn-font-inc" aria-label="Agrandir la police">A+</button>
              </div>

              <!-- Theme Pills -->
              <div class="theme-pills">
                <button class="theme-pill theme-pill-night ${this.currentTheme === 'night' ? 'active' : ''}" data-theme="night" aria-label="Thème Nuit"></button>
                <button class="theme-pill theme-pill-sepia ${this.currentTheme === 'sepia' ? 'active' : ''}" data-theme="sepia" aria-label="Thème Sépia"></button>
                <button class="theme-pill theme-pill-light ${this.currentTheme === 'light' ? 'active' : ''}" data-theme="light" aria-label="Thème Clair"></button>
              </div>
            </div>
          </header>

          <!-- Scrollable Article Reading Area -->
          <main class="reader-scroll-content" id="reader-scroll-viewport">
            <article class="reader-article" id="reader-article-content"></article>
          </main>

          <!-- Slide-out Drawer (Sommaire) -->
          <div class="reader-drawer-overlay" id="reader-drawer-overlay">
            <aside class="reader-drawer">
              <div class="drawer-header">
                <h3>Table des Matières</h3>
                <button class="icon-btn" id="btn-close-drawer" aria-label="Fermer le sommaire">
                  <svg viewBox="0 0 24 24">
                    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                  </svg>
                </button>
              </div>
              <nav class="drawer-items-list" id="drawer-items-list"></nav>
            </aside>
          </div>
        </div>
      `;

      this._renderDrawerItems();
    }

    _renderDrawerItems() {
      const list = document.getElementById('drawer-items-list');
      if (!list || !this.bookData) return;

      let html = `
        <div class="drawer-item ${this.currentSectionType === 'preambule' ? 'active' : ''}" data-type="preambule">
          <div>
            <div class="drawer-item-title">Préambule Canonique</div>
            <div class="drawer-item-sub">Dédicace, Préface & Introduction</div>
          </div>
          <span class="badge badge-gold">Intro</span>
        </div>
      `;

      this.bookData.chapters.forEach((chap, idx) => {
        const isActive = this.currentSectionType === 'chapter' && this.currentChapterIndex === idx;
        html += `
          <div class="drawer-item ${isActive ? 'active' : ''}" data-type="chapter" data-chapter="${chap.number}">
            <div>
              <div class="drawer-item-title">Ch. ${chap.number} : ${chap.title.replace(/^Chapitre \d+\s*:\s*/, '')}</div>
              <div class="drawer-item-sub">${chap.wordCount} mots • ~${chap.readingTimeMinutes} min</div>
            </div>
            <span class="badge ${chap.number <= 3 ? 'badge-free' : 'badge-gold'}">
              ${chap.number <= 3 ? 'Gratuit' : 'Ep ' + chap.number}
            </span>
          </div>
        `;
      });

      html += `
        <div class="drawer-item ${this.currentSectionType === 'guide' ? 'active' : ''}" data-type="guide">
          <div>
            <div class="drawer-item-title">Guide Pratique & Prière</div>
            <div class="drawer-item-sub">3 Principes d'Yvan Castanou</div>
          </div>
          <span class="badge badge-gold">Fin</span>
        </div>
      `;

      list.innerHTML = html;

      // Click bindings for drawer items
      list.querySelectorAll('.drawer-item').forEach(item => {
        item.addEventListener('click', () => {
          const type = item.getAttribute('data-type');
          if (type === 'preambule') {
            this.openPreambule();
          } else if (type === 'guide') {
            this.openGuide();
          } else if (type === 'chapter') {
            const chapNum = parseInt(item.getAttribute('data-chapter'), 10);
            this.openChapter(chapNum);
          }
          this.closeDrawer();
        });
      });
    }

    _bindEvents() {
      // 1. Drawer Toggles
      document.getElementById('btn-open-drawer')?.addEventListener('click', () => this.openDrawer());
      document.getElementById('btn-close-drawer')?.addEventListener('click', () => this.closeDrawer());
      document.getElementById('reader-drawer-overlay')?.addEventListener('click', (e) => {
        if (e.target.id === 'reader-drawer-overlay') this.closeDrawer();
      });

      // 2. Font Size Buttons
      document.getElementById('btn-font-dec')?.addEventListener('click', () => {
        this.setFontSize(this.currentFontSize - 1);
      });
      document.getElementById('btn-font-inc')?.addEventListener('click', () => {
        this.setFontSize(this.currentFontSize + 1);
      });

      // 3. Theme Pills
      document.querySelectorAll('.theme-pill').forEach(pill => {
        pill.addEventListener('click', () => {
          const theme = pill.getAttribute('data-theme');
          this.setTheme(theme);
        });
      });

      // 4. Scroll progress tracking
      const scrollEl = document.getElementById('reader-scroll-viewport');
      if (scrollEl) {
        scrollEl.addEventListener('scroll', () => {
          const maxScroll = scrollEl.scrollHeight - scrollEl.clientHeight;
          const ratio = maxScroll > 0 ? scrollEl.scrollTop / maxScroll : 0;
          const fill = document.getElementById('reader-progress-fill');
          if (fill) fill.style.width = `${Math.min(100, Math.max(0, ratio * 100))}%`;

          // Save progress in AminaState
          if (this.currentSectionType === 'chapter' && window.AminaState) {
            const chap = this.bookData.chapters[this.currentChapterIndex];
            if (chap) {
              window.AminaState.setReadingProgress(chap.id, ratio);
            }
          }
        }, { passive: true });
      }
    }

    openChapter(chapterNumber) {
      if (!this.bookData || !this.bookData.chapters.length) return;
      const num = Number(chapterNumber);
      const safeNum = (Number.isNaN(num) || !Number.isFinite(num)) ? 1 : num;
      const idx = Math.max(0, Math.min(this.bookData.chapters.length - 1, safeNum - 1));
      this.currentChapterIndex = idx;
      this.currentSectionType = 'chapter';

      const chap = this.bookData.chapters[idx];
      const article = document.getElementById('reader-article-content');
      if (!article) return;

      // Update state
      if (window.AminaState) {
        window.AminaState.setPreference('lastChapter', chap.number);
      }

      // Generate HTML
      const titleWithoutPrefix = chap.title.replace(/^Chapitre \d+\s*:\s*/, '');
      const psalmRef = chap.psalmVerse && chap.psalmVerse.ref ? chap.psalmVerse.ref : 'Psaume 91';
      const psalmText = chap.psalmVerse && chap.psalmVerse.text ? chap.psalmVerse.text : '';

      let paragraphsHtml = '';
      chap.paragraphs.forEach((p, pIdx) => {
        const isFirst = pIdx === 0;
        // Escape basic html and add drop-cap to first paragraph
        const formatted = p.replace(/\*(.*?)\*/g, '<em>$1</em>');
        paragraphsHtml += `<p class="${isFirst ? 'drop-cap' : ''}">${formatted}</p>`;
      });

      article.innerHTML = `
        <header class="chapter-header">
          <span class="chapter-number-tag">CHAPITRE ${String(chap.number).padStart(2, '0')}</span>
          <h1 class="chapter-title">${titleWithoutPrefix}</h1>
          <div class="chapter-meta-row">
            <span>⏱️ ${chap.readingTimeMinutes} min de lecture</span>
            <span>•</span>
            <span>✍️ Karl DIGRÉ</span>
          </div>

          <!-- Psalm 91 Scripture Callout -->
          <div class="scripture-card">
            <strong>${psalmRef}</strong>
            « ${psalmText} »
          </div>

          <!-- Contextual CTA to watch matching micro-drama -->
          <button class="contextual-watch-btn" id="btn-contextual-watch">
            <div class="watch-btn-left">
              <svg viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z"/>
              </svg>
              <div style="text-align: left;">
                <div class="watch-btn-title">Voir l'épisode micro-drama ${chap.number}</div>
                <div class="watch-btn-sub">Format vertical 9:16 immersif</div>
              </div>
            </div>
            <span class="badge badge-gold">Regarder</span>
          </button>
        </header>

        <!-- Chapter Body Prose -->
        <div class="reader-body">
          ${paragraphsHtml}
        </div>

        <!-- Chapter Bottom Navigation -->
        <nav class="chapter-bottom-nav">
          ${chap.number > 1 ? `
            <button class="btn btn-outline-gold" id="btn-prev-chapter">
              <span>← Chapitre ${chap.number - 1}</span>
            </button>
          ` : `
            <button class="btn btn-outline-gold" id="btn-to-preambule">
              <span>← Préambule</span>
            </button>
          `}
          ${chap.number < 11 ? `
            <button class="btn btn-gold" id="btn-next-chapter">
              <span>Chapitre ${chap.number + 1} →</span>
            </button>
          ` : `
            <button class="btn btn-gold" id="btn-to-guide">
              <span>Guide Pratique →</span>
            </button>
          `}
        </nav>

        <!-- WhatsApp Book Order Banner -->
        <div class="book-order-banner">
          <h3>Soutenez l'Œuvre & Commandez le Roman Papier</h3>
          <p>Recevez votre exemplaire physique dédicacé par Karl DIGRÉ à Abidjan (ou version e-book complète) pour 5 000 FCFA.</p>
          <a href="https://wa.me/2250700889514?text=Bonjour%20Karl%20DIGR%C3%A9%2C%20je%20souhaite%20commander%20le%20livre%20physique%20AMINA%20d%C3%A9dicac%C3%A9%20%C3%A0%20Abidjan." 
             target="_blank" rel="noopener noreferrer" class="btn btn-whatsapp">
            <span>💬 Commander sur WhatsApp (+225 07 00 88 95 14)</span>
          </a>
        </div>
      `;

      // Bind dynamic buttons
      document.getElementById('btn-contextual-watch')?.addEventListener('click', () => {
        if (window.AminaApp) window.AminaApp.switchTab('player');
        if (window.AminaPlayer) window.AminaPlayer.goToEpisode(chap.number - 1);
      });

      document.getElementById('btn-prev-chapter')?.addEventListener('click', () => {
        this.openChapter(chap.number - 1);
      });
      document.getElementById('btn-next-chapter')?.addEventListener('click', () => {
        this.openChapter(chap.number + 1);
      });
      document.getElementById('btn-to-preambule')?.addEventListener('click', () => {
        this.openPreambule();
      });
      document.getElementById('btn-to-guide')?.addEventListener('click', () => {
        this.openGuide();
      });

      // Scroll to top
      const scrollEl = document.getElementById('reader-scroll-viewport');
      if (scrollEl) scrollEl.scrollTop = 0;

      this._renderDrawerItems();
    }

    openPreambule() {
      if (!this.bookData || !this.bookData.preambule) return;
      this.currentSectionType = 'preambule';
      const p = this.bookData.preambule;
      const article = document.getElementById('reader-article-content');
      if (!article) return;

      article.innerHTML = `
        <header class="chapter-header">
          <span class="chapter-number-tag">LIMINAIRE</span>
          <h1 class="chapter-title">AMINA : L'Autel De Yopougon</h1>
          <div class="chapter-meta-row">
            <span>Auteur : Karl DIGRÉ</span>
            <span>•</span>
            <span>Abidjan, Côte d'Ivoire</span>
          </div>
        </header>

        <div class="reader-body">
          <h2 style="font-family: var(--font-display); color: var(--reader-title-color); margin: 24px 0 12px;">Dédicace</h2>
          ${p.dedicace.paragraphs.map((para, i) => `<p class="${i === 0 ? 'drop-cap' : ''}">${para}</p>`).join('')}

          <hr style="margin: 32px 0; border: none; border-top: 1px solid var(--reader-border);">

          <h2 style="font-family: var(--font-display); color: var(--reader-title-color); margin: 24px 0 12px;">Préface de l'Auteur</h2>
          ${p.preface.paragraphs.map(para => `<p>${para.replace(/\*(.*?)\*/g, '<em>$1</em>')}</p>`).join('')}

          <hr style="margin: 32px 0; border: none; border-top: 1px solid var(--reader-border);">

          <h2 style="font-family: var(--font-display); color: var(--reader-title-color); margin: 24px 0 12px;">${p.introduction.title}</h2>
          ${p.introduction.paragraphs.map(para => `<p>${para.replace(/\*(.*?)\*/g, '<em>$1</em>')}</p>`).join('')}
        </div>

        <nav class="chapter-bottom-nav">
          <div></div>
          <button class="btn btn-gold" id="btn-start-reading">
            <span>Commencer le Chapitre 1 →</span>
          </button>
        </nav>
      `;

      document.getElementById('btn-start-reading')?.addEventListener('click', () => {
        this.openChapter(1);
      });

      const scrollEl = document.getElementById('reader-scroll-viewport');
      if (scrollEl) scrollEl.scrollTop = 0;

      this._renderDrawerItems();
    }

    openGuide() {
      if (!this.bookData || !this.bookData.guide) return;
      this.currentSectionType = 'guide';
      const g = this.bookData.guide;
      const article = document.getElementById('reader-article-content');
      if (!article) return;

      let principlesHtml = '';
      g.principles.forEach(pr => {
        principlesHtml += `
          <div style="background: var(--reader-surface); border: 1px solid var(--reader-border); border-radius: var(--radius-md); padding: 18px; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
              <span class="badge badge-gold">Pilier ${pr.number}</span>
              <h3 style="font-size: 16px; font-weight: 700; color: var(--reader-title-color);">${pr.title}</h3>
            </div>
            <p style="font-size: 14px; line-height: 1.6; opacity: 0.9;">${pr.summary}</p>
          </div>
        `;
      });

      article.innerHTML = `
        <header class="chapter-header">
          <span class="chapter-number-tag">ÉPILOGUE & MINISTÈRE</span>
          <h1 class="chapter-title">${g.title}</h1>
          <div class="chapter-meta-row">
            <span>Enseignements inspirés d'Yvan Castanou</span>
          </div>
        </header>

        <div class="reader-body">
          <p class="drop-cap">${g.paragraphs[0] || ''}</p>
          <div style="margin: 28px 0;">
            ${principlesHtml}
          </div>
          ${g.paragraphs.slice(1).map(p => `<p>${p}</p>`).join('')}
        </div>

        <div class="book-order-banner">
          <h3>Commander le Roman Dédicacé</h3>
          <p>Contact direct avec l'auteur pour obtenir le livre imprimé ou soutenir la production des prochains épisodes.</p>
          <a href="https://wa.me/2250700889514?text=Bonjour%20Karl%20DIGR%C3%A9%2C%20je%20vous%20contacte%20depuis%20la%20PWA%20AMINA%20pour%20commander%20le%20livre."
             target="_blank" rel="noopener noreferrer" class="btn btn-whatsapp">
            <span>💬 Contacter sur WhatsApp (+225 07 00 88 95 14)</span>
          </a>
        </div>

        <nav class="chapter-bottom-nav">
          <button class="btn btn-outline-gold" id="btn-back-chap11">
            <span>← Chapitre 11</span>
          </button>
          <button class="btn btn-gold" id="btn-return-player">
            <span>Retourner aux Vidéos 🎬</span>
          </button>
        </nav>
      `;

      document.getElementById('btn-back-chap11')?.addEventListener('click', () => {
        this.openChapter(11);
      });
      document.getElementById('btn-return-player')?.addEventListener('click', () => {
        if (window.AminaApp) window.AminaApp.switchTab('player');
      });

      const scrollEl = document.getElementById('reader-scroll-viewport');
      if (scrollEl) scrollEl.scrollTop = 0;

      this._renderDrawerItems();
    }

    setTheme(themeName) {
      const validThemes = ['night', 'sepia', 'light'];
      if (!validThemes.includes(themeName)) return;
      this.currentTheme = themeName;

      const screen = document.getElementById('reader-screen-wrap');
      if (screen) {
        screen.classList.remove('theme-night', 'theme-sepia', 'theme-light');
        screen.classList.add(`theme-${themeName}`);
      }

      document.querySelectorAll('.theme-pill').forEach(pill => {
        pill.classList.toggle('active', pill.getAttribute('data-theme') === themeName);
      });

      if (window.AminaState) {
        window.AminaState.setPreference('theme', themeName);
      }
    }

    setFontSize(sizePx) {
      const num = Number(sizePx);
      const safePx = (Number.isNaN(num) || !Number.isFinite(num)) ? 17 : num;
      const clamped = Math.max(15, Math.min(24, safePx));
      this.currentFontSize = clamped;

      const screen = document.getElementById('reader-screen-wrap');
      if (screen) {
        screen.style.setProperty('--reader-font-size', `${clamped}px`);
      }

      const val = document.getElementById('font-size-val');
      if (val) val.textContent = clamped;

      if (window.AminaState) {
        window.AminaState.setPreference('fontSize', clamped);
      }
    }

    openDrawer() {
      this.isDrawerOpen = true;
      document.getElementById('reader-drawer-overlay')?.classList.add('open');
    }

    closeDrawer() {
      this.isDrawerOpen = false;
      document.getElementById('reader-drawer-overlay')?.classList.remove('open');
    }
  }

  const readerInstance = new ReaderEngine();

  if (typeof window !== 'undefined') {
    window.AminaReader = readerInstance;
  }
  if (typeof globalThis !== 'undefined') {
    globalThis.AminaReader = readerInstance;
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AminaReader: readerInstance, ReaderEngine };
  }
})(typeof window !== 'undefined' ? window : globalThis);
