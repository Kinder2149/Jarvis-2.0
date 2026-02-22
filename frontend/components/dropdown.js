class DropdownMenu {
    constructor(config) {
        this.buttonSelector = config.buttonSelector;
        this.menuSelector = config.menuSelector;
        this.items = config.items || [];
        this.onSelect = config.onSelect;
        this.closeOnSelect = config.closeOnSelect ?? true;
        
        this.button = null;
        this.menu = null;
        this.isOpen = false;
        
        this.init();
    }
    
    init() {
        this.button = document.querySelector(this.buttonSelector);
        this.menu = document.querySelector(this.menuSelector);
        
        if (!this.button || !this.menu) {
            console.error('Dropdown: button or menu not found');
            return;
        }
        
        this.button.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggle();
        });
        
        document.addEventListener('click', (e) => {
            if (this.isOpen && !this.menu.contains(e.target) && !this.button.contains(e.target)) {
                this.close();
            }
        });
        
        this.render();
    }
    
    toggle() {
        this.isOpen ? this.close() : this.open();
    }
    
    open() {
        this.menu.classList.add('open');
        this.isOpen = true;
    }
    
    close() {
        this.menu.classList.remove('open');
        this.isOpen = false;
    }
    
    render() {
        if (this.items.length === 0) return;
        
        this.menu.innerHTML = '';
        
        this.items.forEach(item => {
            const itemEl = document.createElement('a');
            itemEl.href = item.href || '#';
            itemEl.className = 'dropdown-item';
            itemEl.textContent = item.label;
            
            if (item.icon) {
                itemEl.innerHTML = `${item.icon} ${item.label}`;
            }
            
            itemEl.addEventListener('click', (e) => {
                if (this.onSelect) {
                    e.preventDefault();
                    this.onSelect(item);
                }
                if (this.closeOnSelect) {
                    this.close();
                }
            });
            
            this.menu.appendChild(itemEl);
        });
    }
    
    updateItems(items) {
        this.items = items;
        this.render();
    }
}
