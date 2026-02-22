class Modal {
    constructor(modalId) {
        this.modalId = modalId;
        this.modal = document.getElementById(modalId);
        
        if (!this.modal) {
            console.error(`Modal with id ${modalId} not found`);
            return;
        }
        
        this.init();
    }
    
    init() {
        const closeBtn = this.modal.querySelector('.modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }
        
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen()) {
                this.close();
            }
        });
    }
    
    open() {
        this.modal.classList.remove('hidden');
        this.modal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
    
    close() {
        this.modal.classList.remove('open');
        this.modal.classList.add('hidden');
        document.body.style.overflow = '';
    }
    
    isOpen() {
        return this.modal.classList.contains('open');
    }
}

function openModal(modalId) {
    const modal = new Modal(modalId);
    modal.open();
}

function closeModal(modalId) {
    const modal = new Modal(modalId);
    modal.close();
}
