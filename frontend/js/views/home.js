/**
 * Home View - JARVIS 2.0
 * Page d'accueil avec navigation vers Chat et Projets
 */

import router from '../core/router.js';
import { createElement, clearContainer } from '../utils/dom.js';

class HomeView {
    constructor() {
        this.container = null;
    }

    /**
     * Rend la vue Home
     * @param {HTMLElement} container - Conteneur
     */
    render(container) {
        this.container = container;
        clearContainer(container);

        const view = createElement('div', { className: 'view-container fade-in' }, [
            this.renderHeader(),
            this.renderCards()
        ]);

        container.appendChild(view);
    }

    /**
     * Rend le header
     * @returns {HTMLElement}
     */
    renderHeader() {
        return createElement('div', { className: 'container text-center' }, [
            createElement('h1', { className: 'mb-md' }, '🏠 Bienvenue dans JARVIS 2.0'),
            createElement('p', { className: 'text-secondary mb-lg' }, 
                'Votre assistant IA personnel pour gérer vos projets et conversations.'
            )
        ]);
    }

    /**
     * Rend les cards de navigation
     * @returns {HTMLElement}
     */
    renderCards() {
        const grid = createElement('div', { className: 'container container-md' }, [
            createElement('div', { className: 'grid grid-3' }, [
                this.createNavigationCard(
                    '💬',
                    'Chat Simple',
                    'Discutez librement avec un agent IA sans contexte projet.',
                    '/chat',
                    'primary'
                ),
                this.createNavigationCard(
                    '📁',
                    'Projets',
                    'Gérez vos projets et discutez avec contexte fichiers.',
                    '/projects',
                    'secondary'
                ),
                this.createNavigationCard(
                    '🤖',
                    'Agents',
                    'Visualisez les agents, leurs paramètres et prompts en temps réel.',
                    '/agents',
                    'primary'
                ),
                this.createNavigationCard(
                    '📚',
                    'Librairie',
                    'Base de connaissances : librairies, méthodologies, prompts et données personnelles.',
                    '/library',
                    'secondary'
                )
            ])
        ]);

        return grid;
    }

    /**
     * Crée une card de navigation
     * @param {string} icon - Icône
     * @param {string} title - Titre
     * @param {string} description - Description
     * @param {string} path - Chemin
     * @param {string} color - Couleur (primary, secondary)
     * @returns {HTMLElement}
     */
    createNavigationCard(icon, title, description, path, color) {
        const card = createElement('div', {
            className: 'card',
            style: 'cursor: pointer; height: 100%;'
        }, [
            createElement('div', { 
                className: 'card-body',
                style: 'text-align: center;'
            }, [
                createElement('div', {
                    style: 'font-size: 4rem; margin-bottom: 1rem;'
                }, icon),
                createElement('h3', { className: 'card-title mb-sm' }, title),
                createElement('p', { className: 'text-secondary' }, description)
            ])
        ]);

        card.addEventListener('click', () => router.navigate(path));
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-4px)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });

        return card;
    }

    /**
     * Nettoie la vue
     */
    destroy() {
        if (this.container) {
            clearContainer(this.container);
        }
    }
}

export default HomeView;
