class CustomDropdown {
    constructor(element, options = {}) {
        this.element = element;
        this.options = options;
        this.isOpen = false;
        this.selectedValue = '';
        this.selectedText = '';
        this.init();
    }

    init() {
        this.createDropdown();
        this.bindEvents();
    }

    createDropdown() {
        const select = this.element;
        const wrapper = document.createElement('div');
        wrapper.className = 'custom-dropdown';
        
        const trigger = document.createElement('div');
        trigger.className = 'dropdown-trigger';
        trigger.setAttribute('tabindex', '0');
        trigger.setAttribute('role', 'button');
        trigger.setAttribute('aria-expanded', 'false');
        
        const selectedText = document.createElement('span');
        selectedText.className = 'dropdown-selected';
        selectedText.textContent = select.getAttribute('placeholder') || 'Select option';
        
        const arrow = document.createElement('i');
        arrow.className = 'bi bi-chevron-down dropdown-arrow';
        
        trigger.appendChild(selectedText);
        trigger.appendChild(arrow);
        
        const menu = document.createElement('div');
        menu.className = 'dropdown-menu';
        menu.setAttribute('role', 'listbox');
        
        // Create options
        Array.from(select.options).forEach((option, index) => {
            if (option.value === '') return; // Skip empty placeholder option
            
            const item = document.createElement('div');
            item.className = 'dropdown-item';
            item.setAttribute('role', 'option');
            item.setAttribute('data-value', option.value);
            item.textContent = option.textContent;
            
            if (option.selected) {
                this.selectedValue = option.value;
                this.selectedText = option.textContent;
                selectedText.textContent = option.textContent;
                item.classList.add('selected');
            }
            
            menu.appendChild(item);
        });
        
        wrapper.appendChild(trigger);
        wrapper.appendChild(menu);
        
        // Replace original select
        select.style.display = 'none';
        select.parentNode.insertBefore(wrapper, select);
        
        this.wrapper = wrapper;
        this.trigger = trigger;
        this.selectedElement = selectedText;
        this.arrow = arrow;
        this.menu = menu;
        this.originalSelect = select;
    }

    bindEvents() {
        // Toggle dropdown
        this.trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggle();
        });

        // Keyboard navigation
        this.trigger.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.toggle();
            }
        });

        // Item selection
        this.menu.addEventListener('click', (e) => {
            if (e.target.classList.contains('dropdown-item')) {
                this.selectItem(e.target);
            }
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!this.wrapper.contains(e.target)) {
                this.close();
            }
        });

        // Close on escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    }

    toggle() {
        this.isOpen ? this.close() : this.open();
    }

    open() {
        this.isOpen = true;
        this.wrapper.classList.add('open');
        this.trigger.setAttribute('aria-expanded', 'true');
        this.arrow.style.transform = 'rotate(180deg)';
        
        // Position dropdown menu
        const rect = this.trigger.getBoundingClientRect();
        this.menu.style.left = rect.left + 'px';
        this.menu.style.top = (rect.bottom + 4) + 'px';
        this.menu.style.width = rect.width + 'px';
    }

    close() {
        this.isOpen = false;
        this.wrapper.classList.remove('open');
        this.trigger.setAttribute('aria-expanded', 'false');
        this.arrow.style.transform = 'rotate(0deg)';
        
        // Reset positioning
        this.menu.style.left = '';
        this.menu.style.top = '';
        this.menu.style.width = '';
    }

    selectItem(item) {
        const value = item.getAttribute('data-value');
        const text = item.textContent;
        
        // Update selected state
        this.menu.querySelectorAll('.dropdown-item').forEach(i => i.classList.remove('selected'));
        item.classList.add('selected');
        
        // Update display
        this.selectedElement.textContent = text;
        this.selectedValue = value;
        this.selectedText = text;
        
        // Update original select
        this.originalSelect.value = value;
        
        // Trigger change event
        const event = new Event('change', { bubbles: true });
        this.originalSelect.dispatchEvent(event);
        
        this.close();
    }

    setValue(value) {
        const item = this.menu.querySelector(`[data-value="${value}"]`);
        if (item) {
            this.selectItem(item);
        }
    }
}

// Initialize all dropdowns
function initCustomDropdowns() {
    document.querySelectorAll('select.form-input, select.form-control-premium').forEach(select => {
        new CustomDropdown(select);
    });
}

// Auto-initialize on DOM load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCustomDropdowns);
} else {
    initCustomDropdowns();
}