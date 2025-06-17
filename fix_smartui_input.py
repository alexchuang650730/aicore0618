#!/usr/bin/env python3
"""
SmartUI MCP 输入框修复脚本
修复输入框无法输入文字的问题
"""

import re

def fix_smartui_input():
    """修复SmartUI输入框问题"""
    
    # 读取原始文件
    with open('/opt/powerautomation/mcp/adapter/smartui_mcp/api_server.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复1: 确保textarea没有readonly或disabled属性
    content = re.sub(
        r'<textarea([^>]*?)(?:readonly|disabled)([^>]*?)>',
        r'<textarea\1\2>',
        content,
        flags=re.IGNORECASE
    )
    
    # 修复2: 确保CSS没有pointer-events: none
    content = re.sub(
        r'\.chat-input\s*\{([^}]*?)pointer-events:\s*none;?([^}]*?)\}',
        r'.chat-input {\1\2}',
        content,
        flags=re.IGNORECASE | re.DOTALL
    )
    
    # 修复3: 添加明确的可编辑属性
    content = re.sub(
        r'<textarea class="chat-input"([^>]*?)>',
        r'<textarea class="chat-input" contenteditable="true" spellcheck="false"\1>',
        content
    )
    
    # 修复4: 确保CSS样式支持输入
    css_fix = """
        .chat-input {
            flex: 1;
            border: none;
            outline: none;
            background: transparent;
            font-size: 14px;
            line-height: 1.5;
            resize: none;
            min-height: 20px;
            max-height: 120px;
            color: #374151;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            pointer-events: auto;
            user-select: text;
            -webkit-user-select: text;
            -moz-user-select: text;
            -ms-user-select: text;
        }
        .chat-input:focus {
            outline: none;
            background: transparent;
        }
        .chat-input::placeholder {
            color: #9ca3af;
            opacity: 1;
        }"""
    
    # 替换原有的chat-input CSS
    content = re.sub(
        r'\.chat-input\s*\{[^}]*\}',
        css_fix,
        content,
        flags=re.DOTALL
    )
    
    # 修复5: 确保JavaScript事件监听器正确绑定
    js_fix = """
            setupEventListeners() {
                // 确保输入框元素存在
                this.chatInput = document.querySelector('.chat-input');
                this.sendBtn = document.querySelector('.send-btn');
                
                if (!this.chatInput) {
                    console.error('Chat input element not found!');
                    return;
                }
                
                // 移除可能的禁用属性
                this.chatInput.removeAttribute('readonly');
                this.chatInput.removeAttribute('disabled');
                this.chatInput.style.pointerEvents = 'auto';
                this.chatInput.style.userSelect = 'text';
                
                // 发送消息事件
                if (this.sendBtn) {
                    this.sendBtn.addEventListener('click', () => this.sendMessage());
                }
                
                // 键盘事件
                this.chatInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        this.sendMessage();
                    }
                });
                
                // 输入事件
                this.chatInput.addEventListener('input', (e) => {
                    console.log('Input detected:', e.target.value);
                });
                
                // 焦点事件
                this.chatInput.addEventListener('focus', (e) => {
                    console.log('Input focused');
                    e.target.style.backgroundColor = 'transparent';
                });
                
                // 介入模式切换
                this.toggleBtns = document.querySelectorAll('.toggle-btn');
                this.toggleBtns.forEach(btn => {
                    btn.addEventListener('click', () => this.toggleInterventionMode(btn));
                });
                
                // 工作流节点点击
                document.querySelectorAll('.workflow-node').forEach(node => {
                    node.addEventListener('click', () => this.selectWorkflowNode(node));
                });
                
                console.log('Event listeners setup completed');
            }"""
    
    # 替换原有的setupEventListeners方法
    content = re.sub(
        r'setupEventListeners\(\)\s*\{[^}]*?\n\s*\}',
        js_fix,
        content,
        flags=re.DOTALL
    )
    
    # 修复6: 添加输入框调试功能
    debug_js = """
            // 输入框调试功能
            debugInputBox() {
                const input = document.querySelector('.chat-input');
                if (input) {
                    console.log('Input element found:', input);
                    console.log('Input readonly:', input.readOnly);
                    console.log('Input disabled:', input.disabled);
                    console.log('Input style:', window.getComputedStyle(input));
                    
                    // 强制启用输入
                    input.readOnly = false;
                    input.disabled = false;
                    input.style.pointerEvents = 'auto';
                    input.style.userSelect = 'text';
                    input.contentEditable = true;
                    
                    console.log('Input box forcibly enabled');
                } else {
                    console.error('Input element not found!');
                }
            }"""
    
    # 在class结束前添加调试方法
    content = re.sub(
        r'(\s+)(}\s*</script>)',
        r'\1' + debug_js + r'\n\1\2',
        content
    )
    
    # 修复7: 在初始化时调用调试功能
    content = re.sub(
        r'(this\.setupEventListeners\(\);)',
        r'\1\n                this.debugInputBox();',
        content
    )
    
    return content

if __name__ == "__main__":
    try:
        fixed_content = fix_smartui_input()
        
        # 写入修复后的文件
        with open('/opt/powerautomation/mcp/adapter/smartui_mcp/api_server_fixed.py', 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("✅ SmartUI输入框修复完成！")
        print("📄 修复后的文件: api_server_fixed.py")
        print("📄 原始备份文件: api_server_backup.py")
        
        print("\n🔧 修复内容:")
        print("1. 移除textarea的readonly/disabled属性")
        print("2. 修复CSS pointer-events问题")
        print("3. 添加明确的可编辑属性")
        print("4. 优化CSS样式支持输入")
        print("5. 增强JavaScript事件监听器")
        print("6. 添加输入框调试功能")
        print("7. 强制启用输入功能")
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")

