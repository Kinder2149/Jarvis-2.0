/**
 * App.js - JARVIS 2.0
 * Point d'entrée de l'application SPA
 */

import router from './js/core/router.js';
import state from './js/core/state.js';
import Navbar from './js/components/navbar.js';
import HomeView from './js/views/home.js';
import ChatSimpleView from './js/views/chat-simple.js';
import ProjectsListView from './js/views/projects-list.js';
import ProjectDetailView from './js/views/project-detail.js';
import AgentsViewEnhanced from './js/views/agents-enhanced.js';
import LibraryViewEnhanced from './js/views/library-enhanced.js';

class App {
    constructor() {
        this.navbar = null;
        this.currentView = null;
        this.mainContainer = null;
    }

    /**
     * Initialise l'application
     */
    async init() {
        console.log('🚀 JARVIS 2.0 - Initialisation...');

        // Créer la structure de base
        this.createAppStructure();

        // Créer la navbar
        this.navbar = new Navbar();
        const navbarElement = this.navbar.render();
        document.getElementById('app').prepend(navbarElement);

        // Enregistrer les routes
        this.registerRoutes();

        // Démarrer le router
        router.handleRoute();

        console.log('✅ JARVIS 2.0 - Prêt !');
    }

    /**
     * Crée la structure HTML de base
     */
    createAppStructure() {
        const app = document.getElementById('app');
        
        this.mainContainer = document.createElement('div');
        this.mainContainer.className = 'main-container';
        this.mainContainer.id = 'main-container';
        
        app.appendChild(this.mainContainer);
    }

    /**
     * Enregistre toutes les routes
     */
    registerRoutes() {
        // Home
        router.register('/', () => {
            this.loadView(HomeView);
        });

        // Chat Simple
        router.register('/chat', () => {
            this.loadView(ChatSimpleView);
        });

        // Liste Projets
        router.register('/projects', () => {
            this.loadView(ProjectsListView);
        });

        // Détail Projet
        router.register('/projects/:id', (params) => {
            this.loadView(ProjectDetailView, params);
        });

        // Agents
        router.register('/agents', () => {
            this.loadView(AgentsViewEnhanced);
        });

        // Librairie
        router.register('/library', () => {
            this.loadView(LibraryViewEnhanced);
        });
    }

    /**
     * Charge une vue
     * @param {Class} ViewClass - Classe de la vue
     * @param {Object} params - Paramètres de la route
     */
    async loadView(ViewClass, params = {}) {
        // Détruire la vue actuelle
        if (this.currentView && this.currentView.destroy) {
            this.currentView.destroy();
        }

        // Créer et afficher la nouvelle vue
        this.currentView = new ViewClass();
        await this.currentView.render(this.mainContainer, params);

        // Mettre à jour la navbar
        if (this.navbar) {
            this.navbar.updateActiveLink();
        }
    }
}

// Démarrer l'application au chargement du DOM
document.addEventListener('DOMContentLoaded', () => {
    const app = new App();
    app.init();
});

export default App;
