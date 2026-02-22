/**
 * Agents View Enhanced - JARVIS 2.0
 * Page de visualisation détaillée avec schémas de flow et état réel
 */

import { createElement, clearContainer } from '../utils/dom.js';

const API_BASE = 'http://localhost:8000';

class AgentsViewEnhanced {
    constructor() {
        this.container = null;
        this.agents = [];
        this.refreshInterval = null;
    }

    async render(container) {
        this.container = container;
        clearContainer(container);

        const view = createElement('div', { className: 'agents-view fade-in' });
        container.appendChild(view);

        this.renderLoading(view);
        await this.loadAgents(view);

        this.refreshInterval = setInterval(() => this.refreshAgents(), 30000);
    }

    renderLoading(container) {
        clearContainer(container);
        const loading = createElement('div', { className: 'agents-loading' }, [
            createElement('div', { className: 'spinner' }),
            createElement('span', {}, 'Chargement des agents...')
        ]);
        container.appendChild(loading);
    }

    async loadAgents(container) {
        try {
            const response = await fetch(`${API_BASE}/api/agents/detailed`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            this.agents = data.agents || [];
            this.renderContent(container);
        } catch (error) {
            console.error('Erreur chargement agents:', error);
            this.renderError(container, error.message);
        }
    }

    async refreshAgents() {
        if (!this.container) return;
        const view = this.container.querySelector('.agents-view');
        if (!view) return;

        try {
            const response = await fetch(`${API_BASE}/api/agents/detailed`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            this.agents = data.agents || [];
            this.renderContent(view);
        } catch (error) {
            console.error('Erreur rafraîchissement agents:', error);
        }
    }

    renderContent(container) {
        clearContainer(container);

        // Header
        const header = createElement('div', { className: 'agents-header' }, [
            createElement('h1', {}, '🤖 Agents JARVIS 2.0'),
            createElement('p', {}, `${this.agents.length} agent(s) configuré(s) — Configuration Gemini Tier 1 validée`)
        ]);
        container.appendChild(header);

        // Grille des agents
        const grid = createElement('div', { className: 'agents-grid' });
        this.agents.forEach(agent => {
            grid.appendChild(this.renderAgentCard(agent));
        });
        container.appendChild(grid);

        // Schémas de flow
        container.appendChild(this.renderFlowDiagrams());

        // État du système
        container.appendChild(this.renderSystemStatus());
    }

    renderAgentCard(agent) {
        const card = createElement('div', { className: 'agent-card slide-in-up' });

        // Header
        card.appendChild(this.renderCardHeader(agent));

        // Body
        const body = createElement('div', { className: 'agent-card-body' });

        // Description
        const desc = createElement('p', { className: 'agent-description' }, agent.description);
        body.appendChild(desc);

        // Section : Configuration IA
        body.appendChild(this.renderSection('🤖 Configuration IA', this.renderAIConfig(agent), true));

        // Section : Paramètres
        body.appendChild(this.renderSection('⚙️ Paramètres', this.renderParams(agent)));

        // Section : Permissions
        body.appendChild(this.renderSection('🔐 Permissions', this.renderPermissions(agent)));

        card.appendChild(body);
        return card;
    }

    renderCardHeader(agent) {
        const isOrchestrator = agent.type === 'orchestrator';
        const iconClass = isOrchestrator ? 'orchestrator' : 'worker';
        const icon = isOrchestrator ? '👑' : (agent.type === 'validator' ? '✅' : '⚡');

        return createElement('div', { className: 'agent-card-header' }, [
            createElement('div', { className: `agent-icon ${iconClass}` }, icon),
            createElement('div', { className: 'agent-header-info' }, [
                createElement('h2', {}, agent.name),
                createElement('p', { className: 'agent-role' }, agent.role)
            ]),
            createElement('span', { className: `agent-type-badge ${iconClass}` }, agent.type)
        ]);
    }

    renderAIConfig(agent) {
        const grid = createElement('div', { className: 'agent-params' });

        const configs = [
            { label: '🔌 Provider', value: agent.provider.toUpperCase(), highlight: true },
            { label: '🧠 Modèle', value: agent.model, highlight: true },
            { label: '📝 Variable .env', value: agent.env_var, mono: true },
            { label: '🌡️ Temperature', value: String(agent.temperature) },
        ];

        configs.forEach(c => {
            const valueClass = c.highlight ? 'agent-param-value highlight' : (c.mono ? 'agent-param-value mono' : 'agent-param-value');
            grid.appendChild(createElement('div', { className: 'agent-param' }, [
                createElement('span', { className: 'agent-param-label' }, c.label),
                createElement('span', { className: valueClass }, c.value)
            ]));
        });

        return grid;
    }

    renderParams(agent) {
        const grid = createElement('div', { className: 'agent-params' });

        const params = [
            { label: 'Max Tokens', value: String(agent.max_tokens) },
            { label: 'Type', value: agent.type },
            { label: 'ID', value: agent.id }
        ];

        params.forEach(p => {
            grid.appendChild(createElement('div', { className: 'agent-param' }, [
                createElement('span', { className: 'agent-param-label' }, p.label),
                createElement('span', { className: 'agent-param-value' }, p.value)
            ]));
        });

        return grid;
    }

    renderPermissions(agent) {
        const container = createElement('div', { className: 'agent-permissions' });

        (agent.permissions || []).forEach(perm => {
            container.appendChild(
                createElement('span', { className: `permission-tag ${perm}` }, perm)
            );
        });

        return container;
    }

    renderFlowDiagrams() {
        const section = createElement('div', { className: 'flow-section' });

        // Header
        section.appendChild(createElement('h2', { className: 'flow-title' }, '📊 Schémas de Flow'));

        // Mode Chat Simple
        section.appendChild(this.renderFlowChat());

        // Mode Projet
        section.appendChild(this.renderFlowProject());

        return section;
    }

    renderFlowChat() {
        const container = createElement('div', { className: 'flow-diagram' });

        container.appendChild(createElement('h3', {}, '💬 Mode Chat Simple'));
        container.appendChild(createElement('p', { className: 'flow-description' }, 
            'Conversation directe avec un agent sans délégation ni écriture disque'
        ));

        const steps = [
            { emoji: '👤', label: 'Utilisateur', desc: 'Envoie message' },
            { emoji: '🎯', label: 'API Backend', desc: 'POST /api/chat' },
            { emoji: '🤖', label: 'Agent Sélectionné', desc: 'Traite le message' },
            { emoji: '🔌', label: 'Gemini Provider', desc: 'Appel API Google' },
            { emoji: '💬', label: 'Réponse', desc: 'Retour utilisateur' }
        ];

        const flowSteps = createElement('div', { className: 'flow-steps' });
        steps.forEach((step, index) => {
            flowSteps.appendChild(createElement('div', { className: 'flow-step' }, [
                createElement('div', { className: 'flow-step-emoji' }, step.emoji),
                createElement('div', { className: 'flow-step-label' }, step.label),
                createElement('div', { className: 'flow-step-desc' }, step.desc)
            ]));
            if (index < steps.length - 1) {
                flowSteps.appendChild(createElement('div', { className: 'flow-arrow' }, '→'));
            }
        });

        container.appendChild(flowSteps);

        // État implémentation
        container.appendChild(createElement('div', { className: 'flow-status success' }, 
            '✅ Implémenté et fonctionnel'
        ));

        return container;
    }

    renderFlowProject() {
        const container = createElement('div', { className: 'flow-diagram' });

        container.appendChild(createElement('h3', {}, '🚀 Mode Projet (Orchestration)'));
        container.appendChild(createElement('p', { className: 'flow-description' }, 
            'Workflow structuré avec délégation entre agents et écriture fichiers'
        ));

        // Phase 1 : Réflexion
        const phase1 = createElement('div', { className: 'flow-phase' });
        phase1.appendChild(createElement('h4', {}, '📋 Phase 1 : RÉFLEXION'));
        const steps1 = [
            { emoji: '👤', label: 'Demande Projet', desc: 'Utilisateur décrit besoin' },
            { emoji: '👑', label: 'JARVIS_Maître', desc: 'Analyse + Plan détaillé' },
            { emoji: '🔍', label: 'Analyse Code', desc: 'Scan projet existant si besoin' },
            { emoji: '⚠️', label: 'Détection Dette', desc: 'Signale problèmes' },
            { emoji: '✋', label: 'Validation User', desc: 'Attente confirmation' }
        ];
        phase1.appendChild(this.renderFlowSteps(steps1));
        phase1.appendChild(createElement('div', { className: 'flow-status success' }, 
            '✅ Implémenté - JARVIS_Maître orchestre'
        ));
        container.appendChild(phase1);

        // Phase 2 : Exécution
        const phase2 = createElement('div', { className: 'flow-phase' });
        phase2.appendChild(createElement('h4', {}, '⚡ Phase 2 : EXÉCUTION'));
        const steps2 = [
            { emoji: '👑', label: 'JARVIS_Maître', desc: 'Délègue au CODEUR' },
            { emoji: '💻', label: 'CODEUR', desc: 'Génère fichiers code' },
            { emoji: '💾', label: 'Écriture Disque', desc: 'Sauvegarde fichiers' },
            { emoji: '✅', label: 'VALIDATEUR', desc: 'Contrôle qualité' },
            { emoji: '📊', label: 'BASE', desc: 'Rapport complétude' },
            { emoji: '👤', label: 'Retour User', desc: 'Résultat final' }
        ];
        phase2.appendChild(this.renderFlowSteps(steps2));
        phase2.appendChild(createElement('div', { className: 'flow-status success' }, 
            '✅ Implémenté - Délégation fonctionnelle'
        ));
        container.appendChild(phase2);

        return container;
    }

    renderFlowSteps(steps) {
        const flowSteps = createElement('div', { className: 'flow-steps' });
        steps.forEach((step, index) => {
            flowSteps.appendChild(createElement('div', { className: 'flow-step' }, [
                createElement('div', { className: 'flow-step-emoji' }, step.emoji),
                createElement('div', { className: 'flow-step-label' }, step.label),
                createElement('div', { className: 'flow-step-desc' }, step.desc)
            ]));
            if (index < steps.length - 1) {
                flowSteps.appendChild(createElement('div', { className: 'flow-arrow' }, '↓'));
            }
        });
        return flowSteps;
    }

    renderSystemStatus() {
        const section = createElement('div', { className: 'system-status-section' });

        section.appendChild(createElement('h2', { className: 'status-title' }, '🔍 État du Système'));

        // Fonctionnalités implémentées
        const implemented = createElement('div', { className: 'status-category' });
        implemented.appendChild(createElement('h3', {}, '✅ Fonctionnalités Implémentées'));
        const implList = createElement('ul', { className: 'status-list' });
        [
            'Configuration Gemini unique (4 modèles Tier 1)',
            'Système multi-agents (JARVIS_Maître, BASE, CODEUR, VALIDATEUR)',
            'Mode Chat simple (conversation directe)',
            'Mode Projet (orchestration + délégation)',
            'Génération de code par CODEUR',
            'Validation qualité par VALIDATEUR',
            'Vérification complétude par BASE',
            'Écriture fichiers sur disque',
            'API REST complète (FastAPI)',
            'Interface frontend (HTML/CSS/JS)',
            'Base de données SQLite (conversations, projets)',
            'Logging détaillé (backend/logs/gemini_api.log)',
            'Tests unitaires (238+ tests)',
            'Tests live validés (Calculatrice, TODO, MiniBlog)'
        ].forEach(item => {
            implList.appendChild(createElement('li', {}, `✅ ${item}`));
        });
        implemented.appendChild(implList);
        section.appendChild(implemented);

        // Fonctionnalités partielles ou en développement
        const partial = createElement('div', { className: 'status-category' });
        partial.appendChild(createElement('h3', {}, '⚠️ Limitations Connues'));
        const partialList = createElement('ul', { className: 'status-list warning' });
        [
            'Quotas Gemini Tier 1 (150 RPM CODEUR, 25 RPM VALIDATEUR)',
            'Pas de gestion multi-utilisateurs (usage personnel)',
            'Pas d\'authentification (localhost uniquement)',
            'Projets complexes nécessitent optimisation tokens',
            'Certains tests unitaires échouent (2-3 tests mineurs)',
            'Mode Projet nécessite validation manuelle utilisateur'
        ].forEach(item => {
            partialList.appendChild(createElement('li', {}, `⚠️ ${item}`));
        });
        partial.appendChild(partialList);
        section.appendChild(partial);

        // Non implémenté
        const notImpl = createElement('div', { className: 'status-category' });
        notImpl.appendChild(createElement('h3', {}, '❌ Non Implémenté'));
        const notImplList = createElement('ul', { className: 'status-list error' });
        [
            'Authentification multi-utilisateurs',
            'Déploiement cloud',
            'Gestion avancée des erreurs API',
            'Retry automatique sur timeout',
            'Cache intelligent des réponses',
            'Historique de versions de code généré',
            'Rollback automatique en cas d\'erreur',
            'Interface mobile responsive',
            'Mode sombre (dark mode)',
            'Export/Import de conversations'
        ].forEach(item => {
            notImplList.appendChild(createElement('li', {}, `❌ ${item}`));
        });
        notImpl.appendChild(notImplList);
        section.appendChild(notImpl);

        return section;
    }

    renderSection(title, content, openByDefault = false) {
        const section = createElement('div', { className: `agent-section${openByDefault ? ' open' : ''}` });

        const header = createElement('div', { className: 'agent-section-header' }, [
            createElement('span', { className: 'agent-section-title' }, title),
            createElement('span', { className: 'agent-section-arrow' }, '▼')
        ]);

        header.addEventListener('click', () => {
            section.classList.toggle('open');
        });

        const contentWrapper = createElement('div', { className: 'agent-section-content' });
        contentWrapper.appendChild(content);

        section.appendChild(header);
        section.appendChild(contentWrapper);
        return section;
    }

    renderError(container, message) {
        clearContainer(container);

        const errorDiv = createElement('div', { className: 'agents-error' }, [
            createElement('div', { style: 'font-size: 3rem; margin-bottom: 1rem;' }, '⚠️'),
            createElement('h2', {}, 'Erreur de chargement'),
            createElement('p', {}, `Impossible de charger les agents : ${message}`)
        ]);

        const retryBtn = createElement('button', { className: 'retry-btn' }, 'Réessayer');
        retryBtn.addEventListener('click', () => this.loadAgents(container));
        errorDiv.appendChild(retryBtn);

        container.appendChild(errorDiv);
    }

    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
        if (this.container) {
            clearContainer(this.container);
        }
    }
}

export default AgentsViewEnhanced;
