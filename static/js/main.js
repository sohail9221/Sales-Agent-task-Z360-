function showNotification(message) {
    const container = document.querySelector('.notification-container');
    const messageElement = container.querySelector('.notification-message');
    
    messageElement.textContent = message;
    container.classList.remove('hidden');
    
    setTimeout(() => {
        container.classList.add('hidden');
    }, 3000);
}

// Listen for custom events for notifications
window.addEventListener('custom-notification', (event) => {
    showNotification(event.detail.message);
});