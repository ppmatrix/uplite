/**
 * Connection Image Selector - Enhanced UI for selecting connection images
 * Supports automatic suggestions, browsing available icons, and file uploads
 */

class ConnectionImageSelector {
    constructor(formSelector = '#addConnectionForm') {
        this.form = document.querySelector(formSelector);
        this.suggestionCache = null;
        this.searchTimeout = null;
        this.availableIcons = [];
        this.currentSuggestion = null;
        
        if (this.form) {
            this.initializeEventListeners();
        }
    }

    initializeEventListeners() {
        // Listen for name/target/type changes to trigger suggestions
        const nameInput = this.form.querySelector('input[name="name"]');
        const targetInput = this.form.querySelector('input[name="target"]');
        const typeInput = this.form.querySelector('select[name="connection_type"]');
        const descInput = this.form.querySelector('input[name="description"]');

        if (nameInput) {
            nameInput.addEventListener('input', this.debounce(() => this.getSuggestion(), 500));
        }
        if (targetInput) {
            targetInput.addEventListener('input', this.debounce(() => this.getSuggestion(), 500));
        }
        if (typeInput) {
            typeInput.addEventListener('change', () => this.getSuggestion());
        }
        if (descInput) {
            descInput.addEventListener('input', this.debounce(() => this.getSuggestion(), 800));
        }

        // Handle radio button changes
        const radioButtons = this.form.querySelectorAll('input[name="image_option"]');
        radioButtons.forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.handleImageOptionChange(e.target.value);
            });
        });

        // Icon search functionality
        const searchInput = this.form.querySelector('#icon-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchIcons(e.target.value);
            });
        }

        // Icon selection in grid
        this.form.addEventListener('click', (e) => {
            const iconOption = e.target.closest('.icon-option');
            if (iconOption) {
                this.selectIcon(iconOption);
            }
        });
    }

    debounce(func, wait) {
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(this.searchTimeout);
                func.apply(this, args);
            };
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(later, wait);
        }.bind(this);
    }

    async getSuggestion() {
        const nameInput = this.form.querySelector('input[name="name"]');
        const targetInput = this.form.querySelector('input[name="target"]');
        const descInput = this.form.querySelector('input[name="description"]');
        const typeInput = this.form.querySelector('select[name="connection_type"]');

        const name = nameInput?.value || '';
        const target = targetInput?.value || '';
        const description = descInput?.value || '';
        const type = typeInput?.value || '';

        // Don't suggest if name is too short
        if (!name || name.length < 2) {
            this.hideSuggestion();
            return;
        }

        // Show loading state
        this.showSuggestionLoading();

        try {
            const params = new URLSearchParams({
                name,
                target,
                description,
                connection_type: type
            });

            const response = await fetch(`/api/images/suggest?${params}`, {
                method: 'GET',
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            if (data.suggested_image) {
                this.showSuggestion(data.suggested_image);
            } else {
                this.hideSuggestion();
            }
        } catch (error) {
            console.warn('Error getting suggestion:', error);
            this.hideSuggestion();
        }
    }

    showSuggestionLoading() {
        const suggestionSection = this.form.querySelector('#suggestion-section');
        if (suggestionSection) {
            suggestionSection.innerHTML = `
                <div class="suggestion-loading">
                    <i class="bi bi-arrow-clockwise spin"></i> Finding matching icon...
                </div>
            `;
            suggestionSection.style.display = 'block';
        }
    }

    showSuggestion(imageName) {
        const suggestionSection = this.form.querySelector('#suggestion-section');
        if (!suggestionSection) return;

        this.currentSuggestion = imageName;
        const imageUrl = `/static/apps_icons/${imageName}`;
        
        suggestionSection.innerHTML = `
            <div class="alert alert-success alert-sm">
                <i class="bi bi-lightbulb"></i> We found a matching icon for your connection!
            </div>
            <div class="suggested-image-preview">
                <img src="${imageUrl}" alt="Suggested image" class="img-thumbnail" 
                     onerror="this.style.display='none';">
                <div>
                    <p class="text-muted mb-0">Suggested: <strong>${imageName}</strong></p>
                    <small class="text-muted">Click to use this icon</small>
                </div>
            </div>
            <div class="form-check">
                <input class="form-check-input" type="radio" name="image_option" id="use_suggestion" value="suggestion">
                <label class="form-check-label" for="use_suggestion">
                    Use suggested icon
                </label>
            </div>
        `;
        
        suggestionSection.style.display = 'block';

        // Auto-select suggestion if no option is selected yet
        const currentSelection = this.form.querySelector('input[name="image_option"]:checked');
        if (!currentSelection) {
            const suggestionRadio = suggestionSection.querySelector('#use_suggestion');
            if (suggestionRadio) {
                suggestionRadio.checked = true;
                this.handleImageOptionChange('suggestion');
            }
        }

        // Re-bind event listeners for the new radio button
        const suggestionRadio = suggestionSection.querySelector('#use_suggestion');
        if (suggestionRadio) {
            suggestionRadio.addEventListener('change', (e) => {
                this.handleImageOptionChange(e.target.value);
            });
        }
    }

    hideSuggestion() {
        const suggestionSection = this.form.querySelector('#suggestion-section');
        if (suggestionSection) {
            suggestionSection.style.display = 'none';
            this.currentSuggestion = null;
        }
    }

    handleImageOptionChange(option) {
        const iconBrowser = this.form.querySelector('#icon-browser');
        const uploadInput = this.form.querySelector('#upload-input');
        const logoChoiceInput = this.form.querySelector('input[name="logo_choice"]');

        // Hide all sections first
        if (iconBrowser) iconBrowser.style.display = 'none';
        if (uploadInput) uploadInput.style.display = 'none';

        switch (option) {
            case 'suggestion':
                if (this.currentSuggestion && logoChoiceInput) {
                    logoChoiceInput.value = this.currentSuggestion;
                }
                break;

            case 'browse':
                if (iconBrowser) {
                    iconBrowser.style.display = 'block';
                    this.loadAvailableIcons();
                }
                if (logoChoiceInput) logoChoiceInput.value = '';
                break;

            case 'upload':
                if (uploadInput) uploadInput.style.display = 'block';
                if (logoChoiceInput) logoChoiceInput.value = '';
                break;
        }
    }

    async loadAvailableIcons(searchQuery = '') {
        const iconGrid = this.form.querySelector('#icon-grid');
        if (!iconGrid) return;

        // Show loading state
        iconGrid.className = 'icon-grid loading';
        iconGrid.innerHTML = '';

        try {
            const url = searchQuery
                ? `/api/images/search?q=${encodeURIComponent(searchQuery)}&limit=100`
                : '/api/images/available';

            const response = await fetch(url, {
                method: 'GET',
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            let icons;
            if (searchQuery) {
                icons = data.results || [];
            } else {
                this.availableIcons = data.icons || [];
                icons = this.availableIcons.map(i => i.filename);
            }

            this.renderIconGrid(icons);

        } catch (error) {
            console.error('Error loading icons:', error);
            iconGrid.className = 'icon-grid empty';
            iconGrid.innerHTML = '<div class="text-center text-muted p-3">Failed to load icons</div>';
        }
    }

    renderIconGrid(icons) {
        const iconGrid = this.form.querySelector('#icon-grid');
        if (!iconGrid) return;

        iconGrid.className = 'icon-grid';

        if (icons.length === 0) {
            iconGrid.className = 'icon-grid empty';
            iconGrid.innerHTML = '';
            return;
        }

        iconGrid.innerHTML = '';

        icons.forEach(iconName => {
            const iconElement = document.createElement('div');
            iconElement.className = 'icon-option';
            iconElement.dataset.icon = iconName;

            // Clean up the icon name for display
            const displayName = iconName.replace(/\.(png|jpg|jpeg|gif|svg)$/i, '');

            iconElement.innerHTML = `
                <img src="/static/apps_icons/${iconName}" alt="${displayName}" 
                     onerror="this.parentElement.style.display='none';">
                <small>${displayName}</small>
            `;

            iconGrid.appendChild(iconElement);
        });
    }

    selectIcon(iconElement) {
        const iconGrid = this.form.querySelector('#icon-grid');
        const logoChoiceInput = this.form.querySelector('input[name="logo_choice"]');

        // Remove previous selection
        iconGrid.querySelectorAll('.icon-option').forEach(el => {
            el.classList.remove('selected');
        });

        // Select new icon
        iconElement.classList.add('selected');
        const iconName = iconElement.dataset.icon;

        if (logoChoiceInput) {
            logoChoiceInput.value = iconName;
        }

        // Ensure browse option is selected
        const browseRadio = this.form.querySelector('input[value="browse"]');
        if (browseRadio) {
            browseRadio.checked = true;
        }
    }

    searchIcons(query) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.loadAvailableIcons(query);
        }, 300);
    }

    // Utility method to get current selection
    getCurrentSelection() {
        const selectedOption = this.form.querySelector('input[name="image_option"]:checked');
        const logoChoiceInput = this.form.querySelector('input[name="logo_choice"]');
        const logoFileInput = this.form.querySelector('input[name="logo"]');

        return {
            option: selectedOption?.value,
            logoChoice: logoChoiceInput?.value,
            logoFile: logoFileInput?.files[0]
        };
    }

    // Method to reset the selector
    reset() {
        this.hideSuggestion();
        const radioButtons = this.form.querySelectorAll('input[name="image_option"]');
        radioButtons.forEach(radio => radio.checked = false);

        const iconBrowser = this.form.querySelector('#icon-browser');
        const uploadInput = this.form.querySelector('#upload-input');
        if (iconBrowser) iconBrowser.style.display = 'none';
        if (uploadInput) uploadInput.style.display = 'none';

        const logoChoiceInput = this.form.querySelector('input[name="logo_choice"]');
        if (logoChoiceInput) logoChoiceInput.value = '';

        const logoFileInput = this.form.querySelector('input[name="logo"]');
        if (logoFileInput) logoFileInput.value = '';
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    // Initialize for add connection form
    window.addConnectionImageSelector = new ConnectionImageSelector('#addConnectionForm');

    // Add CSS animation for spinning icon
    if (!document.querySelector('#image-selector-styles')) {
        const style = document.createElement('style');
        style.id = 'image-selector-styles';
        style.textContent = `
            .spin {
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            .alert-sm {
                padding: 0.375rem 0.75rem;
                font-size: 0.875rem;
            }
        `;
        document.head.appendChild(style);
    }
});

// Export for use in other contexts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ConnectionImageSelector;
}
