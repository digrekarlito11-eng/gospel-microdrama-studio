/**
 * AMINA Experience — Monetization Engine & Mobile Money CI Simulator
 * Wave CI, Orange Money CI, MTN MoMo simulation, WhatsApp viral sharing,
 * direct WhatsApp book order with Karl DIGRÉ (+225 07 00 88 95 14).
 */

(function (global) {
  'use strict';

  class MonetizationEngine {
    constructor() {
      this.currentEpisodeId = null;
      this.selectedOperator = 'wave';
      this.isProcessing = false;
      this.backdropEl = null;
      this.officialWhatsAppNumber = '2250700889514';
    }

    init() {
      this._createModalContainer();
      this._bindGlobalTriggers();
    }

    _createModalContainer() {
      let backdrop = document.getElementById('monetization-modal-backdrop');
      if (!backdrop) {
        backdrop = document.createElement('div');
        backdrop.id = 'monetization-modal-backdrop';
        backdrop.className = 'modal-backdrop';
        document.body.appendChild(backdrop);
      }
      this.backdropEl = backdrop;

      // Close on backdrop click
      backdrop.addEventListener('click', (e) => {
        if (e.target.id === 'monetization-modal-backdrop' && !this.isProcessing) {
          this.closeModal();
        }
      });
    }

    _bindGlobalTriggers() {
      // Listen for escape key
      window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !this.isProcessing) {
          this.closeModal();
        }
      });
    }

    /**
     * Opens the Unlock Modal for a locked episode
     * @param {string} episodeId - e.g. 'ep-004'
     */
    openUnlockModal(episodeId) {
      this.currentEpisodeId = episodeId || 'ep-004';
      const episodes = (window.AMINA_EPISODES) || [];
      const ep = episodes.find(e => e.id === this.currentEpisodeId) || {
        number: 4,
        title: "Épisode Verrouillé",
        hook: "200 000 Francs d'urgence ou les soins s'arrêtent à minuit..."
      };

      const shareText = encodeURIComponent(
        `Découvre AMINA : L'Autel De Yopougon, la première série micro-drama chrétienne d'Abidjan ! Regarde les premiers épisodes ici : https://digrekarlito11-eng.github.io/gospel-microdrama-studio`
      );
      const waShareUrl = `https://api.whatsapp.com/send?text=${shareText}`;

      this.backdropEl.innerHTML = `
        <div class="modal-card" id="unlock-modal-card">
          <button class="modal-close-btn" id="btn-modal-close" aria-label="Fermer">
            <svg viewBox="0 0 24 24">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>

          <div class="modal-header">
            <span class="badge badge-locked">ÉPISODE ${String(ep.number).padStart(2, '0')} VERROUILLÉ</span>
            <h3 class="modal-title">${ep.title}</h3>
            <p class="modal-sub">Choisissez votre mode d'accès ci-dessous</p>
          </div>

          <div class="modal-tabs">
            <button class="modal-tab-btn active" id="tab-btn-share" data-tab="share">
              📱 Partage WhatsApp (Gratuit)
            </button>
            <button class="modal-tab-btn" id="tab-btn-pass" data-tab="pass">
              ⭐ Pass Saison MoMo (1 000 F)
            </button>
          </div>

          <!-- Tab 1: WhatsApp Share Flow -->
          <div class="tab-panel active" id="panel-share">
            <div class="whatsapp-share-card">
              <p class="share-benefit">
                Partagez l'épisode avec <strong>vos proches ou en statut WhatsApp</strong> pour débloquer immédiatement l'épisode ${ep.number} gratuitement !
              </p>
              <div class="share-preview-box">
                « Découvre AMINA : L'Autel De Yopougon, la première série micro-drama chrétienne d'Abidjan... »
              </div>
              <a href="${waShareUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-whatsapp" id="btn-trigger-wa-share">
                <span>💬 Envoyer sur WhatsApp</span>
              </a>
              <button class="btn btn-outline-gold" id="btn-confirm-wa-share">
                <span>✅ J'ai partagé (Débloquer)</span>
              </button>
            </div>
          </div>

          <!-- Tab 2: Mobile Money CI Season Pass Flow -->
          <div class="tab-panel" id="panel-pass">
            <div class="momo-section" id="momo-checkout-wrap">
              <div class="price-banner">
                <div class="price-desc">
                  <div>Pass Saison Intégral</div>
                  <div style="font-size: 11px; opacity: 0.7;">11 Épisodes + Roman Complet</div>
                </div>
                <div class="price-amount">1 000 FCFA</div>
              </div>

              <!-- Operator Selectors -->
              <div class="operator-selector">
                <div class="operator-card selected" data-operator="wave" id="op-wave">
                  <div class="operator-badge-logo">W</div>
                  <div class="operator-name">Wave CI</div>
                  <div class="operator-hint">Push instantané</div>
                </div>
                <div class="operator-card" data-operator="orange" id="op-orange">
                  <div class="operator-badge-logo">OM</div>
                  <div class="operator-name">Orange</div>
                  <div class="operator-hint">#144*82#</div>
                </div>
                <div class="operator-card" data-operator="mtn" id="op-mtn">
                  <div class="operator-badge-logo">MTN</div>
                  <div class="operator-name">MTN MoMo</div>
                  <div class="operator-hint">*133#</div>
                </div>
              </div>

              <!-- Phone Input Form -->
              <div class="form-group">
                <label class="form-label" for="momo-phone-input">Numéro de téléphone Côte d'Ivoire :</label>
                <div class="input-with-prefix">
                  <span class="input-prefix">+225</span>
                  <input type="tel" id="momo-phone-input" class="form-input" placeholder="07 00 88 95 14" value="07 00 88 95 14">
                </div>
              </div>

              <button class="btn btn-gold" id="btn-submit-momo" style="width: 100%;">
                <span>Payer 1 000 FCFA via Wave</span>
              </button>
            </div>

            <!-- Processing Simulation (Hidden initially) -->
            <div class="simulation-processing" id="momo-processing-view" style="display: none;">
              <div class="spinner-ring"></div>
              <div class="processing-step-text" id="processing-step-msg">Connexion sécurisée...</div>
              <div class="processing-sub-text">Ne fermez pas cette fenêtre (simulation CI)</div>
            </div>

            <!-- Success Simulation (Hidden initially) -->
            <div class="simulation-success" id="momo-success-view" style="display: none;">
              <div class="success-icon-wrap">
                <svg viewBox="0 0 24 24">
                  <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/>
                </svg>
              </div>
              <h3 style="color: var(--gold-bright);">Pass Saison Activé !</h3>
              <p style="font-size: 13px; color: rgba(255,255,255,0.8);">
                Félicitations ! Les 11 épisodes et le manuscrit complet sont désormais débloqués en illimité.
              </p>
              <button class="btn btn-gold" id="btn-close-success" style="width: 100%;">
                <span>Continuer le Visionnage 🎬</span>
              </button>
            </div>
          </div>
        </div>
      `;

      this._bindModalEvents();
      this.backdropEl.classList.add('open');
    }

    _bindModalEvents() {
      document.getElementById('btn-modal-close')?.addEventListener('click', () => this.closeModal());

      // Tabs switching
      const tabShare = document.getElementById('tab-btn-share');
      const tabPass = document.getElementById('tab-btn-pass');
      const panelShare = document.getElementById('panel-share');
      const panelPass = document.getElementById('panel-pass');

      tabShare?.addEventListener('click', () => {
        tabShare.classList.add('active');
        tabPass.classList.remove('active');
        panelShare.classList.add('active');
        panelPass.classList.remove('active');
      });

      tabPass?.addEventListener('click', () => {
        tabPass.classList.add('active');
        tabShare.classList.remove('active');
        panelPass.classList.add('active');
        panelShare.classList.remove('active');
      });

      // WhatsApp Share Click
      document.getElementById('btn-trigger-wa-share')?.addEventListener('click', () => {
        if (window.AminaState) {
          window.AminaState.recordWhatsAppShare(this.currentEpisodeId);
        }
      });

      // WhatsApp Confirm Unlock
      document.getElementById('btn-confirm-wa-share')?.addEventListener('click', () => {
        if (window.AminaState && this.currentEpisodeId) {
          window.AminaState.unlockEpisode(this.currentEpisodeId);
          this.triggerConfetti();
          this.showToast(`Épisode débloqué avec succès ! Gloire à Dieu !`, 'success');
          this.closeModal();
        }
      });

      // Operator selection
      const ops = ['wave', 'orange', 'mtn'];
      ops.forEach(op => {
        document.getElementById(`op-${op}`)?.addEventListener('click', () => {
          ops.forEach(o => document.getElementById(`op-${o}`)?.classList.remove('selected'));
          document.getElementById(`op-${op}`)?.classList.add('selected');
          this.selectedOperator = op;

          const btn = document.getElementById('btn-submit-momo');
          if (btn) {
            const opName = op === 'wave' ? 'Wave' : (op === 'orange' ? 'Orange Money' : 'MTN MoMo');
            btn.innerHTML = `<span>Payer 1 000 FCFA via ${opName}</span>`;
          }
        });
      });

      // Submit Mobile Money Simulation
      document.getElementById('btn-submit-momo')?.addEventListener('click', () => {
        const phone = document.getElementById('momo-phone-input')?.value || '07 00 88 95 14';
        this.simulateMoMoPayment(this.selectedOperator, phone);
      });

      document.getElementById('btn-close-success')?.addEventListener('click', () => {
        this.closeModal();
      });
    }

    /**
     * High-Fidelity Realistic Mobile Money Simulation
     */
    simulateMoMoPayment(operator, phone) {
      if (this.isProcessing) return;
      this.isProcessing = true;

      try {
        const checkoutWrap = document.getElementById('momo-checkout-wrap');
        const processingView = document.getElementById('momo-processing-view');
        const successView = document.getElementById('momo-success-view');
        const stepMsg = document.getElementById('processing-step-msg');
        const opName = operator === 'wave' ? 'Wave CI' : (operator === 'orange' ? 'Orange Money CI' : 'MTN MoMo CI');

        if (checkoutWrap) checkoutWrap.style.display = 'none';
        if (processingView) processingView.style.display = 'flex';

        const steps = [
          `Connexion sécurisée au réseau ${opName}...`,
          `Envoi de l'autorisation de débit vers +225 ${phone}...`,
          `Validation du paiement de 1 000 FCFA...`,
          `Génération du Pass Saison illimité...`
        ];

        let stepIndex = 0;
        if (stepMsg) stepMsg.textContent = steps[0];

        const interval = setInterval(() => {
          try {
            stepIndex++;
            if (stepIndex < steps.length) {
              if (stepMsg) stepMsg.textContent = steps[stepIndex];
            } else {
              clearInterval(interval);
              this.isProcessing = false;

              // Unlock season pass in state store
              if (window.AminaState) {
                window.AminaState.unlockSeasonPass();
              }

              if (processingView) processingView.style.display = 'none';
              if (successView) successView.style.display = 'flex';

              this.triggerConfetti();
              this.showToast('Pass Saison activé en illimité !', 'gold');
            }
          } catch (stepErr) {
            clearInterval(interval);
            this.isProcessing = false;
            console.error('[AminaMonetization] MoMo simulation step error:', stepErr);
          }
        }, 700);
      } catch (err) {
        this.isProcessing = false;
        console.error('[AminaMonetization] MoMo simulation start error:', err);
      }
    }

    /**
     * Direct WhatsApp Book Order Modal
     */
    openOrderModal() {
      const waUrl = `https://wa.me/${this.officialWhatsAppNumber}?text=${encodeURIComponent("Bonjour Karl DIGRÉ, je souhaite commander le livre physique 'AMINA : L'Autel De Yopougon' dédicacé à Abidjan (ou e-book).")}`;

      this.backdropEl.innerHTML = `
        <div class="modal-card">
          <button class="modal-close-btn" id="btn-modal-close-order" aria-label="Fermer">
            <svg viewBox="0 0 24 24">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>

          <div class="modal-header">
            <span class="badge badge-gold">ÉDITION OFFICIELLE ABIDJAN</span>
            <h3 class="modal-title">Commander le Roman Papier</h3>
            <p class="modal-sub">Dédicacé par l'auteur Karl DIGRÉ</p>
          </div>

          <div style="text-align: center; margin-bottom: 20px;">
            <img src="assets/cover.jpg" alt="Couverture AMINA" style="width: 140px; height: 210px; object-fit: cover; border-radius: var(--radius-md); border: 2px solid var(--gold-primary); box-shadow: var(--shadow-lg); margin-bottom: 14px;">
            <div style="font-size: 14px; font-weight: 700; color: var(--gold-bright);">Prix : 5 000 FCFA</div>
            <div style="font-size: 12px; opacity: 0.8; margin-top: 4px;">Livraison express à Abidjan & expédition sous-régionale</div>
          </div>

          <div style="display: flex; flex-direction: column; gap: 10px;">
            <a href="${waUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-whatsapp" style="width: 100%;">
              <span>💬 Commander sur WhatsApp (+225 07 00 88 95 14)</span>
            </a>
            <button class="btn btn-ghost" id="btn-close-order-modal">
              <span>Fermer</span>
            </button>
          </div>
        </div>
      `;

      document.getElementById('btn-modal-close-order')?.addEventListener('click', () => this.closeModal());
      document.getElementById('btn-close-order-modal')?.addEventListener('click', () => this.closeModal());
      this.backdropEl.classList.add('open');
    }

    closeModal() {
      this.isProcessing = false;
      if (this.backdropEl) {
        this.backdropEl.classList.remove('open');
      }
    }

    /**
     * Shows a non-intrusive toast alert
     */
    showToast(message, type = 'gold') {
      let container = document.getElementById('toast-container');
      if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
      }

      const toast = document.createElement('div');
      toast.className = `toast toast-${type}`;
      toast.innerHTML = `
        <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
        <span>${message}</span>
      `;
      container.appendChild(toast);

      requestAnimationFrame(() => toast.classList.add('show'));
      setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
      }, 3500);
    }

    /**
     * Festive Golden Particle Confetti Canvas
     */
    triggerConfetti() {
      let canvas = document.getElementById('confetti-canvas');
      if (!canvas) {
        canvas = document.createElement('canvas');
        canvas.id = 'confetti-canvas';
        document.body.appendChild(canvas);
      }

      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const particles = [];
      const colors = ['#D4AF37', '#F5D061', '#FF7A00', '#FFFFFF', '#4EBEFF'];

      for (let i = 0; i < 75; i++) {
        particles.push({
          x: canvas.width / 2,
          y: canvas.height * 0.45,
          vx: (Math.random() - 0.5) * 14,
          vy: (Math.random() - 0.7) * 16,
          size: Math.random() * 7 + 4,
          color: colors[Math.floor(Math.random() * colors.length)],
          rotation: Math.random() * 360,
          rotationSpeed: (Math.random() - 0.5) * 10,
          opacity: 1
        });
      }

      let frame = 0;
      function render() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        let alive = false;

        particles.forEach(p => {
          p.x += p.vx;
          p.y += p.vy;
          p.vy += 0.35; // gravity
          p.rotation += p.rotationSpeed;
          p.opacity -= 0.012;

          if (p.opacity > 0) {
            alive = true;
            ctx.save();
            ctx.translate(p.x, p.y);
            ctx.rotate((p.rotation * Math.PI) / 180);
            ctx.fillStyle = p.color;
            ctx.globalAlpha = Math.max(0, p.opacity);
            ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size);
            ctx.restore();
          }
        });

        frame++;
        if (alive && frame < 180) {
          requestAnimationFrame(render);
        } else {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
      }

      requestAnimationFrame(render);
    }
  }

  const monetizationInstance = new MonetizationEngine();

  if (typeof window !== 'undefined') {
    window.AminaMonetization = monetizationInstance;
  }
  if (typeof globalThis !== 'undefined') {
    globalThis.AminaMonetization = monetizationInstance;
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AminaMonetization: monetizationInstance, MonetizationEngine };
  }
})(typeof window !== 'undefined' ? window : globalThis);
