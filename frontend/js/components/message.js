/**
 * Message Component - JARVIS 2.0
 * Composant message individuel pour le chat
 */

import { createElement } from '../utils/dom.js';
import { formatTime } from '../utils/format.js';

class Message {
    constructor(options = {}) {
        this.role = options.role; // 'user', 'assistant', 'system'
        this.content = options.content;
        this.timestamp = options.timestamp || new Date().toISOString();
        this.author = options.author;
    }

    /**
     * Rend le composant message
     * @returns {HTMLElement}
     */
    render() {
        const messageEl = createElement('div', {
            className: `message ${this.role} slide-in-up`
        }, [
            this.renderAvatar(),
            this.renderContent()
        ]);

        return messageEl;
    }

    /**
     * Rend l'avatar
     * @returns {HTMLElement}
     */
    renderAvatar() {
        const icons = {
            user: '👤',
            assistant: '🤖',
            system: 'ℹ️',
            error: '⚠️'
        };

        return createElement('div', {
            className: 'message-avatar'
        }, icons[this.role] || '?');
    }

    /**
     * Rend le contenu du message
     * @returns {HTMLElement}
     */
    renderContent() {
        return createElement('div', {
            className: 'message-content'
        }, [
            this.renderHeader(),
            this.renderBubble()
        ]);
    }

    /**
     * Rend le header (auteur + timestamp)
     * @returns {HTMLElement}
     */
    renderHeader() {
        const authorName = this.getAuthorName();

        return createElement('div', {
            className: 'message-header'
        }, [
            createElement('span', {
                className: 'message-author'
            }, authorName),
            createElement('span', {
                className: 'message-time'
            }, formatTime(this.timestamp))
        ]);
    }

    /**
     * Rend la bulle de message
     * @returns {HTMLElement}
     */
    renderBubble() {
        return createElement('div', {
            className: 'message-bubble'
        }, this.formatContent());
    }

    /**
     * Récupère le nom de l'auteur
     * @returns {string}
     */
    getAuthorName() {
        if (this.author) return this.author;

        const names = {
            user: 'Vous',
            assistant: 'IA',
            system: 'Système',
            error: 'Erreur'
        };

        return names[this.role] || 'Inconnu';
    }

    /**
     * Formate le contenu (supporte markdown basique)
     * @returns {string}
     */
    formatContent() {
        let content = this.content;

        // Échapper HTML
        const div = document.createElement('div');
        div.textContent = content;
        content = div.innerHTML;

        // Markdown basique
        // Gras : **texte**
        content = content.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        // Italique : *texte*
        content = content.replace(/\*(.+?)\*/g, '<em>$1</em>');
        
        // Code inline : `code`
        content = content.replace(/`(.+?)`/g, '<code style="background: var(--color-surface); padding: 0.125rem 0.25rem; border-radius: 0.25rem; font-family: monospace;">$1</code>');
        
        // Liens : [texte](url)
        content = content.replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" style="color: var(--color-primary);">$1</a>');

        return content;
    }

    /**
     * Crée un message d'erreur
     * @param {string} errorMessage
     * @returns {Message}
     */
    static error(errorMessage) {
        return new Message({
            role: 'error',
            content: errorMessage,
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Crée un message système
     * @param {string} systemMessage
     * @returns {Message}
     */
    static system(systemMessage) {
        return new Message({
            role: 'system',
            content: systemMessage,
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Crée un message utilisateur
     * @param {string} content
     * @returns {Message}
     */
    static user(content) {
        return new Message({
            role: 'user',
            content: content,
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Crée un message assistant
     * @param {string} content
     * @returns {Message}
     */
    static assistant(content) {
        return new Message({
            role: 'assistant',
            content: content,
            timestamp: new Date().toISOString()
        });
    }
}

export default Message;
