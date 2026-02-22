/**
 * Router SPA Simple - JARVIS 2.0
 * Gestion navigation hash-based (#/route)
 */

class Router {
    constructor() {
        this.routes = {};
        this.currentView = null;
        this.params = {};
        
        window.addEventListener('hashchange', () => this.handleRoute());
        window.addEventListener('load', () => this.handleRoute());
    }

    /**
     * Enregistre une route
     * @param {string} path - Chemin (ex: '/', '/chat', '/projects/:id')
     * @param {Function} handler - Fonction à exécuter
     */
    register(path, handler) {
        this.routes[path] = handler;
    }

    /**
     * Navigue vers une route
     * @param {string} path - Chemin de destination
     */
    navigate(path) {
        window.location.hash = path;
    }

    /**
     * Retour arrière
     */
    back() {
        window.history.back();
    }

    /**
     * Gère le changement de route
     */
    handleRoute() {
        const hash = window.location.hash.slice(1) || '/';
        const { route, params } = this.matchRoute(hash);

        if (route && this.routes[route]) {
            this.params = params;
            this.currentView = route;
            this.routes[route](params);
        } else {
            // Route par défaut
            this.navigate('/');
        }
    }

    /**
     * Trouve la route correspondante et extrait les paramètres
     * @param {string} path - Chemin actuel
     * @returns {Object} { route, params }
     */
    matchRoute(path) {
        // Correspondance exacte
        if (this.routes[path]) {
            return { route: path, params: {} };
        }

        // Correspondance avec paramètres
        for (const route in this.routes) {
            const routeParts = route.split('/');
            const pathParts = path.split('/');

            if (routeParts.length !== pathParts.length) continue;

            const params = {};
            let match = true;

            for (let i = 0; i < routeParts.length; i++) {
                if (routeParts[i].startsWith(':')) {
                    // Paramètre dynamique
                    const paramName = routeParts[i].slice(1);
                    params[paramName] = pathParts[i];
                } else if (routeParts[i] !== pathParts[i]) {
                    match = false;
                    break;
                }
            }

            if (match) {
                return { route, params };
            }
        }

        return { route: null, params: {} };
    }

    /**
     * Récupère les paramètres de la route actuelle
     * @returns {Object}
     */
    getParams() {
        return this.params;
    }

    /**
     * Récupère la vue actuelle
     * @returns {string}
     */
    getCurrentView() {
        return this.currentView;
    }
}

// Instance globale
const router = new Router();

export default router;
