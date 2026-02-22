/**
 * Chat Simple View - JARVIS 2.0
 * Vue pour le chat standalone (sans projet)
 */

import state from '../core/state.js';
import { createElement, clearContainer } from '../utils/dom.js';
import AgentSelector from '../components/agent-selector.js';
import Chat from '../components/chat.js';

class ChatSimpleView {
    constructor() {
        this.container = null;
        this.agentSelector = null;
        this.chat = null;
        this.currentConversationId = null;
    }

    /**
     * Rend la vue
     * @param {HTMLElement} container
     */
    async render(container) {
        this.container = container;
        clearContainer(container);

        const view = createElement('div', { className: 'main-container fade-in' }, [
            await this.renderHeader(),
            this.renderChatArea()
        ]);

        container.appendChild(view);
    }

    /**
     * Rend le header avec sélecteur d'agent
     * @returns {HTMLElement}
     */
    async renderHeader() {
        this.agentSelector = new AgentSelector(async (agentId) => {
            await this.createConversation(agentId);
        });

        const header = createElement('div', { className: 'chat-header' }, [
            createElement('div', { className: 'chat-header-left' }, [
                await this.agentSelector.render()
            ]),
            createElement('div', { className: 'chat-header-right' }, [
                this.createNewConversationButton()
            ])
        ]);

        return header;
    }

    /**
     * Crée le bouton nouvelle conversation
     * @returns {HTMLElement}
     */
    createNewConversationButton() {
        const button = createElement('button', {
            className: 'btn-new-conversation',
            title: 'Nouvelle conversation',
            style: `
                padding: 0.75rem 1rem;
                background-color: var(--color-surface-hover);
                color: var(--color-text);
                border: 1px solid var(--color-border);
                border-radius: var(--radius-md);
                cursor: pointer;
                transition: all var(--transition-fast);
            `
        }, '⟳ Nouvelle');

        button.addEventListener('click', async () => {
            const agentId = state.get('currentAgent');
            await this.createConversation(agentId);
        });

        return button;
    }

    /**
     * Rend la zone de chat
     * @returns {HTMLElement}
     */
    renderChatArea() {
        const chatArea = createElement('div', { 
            className: 'content-area',
            style: 'flex: 1; overflow: hidden;'
        });

        // Message initial si pas de conversation
        if (!this.currentConversationId) {
            chatArea.appendChild(this.renderEmptyState());
        }

        return chatArea;
    }

    /**
     * Rend l'état vide
     * @returns {HTMLElement}
     */
    renderEmptyState() {
        return createElement('div', { className: 'empty-state' }, [
            createElement('div', { className: 'empty-state-icon' }, '💬'),
            createElement('h3', { className: 'empty-state-title' }, 'Aucune conversation active'),
            createElement('p', { className: 'empty-state-description' }, 
                'Sélectionnez un agent et cliquez sur "Activer" pour commencer.'
            )
        ]);
    }

    /**
     * Crée une nouvelle conversation
     * @param {string} agentId
     */
    async createConversation(agentId) {
        try {
            const response = await fetch('http://localhost:8000/api/conversations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    agent_id: agentId,
                    title: `Chat ${agentId}`
                })
            });

            const conversation = await response.json();

            if (response.ok) {
                this.currentConversationId = conversation.id;
                state.set('currentConversation', conversation);
                this.renderChat();
            } else {
                alert('Erreur lors de la création de la conversation.');
            }
        } catch (error) {
            console.error('Erreur création conversation:', error);
            alert('Erreur de connexion au serveur.');
        }
    }

    /**
     * Affiche le chat
     */
    renderChat() {
        const chatArea = this.container.querySelector('.content-area');
        clearContainer(chatArea);

        this.chat = new Chat({
            conversationId: this.currentConversationId,
            mode: 'simple'
        });

        chatArea.appendChild(this.chat.render());
    }

    /**
     * Nettoie la vue
     */
    destroy() {
        if (this.chat) {
            this.chat.destroy();
        }
        if (this.container) {
            clearContainer(this.container);
        }
    }
}

export default ChatSimpleView;
