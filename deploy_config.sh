# PowerAutomation 远程部署配置
# 目标服务器: 98.81.255.168:5001

# 服务器信息
TARGET_SERVER="98.81.255.168"
TARGET_PORT="5001"
SSH_KEY="/opt/powerautomation/alexchuang.pem"
SSH_USER="ubuntu"  # 默认用户，可根据实际情况调整

# 部署路径
REMOTE_DEPLOY_PATH="/opt/powerautomation"
REMOTE_BACKUP_PATH="/opt/powerautomation_backup"

# 服务配置
SERVICES=(
    "smartui_devops_api_server.py:5001"
    "test_manager_mcp_server.py:8097"
    "release_manager_mcp_server.py:8096"
    "operations_workflow_mcp_server.py:8090"
)

# 必要的文件列表
REQUIRED_FILES=(
    "smartui_devops_api_server.py"
    "smartui_devops_dashboard.html"
    "mcp/workflow/test_manager_mcp/test_manager_mcp.py"
    "mcp/workflow/test_manager_mcp/test_manager_mcp_server.py"
    "mcp/workflow/release_manager_mcp/release_manager_mcp_server.py"
    "mcp/workflow/operations_workflow_mcp/operations_workflow_mcp_server.py"
    "test/framework/"
    "start_smartui_devops.sh"
)

# Python依赖
PYTHON_REQUIREMENTS="flask flask-cors requests psutil asyncio"

# 系统要求
SYSTEM_REQUIREMENTS=(
    "python3"
    "python3-pip"
    "curl"
    "netstat"
)

export TARGET_SERVER TARGET_PORT SSH_KEY SSH_USER
export REMOTE_DEPLOY_PATH REMOTE_BACKUP_PATH
export SERVICES REQUIRED_FILES PYTHON_REQUIREMENTS SYSTEM_REQUIREMENTS

