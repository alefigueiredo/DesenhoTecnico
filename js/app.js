/* ============================================================
   APP.JS — Lógica do Material Didático Digital SENAI SP
   Leitura e Interpretação de Desenho Técnico Mecânico
   ============================================================ */

(function () {
    'use strict';

    // ==================== ESTADO DA APLICAÇÃO ====================
    const state = {
        courseId: 'desenho_tecnico_mecanico',
        completedPages: new Set(),
        points: 0,
        badges: new Set(),
        gamificationEnabled: true,
        totalPages: 22 // Total de páginas de SAs, exercícios e avaliações
    };

    // ==================== INICIALIZAÇÃO ====================
    document.addEventListener('DOMContentLoaded', function () {
        loadState();
        initNavigation();
        initExercises();
        initGamificationUI();
        markCurrentPageAsVisited();
        updateProgress();
    });

    // ==================== NAVEGAÇÃO ====================

    function initNavigation() {
        // Toggle do menu mobile
        const menuToggle = document.getElementById('menuToggle');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');

        if (menuToggle && sidebar) {
            menuToggle.addEventListener('click', function () {
                sidebar.classList.toggle('open');
                if (overlay) overlay.classList.toggle('show');
            });
        }

        if (overlay && sidebar) {
            overlay.addEventListener('click', function () {
                sidebar.classList.remove('open');
                overlay.classList.remove('show');
            });
        }

        // Módulos expansíveis na sidebar
        document.querySelectorAll('.nav-module-btn').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                const moduleItem = btn.closest('.nav-module');
                if (moduleItem) {
                    moduleItem.classList.toggle('open');
                }
            });
        });

        // Links de navegação na sidebar
        document.querySelectorAll('.nav-link').forEach(function (link) {
            link.addEventListener('click', function (e) {
                var href = link.getAttribute('href');
                var sectionId = link.dataset.section;

                // Se houver um ID de seção na própria página, alterna a seção em tela
                if (sectionId && document.getElementById(sectionId)) {
                    e.preventDefault();
                    showSection(sectionId);
                    closeMobileMenu();
                    return;
                }

                // Caso seja um href normal para outro arquivo HTML, permite a navegação normal
                if (href && href !== '#' && href !== 'javascript:void(0)') {
                    closeMobileMenu();
                    // O navegador fará o redirecionamento naturalmente
                }
            });
        });

        // Destacar módulo atual com base na URL
        highlightActiveNavLink();
    }

    function highlightActiveNavLink() {
        var currentPath = window.location.pathname.replace(/\\/g, '/');
        document.querySelectorAll('.nav-link').forEach(function (link) {
            var href = link.getAttribute('href');
            if (href && href !== '#') {
                // Verificar se a URL atual termina com o href do link
                var cleanHref = href.replace('../', '').replace('../../', '');
                if (currentPath.includes(cleanHref)) {
                    link.classList.add('active');
                    var parentModule = link.closest('.nav-module');
                    if (parentModule) {
                        parentModule.classList.add('open');
                    }
                }
            }
        });
    }

    function showSection(sectionId) {
        if (!sectionId) return;

        document.querySelectorAll('.content-section').forEach(function (s) {
            s.classList.remove('active');
        });

        var target = document.getElementById(sectionId);
        if (target) {
            target.classList.add('active');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }

    function closeMobileMenu() {
        var sidebar = document.getElementById('sidebar');
        var overlay = document.getElementById('sidebarOverlay');
        if (sidebar) sidebar.classList.remove('open');
        if (overlay) overlay.classList.remove('show');
    }

    function markCurrentPageAsVisited() {
        var path = window.location.pathname.replace(/\\/g, '/');
        // Extrair identificador único da página a partir do caminho
        var pageKey = path.split('/').slice(-2).join('/');
        if (pageKey && pageKey !== 'desenho-tecnico-mecanico/') {
            state.completedPages.add(pageKey);
            saveState();
        }
    }

    // ==================== EXERCÍCIOS INTERATIVOS ====================

    function initExercises() {
        // Seleção de opções estilo rádio/card
        document.querySelectorAll('.exercise .option').forEach(function (option) {
            option.addEventListener('click', function () {
                var exercise = option.closest('.exercise');
                if (exercise.classList.contains('answered')) return;

                exercise.querySelectorAll('.option').forEach(function (o) {
                    o.classList.remove('selected');
                });

                option.classList.add('selected');

                var radio = option.querySelector('input[type="radio"]');
                if (radio) radio.checked = true;
            });
        });

        // Botão de verificação de resposta
        document.querySelectorAll('.btn-check').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var exerciseId = btn.dataset.exercise;
                var correctAnswer = btn.dataset.answer;
                checkAnswer(exerciseId, correctAnswer);
            });
        });
    }

    function checkAnswer(exerciseId, correctAnswer) {
        var exercise = document.getElementById(exerciseId);
        if (!exercise || exercise.classList.contains('answered')) return;

        var selectedOption = exercise.querySelector('.option.selected');
        if (!selectedOption) {
            alert('Selecione uma alternativa antes de verificar.');
            return;
        }

        var selectedRadio = selectedOption.querySelector('input[type="radio"]');
        var selectedValue = selectedRadio ? selectedRadio.value : null;
        var isCorrect = selectedValue === correctAnswer;
        var feedback = document.getElementById('feedback-' + exerciseId);

        exercise.classList.add('answered');

        exercise.querySelectorAll('.option').forEach(function (opt) {
            opt.style.cursor = 'default';
            var radio = opt.querySelector('input[type="radio"]');
            var optValue = radio ? radio.value : null;

            if (optValue === correctAnswer) {
                opt.classList.add('correct');
            } else if (opt.classList.contains('selected') && !isCorrect) {
                opt.classList.add('incorrect');
            }
        });

        if (feedback) {
            feedback.classList.add('show');
            if (isCorrect) {
                feedback.classList.add('correct');
                feedback.innerHTML = '✅ <strong>Resposta correta!</strong> +100 Pontos';
                if (state.gamificationEnabled) {
                    addPoints(100);
                }
            } else {
                feedback.classList.add('incorrect');
                feedback.innerHTML = '❌ <strong>Resposta incorreta.</strong> A alternativa correta está destacada em verde.';
            }
        }

        var btn = exercise.querySelector('.btn-check');
        if (btn) btn.disabled = true;

        checkModuleCompletion();
        saveState();
        updateProgress();
    }

    // ==================== GAMIFICAÇÃO ====================

    function initGamificationUI() {
        // Inserir elementos de gamificação no topo se não existirem
        var sidebarHeader = document.querySelector('.sidebar-header');
        if (sidebarHeader && !document.getElementById('gamificationScoreBox')) {
            var scoreBox = document.createElement('div');
            scoreBox.id = 'gamificationScoreBox';
            scoreBox.className = 'gamification-score-box';
            scoreBox.innerHTML = `
                <div class="score-pill">🏆 <span id="userPointsDisplay">${state.points}</span> Pts</div>
                <div class="gamification-controls">
                    <button id="btnToggleGamification" class="btn-icon" title="Ativar/Desativar Gamificação">🎮</button>
                    <button id="btnResetProgress" class="btn-icon" title="Resetar Progresso">🔄</button>
                </div>
            `;
            sidebarHeader.after(scoreBox);

            document.getElementById('btnToggleGamification')?.addEventListener('click', toggleGamification);
            document.getElementById('btnResetProgress')?.addEventListener('click', resetProgress);
        }
    }

    function addPoints(amount) {
        state.points += amount;
        var display = document.getElementById('userPointsDisplay');
        if (display) {
            display.textContent = state.points;
            display.classList.add('pulse');
            setTimeout(() => display.classList.remove('pulse'), 500);
        }
        saveState();
    }

    function unlockBadge(badgeId, badgeTitle) {
        if (!state.badges.has(badgeId)) {
            state.badges.add(badgeId);
            saveState();

            if (state.gamificationEnabled) {
                showBadgeNotification(badgeTitle);
            }
        }
    }

    function showBadgeNotification(title) {
        var toast = document.createElement('div');
        toast.className = 'badge-toast';
        toast.innerHTML = `
            <div class="badge-icon">🎖️</div>
            <div class="badge-info">
                <strong>Nova Conquista Desbloqueada!</strong>
                <p>${title}</p>
            </div>
        `;
        document.body.appendChild(toast);

        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    function toggleGamification() {
        state.gamificationEnabled = !state.gamificationEnabled;
        alert(state.gamificationEnabled ? '🎮 Gamificação ativada!' : '⏸️ Gamificação desativada.');
        saveState();
    }

    function resetProgress() {
        if (confirm('Tem certeza de que deseja resetar todo o seu progresso e pontuação?')) {
            state.completedPages.clear();
            state.points = 0;
            state.badges.clear();
            saveState();
            location.reload();
        }
    }

    function checkModuleCompletion() {
        var allAnswered = true;
        document.querySelectorAll('.exercise').forEach(function (ex) {
            if (!ex.classList.contains('answered')) {
                allAnswered = false;
            }
        });

        if (allAnswered && document.querySelectorAll('.exercise').length > 0) {
            unlockBadge('modulo_completo', 'Conquistador de Exercícios!');
        }
    }

    // ==================== PROGRESSO E PERSISTÊNCIA ====================

    function updateProgress() {
        var count = state.completedPages.size;
        var percent = Math.min(100, Math.round((count / state.totalPages) * 100));

        var progressFill = document.getElementById('navProgressFill');
        var progressText = document.getElementById('navProgressText');

        if (progressFill) progressFill.style.width = percent + '%';
        if (progressText) progressText.textContent = percent + '%';
    }

    function saveState() {
        try {
            var data = {
                completedPages: Array.from(state.completedPages),
                points: state.points,
                badges: Array.from(state.badges),
                gamificationEnabled: state.gamificationEnabled,
                savedAt: new Date().toISOString()
            };
            localStorage.setItem('senai_' + state.courseId, JSON.stringify(data));
        } catch (e) {
            // localStorage indisponível
        }
    }

    function loadState() {
        try {
            var saved = localStorage.getItem('senai_' + state.courseId);
            if (saved) {
                var data = JSON.parse(saved);
                if (data.completedPages) state.completedPages = new Set(data.completedPages);
                if (data.points) state.points = data.points;
                if (data.badges) state.badges = new Set(data.badges);
                if (typeof data.gamificationEnabled === 'boolean') state.gamificationEnabled = data.gamificationEnabled;
            }
        } catch (e) {
            // erro ao carregar localStorage
        }
    }

})();

