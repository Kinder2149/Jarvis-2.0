/**
 * Helpers DOM - JARVIS 2.0
 * Utilitaires manipulation DOM
 */

/**
 * Crée un élément DOM avec attributs et enfants
 * @param {string} tag - Tag HTML
 * @param {Object} attrs - Attributs (class, id, etc.)
 * @param {Array|string} children - Enfants (éléments ou texte)
 * @returns {HTMLElement}
 */
export function createElement(tag, attrs = {}, children = []) {
    const element = document.createElement(tag);

    // Attributs
    Object.keys(attrs).forEach(key => {
        if (key === 'className') {
            element.className = attrs[key];
        } else if (key === 'dataset') {
            Object.keys(attrs[key]).forEach(dataKey => {
                element.dataset[dataKey] = attrs[key][dataKey];
            });
        } else if (key.startsWith('on')) {
            // Event listeners
            const eventName = key.slice(2).toLowerCase();
            element.addEventListener(eventName, attrs[key]);
        } else {
            element.setAttribute(key, attrs[key]);
        }
    });

    // Enfants
    if (typeof children === 'string') {
        element.textContent = children;
    } else if (Array.isArray(children)) {
        children.forEach(child => {
            if (typeof child === 'string') {
                element.appendChild(document.createTextNode(child));
            } else if (child instanceof HTMLElement) {
                element.appendChild(child);
            }
        });
    }

    return element;
}

/**
 * Vide un conteneur
 * @param {HTMLElement} container
 */
export function clearContainer(container) {
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }
}

/**
 * Affiche/masque un élément
 * @param {HTMLElement} element
 * @param {boolean} show
 */
export function toggleElement(element, show) {
    if (show) {
        element.style.display = '';
        element.classList.remove('hidden');
    } else {
        element.style.display = 'none';
        element.classList.add('hidden');
    }
}

/**
 * Ajoute une classe avec animation
 * @param {HTMLElement} element
 * @param {string} className
 */
export function addClassWithAnimation(element, className) {
    element.classList.add(className);
    element.offsetHeight; // Force reflow
}

/**
 * Scroll vers le bas d'un conteneur
 * @param {HTMLElement} container
 * @param {boolean} smooth - Animation smooth
 */
export function scrollToBottom(container, smooth = true) {
    container.scrollTo({
        top: container.scrollHeight,
        behavior: smooth ? 'smooth' : 'auto'
    });
}

/**
 * Escape HTML pour éviter XSS
 * @param {string} text
 * @returns {string}
 */
export function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Sélecteur querySelector simplifié
 * @param {string} selector
 * @param {HTMLElement} parent
 * @returns {HTMLElement}
 */
export function $(selector, parent = document) {
    return parent.querySelector(selector);
}

/**
 * Sélecteur querySelectorAll simplifié
 * @param {string} selector
 * @param {HTMLElement} parent
 * @returns {NodeList}
 */
export function $$(selector, parent = document) {
    return parent.querySelectorAll(selector);
}
