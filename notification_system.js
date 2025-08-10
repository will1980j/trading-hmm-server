// Notification System for Trading Dashboard
function showNotification(message, type = 'info', duration = 5000) {
    try {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        // Sanitize message to prevent XSS
        const safeMessage = message.replace(/</g, '&lt;').replace(/>/g, '&gt;');
        notification.textContent = safeMessage;
        
        // Use object for better maintainability instead of inline styles
        const baseStyles = {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '15px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '10000',
            maxWidth: '400px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease'
        };
        
        const typeStyles = {
            error: { background: '#dc3545' },
            success: { background: '#28a745' },
            warning: { background: '#ffc107', color: '#000' },
            info: { background: '#17a2b8' }
        };
        
        Object.assign(notification.style, baseStyles, typeStyles[type] || typeStyles.info);
        
        if (!document.body) {
            console.error('Document body not available for notification');
            return;
        }
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.transform = 'translateX(0)';
            }
        }, 100);
        
        // Auto remove
        const removeNotification = () => {
            if (notification.parentNode) {
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }
        };
        
        setTimeout(removeNotification, duration);
        
        // Click to dismiss
        notification.addEventListener('click', removeNotification);
        
    } catch (error) {
        console.error('Error showing notification:', error);
        // Fallback to console log if DOM manipulation fails
        console.log(`${type.toUpperCase()}: ${message}`);
    }
}

// Make globally available
window.showNotification = showNotification;