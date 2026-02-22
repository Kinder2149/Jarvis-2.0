class FilePicker {
    constructor(config) {
        this.projectId = config.projectId;
        this.onSelect = config.onSelect;
        this.container = config.container;
        this.currentPath = '';
        this.fileTree = null;
    }
    
    async init() {
        await this.loadFileTree();
        this.render();
    }
    
    async loadFileTree() {
        try {
            const response = await fetch(`http://localhost:8000/api/projects/${this.projectId}/files/tree?max_depth=3`);
            if (response.ok) {
                this.fileTree = await response.json();
            }
        } catch (error) {
            console.error('Error loading file tree:', error);
        }
    }
    
    render() {
        if (!this.container || !this.fileTree) return;
        
        this.container.innerHTML = '';
        this.renderTree(this.fileTree, this.container, 0);
    }
    
    renderTree(node, parentEl, depth) {
        if (node.type === 'directory') {
            const dirEl = document.createElement('div');
            dirEl.className = 'file-tree-item directory';
            dirEl.style.paddingLeft = `${depth * 20}px`;
            
            const icon = document.createElement('span');
            icon.className = 'file-icon';
            icon.textContent = '📁';
            
            const name = document.createElement('span');
            name.className = 'file-name';
            name.textContent = node.name;
            
            dirEl.appendChild(icon);
            dirEl.appendChild(name);
            parentEl.appendChild(dirEl);
            
            if (node.items && node.items.length > 0) {
                node.items.forEach(item => {
                    this.renderTree(item, parentEl, depth + 1);
                });
            }
        } else {
            const fileEl = document.createElement('div');
            fileEl.className = 'file-tree-item file';
            fileEl.style.paddingLeft = `${depth * 20}px`;
            
            const icon = document.createElement('span');
            icon.className = 'file-icon';
            icon.textContent = '📄';
            
            const name = document.createElement('span');
            name.className = 'file-name';
            name.textContent = node.name;
            
            fileEl.appendChild(icon);
            fileEl.appendChild(name);
            
            fileEl.addEventListener('click', () => {
                if (this.onSelect) {
                    this.onSelect(node);
                }
            });
            
            parentEl.appendChild(fileEl);
        }
    }
}
