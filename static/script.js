// Project VICTUS Frontend JavaScript - Enhanced with Full Features

class VICTUSClient {
    constructor() {
        // Check authentication
        this.token = localStorage.getItem('victus_token');
        this.user = JSON.parse(localStorage.getItem('victus_user') || 'null');
        
        if (!this.token) {
            window.location.href = '/login';
            return;
        }
        
        this.sessionId = this.getOrCreateSessionId();
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.currentEventSource = null;
        this.conversations = [];
        this.selectedModel = localStorage.getItem('selected_model') || 'gpt-4o';
        
        this.initializeElements();
        this.attachEventListeners();
        this.setupAuthUI();
        this.setupModelSelector();
        this.fetchUserInfo().then(() => {
            this.setupAuthUI();
        }).catch((error) => {
            console.error('Failed to fetch user info:', error);
            if (error.message && error.message.includes('401')) {
                localStorage.removeItem('victus_token');
                localStorage.removeItem('victus_user');
                window.location.href = '/login';
            }
        });
        this.loadConversations();
        this.loadChatHistory();
    }
    
    initializeElements() {
        // Chat elements
        this.chatMessages = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendBtn = document.getElementById('send-btn');
        this.voiceBtn = document.getElementById('voice-btn');
        this.uploadBtn = document.getElementById('upload-btn');
        this.fileInput = document.getElementById('file-input');
        this.audioInput = document.getElementById('audio-input');
        this.welcomeScreen = document.getElementById('welcome-screen');
        
        // Sidebar elements
        this.sidebar = document.getElementById('sidebar');
        this.sidebarToggle = document.getElementById('sidebar-toggle');
        this.sidebarCloseBtn = document.getElementById('sidebar-close-btn');
        this.newChatBtn = document.getElementById('new-chat-btn');
        this.chatHistoryList = document.getElementById('chat-history-list');
        this.historySearch = document.getElementById('history-search');
        this.modelSelector = document.getElementById('model-selector');
        this.modelDropdown = document.getElementById('model-dropdown');
        
        // Settings
        this.settingsBtn = document.getElementById('settings-btn');
        this.settingsOverlay = document.getElementById('settings-overlay');
        this.settingsClose = document.getElementById('settings-close');
        
        // Panels
        this.documentsBtn = document.getElementById('documents-btn');
        this.documentsOverlay = document.getElementById('documents-overlay');
        this.memoryBtn = document.getElementById('memory-btn');
        this.memoryOverlay = document.getElementById('memory-overlay');
        
        // User profile
        this.userProfile = document.getElementById('user-profile');
        this.userAvatar = document.getElementById('user-avatar');
        this.userName = document.getElementById('user-name');
        this.userEmail = document.getElementById('user-email');
        this.profileMenu = document.getElementById('profile-menu');
        this.settingsMenuBtn = document.getElementById('settings-menu-btn');
        this.logoutMenuBtn = document.getElementById('logout-menu-btn');
        this.themeToggleBtn = document.getElementById('theme-toggle-btn');
        this.themeIcon = document.getElementById('theme-icon');
        this.themeText = document.getElementById('theme-text');
    }

    attachEventListeners() {
        // Chat
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        });
        this.voiceBtn.addEventListener('click', () => this.toggleVoiceRecording());
        this.uploadBtn.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
        
        // Sidebar
        this.sidebarToggle?.addEventListener('click', () => this.toggleSidebar());
        this.sidebarCloseBtn?.addEventListener('click', () => this.closeSidebar());
        this.sidebarOverlay?.addEventListener('click', () => this.closeSidebar());
        this.newChatBtn.addEventListener('click', () => this.createNewChat());
        this.historySearch?.addEventListener('input', (e) => this.filterHistory(e.target.value));
        
        // Model selector (inline)
        this.modelSelector.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleModelDropdown();
        });
        document.querySelectorAll('.model-option').forEach(option => {
            option.addEventListener('click', (e) => {
                e.stopPropagation();
                this.selectModel(option.dataset.model);
            });
        });
        
        // Close model dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.modelSelector.contains(e.target) && !this.modelDropdown.contains(e.target)) {
                this.modelSelector.classList.remove('active');
                this.modelDropdown.classList.remove('show');
            }
        });
        
        // Profile menu
        if (this.userProfile && this.profileMenu) {
            this.userProfile.addEventListener('click', (e) => {
                e.stopPropagation();
                e.preventDefault();
                this.toggleProfileMenu();
            });
            
            if (this.settingsMenuBtn) {
                this.settingsMenuBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.closeProfileMenu();
                    this.openSettings();
                });
            }
            
            if (this.logoutMenuBtn) {
                this.logoutMenuBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.logout();
                });
            }
            
            if (this.themeToggleBtn) {
                this.themeToggleBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.toggleTheme();
                });
            }
            
            // Close profile menu when clicking outside
            document.addEventListener('click', (e) => {
                if (this.userProfile && this.profileMenu && 
                    !this.userProfile.contains(e.target) && 
                    !this.profileMenu.contains(e.target)) {
                    this.closeProfileMenu();
                }
            });
        }
        
        // Settings
        this.settingsClose.addEventListener('click', () => this.closeSettings());
        this.settingsSaveBtn = document.getElementById('settings-save-btn');
        this.settingsSaveBtn.addEventListener('click', () => this.saveAndCloseSettings());
        this.settingsOverlay.addEventListener('click', (e) => {
            if (e.target === this.settingsOverlay) this.closeSettings();
        });
        
        // Panels
        this.documentsBtn?.addEventListener('click', () => this.openDocuments());
        this.memoryBtn?.addEventListener('click', () => this.openMemory());
        document.querySelectorAll('.panel-close').forEach(btn => {
            btn.addEventListener('click', () => {
                const panel = btn.dataset.panel;
                if (panel === 'documents') this.closeDocuments();
                if (panel === 'memory') this.closeMemory();
            });
        });
        
        // Welcome screen prompts
        document.querySelectorAll('.prompt-card').forEach(card => {
            card.addEventListener('click', () => {
                const prompt = card.dataset.prompt;
                this.messageInput.value = prompt;
                this.sendMessage();
            });
        });
        
        // Load theme preference
        this.loadTheme();
    }
            
    setupAuthUI() {
            if (this.user) {
                const displayName = this.user.full_name || this.user.username || this.user.email || 'User';
            const email = this.user.email || 'user@example.com';
            const initials = displayName.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
            
            if (this.userName) this.userName.textContent = displayName;
            if (this.userEmail) this.userEmail.textContent = email;
            if (this.userAvatar) this.userAvatar.textContent = initials;
        }
    }

    setupModelSelector() {
        const models = {
            'gpt-4o': { name: 'GPT-4o', desc: 'Most capable' },
            'gpt-4o-mini': { name: 'GPT-4o-mini', desc: 'Fast & efficient' },
            'gpt-4-turbo': { name: 'GPT-4-turbo', desc: 'Balanced' },
            'gpt-4': { name: 'GPT-4', desc: 'High quality' },
            'gpt-3.5-turbo': { name: 'GPT-3.5-turbo', desc: 'Fastest' }
        };
        
        const current = models[this.selectedModel] || models['gpt-4o'];
        document.getElementById('current-model').textContent = current.name;
        
        document.querySelectorAll('.model-option').forEach(option => {
            option.classList.remove('selected');
            if (option.dataset.model === this.selectedModel) {
                option.classList.add('selected');
            }
        });
    }

    toggleModelDropdown() {
        this.modelSelector.classList.toggle('active');
        this.modelDropdown.classList.toggle('show');
    }
    
    toggleProfileMenu() {
        if (this.profileMenu) {
            this.profileMenu.classList.toggle('show');
        }
    }
    
    closeProfileMenu() {
        this.profileMenu.classList.remove('show');
    }
    
    loadTheme() {
        const savedTheme = localStorage.getItem('victus_theme') || 'dark';
        this.setTheme(savedTheme);
    }
    
    toggleTheme() {
        const currentTheme = document.body.classList.contains('light-mode') ? 'light' : 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
        localStorage.setItem('victus_theme', newTheme);
    }
    
    setTheme(theme) {
        document.body.classList.remove('dark-mode', 'light-mode');
        document.body.classList.add(`${theme}-mode`);
        
        // Update theme toggle button
        if (this.themeIcon && this.themeText) {
            if (theme === 'light') {
                this.themeIcon.textContent = '☀️';
                this.themeText.textContent = 'Light Mode';
            } else {
                this.themeIcon.textContent = '🌙';
                this.themeText.textContent = 'Dark Mode';
            }
        }
    }

    selectModel(model) {
        this.selectedModel = model;
        localStorage.setItem('selected_model', model);
        this.setupModelSelector();
        this.toggleModelDropdown();
    }

    toggleSidebar() {
        const isActive = this.sidebar.classList.contains('active');
        if (isActive) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }

    openSidebar() {
        this.sidebar.classList.add('active');
        if (this.sidebarOverlay) {
            this.sidebarOverlay.classList.add('active');
        }
        // Add class to body for animation
        document.body.classList.add('sidebar-open');
        // Prevent body scroll when sidebar is open on mobile
        if (window.innerWidth <= 768) {
            document.body.style.overflow = 'hidden';
        }
    }

    closeSidebar() {
        this.sidebar.classList.remove('active');
        if (this.sidebarOverlay) {
            this.sidebarOverlay.classList.remove('active');
        }
        // Remove class from body
        document.body.classList.remove('sidebar-open');
        // Restore body scroll
        document.body.style.overflow = '';
    }

    createNewChat() {
        this.sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('victus_session_id', this.sessionId);
        this.chatMessages.innerHTML = '';
        this.welcomeScreen.style.display = 'flex';
        this.loadConversations();
        // Close sidebar on mobile after creating new chat
        if (window.innerWidth <= 768) {
            this.closeSidebar();
        }
    }

    async loadConversations() {
        try {
            const response = await fetch('/api/conversations', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.conversations = data.conversations || [];
                this.renderConversations();
            }
        } catch (error) {
            console.error('Error loading conversations:', error);
        }
    }

    renderConversations() {
        if (!this.chatHistoryList) return;
        
        this.chatHistoryList.innerHTML = '';
        
        if (this.conversations.length === 0) {
            this.chatHistoryList.innerHTML = '<div style="text-align: center; padding: 20px; color: var(--text-secondary); font-size: 13px;">No conversations yet</div>';
            return;
        }
        
        this.conversations.forEach(conv => {
            const item = document.createElement('div');
            item.className = 'history-item';
            if (conv.session_id === this.sessionId) {
                item.classList.add('active');
            }
            
            const title = conv.title || conv.last_message?.substring(0, 40) || 'New Chat';
            const time = this.formatRelativeTime(conv.timestamp);
            
            item.innerHTML = `
                <div class="history-item-title">${this.escapeHtml(title)}</div>
                <div class="history-item-meta">
                    <span>${time}</span>
                    <span>•</span>
                    <span>${conv.message_count} messages</span>
                    </div>
                <div class="history-item-actions">
                    <button class="history-item-action" onclick="victusClient.deleteConversation('${conv.session_id}')" title="Delete">🗑️</button>
                </div>
            `;
            
            item.addEventListener('click', (e) => {
                if (!e.target.closest('.history-item-action')) {
                    this.loadConversation(conv.session_id);
                }
            });
            
            this.chatHistoryList.appendChild(item);
        });
    }

    filterHistory(query) {
        const items = this.chatHistoryList.querySelectorAll('.history-item');
        items.forEach(item => {
            const title = item.querySelector('.history-item-title').textContent.toLowerCase();
            if (title.includes(query.toLowerCase())) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }

    formatRelativeTime(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diff = now - time;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days < 7) return `${days}d ago`;
        return time.toLocaleDateString();
    }

    async loadConversation(sessionId) {
        this.sessionId = sessionId;
        localStorage.setItem('victus_session_id', sessionId);
        this.chatMessages.innerHTML = '';
        this.welcomeScreen.style.display = 'none';
        
        try {
            const response = await fetch('/api/history', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({ session_id: sessionId })
            });
            const data = await response.json();
            
            if (data.history && data.history.length > 0) {
                data.history.forEach(msg => {
                    this.addMessage(msg.message, msg.sender);
                });
            } else {
                this.welcomeScreen.style.display = 'flex';
            }
            this.loadConversations();
        } catch (error) {
            console.error('Error loading conversation:', error);
        }
    }

    async deleteConversation(sessionId) {
        if (!confirm('Delete this conversation?')) return;
        
        try {
            const response = await fetch(`/api/conversations/${sessionId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });
            
            if (response.ok) {
                if (sessionId === this.sessionId) {
                    this.createNewChat();
                }
                this.loadConversations();
                this.showStatus('Conversation deleted', 'success');
            }
        } catch (error) {
            console.error('Error deleting conversation:', error);
            this.showStatus('Error deleting conversation', 'error');
        }
    }

    openSettings() {
        this.settingsOverlay.classList.add('active');
        this.loadSettings();
    }

    closeSettings() {
        this.settingsOverlay.classList.remove('active');
        // Don't auto-save - user must click Save button
    }


    loadSettings() {
        const context = localStorage.getItem('system_context') || '';
        const voiceOutput = localStorage.getItem('voice_output') === 'true';
        const autoScroll = localStorage.getItem('auto_scroll') !== 'false';
        const savedUsername = localStorage.getItem('victus_username');
        
        document.getElementById('settings-context').value = context;
        document.getElementById('settings-voice-output').checked = voiceOutput;
        document.getElementById('settings-auto-scroll').checked = autoScroll;
        
        if (this.user) {
            document.getElementById('settings-username').value = savedUsername || this.user.username || '';
            document.getElementById('settings-email').value = this.user.email || '';
        }
    }

    async saveSettings() {
        try {
            const context = document.getElementById('settings-context').value;
            const voiceOutput = document.getElementById('settings-voice-output').checked;
            const autoScroll = document.getElementById('settings-auto-scroll').checked;
            const username = document.getElementById('settings-username').value.trim();
            
            // Save to localStorage
            localStorage.setItem('system_context', context);
            localStorage.setItem('voice_output', voiceOutput);
            localStorage.setItem('auto_scroll', autoScroll);
            
            // Update user profile if username changed
            if (this.user && username && username !== this.user.username) {
                try {
                    // Note: Backend doesn't have user update endpoint yet
                    // This is prepared for when it's added
                    // For now, just save to localStorage
                    localStorage.setItem('victus_username', username);
                    
                    // Update local user object
                    if (this.user) {
                        this.user.username = username;
                        localStorage.setItem('victus_user', JSON.stringify(this.user));
                        this.setupAuthUI(); // Update UI with new username
                    }
                } catch (error) {
                    console.error('Error updating username:', error);
                    // Continue even if username update fails
                }
            }
        } catch (error) {
            console.error('Error saving settings:', error);
            throw error;
        }
    }

    async saveAndCloseSettings() {
        const saveBtn = document.getElementById('settings-save-btn');
        if (saveBtn) {
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<span>Saving...</span>';
        }
        
        try {
            await this.saveSettings();
            this.closeSettings();
            this.showStatus('Settings saved successfully!', 'success');
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showStatus('Error saving settings. Please try again.', 'error');
        } finally {
            if (saveBtn) {
                saveBtn.disabled = false;
                saveBtn.innerHTML = `
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M5 13L9 17L19 7" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <span>Save Settings</span>
                `;
            }
        }
    }
    
    async openDocuments() {
        this.documentsOverlay.classList.add('active');
        await this.loadDocuments();
    }

    closeDocuments() {
        this.documentsOverlay.classList.remove('active');
    }

    async loadDocuments() {
        try {
            const response = await fetch('/api/documents', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.renderDocuments(data.documents || []);
            }
        } catch (error) {
            console.error('Error loading documents:', error);
        }
    }

    renderDocuments(documents) {
        const content = document.getElementById('documents-content');
        if (!content) return;
        
        if (documents.length === 0) {
            content.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-secondary);">No documents uploaded yet</div>';
                return;
            }
        
        content.innerHTML = documents.map(doc => `
            <div class="document-item" style="padding: 16px; background: rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">${this.escapeHtml(doc.filename)}</div>
                        <div style="font-size: 12px; color: var(--text-secondary);">
                            ${this.formatFileSize(doc.size)} • ${new Date(doc.upload_date).toLocaleDateString()}
                        </div>
                        <div style="font-size: 12px; color: ${doc.indexed ? '#10b981' : '#f59e0b'}; margin-top: 4px;">
                            ${doc.indexed ? '✓ Indexed' : '⏳ Processing'}
                        </div>
                    </div>
                    <button onclick="victusClient.deleteDocument('${doc.filename}')" style="padding: 6px 12px; background: rgba(239,68,68,0.2); border: 1px solid #ef4444; border-radius: 8px; color: #ef4444; cursor: pointer; font-size: 12px;">Delete</button>
                </div>
            </div>
        `).join('');
    }

    formatFileSize(bytes) {
        if (!bytes) return 'Unknown size';
        const kb = bytes / 1024;
        const mb = kb / 1024;
        if (mb >= 1) return `${mb.toFixed(2)} MB`;
        return `${kb.toFixed(2)} KB`;
    }

    async deleteDocument(filename) {
        if (!confirm(`Delete ${filename}?`)) return;
        
        try {
            const response = await fetch(`/api/documents/${encodeURIComponent(filename)}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });
            
            if (response.ok) {
                this.loadDocuments();
                this.showStatus('Document deleted', 'success');
            }
        } catch (error) {
            console.error('Error deleting document:', error);
            this.showStatus('Error deleting document', 'error');
        }
    }

    async openMemory() {
        this.memoryOverlay.classList.add('active');
        await this.loadFacts();
    }

    closeMemory() {
        this.memoryOverlay.classList.remove('active');
    }

    async loadFacts() {
        try {
            const response = await fetch('/api/facts', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.renderFacts(data.facts || []);
            }
        } catch (error) {
            console.error('Error loading facts:', error);
        }
    }

    renderFacts(facts) {
        const content = document.getElementById('memory-content');
        if (!content) return;
        
        if (facts.length === 0) {
            content.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-secondary);">No facts stored yet</div>';
            return;
        }
        
        content.innerHTML = facts.map(fact => `
            <div class="fact-item" style="padding: 16px; background: rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">${this.escapeHtml(fact.key)}</div>
                        <div style="font-size: 14px; color: var(--text-secondary);">${this.escapeHtml(fact.value)}</div>
                    </div>
                    <button onclick="victusClient.deleteFact(${fact.id})" style="padding: 6px 12px; background: rgba(239,68,68,0.2); border: 1px solid #ef4444; border-radius: 8px; color: #ef4444; cursor: pointer; font-size: 12px;">Delete</button>
                </div>
            </div>
        `).join('');
    }

    async deleteFact(id) {
        if (!confirm('Delete this fact?')) return;
        
        try {
            const response = await fetch(`/api/facts/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });
            
            if (response.ok) {
                this.loadFacts();
                this.showStatus('Fact deleted', 'success');
            }
        } catch (error) {
            console.error('Error deleting fact:', error);
            this.showStatus('Error deleting fact', 'error');
        }
    }
    
    async fetchUserInfo() {
        try {
            if (!this.token) return;
            
            const response = await fetch('/api/auth/me', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });
            
            if (response.ok) {
                const userData = await response.json();
                this.user = userData;
                localStorage.setItem('victus_user', JSON.stringify(userData));
                return userData;
            } else if (response.status === 401) {
                localStorage.removeItem('victus_token');
                localStorage.removeItem('victus_user');
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Error fetching user info:', error);
        }
        return null;
    }
    
    async logout() {
        try {
            await fetch('/api/auth/logout', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            localStorage.removeItem('victus_token');
            localStorage.removeItem('victus_user');
            window.location.href = '/login';
        }
    }

    getOrCreateSessionId() {
        let sessionId = localStorage.getItem('victus_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('victus_session_id', sessionId);
        }
        return sessionId;
    }

    async loadChatHistory() {
        try {
            const response = await fetch('/api/history', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({ session_id: this.sessionId })
            });
            const data = await response.json();
            
            if (data.history && data.history.length > 0) {
                this.welcomeScreen.style.display = 'none';
                data.history.forEach(msg => {
                    this.addMessage(msg.message, msg.sender);
                });
            }
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        this.sendBtn.disabled = true;
        this.welcomeScreen.style.display = 'none';

        const typingId = this.showTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let aiMessageBuffer = '';
            let aiMessageElement = null;

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        
                        if (data.startsWith('OUTPUT_STREAM:')) {
                            this.removeTypingIndicator(typingId);
                            
                            if (!aiMessageElement) {
                                aiMessageElement = this.createMessageElement('', 'ai');
                                this.chatMessages.appendChild(aiMessageElement);
                            }
                            
                            const text = data.slice(14);
                            aiMessageBuffer += text;
                            const messageText = aiMessageElement.querySelector('.message-text');
                            if (messageText) {
                                messageText.textContent = aiMessageBuffer;
                            }
                            
                            this.scrollToBottom();
                        } else if (data.startsWith('EVENT_TOOL_START:')) {
                            const toolInfo = data.slice(17);
                            this.addToolEvent(`🔧 Using tool: ${toolInfo.split('|')[0]}`, 'start');
                        } else if (data.startsWith('EVENT_TOOL_END:')) {
                            const toolName = data.slice(15);
                            this.addToolEvent(`✓ Completed: ${toolName}`, 'end');
                        } else if (data.startsWith('ERROR:')) {
                            this.removeTypingIndicator(typingId);
                            const errorMsg = data.slice(7);
                            this.addMessage(`Error: ${errorMsg}`, 'ai');
                            this.showStatus('An error occurred', 'error');
                        } else if (data === 'STREAM_END') {
                            this.removeTypingIndicator(typingId);
                            if (aiMessageElement && aiMessageBuffer) {
                                this.addAudioButton(aiMessageElement, aiMessageBuffer);
                            }
                            this.loadConversations();
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.removeTypingIndicator(typingId);
            this.addMessage('Sorry, I encountered an error. Please try again.', 'ai');
            this.showStatus('Error sending message', 'error');
        } finally {
            this.sendBtn.disabled = false;
        }
    }

    addMessage(text, sender) {
        const messageElement = this.createMessageElement(text, sender);
        this.chatMessages.appendChild(messageElement);
        this.scrollToBottom();
        
        if (sender === 'ai') {
            this.addAudioButton(messageElement, text);
        }
    }

    createMessageElement(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = sender === 'user' ? 'U' : 'V';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const headerDiv = document.createElement('div');
        headerDiv.className = 'message-header';
        headerDiv.textContent = sender === 'user' ? 'You' : 'VICTUS';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.textContent = text;

        contentDiv.appendChild(headerDiv);
        contentDiv.appendChild(textDiv);
        
        // Message actions for AI messages
        if (sender === 'ai') {
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'message-actions';
            actionsDiv.innerHTML = `
                <button class="message-action" onclick="navigator.clipboard.writeText('${this.escapeHtml(text)}'); victusClient.showStatus('Copied!', 'success')">Copy</button>
                <button class="message-action" onclick="victusClient.regenerateMessage()">Regenerate</button>
            `;
            contentDiv.appendChild(actionsDiv);
        }

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);

        return messageDiv;
    }

    addToolEvent(text, type) {
        const eventDiv = document.createElement('div');
        eventDiv.className = 'tool-event';
        eventDiv.textContent = text;
        this.chatMessages.appendChild(eventDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai';
        typingDiv.id = 'typing-indicator';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = 'V';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            typingIndicator.appendChild(dot);
        }
        
        contentDiv.appendChild(typingIndicator);
        typingDiv.appendChild(avatar);
        typingDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
        
        return 'typing-indicator';
    }

    removeTypingIndicator(id) {
        const indicator = document.getElementById(id);
        if (indicator) {
            indicator.remove();
        }
    }

    addAudioButton(messageElement, text) {
        const audioBtn = document.createElement('button');
        audioBtn.className = 'message-action';
        audioBtn.textContent = '🔊 Play';
        audioBtn.title = 'Play audio';
        audioBtn.onclick = () => this.synthesizeSpeech(text, audioBtn);
        
        const actionsDiv = messageElement.querySelector('.message-actions');
        if (actionsDiv) {
            actionsDiv.appendChild(audioBtn);
        }
    }

    async synthesizeSpeech(text, button) {
        try {
            button.disabled = true;
            button.textContent = '⏳';
            
            const response = await fetch('/api/synthesize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });
            
            const data = await response.json();
            
            if (data.audio_url) {
                const audio = new Audio(data.audio_url);
                audio.play();
                button.textContent = '🔊 Play';
            }
        } catch (error) {
            console.error('Error synthesizing speech:', error);
            button.textContent = '🔊 Play';
        } finally {
            button.disabled = false;
        }
    }

    async toggleVoiceRecording() {
        if (!this.isRecording) {
            await this.startRecording();
        } else {
            await this.stopRecording();
        }
    }

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                await this.transcribeAudio(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            this.voiceBtn.textContent = '⏹️';
            this.voiceBtn.classList.add('recording');
            this.showStatus('Recording... Click again to stop', 'success');
        } catch (error) {
            console.error('Error starting recording:', error);
            this.showStatus('Error accessing microphone', 'error');
        }
    }

    async stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.voiceBtn.textContent = '🎤';
            this.voiceBtn.classList.remove('recording');
            this.showStatus('Processing audio...', 'success');
        }
    }

    async transcribeAudio(audioBlob) {
        try {
            const formData = new FormData();
            formData.append('file', audioBlob, 'recording.wav');

            const response = await fetch('/api/transcribe', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.transcription) {
                this.messageInput.value = data.transcription;
                this.sendMessage();
            }
        } catch (error) {
            console.error('Error transcribing audio:', error);
            this.showStatus('Error transcribing audio', 'error');
        }
    }

    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (!file.name.endsWith('.pdf') && !file.name.endsWith('.docx')) {
            this.showStatus('Please upload a PDF or DOCX file', 'error');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('file', file);

            this.showStatus('Uploading file...', 'success');

            const response = await fetch('/api/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                },
                body: formData
            });

            const data = await response.json();

            if (data.status === 'success') {
                this.showStatus(`File "${data.filename}" uploaded successfully!`, 'success');
                if (this.documentsOverlay.classList.contains('active')) {
                    this.loadDocuments();
                }
            } else {
                this.showStatus('Error uploading file', 'error');
            }
        } catch (error) {
            console.error('Error uploading file:', error);
            this.showStatus('Error uploading file', 'error');
        } finally {
            event.target.value = '';
        }
    }

    regenerateMessage() {
        const messages = this.chatMessages.querySelectorAll('.message.user');
        if (messages.length > 0) {
            const lastUserMessage = messages[messages.length - 1];
            const text = lastUserMessage.querySelector('.message-text').textContent;
            this.messageInput.value = text;
            this.sendMessage();
        }
    }

    showStatus(message, type = '') {
        let statusEl = document.querySelector('.status');
        if (!statusEl) {
            statusEl = document.createElement('div');
            statusEl.className = 'status';
            document.body.appendChild(statusEl);
        }
        
        statusEl.textContent = message;
        statusEl.className = `status ${type} show`;
        
            setTimeout(() => {
            statusEl.classList.remove('show');
        }, 3000);
    }

    scrollToBottom() {
        if (localStorage.getItem('auto_scroll') !== 'false') {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global reference
let victusClient;

// PWA Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/service-worker.js')
            .then((registration) => {
                console.log('Service Worker registered:', registration);
                
                // Check for updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            // New service worker available
                            if (confirm('New version available! Reload to update?')) {
                                window.location.reload();
                            }
                        }
                    });
                });
            })
            .catch((error) => {
                console.error('Service Worker registration failed:', error);
            });

        // Check for updates periodically
        setInterval(() => {
            navigator.serviceWorker.getRegistration().then((registration) => {
                if (registration) {
                    registration.update();
                }
            });
        }, 60000); // Check every minute
    });
}

// Handle PWA install prompt
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    // Show install button (you can add this to your UI)
    const installBtn = document.createElement('button');
    installBtn.textContent = 'Install VICTUS';
    installBtn.className = 'install-pwa-btn';
    installBtn.style.cssText = `
        position: fixed;
        bottom: 80px;
        right: 20px;
        padding: 12px 24px;
        background: var(--primary-gradient);
        color: white;
        border: none;
        border-radius: 25px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        z-index: 1000;
        font-family: 'DM Sans', sans-serif;
    `;
    installBtn.addEventListener('click', () => {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the install prompt');
            }
            deferredPrompt = null;
            installBtn.remove();
        });
    });
    document.body.appendChild(installBtn);
    
    // Auto-hide after 10 seconds
    setTimeout(() => {
        if (installBtn.parentNode) {
            installBtn.remove();
        }
    }, 10000);
});

// Handle PWA installed
window.addEventListener('appinstalled', () => {
    console.log('PWA installed');
    deferredPrompt = null;
});

// Prevent zoom on double tap (mobile)
let lastTouchEnd = 0;
document.addEventListener('touchend', (event) => {
    const now = Date.now();
    if (now - lastTouchEnd <= 300) {
        event.preventDefault();
    }
    lastTouchEnd = now;
}, false);

// Initialize the client when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
        localStorage.setItem('victus_token', token);
        fetch('/api/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(res => {
            if (res.ok) {
                return res.json();
            } else if (res.status === 401) {
                throw new Error('401 Unauthorized');
            } else {
                throw new Error(`Failed: ${res.status}`);
            }
        })
        .then(user => {
            if (user) {
                localStorage.setItem('victus_user', JSON.stringify(user));
                window.history.replaceState({}, document.title, '/');
                window.location.reload();
            } else {
                window.history.replaceState({}, document.title, '/');
                victusClient = new VICTUSClient();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (error.message && error.message.includes('401')) {
                localStorage.removeItem('victus_token');
                localStorage.removeItem('victus_user');
                window.history.replaceState({}, document.title, '/login');
                window.location.href = '/login';
            } else {
                window.history.replaceState({}, document.title, '/');
                victusClient = new VICTUSClient();
            }
        });
    } else {
        victusClient = new VICTUSClient();
    }
});
