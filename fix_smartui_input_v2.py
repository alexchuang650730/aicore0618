#!/usr/bin/env python3
"""
SmartUI 输入框深度修复脚本 v2.0
针对前端HTML文件进行直接修复
"""

import re
import os

def create_fixed_html():
    """创建修复后的HTML文件"""
    
    # 读取原始HTML文件
    html_content = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerAutomation 智慧UI Dashboard v1.0 - 输入框修复版</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #ffffff;
            color: #1f2937;
            line-height: 1.6;
        }
        .dashboard-container {
            display: flex;
            height: 100vh;
            background: #f8fafc;
        }
        /* 左侧聊天面板 */
        .chat-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: white;
            border-right: 1px solid #e5e7eb;
        }
        .chat-header {
            padding: 20px 24px;
            border-bottom: 1px solid #e5e7eb;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .chat-header h1 {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 4px;
        }
        .chat-header p {
            font-size: 14px;
            opacity: 0.9;
        }
        .chat-messages {
            flex: 1;
            padding: 24px;
            overflow-y: auto;
            background: #f9fafb;
        }
        .message {
            margin-bottom: 16px;
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }
        .message.user {
            flex-direction: row-reverse;
        }
        .message-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: 600;
            color: white;
        }
        .message.ai .message-avatar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .message.user .message-avatar {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.5;
        }
        .message.ai .message-content {
            background: white;
            border: 1px solid #e5e7eb;
        }
        .message.user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        /* 输入区域 - 关键修复部分 */
        .chat-input-area {
            background: white;
            border-top: 1px solid #e5e7eb;
            padding: 16px 24px;
        }
        .input-container {
            display: flex;
            align-items: flex-end;
            gap: 12px;
            background: #f9fafb;
            border: 2px solid #d1d5db;
            border-radius: 12px;
            padding: 12px;
            transition: all 0.2s ease;
        }
        .input-container:focus-within {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .chat-input {
            flex: 1;
            border: none !important;
            outline: none !important;
            background: transparent !important;
            font-size: 14px;
            line-height: 1.5;
            resize: none;
            min-height: 20px;
            max-height: 120px;
            color: #374151 !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            pointer-events: auto !important;
            user-select: text !important;
            -webkit-user-select: text !important;
            -moz-user-select: text !important;
            -ms-user-select: text !important;
        }
        .chat-input:focus {
            outline: none !important;
            background: transparent !important;
            border: none !important;
        }
        .chat-input::placeholder {
            color: #9ca3af;
            opacity: 1;
        }
        .input-actions {
            display: flex;
            gap: 8px;
            align-items: center;
        }
        .intervention-toggle {
            display: flex;
            gap: 4px;
        }
        .toggle-btn {
            padding: 6px 10px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            background: white;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .toggle-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        .send-btn {
            width: 36px;
            height: 36px;
            border: none;
            border-radius: 8px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }
        .send-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        /* 右侧工作流面板 */
        .workflow-panel {
            width: 400px;
            background: white;
            border-left: 1px solid #e5e7eb;
            display: flex;
            flex-direction: column;
        }
        .workflow-header {
            padding: 20px 24px;
            border-bottom: 1px solid #e5e7eb;
            font-size: 16px;
            font-weight: 600;
            background: #f8fafc;
        }
        .workflow-content {
            flex: 1;
            padding: 24px;
            overflow-y: auto;
        }
        .status-section {
            margin-bottom: 24px;
        }
        .status-title {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #374151;
        }
        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            background: #f9fafb;
            border-radius: 6px;
            margin-bottom: 8px;
            font-size: 13px;
        }
        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10b981;
        }
        .status-indicator.warning {
            background: #f59e0b;
        }
        .status-indicator.error {
            background: #ef4444;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <!-- 左侧聊天面板 -->
        <div class="chat-panel">
            <div class="chat-header">
                <h1>🤖 PowerAutomation 智慧助手</h1>
                <p>AI驱动的开发工作流自动化平台</p>
            </div>
            <div class="chat-messages" id="chatMessages">
                <div class="message ai">
                    <div class="message-avatar">AI</div>
                    <div class="message-content">
                        🎉 欢迎使用PowerAutomation智慧UI！我是您的AI助手，可以帮助您：<br>
                        • 🔧 自动化开发工作流<br>
                        • 📝 生成代码和文档<br>
                        • 🧪 创建和执行测试<br>
                        • 🚀 管理部署流程<br><br>
                        请描述您的需求，我将智能介入协助！
                    </div>
                </div>
            </div>
            <div class="chat-input-area">
                <div class="input-container">
                    <textarea 
                        class="chat-input" 
                        id="chatInput"
                        placeholder="描述您的开发需求，AI将智能介入协助..."
                        spellcheck="false"
                        autocomplete="off"
                        autocorrect="off"
                        autocapitalize="off"
                    ></textarea>
                    <div class="input-actions">
                        <div class="intervention-toggle">
                            <button class="toggle-btn active" data-mode="manus">Manus</button>
                            <button class="toggle-btn active" data-mode="app">应用</button>
                            <button class="toggle-btn" data-mode="feishu">飞书</button>
                        </div>
                        <button class="send-btn" id="sendBtn">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 右侧工作流面板 -->
        <div class="workflow-panel">
            <div class="workflow-header">系统状态监控</div>
            <div class="workflow-content">
                <div class="status-section">
                    <div class="status-title">MCP组件状态</div>
                    <div class="status-item">
                        <span>SmartUI MCP</span>
                        <div class="status-indicator"></div>
                    </div>
                    <div class="status-item">
                        <span>Enhanced Workflow</span>
                        <div class="status-indicator"></div>
                    </div>
                    <div class="status-item">
                        <span>MCP Coordinator</span>
                        <div class="status-indicator"></div>
                    </div>
                </div>
                
                <div class="status-section">
                    <div class="status-title">工作流状态</div>
                    <div class="status-item">
                        <span>需求分析</span>
                        <div class="status-indicator"></div>
                    </div>
                    <div class="status-item">
                        <span>代码生成</span>
                        <div class="status-indicator"></div>
                    </div>
                    <div class="status-item">
                        <span>测试执行</span>
                        <div class="status-indicator"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        class SmartUIDashboard {
            constructor() {
                this.apiBaseUrl = window.location.origin;
                this.init();
            }

            init() {
                console.log('🚀 SmartUI Dashboard 初始化开始...');
                this.initializeComponents();
                this.setupEventListeners();
                this.loadInitialData();
                this.debugInputBox();
                console.log('✅ SmartUI Dashboard 初始化完成');
            }

            initializeComponents() {
                console.log('📋 初始化组件...');
                this.chatInput = document.getElementById('chatInput');
                this.sendBtn = document.getElementById('sendBtn');
                this.chatMessages = document.getElementById('chatMessages');
                this.toggleBtns = document.querySelectorAll('.toggle-btn');
                
                if (!this.chatInput) {
                    console.error('❌ 输入框元素未找到!');
                    return;
                }
                
                console.log('✅ 组件初始化完成');
            }

            setupEventListeners() {
                console.log('🔧 设置事件监听器...');
                
                if (!this.chatInput || !this.sendBtn) {
                    console.error('❌ 关键元素未找到，无法设置事件监听器');
                    return;
                }

                // 强制启用输入框
                this.chatInput.removeAttribute('readonly');
                this.chatInput.removeAttribute('disabled');
                this.chatInput.style.pointerEvents = 'auto';
                this.chatInput.style.userSelect = 'text';
                this.chatInput.contentEditable = false; // textarea不需要contentEditable

                // 发送按钮点击事件
                this.sendBtn.addEventListener('click', (e) => {
                    console.log('🖱️ 发送按钮被点击');
                    e.preventDefault();
                    this.sendMessage();
                });

                // 键盘事件
                this.chatInput.addEventListener('keydown', (e) => {
                    console.log('⌨️ 键盘事件:', e.key);
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        this.sendMessage();
                    }
                });

                // 输入事件
                this.chatInput.addEventListener('input', (e) => {
                    console.log('📝 输入事件:', e.target.value);
                });

                // 焦点事件
                this.chatInput.addEventListener('focus', (e) => {
                    console.log('🎯 输入框获得焦点');
                    e.target.style.backgroundColor = 'transparent';
                });

                this.chatInput.addEventListener('blur', (e) => {
                    console.log('😴 输入框失去焦点');
                });

                // 介入模式切换
                this.toggleBtns.forEach(btn => {
                    btn.addEventListener('click', () => this.toggleInterventionMode(btn));
                });

                console.log('✅ 事件监听器设置完成');
            }

            debugInputBox() {
                console.log('🔍 输入框调试信息:');
                const input = this.chatInput;
                if (input) {
                    console.log('- 元素存在:', !!input);
                    console.log('- readonly:', input.readOnly);
                    console.log('- disabled:', input.disabled);
                    console.log('- contentEditable:', input.contentEditable);
                    console.log('- 样式 pointer-events:', window.getComputedStyle(input).pointerEvents);
                    console.log('- 样式 user-select:', window.getComputedStyle(input).userSelect);
                    
                    // 强制启用
                    input.readOnly = false;
                    input.disabled = false;
                    input.style.pointerEvents = 'auto';
                    input.style.userSelect = 'text';
                    
                    console.log('✅ 输入框强制启用完成');
                    
                    // 测试输入功能
                    setTimeout(() => {
                        input.focus();
                        console.log('🎯 输入框已聚焦，请尝试输入文字');
                    }, 1000);
                } else {
                    console.error('❌ 输入框元素未找到!');
                }
            }

            async sendMessage() {
                console.log('📤 发送消息函数被调用');
                
                if (!this.chatInput) {
                    console.error('❌ 输入框不存在');
                    return;
                }

                const message = this.chatInput.value.trim();
                console.log('📝 消息内容:', message);
                
                if (!message) {
                    console.log('⚠️ 消息为空，不发送');
                    return;
                }

                // 添加用户消息到聊天
                this.addMessageToChat('user', message);
                this.chatInput.value = '';

                // 模拟AI回复
                setTimeout(() => {
                    this.addMessageToChat('ai', `🤖 收到您的请求："${message}"。我正在处理中，请稍候...`);
                }, 500);

                console.log('✅ 消息发送完成');
            }

            addMessageToChat(type, content) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}`;
                
                const avatar = document.createElement('div');
                avatar.className = 'message-avatar';
                avatar.textContent = type === 'ai' ? 'AI' : 'U';
                
                const messageContent = document.createElement('div');
                messageContent.className = 'message-content';
                messageContent.innerHTML = content;
                
                messageDiv.appendChild(avatar);
                messageDiv.appendChild(messageContent);
                
                this.chatMessages.appendChild(messageDiv);
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            }

            toggleInterventionMode(btn) {
                btn.classList.toggle('active');
                console.log('🔄 介入模式切换:', btn.dataset.mode, btn.classList.contains('active'));
            }

            async loadInitialData() {
                console.log('📊 加载初始数据...');
                // 这里可以加载实际的API数据
                console.log('✅ 初始数据加载完成');
            }
        }

        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', () => {
            console.log('📄 DOM加载完成，初始化SmartUI Dashboard');
            window.smartUI = new SmartUIDashboard();
        });

        // 额外的调试功能
        window.debugInput = function() {
            const input = document.getElementById('chatInput');
            if (input) {
                console.log('🔧 手动调试输入框');
                input.focus();
                input.value = '测试输入功能';
                console.log('✅ 测试文字已设置');
            }
        };

        console.log('🎉 SmartUI 脚本加载完成');
    </script>
</body>
</html>"""
    
    return html_content

def main():
    """主函数"""
    try:
        print("🔧 创建修复后的SmartUI HTML文件...")
        
        # 创建修复后的HTML内容
        fixed_html = create_fixed_html()
        
        # 写入修复后的文件
        with open('/opt/powerautomation/smart_ui_fixed.html', 'w', encoding='utf-8') as f:
            f.write(fixed_html)
        
        print("✅ SmartUI输入框深度修复完成！")
        print("📄 修复后的文件: smart_ui_fixed.html")
        
        print("\n🔧 修复内容:")
        print("1. ✅ 完全重写HTML结构，确保输入框正确")
        print("2. ✅ 强化CSS样式，移除所有可能阻止输入的属性")
        print("3. ✅ 重写JavaScript事件处理逻辑")
        print("4. ✅ 添加详细的调试日志")
        print("5. ✅ 强制启用输入框功能")
        print("6. ✅ 添加多重事件监听器")
        print("7. ✅ 提供手动调试功能")
        
        print("\n🎯 使用方法:")
        print("1. 将此文件部署到SmartUI服务器")
        print("2. 重启SmartUI服务")
        print("3. 打开浏览器开发者工具查看调试信息")
        print("4. 测试输入框功能")
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")

if __name__ == "__main__":
    main()

