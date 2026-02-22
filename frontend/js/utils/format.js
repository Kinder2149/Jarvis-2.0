/**
 * Formatage - JARVIS 2.0
 * Utilitaires formatage dates, texte, etc.
 */

/**
 * Formate une date ISO en format lisible
 * @param {string} isoDate - Date ISO
 * @returns {string}
 */
export function formatDate(isoDate) {
    const date = new Date(isoDate);
    const now = new Date();
    const diff = now - date;

    // Moins d'une minute
    if (diff < 60000) {
        return 'À l\'instant';
    }

    // Moins d'une heure
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `Il y a ${minutes} min`;
    }

    // Aujourd'hui
    if (date.toDateString() === now.toDateString()) {
        return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    }

    // Hier
    const yesterday = new Date(now);
    yesterday.setDate(yesterday.getDate() - 1);
    if (date.toDateString() === yesterday.toDateString()) {
        return `Hier ${date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}`;
    }

    // Cette semaine
    if (diff < 604800000) {
        return date.toLocaleDateString('fr-FR', { weekday: 'short', hour: '2-digit', minute: '2-digit' });
    }

    // Date complète
    return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

/**
 * Formate une date en format court (HH:MM)
 * @param {string} isoDate
 * @returns {string}
 */
export function formatTime(isoDate) {
    const date = new Date(isoDate);
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
}

/**
 * Tronque un texte avec ellipse
 * @param {string} text
 * @param {number} maxLength
 * @returns {string}
 */
export function truncate(text, maxLength = 50) {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
}

/**
 * Formate une taille de fichier
 * @param {number} bytes
 * @returns {string}
 */
export function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Capitalise la première lettre
 * @param {string} text
 * @returns {string}
 */
export function capitalize(text) {
    return text.charAt(0).toUpperCase() + text.slice(1);
}

/**
 * Pluralise un mot selon un nombre
 * @param {number} count
 * @param {string} singular
 * @param {string} plural
 * @returns {string}
 */
export function pluralize(count, singular, plural = null) {
    if (count <= 1) return singular;
    return plural || singular + 's';
}
