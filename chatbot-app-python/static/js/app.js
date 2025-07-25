// Chatbot Application JavaScript

class ChatApp {
    constructor() {
        this.currentUser = null;
        this.messages = [];
        this.isLoading = false;
        
        this.initializeElements();
        this.attachEventListeners();
        this.initialize();
    }
    
    initializeElements() {
        // Screens
        this.loadingScreen = document.getElementById('loading-screen');
        this.loginForm = document.getElementById('login-form');
        this.chatInterface = document.getElementById('chat-interface');
        
        // Login elements
        this.loginFormElement = document.getElementById('login-form-element');
        this.usernameInput = document.getElementById('username-input');
        this.loginButton = document.getElementById('login-button');
        this.loginButtonText = document.getElementById('login-button-text');
        this.loginSpinner = document.getElementById('login-spinner');
        
        // Chat elements
        this.currentUserSpan = document.getElementById('current-user');
        this.messagesContainer = document.getElementById('messages-container');
        this.chatForm = document.getElementById('chat-form');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.sendIcon = document.getElementById('send-icon');
        this.sendSpinner = document.getElementById('send-spinner');
        
        // Action buttons
        this.refreshButton = document.getElementById('refresh-button');
        this.clearHistoryButton = document.getElementById('clear-history-button');
        this.logoutButton = document.getElementById('logout-button');
    }
    
    attachEventListeners() {
        // Login form
        this.loginFormElement.addEventListener('submit', (e) => this.handleLogin(e));
        
        // Chat form
        this.chatForm.addEventListener('submit', (e) => this.handleSendMessage(e));
        
        // Action buttons
        this.refreshButton.addEventListener('click', () => this.refreshHistory());
        this.clearHistoryButton.addEventListener('click', () => this.clearHistory());
        this.logoutButton.addEventListener('click', () => this.handleLogout());
        
        // Enter key in message input
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage(e);
            }
        });
    }
    
    async initialize() {
        // Simulate loading
        await this.delay(1000);
        
        // Hide loading screen and show login form
        this.loadingScreen.classList.add('hidden');
        this.loginForm.classList.remove('hidden');
        
        // Focus on username input
        this.usernameInput.focus();
    }
    
    async handleLogin(e) {
        e.preventDefault();
        
        const username = this.usernameInput.value.trim();
        if (!username) return;
        
        this.setLoginLoading(true);
        
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username }),
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentUser = data.username;
                this.messages = data.messages || [];
                this.showChatInterface();
            } else {
                this.showError('Error al iniciar sesión');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showError('Error de conexión');
        } finally {
            this.setLoginLoading(false);
        }
    }
    
    async handleSendMessage(e) {
        e.preventDefault();
        
        const message = this.messageInput.value.trim();
        if (!message || this.isLoading) return;
        
        // Add user message to UI immediately
        this.addMessage('user', message);
        this.messageInput.value = '';
        this.setSendLoading(true);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.hideTypingIndicator();
                this.addMessage('assistant', data.message);
                // Refresh history after sending message to get updated list
                await this.refreshHistory();
            } else {
                this.hideTypingIndicator();
                this.showError(data.error || 'Error al enviar mensaje');
            }
        } catch (error) {
            console.error('Send message error:', error);
            this.hideTypingIndicator();
            this.showError('Error de conexión');
        } finally {
            this.setSendLoading(false);
        }
    }
    
    async handleLogout() {
        try {
            await fetch('/api/logout', {
                method: 'POST',
            });
            
            this.currentUser = null;
            this.messages = [];
            this.showLoginForm();
            this.usernameInput.value = '';
        } catch (error) {
            console.error('Logout error:', error);
        }
    }
    
    async refreshHistory() {
        try {
            const response = await fetch('/api/history');
            const data = await response.json();
            
            if (data.messages) {
                this.messages = data.messages;
                this.renderMessages();
            }
        } catch (error) {
            console.error('Refresh history error:', error);
            this.showError('Error al actualizar historial');
        }
    }
    
    async clearHistory() {
        if (!confirm('¿Estás seguro de que quieres limpiar el historial?')) {
            return;
        }
        
        try {
            const response = await fetch('/api/clear-history', {
                method: 'POST',
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.messages = [];
                this.renderMessages();
            }
        } catch (error) {
            console.error('Clear history error:', error);
            this.showError('Error al limpiar historial');
        }
    }
    
    showLoginForm() {
        this.chatInterface.classList.add('hidden');
        this.loginForm.classList.remove('hidden');
        this.usernameInput.focus();
    }
    
    showChatInterface() {
        this.loginForm.classList.add('hidden');
        this.chatInterface.classList.remove('hidden');
        this.currentUserSpan.textContent = this.currentUser;
        this.renderMessages();
        this.messageInput.focus();
    }
    
    renderMessages() {
        this.messagesContainer.innerHTML = '';
        
        this.messages.forEach(message => {
            // Handle both old format (role/content) and new API format (role/content)
            const role = message.role;
            const content = message.content;
            this.addMessageToDOM(role, content, false);
        });
        
        this.scrollToBottom();
    }
    
    addMessage(role, content) {
        const message = {
            role,
            content,
            timestamp: new Date().toISOString()
        };
        
        this.messages.push(message);
        this.addMessageToDOM(role, content, true);
    }
    
    addMessageToDOM(role, content, animate = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = role === 'user' 
            ? '<i class="fas fa-user text-white text-sm"></i>'
            : '<i class="fas fa-robot text-white text-sm"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Process markdown-like content
        messageContent.innerHTML = this.processMarkdown(content);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        if (animate) {
            messageDiv.style.opacity = '0';
            messageDiv.style.transform = 'translateY(10px)';
        }
        
        this.messagesContainer.appendChild(messageDiv);
        
        if (animate) {
            requestAnimationFrame(() => {
                messageDiv.style.transition = 'all 0.3s ease-in';
                messageDiv.style.opacity = '1';
                messageDiv.style.transform = 'translateY(0)';
            });
        }
        
        this.scrollToBottom();
    }
    
    processMarkdown(text) {
        // Simple markdown processing
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>')
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    }
    
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant';
        typingDiv.id = 'typing-indicator';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = '<i class="fas fa-robot text-white text-sm"></i>';
        
        const typingContent = document.createElement('div');
        typingContent.className = 'typing-indicator';
        typingContent.innerHTML = `
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        
        typingDiv.appendChild(avatar);
        typingDiv.appendChild(typingContent);
        
        this.messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    setLoginLoading(loading) {
        this.isLoading = loading;
        this.loginButton.disabled = loading;
        
        if (loading) {
            this.loginButtonText.textContent = 'Conectando...';
            this.loginSpinner.classList.remove('hidden');
        } else {
            this.loginButtonText.textContent = 'Comenzar Chat';
            this.loginSpinner.classList.add('hidden');
        }
    }
    
    setSendLoading(loading) {
        this.isLoading = loading;
        this.sendButton.disabled = loading;
        this.messageInput.disabled = loading;
        
        if (loading) {
            this.sendIcon.classList.add('hidden');
            this.sendSpinner.classList.remove('hidden');
        } else {
            this.sendIcon.classList.remove('hidden');
            this.sendSpinner.classList.add('hidden');
        }
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }
    
    showError(message) {
        // Simple error display - could be enhanced with a toast system
        alert(message);
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});
