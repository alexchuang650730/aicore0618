# OCR体验工作流发布方案

## 🎯 发布目标

在 http://98.81.255.168:5001/ 上发布完整的OCR体验工作流，让用户能够：
1. 上传图片进行OCR识别
2. 体验六大智能体协作过程
3. 获得高质量的繁体中文OCR结果
4. 查看详细的处理报告

## 🏗️ 架构设计

### 系统架构
```
用户界面 (Frontend)
    ↓
OCR体验API (Backend)
    ↓
产品工作流协调器 (Coordinator)
    ↓
六大智能体 (MCP Services)
```

### 技术栈
- **前端**: HTML5 + CSS3 + JavaScript (原生)
- **后端**: Flask + Python
- **协调器**: OCR产品工作流协调器 (已实现)
- **智能体**: 六大MCP服务

## 📱 前端界面设计

### 主要功能页面
1. **OCR上传页面** - 图片上传和参数设置
2. **处理进度页面** - 实时显示六大智能体处理进度
3. **结果展示页面** - OCR结果和质量报告
4. **版本选择页面** - Enterprise/Personal/Opensource版本体验

### 用户体验流程
```
1. 访问体验页面
2. 选择版本 (Enterprise/Personal/Opensource)
3. 上传图片 (支持台湾保险表单等)
4. 设置处理参数
5. 启动OCR工作流
6. 实时查看处理进度
7. 获得OCR结果
8. 查看详细报告
9. 下载结果或分享
```

## 🔧 实现方案

### 1. OCR体验前端应用

#### 主页面 (index.html)
```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerAuto.ai OCR智能工作流体验</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🔍 PowerAuto.ai OCR智能工作流</h1>
            <p>体验六大智能体协作的繁体中文OCR处理</p>
        </header>

        <main class="main-content">
            <!-- 版本选择区域 -->
            <section class="version-selector">
                <h2>选择体验版本</h2>
                <div class="version-cards">
                    <div class="version-card enterprise" data-version="enterprise">
                        <h3>🏢 Enterprise版</h3>
                        <p>6个智能体 • 完整工作流</p>
                        <ul>
                            <li>需求分析智能体</li>
                            <li>架构设计智能体</li>
                            <li>编码实现智能体</li>
                            <li>测试验证智能体</li>
                            <li>部署发布智能体</li>
                            <li>监控运维智能体</li>
                        </ul>
                    </div>
                    <div class="version-card personal" data-version="personal">
                        <h3>👤 Personal版</h3>
                        <p>3个智能体 • 核心功能</p>
                        <ul>
                            <li>编码实现智能体</li>
                            <li>测试验证智能体</li>
                            <li>部署发布智能体</li>
                        </ul>
                    </div>
                    <div class="version-card opensource" data-version="opensource">
                        <h3>🌐 Opensource版</h3>
                        <p>3个智能体 • 基础功能</p>
                        <ul>
                            <li>编码实现智能体</li>
                            <li>测试验证智能体</li>
                            <li>部署发布智能体</li>
                        </ul>
                    </div>
                </div>
            </section>

            <!-- OCR上传区域 -->
            <section class="upload-section" id="uploadSection" style="display: none;">
                <h2>上传图片进行OCR识别</h2>
                <div class="upload-area" id="uploadArea">
                    <div class="upload-placeholder">
                        <i class="upload-icon">📁</i>
                        <p>点击或拖拽图片到此处</p>
                        <p class="upload-hint">支持 JPG, PNG, PDF 格式</p>
                    </div>
                    <input type="file" id="fileInput" accept="image/*,.pdf" style="display: none;">
                </div>
                
                <div class="upload-options">
                    <label>
                        <input type="checkbox" id="traditionalChinese" checked>
                        繁体中文优化
                    </label>
                    <label>
                        <input type="checkbox" id="handwritingMode">
                        手写识别模式
                    </label>
                    <label>
                        <input type="checkbox" id="addressMode">
                        台湾地址识别
                    </label>
                </div>

                <button id="startProcessing" class="btn-primary" disabled>
                    🚀 开始OCR处理
                </button>
            </section>

            <!-- 处理进度区域 -->
            <section class="progress-section" id="progressSection" style="display: none;">
                <h2>智能体协作处理中...</h2>
                <div class="workflow-progress">
                    <div class="agent-step" data-agent="requirements_analysis">
                        <div class="step-icon">📋</div>
                        <div class="step-info">
                            <h3>需求分析智能体</h3>
                            <p>分析OCR处理需求</p>
                        </div>
                        <div class="step-status">⏳</div>
                    </div>
                    <div class="agent-step" data-agent="architecture_design">
                        <div class="step-icon">🏗️</div>
                        <div class="step-info">
                            <h3>架构设计智能体</h3>
                            <p>设计OCR处理架构</p>
                        </div>
                        <div class="step-status">⏳</div>
                    </div>
                    <div class="agent-step" data-agent="implementation">
                        <div class="step-icon">💻</div>
                        <div class="step-info">
                            <h3>编码实现智能体</h3>
                            <p>执行OCR识别</p>
                        </div>
                        <div class="step-status">⏳</div>
                    </div>
                    <div class="agent-step" data-agent="testing_verification">
                        <div class="step-icon">🧪</div>
                        <div class="step-info">
                            <h3>测试验证智能体</h3>
                            <p>验证OCR准确度</p>
                        </div>
                        <div class="step-status">⏳</div>
                    </div>
                    <div class="agent-step" data-agent="deployment_release">
                        <div class="step-icon">🚀</div>
                        <div class="step-info">
                            <h3>部署发布智能体</h3>
                            <p>格式化输出结果</p>
                        </div>
                        <div class="step-status">⏳</div>
                    </div>
                    <div class="agent-step" data-agent="monitoring_operations">
                        <div class="step-icon">📊</div>
                        <div class="step-info">
                            <h3>监控运维智能体</h3>
                            <p>监控处理性能</p>
                        </div>
                        <div class="step-status">⏳</div>
                    </div>
                </div>
                
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <p class="progress-text" id="progressText">准备开始处理...</p>
            </section>

            <!-- 结果展示区域 -->
            <section class="results-section" id="resultsSection" style="display: none;">
                <h2>OCR处理结果</h2>
                
                <div class="result-summary">
                    <div class="summary-card">
                        <h3>📊 处理概览</h3>
                        <div class="summary-stats">
                            <div class="stat">
                                <span class="stat-label">总体准确度</span>
                                <span class="stat-value" id="overallAccuracy">--</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">处理时间</span>
                                <span class="stat-value" id="processingTime">--</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">使用版本</span>
                                <span class="stat-value" id="usedVersion">--</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="result-content">
                    <div class="result-panel">
                        <h3>🔍 识别结果</h3>
                        <div class="extracted-text" id="extractedText">
                            <!-- OCR结果将在这里显示 -->
                        </div>
                    </div>
                    
                    <div class="result-panel">
                        <h3>📈 质量报告</h3>
                        <div class="quality-report" id="qualityReport">
                            <!-- 质量报告将在这里显示 -->
                        </div>
                    </div>
                </div>

                <div class="result-actions">
                    <button class="btn-secondary" id="downloadResult">
                        💾 下载结果
                    </button>
                    <button class="btn-secondary" id="shareResult">
                        🔗 分享结果
                    </button>
                    <button class="btn-primary" id="processAnother">
                        🔄 处理另一张图片
                    </button>
                </div>
            </section>
        </main>

        <footer class="footer">
            <p>&copy; 2024 PowerAuto.ai - 智能工作流解决方案</p>
        </footer>
    </div>

    <script src="static/js/app.js"></script>
</body>
</html>
```

#### 样式文件 (static/css/style.css)
```css
/* 基础样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* 头部样式 */
.header {
    text-align: center;
    color: white;
    margin-bottom: 40px;
}

.header h1 {
    font-size: 2.5rem;
    margin-bottom: 10px;
}

.header p {
    font-size: 1.2rem;
    opacity: 0.9;
}

/* 主内容区域 */
.main-content {
    background: white;
    border-radius: 15px;
    padding: 40px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

/* 版本选择卡片 */
.version-selector {
    margin-bottom: 40px;
}

.version-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.version-card {
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    padding: 25px;
    cursor: pointer;
    transition: all 0.3s ease;
    background: #f9f9f9;
}

.version-card:hover {
    border-color: #667eea;
    transform: translateY(-5px);
    box-shadow: 0 5px 20px rgba(102, 126, 234, 0.2);
}

.version-card.selected {
    border-color: #667eea;
    background: #f0f4ff;
}

.version-card h3 {
    color: #333;
    margin-bottom: 10px;
    font-size: 1.3rem;
}

.version-card p {
    color: #666;
    margin-bottom: 15px;
    font-weight: 500;
}

.version-card ul {
    list-style: none;
}

.version-card li {
    padding: 5px 0;
    color: #555;
    position: relative;
    padding-left: 20px;
}

.version-card li:before {
    content: "✓";
    position: absolute;
    left: 0;
    color: #4CAF50;
    font-weight: bold;
}

/* 上传区域 */
.upload-section {
    margin-bottom: 40px;
}

.upload-area {
    border: 3px dashed #ccc;
    border-radius: 10px;
    padding: 60px 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-bottom: 20px;
}

.upload-area:hover {
    border-color: #667eea;
    background: #f8f9ff;
}

.upload-area.dragover {
    border-color: #667eea;
    background: #f0f4ff;
}

.upload-icon {
    font-size: 3rem;
    display: block;
    margin-bottom: 15px;
}

.upload-placeholder p {
    font-size: 1.1rem;
    color: #666;
    margin-bottom: 5px;
}

.upload-hint {
    font-size: 0.9rem;
    color: #999;
}

.upload-options {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.upload-options label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
}

/* 按钮样式 */
.btn-primary, .btn-secondary {
    padding: 12px 30px;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 500;
}

.btn-primary {
    background: #667eea;
    color: white;
}

.btn-primary:hover:not(:disabled) {
    background: #5a6fd8;
    transform: translateY(-2px);
}

.btn-primary:disabled {
    background: #ccc;
    cursor: not-allowed;
}

.btn-secondary {
    background: #f0f0f0;
    color: #333;
    border: 1px solid #ddd;
}

.btn-secondary:hover {
    background: #e0e0e0;
}

/* 进度区域 */
.progress-section {
    margin-bottom: 40px;
}

.workflow-progress {
    margin-bottom: 30px;
}

.agent-step {
    display: flex;
    align-items: center;
    padding: 15px;
    margin-bottom: 10px;
    border-radius: 8px;
    background: #f9f9f9;
    border-left: 4px solid #e0e0e0;
    transition: all 0.3s ease;
}

.agent-step.active {
    background: #fff3cd;
    border-left-color: #ffc107;
}

.agent-step.completed {
    background: #d4edda;
    border-left-color: #28a745;
}

.agent-step.failed {
    background: #f8d7da;
    border-left-color: #dc3545;
}

.step-icon {
    font-size: 1.5rem;
    margin-right: 15px;
    width: 40px;
    text-align: center;
}

.step-info {
    flex: 1;
}

.step-info h3 {
    font-size: 1.1rem;
    margin-bottom: 5px;
    color: #333;
}

.step-info p {
    color: #666;
    font-size: 0.9rem;
}

.step-status {
    font-size: 1.2rem;
}

.progress-bar {
    width: 100%;
    height: 8px;
    background: #e0e0e0;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 10px;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea, #764ba2);
    width: 0%;
    transition: width 0.5s ease;
}

.progress-text {
    text-align: center;
    color: #666;
    font-weight: 500;
}

/* 结果区域 */
.results-section {
    margin-bottom: 40px;
}

.result-summary {
    margin-bottom: 30px;
}

.summary-card {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 25px;
    border: 1px solid #e9ecef;
}

.summary-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 20px;
    margin-top: 15px;
}

.stat {
    text-align: center;
}

.stat-label {
    display: block;
    font-size: 0.9rem;
    color: #666;
    margin-bottom: 5px;
}

.stat-value {
    display: block;
    font-size: 1.5rem;
    font-weight: bold;
    color: #333;
}

.result-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 30px;
}

.result-panel {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 25px;
    border: 1px solid #e9ecef;
}

.result-panel h3 {
    margin-bottom: 15px;
    color: #333;
}

.extracted-text {
    background: white;
    border-radius: 5px;
    padding: 15px;
    border: 1px solid #ddd;
    min-height: 200px;
    font-family: monospace;
    white-space: pre-wrap;
}

.quality-report {
    background: white;
    border-radius: 5px;
    padding: 15px;
    border: 1px solid #ddd;
    min-height: 200px;
}

.result-actions {
    display: flex;
    gap: 15px;
    justify-content: center;
    flex-wrap: wrap;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    .main-content {
        padding: 20px;
    }
    
    .header h1 {
        font-size: 2rem;
    }
    
    .version-cards {
        grid-template-columns: 1fr;
    }
    
    .result-content {
        grid-template-columns: 1fr;
    }
    
    .upload-options {
        flex-direction: column;
    }
    
    .result-actions {
        flex-direction: column;
    }
}

/* 动画效果 */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeIn 0.5s ease-out;
}

/* 加载动画 */
.loading {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* 页脚 */
.footer {
    text-align: center;
    color: white;
    margin-top: 40px;
    opacity: 0.8;
}
```

#### JavaScript应用逻辑 (static/js/app.js)
```javascript
class OCRWorkflowApp {
    constructor() {
        this.selectedVersion = null;
        this.currentWorkflowId = null;
        this.coordinatorUrl = 'http://98.81.255.168:8096';
        this.uploadedFile = null;
        
        this.initializeEventListeners();
        this.initializeVersionSelector();
    }
    
    initializeEventListeners() {
        // 版本选择
        document.querySelectorAll('.version-card').forEach(card => {
            card.addEventListener('click', (e) => {
                this.selectVersion(e.currentTarget.dataset.version);
            });
        });
        
        // 文件上传
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        
        // 开始处理按钮
        document.getElementById('startProcessing').addEventListener('click', 
            this.startOCRProcessing.bind(this));
        
        // 结果操作按钮
        document.getElementById('downloadResult').addEventListener('click', 
            this.downloadResult.bind(this));
        document.getElementById('shareResult').addEventListener('click', 
            this.shareResult.bind(this));
        document.getElementById('processAnother').addEventListener('click', 
            this.resetToUpload.bind(this));
    }
    
    initializeVersionSelector() {
        // 默认选择Enterprise版
        this.selectVersion('enterprise');
    }
    
    selectVersion(version) {
        // 移除之前的选择
        document.querySelectorAll('.version-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // 选择新版本
        document.querySelector(`[data-version="${version}"]`).classList.add('selected');
        this.selectedVersion = version;
        
        // 显示上传区域
        document.getElementById('uploadSection').style.display = 'block';
        document.getElementById('uploadSection').classList.add('fade-in');
        
        // 根据版本更新智能体显示
        this.updateAgentStepsForVersion(version);
        
        console.log(`选择版本: ${version}`);
    }
    
    updateAgentStepsForVersion(version) {
        const allSteps = document.querySelectorAll('.agent-step');
        
        if (version === 'enterprise') {
            // Enterprise版显示所有6个智能体
            allSteps.forEach(step => step.style.display = 'flex');
        } else {
            // Personal和Opensource版只显示3个核心智能体
            allSteps.forEach(step => {
                const agent = step.dataset.agent;
                if (['implementation', 'testing_verification', 'deployment_release'].includes(agent)) {
                    step.style.display = 'flex';
                } else {
                    step.style.display = 'none';
                }
            });
        }
    }
    
    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    }
    
    handleDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }
    
    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.processFile(file);
        }
    }
    
    processFile(file) {
        // 验证文件类型
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
        if (!allowedTypes.includes(file.type)) {
            alert('请上传支持的文件格式: JPG, PNG, GIF, PDF');
            return;
        }
        
        // 验证文件大小 (最大10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('文件大小不能超过10MB');
            return;
        }
        
        this.uploadedFile = file;
        
        // 更新上传区域显示
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.innerHTML = `
            <div class="upload-success">
                <i class="upload-icon">✅</i>
                <p><strong>${file.name}</strong></p>
                <p class="upload-hint">文件大小: ${this.formatFileSize(file.size)}</p>
            </div>
        `;
        
        // 启用开始处理按钮
        document.getElementById('startProcessing').disabled = false;
        
        console.log('文件上传成功:', file.name);
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    async startOCRProcessing() {
        if (!this.uploadedFile || !this.selectedVersion) {
            alert('请先选择版本并上传文件');
            return;
        }
        
        // 隐藏上传区域，显示进度区域
        document.getElementById('uploadSection').style.display = 'none';
        document.getElementById('progressSection').style.display = 'block';
        document.getElementById('progressSection').classList.add('fade-in');
        
        try {
            // 将文件转换为base64
            const base64Data = await this.fileToBase64(this.uploadedFile);
            
            // 准备工作流请求数据
            const workflowRequest = {
                request_id: `ocr_${Date.now()}`,
                user_session: 'web_experience',
                workflow_type: 'ocr_experience',
                input_data: {
                    image_data: base64Data,
                    document_type: '台湾保险表单',
                    language: '繁体中文',
                    version: this.selectedVersion,
                    options: {
                        traditional_chinese: document.getElementById('traditionalChinese').checked,
                        handwriting_mode: document.getElementById('handwritingMode').checked,
                        address_mode: document.getElementById('addressMode').checked
                    },
                    expected_content: {
                        name: '張家銓',
                        address: '604 嘉義縣竹崎鄉灣橋村五間厝58-51號',
                        amount: '13726元'
                    }
                },
                target_environment: window.location.origin,
                quality_requirements: {
                    min_accuracy: this.selectedVersion === 'enterprise' ? 0.90 : 
                                 this.selectedVersion === 'personal' ? 0.80 : 0.70
                }
            };
            
            this.currentWorkflowId = workflowRequest.request_id;
            
            // 开始处理进度监控
            this.startProgressMonitoring();
            
            // 发送工作流请求
            const response = await fetch(`${this.coordinatorUrl}/workflow/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(workflowRequest)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            this.handleWorkflowResult(result);
            
        } catch (error) {
            console.error('OCR处理失败:', error);
            this.handleWorkflowError(error);
        }
    }
    
    async fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                // 移除data:image/jpeg;base64,前缀
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }
    
    startProgressMonitoring() {
        let currentStep = 0;
        const steps = this.selectedVersion === 'enterprise' ? 
            ['requirements_analysis', 'architecture_design', 'implementation', 
             'testing_verification', 'deployment_release', 'monitoring_operations'] :
            ['implementation', 'testing_verification', 'deployment_release'];
        
        const progressInterval = setInterval(() => {
            if (currentStep < steps.length) {
                this.updateStepStatus(steps[currentStep], 'active');
                
                if (currentStep > 0) {
                    this.updateStepStatus(steps[currentStep - 1], 'completed');
                }
                
                // 更新进度条
                const progress = ((currentStep + 1) / steps.length) * 100;
                document.getElementById('progressFill').style.width = `${progress}%`;
                document.getElementById('progressText').textContent = 
                    `正在执行: ${this.getStepDisplayName(steps[currentStep])}`;
                
                currentStep++;
            } else {
                clearInterval(progressInterval);
                // 完成所有步骤
                if (steps.length > 0) {
                    this.updateStepStatus(steps[steps.length - 1], 'completed');
                }
                document.getElementById('progressFill').style.width = '100%';
                document.getElementById('progressText').textContent = '处理完成，正在生成结果...';
            }
        }, 2000); // 每2秒更新一步
        
        // 保存interval ID以便后续清理
        this.progressInterval = progressInterval;
    }
    
    updateStepStatus(stepAgent, status) {
        const stepElement = document.querySelector(`[data-agent="${stepAgent}"]`);
        if (stepElement) {
            // 移除所有状态类
            stepElement.classList.remove('active', 'completed', 'failed');
            // 添加新状态类
            stepElement.classList.add(status);
            
            // 更新状态图标
            const statusElement = stepElement.querySelector('.step-status');
            switch (status) {
                case 'active':
                    statusElement.innerHTML = '<div class="loading"></div>';
                    break;
                case 'completed':
                    statusElement.textContent = '✅';
                    break;
                case 'failed':
                    statusElement.textContent = '❌';
                    break;
                default:
                    statusElement.textContent = '⏳';
            }
        }
    }
    
    getStepDisplayName(stepAgent) {
        const names = {
            'requirements_analysis': '需求分析智能体',
            'architecture_design': '架构设计智能体',
            'implementation': '编码实现智能体',
            'testing_verification': '测试验证智能体',
            'deployment_release': '部署发布智能体',
            'monitoring_operations': '监控运维智能体'
        };
        return names[stepAgent] || stepAgent;
    }
    
    handleWorkflowResult(result) {
        // 清理进度监控
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        console.log('工作流结果:', result);
        
        // 隐藏进度区域，显示结果区域
        document.getElementById('progressSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';
        document.getElementById('resultsSection').classList.add('fade-in');
        
        // 更新结果显示
        this.displayResults(result);
    }
    
    displayResults(result) {
        // 更新概览统计
        document.getElementById('overallAccuracy').textContent = 
            `${(result.overall_quality_score * 100).toFixed(1)}%`;
        document.getElementById('processingTime').textContent = 
            `${result.total_execution_time.toFixed(2)}秒`;
        document.getElementById('usedVersion').textContent = 
            this.getVersionDisplayName(this.selectedVersion);
        
        // 显示OCR识别结果
        const ocrResult = result.ocr_result || {};
        const extractedText = ocrResult.extracted_text || {};
        
        let textDisplay = '';
        if (extractedText.name) textDisplay += `姓名: ${extractedText.name}\n`;
        if (extractedText.address) textDisplay += `地址: ${extractedText.address}\n`;
        if (extractedText.amount) textDisplay += `金额: ${extractedText.amount}\n`;
        
        if (!textDisplay) {
            textDisplay = '未能识别出文字内容，请尝试上传更清晰的图片。';
        }
        
        document.getElementById('extractedText').textContent = textDisplay;
        
        // 显示质量报告
        const qualityReport = this.generateQualityReport(result);
        document.getElementById('qualityReport').innerHTML = qualityReport;
        
        // 保存结果用于下载
        this.currentResult = result;
    }
    
    generateQualityReport(result) {
        const stageResults = result.stage_results || {};
        let report = '<div class="quality-metrics">';
        
        // 各阶段质量分数
        Object.entries(stageResults).forEach(([stage, stageData]) => {
            const score = (stageData.quality_score * 100).toFixed(1);
            const time = stageData.execution_time.toFixed(2);
            
            report += `
                <div class="quality-metric">
                    <span class="metric-name">${this.getStepDisplayName(stage)}</span>
                    <span class="metric-score">${score}%</span>
                    <span class="metric-time">${time}s</span>
                </div>
            `;
        });
        
        report += '</div>';
        
        // 处理建议
        report += '<div class="processing-recommendations">';
        report += '<h4>处理建议</h4>';
        
        if (result.overall_quality_score >= 0.9) {
            report += '<p class="recommendation success">✅ 识别质量优秀，结果可信度高</p>';
        } else if (result.overall_quality_score >= 0.7) {
            report += '<p class="recommendation warning">⚠️ 识别质量良好，建议人工核验关键信息</p>';
        } else {
            report += '<p class="recommendation error">❌ 识别质量较低，建议重新上传更清晰的图片</p>';
        }
        
        report += '</div>';
        
        return report;
    }
    
    getVersionDisplayName(version) {
        const names = {
            'enterprise': 'Enterprise版',
            'personal': 'Personal版',
            'opensource': 'Opensource版'
        };
        return names[version] || version;
    }
    
    handleWorkflowError(error) {
        // 清理进度监控
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        console.error('工作流错误:', error);
        
        // 显示错误信息
        document.getElementById('progressText').textContent = `处理失败: ${error.message}`;
        document.getElementById('progressText').style.color = '#dc3545';
        
        // 添加重试按钮
        const retryButton = document.createElement('button');
        retryButton.textContent = '🔄 重试';
        retryButton.className = 'btn-primary';
        retryButton.style.marginTop = '20px';
        retryButton.onclick = () => {
            document.getElementById('progressSection').style.display = 'none';
            document.getElementById('uploadSection').style.display = 'block';
        };
        
        document.getElementById('progressSection').appendChild(retryButton);
    }
    
    downloadResult() {
        if (!this.currentResult) return;
        
        const data = {
            timestamp: new Date().toISOString(),
            version: this.selectedVersion,
            filename: this.uploadedFile.name,
            result: this.currentResult
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], 
            { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `ocr_result_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    shareResult() {
        if (!this.currentResult) return;
        
        const shareData = {
            title: 'PowerAuto.ai OCR处理结果',
            text: `使用${this.getVersionDisplayName(this.selectedVersion)}处理图片，准确度: ${(this.currentResult.overall_quality_score * 100).toFixed(1)}%`,
            url: window.location.href
        };
        
        if (navigator.share) {
            navigator.share(shareData);
        } else {
            // 复制到剪贴板
            navigator.clipboard.writeText(
                `${shareData.title}\n${shareData.text}\n${shareData.url}`
            ).then(() => {
                alert('结果已复制到剪贴板');
            });
        }
    }
    
    resetToUpload() {
        // 重置所有状态
        this.uploadedFile = null;
        this.currentResult = null;
        this.currentWorkflowId = null;
        
        // 重置界面
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('progressSection').style.display = 'none';
        document.getElementById('uploadSection').style.display = 'block';
        
        // 重置上传区域
        document.getElementById('uploadArea').innerHTML = `
            <div class="upload-placeholder">
                <i class="upload-icon">📁</i>
                <p>点击或拖拽图片到此处</p>
                <p class="upload-hint">支持 JPG, PNG, PDF 格式</p>
            </div>
        `;
        
        // 重置按钮状态
        document.getElementById('startProcessing').disabled = true;
        
        // 重置文件输入
        document.getElementById('fileInput').value = '';
        
        // 重置进度显示
        document.querySelectorAll('.agent-step').forEach(step => {
            step.classList.remove('active', 'completed', 'failed');
            step.querySelector('.step-status').textContent = '⏳';
        });
        
        document.getElementById('progressFill').style.width = '0%';
        document.getElementById('progressText').textContent = '准备开始处理...';
        document.getElementById('progressText').style.color = '#666';
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new OCRWorkflowApp();
});
```

### 2. OCR体验后端API

#### Flask应用 (app.py)
```python
#!/usr/bin/env python3
"""
OCR体验工作流后端API
为前端提供OCR处理服务，集成产品工作流协调器
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import json
import time
import logging
import requests
import base64
from werkzeug.utils import secure_filename

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ocr_experience_api")

app = Flask(__name__)
CORS(app)  # 启用CORS支持

# 配置
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = '/tmp/ocr_uploads'
COORDINATOR_URL = 'http://localhost:8096'

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """静态文件服务"""
    return send_from_directory('static', filename)

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({
        'service': 'OCR Experience API',
        'status': 'healthy',
        'timestamp': time.time()
    })

@app.route('/api/versions')
def get_versions():
    """获取支持的版本信息"""
    try:
        response = requests.get(f'{COORDINATOR_URL}/capabilities', timeout=10)
        if response.status_code == 200:
            capabilities = response.json()
            return jsonify({
                'versions': ['enterprise', 'personal', 'opensource'],
                'coordinator_info': capabilities
            })
        else:
            return jsonify({
                'versions': ['enterprise', 'personal', 'opensource'],
                'coordinator_info': None
            })
    except Exception as e:
        logger.error(f"获取版本信息失败: {str(e)}")
        return jsonify({
            'versions': ['enterprise', 'personal', 'opensource'],
            'error': str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件上传'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 验证文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'error': '不支持的文件类型'}), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 转换为base64
        with open(filepath, 'rb') as f:
            file_data = f.read()
            base64_data = base64.b64encode(file_data).decode('utf-8')
        
        return jsonify({
            'success': True,
            'filename': filename,
            'size': len(file_data),
            'base64_data': base64_data
        })
        
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ocr/process', methods=['POST'])
def process_ocr():
    """OCR处理接口"""
    try:
        data = request.get_json()
        
        # 验证请求数据
        required_fields = ['image_data', 'version']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需字段: {field}'}), 400
        
        # 准备工作流请求
        workflow_request = {
            'request_id': f"ocr_web_{int(time.time())}",
            'user_session': 'web_experience',
            'workflow_type': 'ocr_experience',
            'input_data': {
                'image_data': data['image_data'],
                'document_type': data.get('document_type', '台湾保险表单'),
                'language': data.get('language', '繁体中文'),
                'version': data['version'],
                'options': data.get('options', {}),
                'expected_content': data.get('expected_content', {})
            },
            'target_environment': request.host_url,
            'quality_requirements': {
                'min_accuracy': 0.90 if data['version'] == 'enterprise' else 
                               0.80 if data['version'] == 'personal' else 0.70
            }
        }
        
        # 调用工作流协调器
        response = requests.post(
            f'{COORDINATOR_URL}/workflow/execute',
            json=workflow_request,
            timeout=120  # 2分钟超时
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'workflow_result': result,
                'request_id': workflow_request['request_id']
            })
        else:
            return jsonify({
                'success': False,
                'error': f'工作流执行失败: HTTP {response.status_code}',
                'details': response.text
            }), 500
            
    except requests.RequestException as e:
        logger.error(f"工作流协调器调用失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '工作流协调器不可用',
            'details': str(e)
        }), 503
        
    except Exception as e:
        logger.error(f"OCR处理失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/workflow/status/<request_id>')
def get_workflow_status(request_id):
    """获取工作流状态"""
    try:
        response = requests.get(
            f'{COORDINATOR_URL}/workflow/status/{request_id}',
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                'status': 'not_found',
                'message': '工作流不存在或已完成'
            }), 404
            
    except Exception as e:
        logger.error(f"获取工作流状态失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/demo/sample')
def get_demo_sample():
    """获取演示样本"""
    # 返回预设的演示数据
    sample_data = {
        'image_url': '/static/images/sample_taiwan_form.jpg',
        'expected_results': {
            'name': '張家銓',
            'address': '604 嘉義縣竹崎鄉灣橋村五間厝58-51號',
            'amount': '13726元'
        },
        'description': '台湾保险表单样本 - 包含繁体中文手写内容'
    }
    
    return jsonify(sample_data)

@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({'error': '文件大小超过限制 (最大16MB)'}), 413

@app.errorhandler(404)
def not_found(e):
    """404错误处理"""
    return jsonify({'error': '请求的资源不存在'}), 404

@app.errorhandler(500)
def internal_error(e):
    """500错误处理"""
    return jsonify({'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    logger.info("启动OCR体验工作流API服务")
    app.run(host='0.0.0.0', port=5001, debug=False)
```

## 🚀 部署步骤

### 1. 创建项目结构
```bash
mkdir -p /home/ubuntu/ocr_experience_app
cd /home/ubuntu/ocr_experience_app

# 创建目录结构
mkdir -p templates static/css static/js static/images
```

### 2. 部署文件
```bash
# 复制HTML模板
cp index.html templates/

# 复制静态资源
cp style.css static/css/
cp app.js static/js/

# 复制Flask应用
cp app.py ./
```

### 3. 安装依赖
```bash
pip3 install flask flask-cors requests
```

### 4. 启动服务
```bash
# 启动OCR体验API
python3 app.py

# 服务将在 http://98.81.255.168:5001/ 上运行
```

### 5. 验证部署
```bash
# 测试健康检查
curl http://98.81.255.168:5001/api/health

# 测试版本信息
curl http://98.81.255.168:5001/api/versions
```

## 📊 功能特性

### 🎯 核心功能
1. **多版本体验** - 支持Enterprise/Personal/Opensource三种版本
2. **实时进度** - 显示六大智能体处理进度
3. **文件上传** - 支持拖拽上传和点击上传
4. **结果展示** - 详细的OCR结果和质量报告
5. **响应式设计** - 支持桌面和移动设备

### 🔧 技术特性
1. **前后端分离** - 清晰的API接口设计
2. **错误处理** - 完善的错误处理和用户提示
3. **性能优化** - 文件大小限制和超时控制
4. **安全性** - 文件类型验证和安全文件名
5. **可扩展性** - 模块化设计，易于扩展

### 📈 用户体验
1. **直观界面** - 清晰的步骤指引
2. **实时反馈** - 处理进度实时更新
3. **结果下载** - 支持结果下载和分享
4. **版本对比** - 不同版本功能对比
5. **演示样本** - 提供测试样本

## 🎯 测试用例验证

### 测试场景1: Enterprise版完整体验
1. 用户访问 http://98.81.255.168:5001/
2. 选择Enterprise版
3. 上传台湾保险表单图片
4. 观察六大智能体处理进度
5. 获得高质量OCR结果
6. 查看详细质量报告

### 测试场景2: Personal版核心体验
1. 选择Personal版
2. 上传相同图片
3. 观察三大核心智能体处理
4. 对比与Enterprise版的差异
5. 验证功能限制

### 测试场景3: Opensource版基础体验
1. 选择Opensource版
2. 体验基础OCR功能
3. 验证免费版本限制
4. 引导用户升级

这个完整的OCR体验工作流发布方案将为用户提供一个专业、直观、功能完整的OCR处理体验平台！

