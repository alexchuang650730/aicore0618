/**
 * Human-in-the-Loop 交互界面主脚本
 * 处理WebSocket通信、UI交互和会话管理
 */

class HumanLoopClient {
    constructor() {
        this.apiBase = '/api';
        this.socket = null;
        this.activeSessions = new Map();
        this.currentSession = null;
        
        // DOM元素
        this.elements = {
            connectionStatus: document.getElementById('connectionStatus'),
            sessionList: document.getElementById('sessionList'),
            interactionPanel: document.getElementById('interactionPanel'),
            welcomeScreen: document.getElementById('welcomeScreen'),
            interactionContent: document.getElementById('interactionContent'),
            notificationContainer: document.getElementById('notificationContainer'),
            modalOverlay: document.getElementById('modalOverlay'),
            modalTitle: document.getElementById('modalTitle'),
            modalBody: document.getElementById('modalBody'),
            modalFooter: document.getElementById('modalFooter'),
            modalClose: document.getElementById('modalClose'),
            statsGrid: document.getElementById('statsGrid'),
            activeSessions: document.getElementById('activeSessions'),
            totalSessions: document.getElementById('totalSessions'),
            completedSessions: document.getElementById('completedSessions')
        };
        
        this.init();
    }
    
    async init() {
        console.log('初始化Human-in-the-Loop客户端...');
        
        // 初始化WebSocket连接
        this.initWebSocket();
        
        // 绑定事件监听器
        this.bindEventListeners();
        
        // 加载初始数据
        await this.loadInitialData();
        
        console.log('客户端初始化完成');
    }
    
    initWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}`;
        
        this.socket = io(wsUrl);
        
        this.socket.on('connect', () => {
            console.log('WebSocket连接成功');
            this.updateConnectionStatus('connected', '已连接');
        });
        
        this.socket.on('disconnect', () => {
            console.log('WebSocket连接断开');
            this.updateConnectionStatus('disconnected', '连接断开');
        });
        
        this.socket.on('new_session', (sessionData) => {
            console.log('收到新会话:', sessionData);
            this.handleNewSession(sessionData);
        });
        
        this.socket.on('session_completed', (data) => {
            console.log('会话已完成:', data);
            this.handleSessionCompleted(data);
        });
        
        this.socket.on('session_cancelled', (data) => {
            console.log('会话已取消:', data);
            this.handleSessionCancelled(data);
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('WebSocket连接错误:', error);
            this.updateConnectionStatus('disconnected', '连接失败');
        });
    }
    
    bindEventListeners() {
        // 模态框关闭
        this.elements.modalClose.addEventListener('click', () => {
            this.hideModal();
        });
        
        this.elements.modalOverlay.addEventListener('click', (e) => {
            if (e.target === this.elements.modalOverlay) {
                this.hideModal();
            }
        });
        
        // 键盘事件
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideModal();
            }
        });
    }
    
    async loadInitialData() {
        try {
            // 加载活跃会话
            await this.loadActiveSessions();
            
            // 加载统计信息
            await this.loadStatistics();
            
        } catch (error) {
            console.error('加载初始数据失败:', error);
            this.showNotification('加载数据失败', 'error');
        }
    }
    
    async loadActiveSessions() {
        try {
            const response = await fetch(`${this.apiBase}/sessions`);
            const data = await response.json();
            
            if (data.success) {
                this.activeSessions.clear();
                data.sessions.forEach(session => {
                    this.activeSessions.set(session.session_id, session);
                });
                this.renderSessionList();
            }
        } catch (error) {
            console.error('加载会话列表失败:', error);
        }
    }
    
    async loadStatistics() {
        try {
            const response = await fetch(`${this.apiBase}/statistics`);
            const data = await response.json();
            
            if (data.success) {
                this.updateStatistics(data.statistics);
            }
        } catch (error) {
            console.error('加载统计信息失败:', error);
        }
    }
    
    updateConnectionStatus(status, text) {
        const statusDot = this.elements.connectionStatus.querySelector('.status-dot');
        const statusText = this.elements.connectionStatus.querySelector('.status-text');
        
        statusDot.className = `status-dot ${status}`;
        statusText.textContent = text;
    }
    
    updateStatistics(stats) {
        this.elements.activeSessions.textContent = stats.active_sessions || 0;
        this.elements.totalSessions.textContent = stats.total_sessions || 0;
        this.elements.completedSessions.textContent = stats.completed_sessions || 0;
    }
    
    handleNewSession(sessionData) {
        this.activeSessions.set(sessionData.session_id, sessionData);
        this.renderSessionList();
        this.showNotification('收到新的交互请求', 'info');
        
        // 如果当前没有显示会话，自动显示新会话
        if (!this.currentSession) {
            this.showSession(sessionData.session_id);
        }
    }
    
    handleSessionCompleted(data) {
        if (this.activeSessions.has(data.session_id)) {
            this.activeSessions.delete(data.session_id);
            this.renderSessionList();
            
            if (this.currentSession && this.currentSession.session_id === data.session_id) {
                this.showWelcomeScreen();
                this.currentSession = null;
            }
            
            this.showNotification('会话已完成', 'success');
        }
    }
    
    handleSessionCancelled(data) {
        if (this.activeSessions.has(data.session_id)) {
            this.activeSessions.delete(data.session_id);
            this.renderSessionList();
            
            if (this.currentSession && this.currentSession.session_id === data.session_id) {
                this.showWelcomeScreen();
                this.currentSession = null;
            }
            
            this.showNotification(`会话已取消: ${data.reason}`, 'warning');
        }
    }
    
    renderSessionList() {
        const sessionList = this.elements.sessionList;
        
        if (this.activeSessions.size === 0) {
            sessionList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <p>暂无活跃会话</p>
                </div>
            `;
            return;
        }
        
        const sessionsHtml = Array.from(this.activeSessions.values())
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
            .map(session => this.renderSessionItem(session))
            .join('');
        
        sessionList.innerHTML = sessionsHtml;
    }
    
    renderSessionItem(session) {
        const isActive = this.currentSession && this.currentSession.session_id === session.session_id;
        const createdAt = new Date(session.created_at);
        const timeAgo = this.getTimeAgo(createdAt);
        
        return `
            <div class="session-item ${isActive ? 'active' : ''}" 
                 onclick="humanLoopClient.showSession('${session.session_id}')">
                <div class="session-header">
                    <div class="session-title">${this.escapeHtml(session.interaction_data.title)}</div>
                    <div class="session-status ${session.status}">${this.getStatusText(session.status)}</div>
                </div>
                <div class="session-message">${this.escapeHtml(session.interaction_data.message)}</div>
                <div class="session-time">${timeAgo}</div>
            </div>
        `;
    }
    
    async showSession(sessionId) {
        try {
            const session = this.activeSessions.get(sessionId);
            if (!session) {
                console.error('会话不存在:', sessionId);
                return;
            }
            
            this.currentSession = session;
            this.renderSessionList(); // 更新选中状态
            
            // 隐藏欢迎屏幕，显示交互内容
            this.elements.welcomeScreen.style.display = 'none';
            this.elements.interactionContent.style.display = 'block';
            
            // 渲染交互界面
            this.renderInteractionContent(session);
            
        } catch (error) {
            console.error('显示会话失败:', error);
            this.showNotification('显示会话失败', 'error');
        }
    }
    
    showWelcomeScreen() {
        this.elements.welcomeScreen.style.display = 'flex';
        this.elements.interactionContent.style.display = 'none';
        this.currentSession = null;
        this.renderSessionList(); // 更新选中状态
    }
    
    renderInteractionContent(session) {
        const interactionData = session.interaction_data;
        let contentHtml = '';
        
        switch (interactionData.interaction_type) {
            case 'confirmation':
                contentHtml = this.renderConfirmationInteraction(session);
                break;
            case 'selection':
                contentHtml = this.renderSelectionInteraction(session);
                break;
            case 'text_input':
                contentHtml = this.renderTextInputInteraction(session);
                break;
            case 'file_upload':
                contentHtml = this.renderFileUploadInteraction(session);
                break;
            default:
                contentHtml = this.renderCustomInteraction(session);
        }
        
        this.elements.interactionContent.innerHTML = contentHtml;
    }
    
    renderConfirmationInteraction(session) {
        const data = session.interaction_data;
        const options = data.options || [
            {value: 'confirm', label: '确认'},
            {value: 'cancel', label: '取消'}
        ];
        
        return `
            <div class="interaction-card">
                <div class="interaction-header">
                    <h2 class="interaction-title">${this.escapeHtml(data.title)}</h2>
                    <p class="interaction-message">${this.escapeHtml(data.message)}</p>
                </div>
                <div class="interaction-footer">
                    ${options.map(option => `
                        <button class="btn ${option.value === 'confirm' ? 'btn-primary' : 'btn-secondary'}"
                                onclick="humanLoopClient.submitResponse('${session.session_id}', {choice: '${option.value}'})">
                            ${this.escapeHtml(option.label)}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    renderSelectionInteraction(session) {
        const data = session.interaction_data;
        const inputType = data.multiple ? 'checkbox' : 'radio';
        const inputName = `selection_${session.session_id}`;
        
        return `
            <div class="interaction-card">
                <div class="interaction-header">
                    <h2 class="interaction-title">${this.escapeHtml(data.title)}</h2>
                    <p class="interaction-message">${this.escapeHtml(data.message)}</p>
                </div>
                <div class="interaction-body">
                    <form id="selectionForm_${session.session_id}">
                        <div class="options-group">
                            ${data.options.map((option, index) => `
                                <div class="option-item">
                                    <input type="${inputType}" 
                                           id="${inputName}_${index}"
                                           name="${inputName}"
                                           value="${option.value}"
                                           class="option-${inputType}">
                                    <label for="${inputName}_${index}" class="option-label">
                                        ${this.escapeHtml(option.label)}
                                    </label>
                                </div>
                            `).join('')}
                        </div>
                    </form>
                </div>
                <div class="interaction-footer">
                    <button class="btn btn-secondary" 
                            onclick="humanLoopClient.cancelSession('${session.session_id}')">
                        取消
                    </button>
                    <button class="btn btn-primary" 
                            onclick="humanLoopClient.submitSelectionResponse('${session.session_id}')">
                        提交
                    </button>
                </div>
            </div>
        `;
    }
    
    renderTextInputInteraction(session) {
        const data = session.interaction_data;
        
        return `
            <div class="interaction-card">
                <div class="interaction-header">
                    <h2 class="interaction-title">${this.escapeHtml(data.title)}</h2>
                    <p class="interaction-message">${this.escapeHtml(data.message)}</p>
                </div>
                <div class="interaction-body">
                    <form id="textInputForm_${session.session_id}">
                        ${data.fields.map(field => this.renderFormField(field)).join('')}
                    </form>
                </div>
                <div class="interaction-footer">
                    <button class="btn btn-secondary" 
                            onclick="humanLoopClient.cancelSession('${session.session_id}')">
                        取消
                    </button>
                    <button class="btn btn-primary" 
                            onclick="humanLoopClient.submitTextInputResponse('${session.session_id}')">
                        提交
                    </button>
                </div>
            </div>
        `;
    }
    
    renderFormField(field) {
        let inputHtml = '';
        
        switch (field.field_type) {
            case 'textarea':
                inputHtml = `
                    <textarea class="form-input form-textarea" 
                              name="${field.name}" 
                              ${field.required ? 'required' : ''}
                              placeholder="${field.label}">${field.default || ''}</textarea>
                `;
                break;
            case 'select':
                inputHtml = `
                    <select class="form-input form-select" 
                            name="${field.name}" 
                            ${field.required ? 'required' : ''}>
                        <option value="">请选择...</option>
                        ${field.options.map(option => `
                            <option value="${option.value}" 
                                    ${option.value === field.default ? 'selected' : ''}>
                                ${this.escapeHtml(option.label)}
                            </option>
                        `).join('')}
                    </select>
                `;
                break;
            default:
                inputHtml = `
                    <input type="${field.field_type}" 
                           class="form-input" 
                           name="${field.name}" 
                           ${field.required ? 'required' : ''}
                           ${field.min_value !== undefined ? `min="${field.min_value}"` : ''}
                           ${field.max_value !== undefined ? `max="${field.max_value}"` : ''}
                           ${field.validation ? `pattern="${field.validation}"` : ''}
                           value="${field.default || ''}"
                           placeholder="${field.label}">
                `;
        }
        
        return `
            <div class="form-group">
                <label class="form-label">
                    ${this.escapeHtml(field.label)}
                    ${field.required ? '<span style="color: var(--error-color);">*</span>' : ''}
                </label>
                ${inputHtml}
            </div>
        `;
    }
    
    renderFileUploadInteraction(session) {
        const data = session.interaction_data;
        
        return `
            <div class="interaction-card">
                <div class="interaction-header">
                    <h2 class="interaction-title">${this.escapeHtml(data.title)}</h2>
                    <p class="interaction-message">${this.escapeHtml(data.message)}</p>
                </div>
                <div class="interaction-body">
                    <form id="fileUploadForm_${session.session_id}">
                        <div class="form-group">
                            <label class="form-label">选择文件</label>
                            <input type="file" 
                                   class="form-input" 
                                   name="files"
                                   ${data.multiple ? 'multiple' : ''}
                                   ${data.accept_types ? `accept="${data.accept_types.join(',')}"` : ''}>
                            <small style="color: var(--text-secondary);">
                                ${data.accept_types ? `支持格式: ${data.accept_types.join(', ')}` : ''}
                                ${data.max_file_size ? ` | 最大大小: ${data.max_file_size}` : ''}
                            </small>
                        </div>
                    </form>
                </div>
                <div class="interaction-footer">
                    <button class="btn btn-secondary" 
                            onclick="humanLoopClient.cancelSession('${session.session_id}')">
                        取消
                    </button>
                    <button class="btn btn-primary" 
                            onclick="humanLoopClient.submitFileUploadResponse('${session.session_id}')">
                        上传
                    </button>
                </div>
            </div>
        `;
    }
    
    renderCustomInteraction(session) {
        const data = session.interaction_data;
        
        return `
            <div class="interaction-card">
                <div class="interaction-header">
                    <h2 class="interaction-title">${this.escapeHtml(data.title)}</h2>
                    <p class="interaction-message">${this.escapeHtml(data.message)}</p>
                </div>
                <div class="interaction-body">
                    <p>自定义交互类型，请联系管理员。</p>
                </div>
                <div class="interaction-footer">
                    <button class="btn btn-secondary" 
                            onclick="humanLoopClient.cancelSession('${session.session_id}')">
                        取消
                    </button>
                </div>
            </div>
        `;
    }
    
    async submitResponse(sessionId, responseData) {
        try {
            const response = await fetch(`${this.apiBase}/sessions/${sessionId}/respond`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    response: responseData,
                    user_id: 'current_user' // TODO: 实际的用户ID
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('响应已提交', 'success');
            } else {
                this.showNotification(`提交失败: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('提交响应失败:', error);
            this.showNotification('提交失败', 'error');
        }
    }
    
    async submitSelectionResponse(sessionId) {
        const form = document.getElementById(`selectionForm_${sessionId}`);
        const formData = new FormData(form);
        const session = this.activeSessions.get(sessionId);
        
        let selectedValues = [];
        if (session.interaction_data.multiple) {
            selectedValues = formData.getAll(`selection_${sessionId}`);
        } else {
            const value = formData.get(`selection_${sessionId}`);
            if (value) selectedValues = [value];
        }
        
        if (selectedValues.length === 0) {
            this.showNotification('请选择至少一个选项', 'warning');
            return;
        }
        
        await this.submitResponse(sessionId, {
            selection: session.interaction_data.multiple ? selectedValues : selectedValues[0]
        });
    }
    
    async submitTextInputResponse(sessionId) {
        const form = document.getElementById(`textInputForm_${sessionId}`);
        const formData = new FormData(form);
        
        // 验证表单
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const responseData = {};
        for (const [key, value] of formData.entries()) {
            responseData[key] = value;
        }
        
        await this.submitResponse(sessionId, responseData);
    }
    
    async submitFileUploadResponse(sessionId) {
        const form = document.getElementById(`fileUploadForm_${sessionId}`);
        const fileInput = form.querySelector('input[type="file"]');
        
        if (!fileInput.files.length) {
            this.showNotification('请选择文件', 'warning');
            return;
        }
        
        // TODO: 实现文件上传逻辑
        this.showNotification('文件上传功能待实现', 'info');
    }
    
    async cancelSession(sessionId) {
        try {
            const response = await fetch(`${this.apiBase}/sessions/${sessionId}/cancel`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    reason: '用户取消'
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('会话已取消', 'info');
            } else {
                this.showNotification(`取消失败: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('取消会话失败:', error);
            this.showNotification('取消失败', 'error');
        }
    }
    
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icon = this.getNotificationIcon(type);
        notification.innerHTML = `
            <i class="${icon}"></i>
            <span>${this.escapeHtml(message)}</span>
        `;
        
        this.elements.notificationContainer.appendChild(notification);
        
        // 自动移除
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, duration);
    }
    
    getNotificationIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }
    
    showModal(title, content, buttons = []) {
        this.elements.modalTitle.textContent = title;
        this.elements.modalBody.innerHTML = content;
        
        this.elements.modalFooter.innerHTML = buttons.map(button => `
            <button class="btn ${button.class || 'btn-secondary'}" 
                    onclick="${button.onclick || 'humanLoopClient.hideModal()'}">
                ${this.escapeHtml(button.text)}
            </button>
        `).join('');
        
        this.elements.modalOverlay.style.display = 'flex';
    }
    
    hideModal() {
        this.elements.modalOverlay.style.display = 'none';
    }
    
    getStatusText(status) {
        const statusTexts = {
            pending: '等待中',
            active: '进行中',
            completed: '已完成',
            timeout: '已超时',
            cancelled: '已取消',
            error: '错误'
        };
        return statusTexts[status] || status;
    }
    
    getTimeAgo(date) {
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return '刚刚';
        if (minutes < 60) return `${minutes}分钟前`;
        if (hours < 24) return `${hours}小时前`;
        return `${days}天前`;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// 全局实例
let humanLoopClient;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    humanLoopClient = new HumanLoopClient();
});

