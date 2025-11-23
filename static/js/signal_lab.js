/* ========================================
   SIGNAL LAB LEGACY ARCHIVE JAVASCRIPT
   ======================================== */

(function() {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        
        // Disable all input elements
        disableAllInputs();
        
        // Disable all buttons
        disableAllButtons();
        
        // Add legacy watermark
        addLegacyWatermark();
        
        // Prevent form submissions
        preventFormSubmissions();
        
        console.log('Signal Lab Dashboard frozen in legacy mode - all inputs disabled');
    });

    /**
     * Disable all input elements on the page
     */
    function disableAllInputs() {
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.disabled = true;
            input.setAttribute('readonly', 'readonly');
        });
    }

    /**
     * Disable all buttons on the page
     */
    function disableAllButtons() {
        const buttons = document.querySelectorAll('button, .btn, input[type="submit"], input[type="button"]');
        buttons.forEach(button => {
            button.disabled = true;
            button.style.pointerEvents = 'none';
        });
    }

    /**
     * Add legacy watermark to the page
     */
    function addLegacyWatermark() {
        const watermark = document.createElement('div');
        watermark.className = 'legacy-watermark';
        watermark.textContent = 'LEGACY ARCHIVE';
        document.body.appendChild(watermark);
    }

    /**
     * Prevent all form submissions
     */
    function preventFormSubmissions() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                alert('This is a legacy archive dashboard. Manual entries are disabled.');
                return false;
            });
        });
    }

    /**
     * Disable any dynamically added inputs
     */
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        // Disable inputs in the new node
                        const inputs = node.querySelectorAll('input, select, textarea, button');
                        inputs.forEach(input => {
                            input.disabled = true;
                        });
                    }
                });
            }
        });
    });

    // Start observing the document for changes
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

})();
