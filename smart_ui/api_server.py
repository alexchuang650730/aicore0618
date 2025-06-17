"""
智慧UI Flask API服務器
為端側WebAdmin提供REST API接口
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys
import logging
from datetime import datetime

# 添加項目路徑
sys.path.append('/opt/powerautomation')

from smart_ui import get_smart_ui
from smart_ui.user_manager import User
from smart_ui.workflow_manager import WorkflowType, WorkflowStatus
from github_sync_manager import github_sync_manager
from coding_workflow_connector import (
    get_coding_workflow_metrics,
    get_three_node_dashboard,
    get_three_node_status,
    get_directory_compliance
)
from feishu_group_manager import FeishuGroupManager
from feishu_long_connection import get_feishu_client, initialize_feishu_client
from multi_agent_manager import get_multi_agent_manager
from real_agent_adapter import call_real_agent, REAL_AGENTS
from feishu_webhook import setup_webhook_routes

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建Flask應用
app = Flask(__name__)
CORS(app)  # 允許跨域請求

# 初始化智慧UI系統
smart_ui = get_smart_ui()
smart_ui.initialize()

# 設置同步引擎關聯
smart_ui.user_manager.set_sync_engine(smart_ui.sync_engine)
smart_ui.workflow_manager.set_sync_engine(smart_ui.sync_engine)

# 啟動同步引擎
smart_ui.sync_engine.start_sync_engine()

# 设置飞书webhook路由
setup_webhook_routes(app)

@app.route('/')
def index():
    """主頁面"""
    return send_from_directory('frontend', 'client_webadmin.html')

@app.route('/api/status')
def get_system_status():
    """獲取系統狀態"""
    try:
        status = smart_ui.get_system_status()
        sync_metrics = smart_ui.sync_engine.get_sync_status()
        
        return jsonify({
            "success": True,
            "data": {
                "system": status,
                "sync": sync_metrics,
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"獲取系統狀態失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/dashboard')
def get_dashboard_data():
    """獲取儀表板數據"""
    try:
        # 獲取用戶統計
        user_stats = smart_ui.user_manager.get_user_statistics()
        
        # 獲取工作流統計
        workflow_stats = smart_ui.workflow_manager.get_workflow_statistics()
        
        # 模擬項目數據
        project_data = {
            "active_projects": 12,
            "total_tasks": 156,
            "completed_tasks": 140,
            "user_credits": 2847
        }
        
        return jsonify({
            "success": True,
            "data": {
                "projects": project_data,
                "users": user_stats,
                "workflows": workflow_stats,
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"獲取儀表板數據失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/workflows')
def get_workflows():
    """獲取工作流列表"""
    try:
        # 獲取所有類型的工作流
        coding_workflows = smart_ui.workflow_manager.get_workflows_by_type(WorkflowType.CODING)
        deployment_workflows = smart_ui.workflow_manager.get_workflows_by_type(WorkflowType.DEPLOYMENT)
        testing_workflows = smart_ui.workflow_manager.get_workflows_by_type(WorkflowType.TESTING)
        
        workflows = {
            "coding": [_workflow_to_dict(w) for w in coding_workflows],
            "deployment": [_workflow_to_dict(w) for w in deployment_workflows],
            "testing": [_workflow_to_dict(w) for w in testing_workflows]
        }
        
        return jsonify({
            "success": True,
            "data": workflows
        })
    except Exception as e:
        logger.error(f"獲取工作流列表失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/workflows', methods=['POST'])
def create_workflow():
    """創建新工作流"""
    try:
        data = request.get_json()
        
        workflow_type = WorkflowType(data.get('type', 'coding'))
        name = data.get('name', f'新{workflow_type.value}工作流')
        project_id = data.get('project_id', 1)
        description = data.get('description', '')
        
        workflow = smart_ui.workflow_manager.create_workflow(
            project_id=project_id,
            name=name,
            workflow_type=workflow_type,
            description=description
        )
        
        if workflow:
            return jsonify({
                "success": True,
                "data": _workflow_to_dict(workflow)
            })
        else:
            return jsonify({"success": False, "error": "創建工作流失敗"}), 500
            
    except Exception as e:
        logger.error(f"創建工作流失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/workflows/<int:workflow_id>/execute', methods=['POST'])
def execute_workflow(workflow_id):
    """執行工作流"""
    try:
        # 先更新狀態為活躍
        smart_ui.workflow_manager.update_workflow_status(workflow_id, WorkflowStatus.ACTIVE)
        
        # 執行工作流
        success = smart_ui.workflow_manager.execute_workflow(workflow_id)
        
        return jsonify({
            "success": success,
            "message": "工作流執行成功" if success else "工作流執行失敗"
        })
    except Exception as e:
        logger.error(f"執行工作流失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/users')
def get_users():
    """獲取用戶列表"""
    try:
        users = smart_ui.user_manager.get_all_users(limit=50)
        user_data = [_user_to_dict(user) for user in users]
        
        return jsonify({
            "success": True,
            "data": user_data
        })
    except Exception as e:
        logger.error(f"獲取用戶列表失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """創建新用戶"""
    try:
        data = request.get_json()
        
        user = smart_ui.user_manager.create_user(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            role=data.get('role', 'user'),
            version=data.get('version', 'free')
        )
        
        if user:
            return jsonify({
                "success": True,
                "data": _user_to_dict(user)
            })
        else:
            return jsonify({"success": False, "error": "創建用戶失敗"}), 500
            
    except Exception as e:
        logger.error(f"創建用戶失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/users/<int:user_id>/credits', methods=['PUT'])
def update_user_credits(user_id):
    """更新用戶積分"""
    try:
        data = request.get_json()
        credits = data.get('credits', 0)
        
        success = smart_ui.user_manager.update_user_credits(user_id, credits)
        
        return jsonify({
            "success": success,
            "message": "積分更新成功" if success else "積分更新失敗"
        })
    except Exception as e:
        logger.error(f"更新用戶積分失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/sync/status')
def get_sync_status():
    """獲取同步狀態"""
    try:
        status = smart_ui.sync_engine.get_sync_status()
        return jsonify({
            "success": True,
            "data": status
        })
    except Exception as e:
        logger.error(f"獲取同步狀態失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/sync/force', methods=['POST'])
def force_sync():
    """強制全量同步"""
    try:
        success = smart_ui.sync_engine.force_full_sync()
        return jsonify({
            "success": success,
            "message": "強制同步成功" if success else "強制同步失敗"
        })
    except Exception as e:
        logger.error(f"強制同步失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

def _workflow_to_dict(workflow):
    """工作流對象轉字典"""
    return {
        "id": workflow.id,
        "name": workflow.name,
        "type": workflow.type.value,
        "status": workflow.status.value,
        "project_id": workflow.project_id,
        "steps_count": len(workflow.steps),
        "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
        "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None
    }

def _user_to_dict(user):
    """用戶對象轉字典"""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "credits": user.credits,
        "version": user.version,
        "status": user.status,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "API端點不存在"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "內部服務器錯誤"}), 500


@app.route('/api/github-sync')
def get_github_sync_status():
    """获取GitHub同步状态"""
    try:
        github_status = github_sync_manager.get_github_sync_status()
        return jsonify({
            'success': True,
            'data': github_status
        })
    except Exception as e:
        logger.error(f"获取GitHub同步状态失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/coding-workflow/metrics')
def get_coding_workflow_api():
    """获取编码工作流指标数据"""
    try:
        metrics_data = get_coding_workflow_metrics()
        return jsonify(metrics_data)
    except Exception as e:
        logger.error(f"获取编码工作流指标失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/coding-workflow/dashboard')
def get_coding_workflow_dashboard():
    """获取编码工作流完整Dashboard数据"""
    try:
        dashboard_data = get_three_node_dashboard()
        return jsonify({
            'success': True,
            'data': dashboard_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"获取编码工作流Dashboard失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/coding-workflow/nodes')
def get_three_node_workflow():
    """获取三节点工作流状态"""
    try:
        nodes_data = get_three_node_status()
        return jsonify(nodes_data)
    except Exception as e:
        logger.error(f"获取三节点工作流状态失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/coding-workflow/compliance')
def get_directory_compliance_api():
    """获取目录规范合规状态"""
    try:
        compliance_data = get_directory_compliance()
        return jsonify(compliance_data)
    except Exception as e:
        logger.error(f"获取目录合规状态失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/github-webhook', methods=['POST'])
def github_webhook():
    """接收GitHub webhook事件"""
    try:
        payload = request.get_json()
        event_type = request.headers.get('X-GitHub-Event')
        delivery_id = request.headers.get('X-GitHub-Delivery')
        
        logger.info(f"收到GitHub webhook事件: {event_type}, 交付ID: {delivery_id}")
        
        if event_type == 'ping':
            # GitHub webhook测试事件
            return jsonify({
                "status": "success", 
                "message": "PowerAutomation webhook接收器正常工作",
                "zen": payload.get('zen', '')
            })
        
        elif event_type == 'push':
            # 处理代码推送事件
            return handle_push_event(payload)
        
        elif event_type == 'pull_request':
            # 处理PR事件
            return handle_pr_event(payload)
        
        else:
            logger.info(f"未处理的事件类型: {event_type}")
            return jsonify({"status": "ignored", "message": f"事件类型 {event_type} 已忽略"})
        
    except Exception as e:
        logger.error(f"Webhook处理错误: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def handle_push_event(payload):
    """处理GitHub push事件"""
    try:
        repo_name = payload['repository']['name']
        repo_url = payload['repository']['html_url']
        branch = payload['ref'].split('/')[-1]
        commits = payload['commits']
        pusher = payload['pusher']['name']
        
        logger.info(f"处理push事件: {repo_name}/{branch}, 提交数: {len(commits)}, 推送者: {pusher}")
        
        # 发送飞书通知
        feishu_manager = get_feishu_manager()
        
        # 构建通知消息
        commit_messages = []
        for commit in commits[:3]:  # 最多显示3个提交
            commit_messages.append(f"• {commit['message'][:50]}...")
        
        message = f"""🔄 **GitHub Push 通知**

**仓库**: {repo_name}
**分支**: {branch}
**推送者**: {pusher}
**提交数量**: {len(commits)}

**最新提交**:
{chr(10).join(commit_messages)}

**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
        # 发送到部署监控群
        old_group = feishu_manager.current_group
        feishu_manager.switch_group('deployment')
        feishu_result = feishu_manager.send_message_to_current_group(message)
        feishu_manager.switch_group(old_group)  # 恢复原群组
        
        logger.info(f"GitHub push事件已发送到飞书: {feishu_result}")
        
        # 触发编码工作流检查
        for commit in commits:
            commit_sha = commit['id']
            commit_message = commit['message']
            
            logger.info(f"检查提交: {commit_sha[:8]} - {commit_message}")
            
            # 这里可以触发目录规范检查、代码质量检查等
            # 暂时记录事件
            
        return jsonify({
            "status": "success",
            "message": f"已处理 {len(commits)} 个提交",
            "repository": repo_name,
            "branch": branch,
            "feishu_result": feishu_result
        })
        
    except Exception as e:
        logger.error(f"处理push事件失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def handle_pr_event(payload):
    """处理GitHub PR事件"""
    try:
        action = payload['action']
        pr_number = payload['number']
        repo_name = payload['repository']['name']
        pr_title = payload['pull_request']['title']
        pr_author = payload['pull_request']['user']['login']
        pr_url = payload['pull_request']['html_url']
        
        logger.info(f"处理PR事件: {action} - {repo_name}#{pr_number} by {pr_author}")
        
        # 发送飞书通知
        feishu_manager = get_feishu_manager()
        
        # 根据PR动作选择不同的消息
        action_emoji = {
            'opened': '🆕',
            'closed': '✅' if payload['pull_request'].get('merged') else '❌',
            'reopened': '🔄',
            'synchronize': '🔄'
        }
        
        action_text = {
            'opened': '创建了新的',
            'closed': '合并了' if payload['pull_request'].get('merged') else '关闭了',
            'reopened': '重新打开了',
            'synchronize': '更新了'
        }
        
        message = f"""{action_emoji.get(action, '📝')} **Pull Request {action_text.get(action, '操作了')}**

**仓库**: {repo_name}
**PR**: #{pr_number} {pr_title}
**作者**: {pr_author}
**动作**: {action}

**链接**: {pr_url}

**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
        # 发送到代码审查群
        old_group = feishu_manager.current_group
        feishu_manager.switch_group('pr_review')
        feishu_result = feishu_manager.send_message_to_current_group(message)
        feishu_manager.switch_group(old_group)  # 恢复原群组
        
        logger.info(f"GitHub PR事件已发送到飞书: {feishu_result}")
        
        if action in ['opened', 'synchronize', 'reopened']:
            # 触发PR审查流程
            logger.info(f"触发PR审查: {pr_title}")
            
            # 这里可以触发自动化审查流程
            # 暂时记录事件
            
        return jsonify({
            "status": "success",
            "message": f"已处理PR {action}事件",
            "pr_number": pr_number,
            "repository": repo_name
        })
        
    except Exception as e:
        logger.error(f"处理PR事件失败: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 飞书群组管理API端点
@app.route('/api/feishu/groups', methods=['GET'])
def get_feishu_groups():
    """获取所有飞书群组信息"""
    try:
        feishu_manager = get_feishu_manager()
        groups = feishu_manager.get_all_groups()
        
        return jsonify({
            "success": True,
            "data": groups,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"获取飞书群组失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/feishu/switch-group', methods=['POST'])
def switch_feishu_group():
    """切换飞书群组"""
    try:
        data = request.get_json()
        group_key = data.get('group_key')
        
        if not group_key:
            return jsonify({"success": False, "error": "缺少群组标识"}), 400
        
        feishu_manager = get_feishu_manager()
        result = feishu_manager.switch_group(group_key)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"切换飞书群组失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/feishu/status', methods=['GET'])
def get_feishu_status():
    """获取飞书状态统计"""
    try:
        feishu_manager = get_feishu_manager()
        status = feishu_manager.get_group_status()
        
        return jsonify({
            "success": True,
            "data": status,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"获取飞书状态失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/feishu/send-message', methods=['POST'])
def send_feishu_message():
    """向当前飞书群组发送消息"""
    try:
        data = request.get_json()
        message = data.get('message')
        
        if not message:
            return jsonify({"success": False, "error": "缺少消息内容"}), 400
        
        feishu_manager = get_feishu_manager()
        result = feishu_manager.send_message_to_current_group(message)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"发送飞书消息失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# 全局飞书管理器实例
_feishu_manager = None

def get_feishu_manager():
    """获取飞书管理器实例"""
    global _feishu_manager
    if _feishu_manager is None:
        # 使用环境变量或默认测试凭证
        app_id = os.environ.get('FEISHU_APP_ID', 'cli_test_app_id')
        app_secret = os.environ.get('FEISHU_APP_SECRET', 'test_app_secret')
        _feishu_manager = FeishuGroupManager(app_id, app_secret)
    return _feishu_manager

if __name__ == '__main__':
    try:
        print("🧠 PowerAutomation 智慧UI API服務器啟動中...")
        print("📊 數據庫連接: ✅")
        print("🔄 同步引擎: ✅")
        print("🌐 API服務: ✅")
        print("🚀 服務器就緒！")
        print("📱 訪問地址: http://localhost:5001")
        
        app.run(host='0.0.0.0', port=5001, debug=True)
        
    except KeyboardInterrupt:
        print("\n🛑 服務器停止中...")
        smart_ui.sync_engine.stop_sync_engine()
        print("✅ 智慧UI系統已安全關閉")
    except Exception as e:
        print(f"❌ 服務器啟動失敗: {e}")
        smart_ui.sync_engine.stop_sync_engine()


# ==================== 多智能体管理API ====================

@app.route('/api/agents/list', methods=['GET'])
def get_agents_list():
    """获取智能体列表"""
    try:
        agent_manager = get_multi_agent_manager()
        return jsonify({
            "success": True,
            "data": agent_manager.get_agent_status()
        })
    except Exception as e:
        logger.error(f"获取智能体列表失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/agents/call', methods=['POST'])
def call_agent():
    """调用指定智能体"""
    try:
        data = request.get_json()
        agent_name = data.get('agent_name')
        command = data.get('command')
        context = data.get('context', {})
        
        if not agent_name or not command:
            return jsonify({
                "success": False, 
                "error": "缺少agent_name或command参数"
            }), 400
        
        agent_manager = get_multi_agent_manager()
        
        # 检查智能体是否存在
        if agent_name not in agent_manager.agents:
            return jsonify({
                "success": False,
                "error": f"智能体 {agent_name} 不存在"
            }), 404
        
        agent = agent_manager.agents[agent_name]
        
        # 异步调用智能体
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            agent_manager.call_agent(agent, command, context)
        )
        loop.close()
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"调用智能体失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/agents/parse-command', methods=['POST'])
def parse_agent_command():
    """解析群组命令"""
    try:
        data = request.get_json()
        message = data.get('message')
        
        if not message:
            return jsonify({
                "success": False,
                "error": "缺少message参数"
            }), 400
        
        agent_manager = get_multi_agent_manager()
        parsed = agent_manager.parse_command(message)
        
        if parsed:
            return jsonify({
                "success": True,
                "data": {
                    "agent_name": parsed["agent_name"],
                    "command": parsed["command"],
                    "agent_info": {
                        "name": parsed["agent"].name,
                        "description": parsed["agent"].description,
                        "icon": parsed["agent"].icon,
                        "color": parsed["agent"].color
                    }
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": "未识别到有效的智能体命令"
            })
    except Exception as e:
        logger.error(f"解析命令失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ==================== 飞书智能体集成 ====================

@app.route('/api/feishu/agent-message', methods=['POST'])
def handle_feishu_agent_message():
    """处理飞书群组中的智能体命令"""
    try:
        data = request.get_json()
        message = data.get('message')
        
        if not message:
            return jsonify({
                "success": False,
                "error": "缺少消息内容"
            }), 400
        
        agent_manager = get_multi_agent_manager()
        
        # 特殊命令处理
        if message.strip() == "@agents" or message.strip() == "@help":
            # 返回智能体列表（包括实际智能体）
            agent_list = agent_manager.get_agent_list()
            
            # 添加实际智能体信息
            real_agent_list = "\n\n🎯 **实际可用智能体**\n"
            for key, config in REAL_AGENTS.items():
                real_agent_list += f"🟢 {config['icon']} **{config['command_prefix']}** - {config['description']}\n"
            
            full_list = agent_list + real_agent_list
            
            feishu_manager = get_feishu_manager()
            result = feishu_manager.send_message_to_current_group(full_list)
            return jsonify(result)
        
        # 检查是否是实际智能体命令
        for agent_key, config in REAL_AGENTS.items():
            if message.startswith(config["command_prefix"]):
                # 提取命令内容
                command_content = message[len(config["command_prefix"]):].strip()
                
                # 调用实际智能体
                agent_result = call_real_agent(agent_key, command_content)
                
                # 格式化响应
                if agent_result["success"]:
                    formatted_response = f"""{config['icon']} **{config['name']}** 响应

{agent_result['response']}

---
💡 模型: {agent_result.get('model_used', 'unknown')}"""
                else:
                    formatted_response = f"❌ {config['name']} 调用失败: {agent_result['error']}"
                
                # 发送到飞书群组
                feishu_manager = get_feishu_manager()
                feishu_result = feishu_manager.send_message_to_current_group(formatted_response)
                
                return jsonify({
                    "success": True,
                    "agent_result": agent_result,
                    "feishu_result": feishu_result
                })
        
        # 解析虚拟智能体命令
        parsed = agent_manager.parse_command(message)
        
        if not parsed:
            return jsonify({
                "success": False,
                "error": "未识别到有效的智能体命令"
            })
        
        # 调用虚拟智能体（显示离线消息）
        formatted_response = f"""⚠️ **{parsed['agent'].name}** 当前离线

该智能体尚未连接到实际服务。

🎯 **可用的实际智能体**:
"""
        for key, config in REAL_AGENTS.items():
            formatted_response += f"• {config['command_prefix']} - {config['description']}\n"
        
        # 发送到飞书群组
        feishu_manager = get_feishu_manager()
        feishu_result = feishu_manager.send_message_to_current_group(formatted_response)
        
        return jsonify({
            "success": True,
            "message": "虚拟智能体离线，已提示用户使用实际智能体",
            "feishu_result": feishu_result
        })
        
    except Exception as e:
        logger.error(f"处理飞书智能体消息失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

