/**
 * Project Detail View - JARVIS 2.0
 * Vue détail projet avec 3 colonnes (conversations, chat, fichiers)
 */

import state from '../core/state.js';
import { createElement, clearContainer } from '../utils/dom.js';
import ConversationList from '../components/conversation-list.js';
import Chat from '../components/chat.js';
import FileExplorer from '../components/file-explorer.js';

class ProjectDetailView {
    constructor() {
        this.container = null;
        this.projectId = null;
        this.project = null;
        
        this.conversationList = null;
        this.chat = null;
        this.fileExplorer = null;
        
        this.currentConversationId = null;
    }

    /**
     * Rend la vue
     * @param {HTMLElement} container
     * @param {Object} params - { id: projectId }
     */
    async render(container, params) {
        this.container = container;
        this.projectId = params.id;
        
        clearContainer(container);

        // Charger le projet
        await this.loadProject();

        if (!this.project) {
            container.appendChild(this.renderError());
            return;
        }

        // Créer layout 3 colonnes
        const view = createElement('div', { 
            className: 'layout-three-columns fade-in',
            style: 'height: 100%;'
        }, [
            await this.renderConversationsColumn(),
            this.renderChatColumn(),
            await this.renderFilesColumn()
        ]);

        container.appendChild(view);
    }

    /**
     * Charge le projet
     */
    async loadProject() {
        try {
            const response = await fetch(
                `http://localhost:8000/api/projects/${this.projectId}`
            );
            
            if (response.ok) {
                this.project = await response.json();
                state.set('currentProject', this.project);
            } else {
                this.project = null;
            }
        } catch (error) {
            console.error('Erreur chargement projet:', error);
            this.project = null;
        }
    }

    /**
     * Rend la colonne conversations
     * @returns {HTMLElement}
     */
    async renderConversationsColumn() {
        const column = createElement('div', { 
            className: 'column',
            style: 'background-color: var(--color-surface);'
        });

        // Header projet
        const header = createElement('div', {
            className: 'column-header',
            style: 'background-color: var(--color-bg);'
        }, [
            createElement('h2', { 
                style: 'font-size: 1.125rem; font-weight: 600; margin-bottom: 0.25rem;'
            }, this.project.name),
            createElement('p', {
                style: 'font-size: 0.75rem; color: var(--color-text-muted); word-break: break-all;'
            }, this.project.path)
        ]);

        column.appendChild(header);

        // Liste conversations
        this.conversationList = new ConversationList({
            projectId: this.projectId,
            onConversationSelect: (conversation) => {
                this.handleConversationSelect(conversation);
            },
            onConversationDelete: (conversationId) => {
                if (this.currentConversationId === conversationId) {
                    this.currentConversationId = null;
                    this.renderChatArea();
                }
            },
            onNewConversation: async () => {
                await this.createNewConversation();
            }
        });

        const listElement = await this.conversationList.render();
        column.appendChild(listElement);

        return column;
    }

    /**
     * Rend la colonne chat
     * @returns {HTMLElement}
     */
    renderChatColumn() {
        const column = createElement('div', { 
            className: 'column',
            style: 'display: flex; flex-direction: column;'
        });

        // Header chat
        const header = createElement('div', {
            className: 'column-header'
        }, [
            createElement('h3', { 
                style: 'font-size: 1rem; font-weight: 600;'
            }, '💬 Chat')
        ]);

        column.appendChild(header);

        // Zone chat
        const chatArea = createElement('div', {
            className: 'chat-area',
            style: 'flex: 1; overflow: hidden; display: flex; flex-direction: column;'
        });

        column.appendChild(chatArea);

        // Afficher état initial
        this.renderChatArea(chatArea);

        return column;
    }

    /**
     * Rend la zone de chat
     * @param {HTMLElement} chatArea
     */
    renderChatArea(chatArea = null) {
        if (!chatArea) {
            chatArea = this.container.querySelector('.chat-area');
        }

        clearContainer(chatArea);

        if (!this.currentConversationId) {
            chatArea.appendChild(this.renderEmptyChat());
        } else {
            this.chat = new Chat({
                conversationId: this.currentConversationId,
                mode: 'project',
                projectId: this.projectId
            });
            chatArea.appendChild(this.chat.render());
        }
    }

    /**
     * Rend l'état vide du chat
     * @returns {HTMLElement}
     */
    renderEmptyChat() {
        return createElement('div', { className: 'empty-state' }, [
            createElement('div', { className: 'empty-state-icon' }, '💬'),
            createElement('h3', { className: 'empty-state-title' }, 'Aucune conversation sélectionnée'),
            createElement('p', { className: 'empty-state-description' }, 
                'Créez ou sélectionnez une conversation pour commencer à discuter avec l\'IA.'
            )
        ]);
    }

    /**
     * Rend la colonne fichiers
     * @returns {HTMLElement}
     */
    async renderFilesColumn() {
        const column = createElement('div', { 
            className: 'column',
            style: 'background-color: var(--color-surface);'
        });

        this.fileExplorer = new FileExplorer({
            projectId: this.projectId,
            onFileSelect: (file) => {
                this.handleFileSelect(file);
            }
        });

        const explorerElement = await this.fileExplorer.render();
        column.appendChild(explorerElement);

        return column;
    }

    /**
     * Gère la sélection d'une conversation
     * @param {Object} conversation
     */
    handleConversationSelect(conversation) {
        this.currentConversationId = conversation.id;
        state.set('currentConversation', conversation);
        this.renderChatArea();
    }

    /**
     * Gère la sélection d'un fichier
     * @param {Object} file
     */
    handleFileSelect(file) {
        if (!this.chat || !this.currentConversationId) {
            alert('Veuillez d\'abord sélectionner une conversation.');
            return;
        }

        // Insérer le contenu du fichier dans l'input du chat
        const chatInput = this.container.querySelector('.chat-input');
        if (chatInput) {
            const fileContent = `\`\`\`${file.name}\n${file.content}\n\`\`\``;
            chatInput.value = chatInput.value 
                ? `${chatInput.value}\n\n${fileContent}` 
                : fileContent;
            chatInput.focus();
            
            // Auto-resize
            chatInput.style.height = 'auto';
            chatInput.style.height = chatInput.scrollHeight + 'px';
        }
    }

    /**
     * Crée une nouvelle conversation
     */
    async createNewConversation() {
        try {
            const agentId = state.get('currentAgent');
            
            const response = await fetch(
                `http://localhost:8000/api/projects/${this.projectId}/conversations`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        agent_id: agentId,
                        title: `Conversation ${new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}`
                    })
                }
            );

            if (response.ok) {
                const conversation = await response.json();
                this.currentConversationId = conversation.id;
                this.conversationList.setSelectedConversation(conversation.id);
                this.renderChatArea();
            } else {
                alert('Erreur lors de la création de la conversation.');
            }
        } catch (error) {
            console.error('Erreur création conversation:', error);
            alert('Erreur de connexion au serveur.');
        }
    }

    /**
     * Rend une erreur
     * @returns {HTMLElement}
     */
    renderError() {
        return createElement('div', { className: 'view-container' }, [
            createElement('div', { className: 'empty-state' }, [
                createElement('div', { className: 'empty-state-icon' }, '⚠️'),
                createElement('h3', { className: 'empty-state-title' }, 'Projet introuvable'),
                createElement('p', { className: 'empty-state-description' }, 
                    'Le projet demandé n\'existe pas ou a été supprimé.'
                ),
                createElement('button', {
                    style: `
                        padding: 0.75rem 1.5rem;
                        background-color: var(--color-primary);
                        color: white;
                        border: none;
                        border-radius: var(--radius-md);
                        font-weight: 600;
                        cursor: pointer;
                        margin-top: var(--spacing-lg);
                    `,
                    onClick: () => {
                        window.location.hash = '/projects';
                    }
                }, 'Retour aux projets')
            ])
        ]);
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

export default ProjectDetailView;
