import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Activity, 
  Settings, 
  BarChart3, 
  Zap, 
  Shield, 
  Cpu,
  Server,
  Database,
  Globe,
  CheckCircle,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Play,
  Pause,
  Monitor,
  Code,
  TestTube,
  Rocket,
  Wrench
} from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert.jsx'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'
import './App.css'

// MCP服务配置
const MCP_SERVICES = [
  {
    id: 'requirements_analysis',
    name: 'Requirements Analysis MCP',
    description: '需求分析工作流',
    port: 8091,
    icon: <Code className="w-5 h-5" />,
    color: 'bg-blue-500',
    capabilities: ['需求收集和分析', '用户故事生成', '功能规格定义', '验收标准制定']
  },
  {
    id: 'architecture_design',
    name: 'Architecture Design MCP',
    description: '架构设计工作流',
    port: 8092,
    icon: <Database className="w-5 h-5" />,
    color: 'bg-green-500',
    capabilities: ['系统架构设计', '技术栈选择', '组件设计', '接口定义']
  },
  {
    id: 'coding_workflow',
    name: 'Coding Workflow MCP',
    description: '编码工作流',
    port: 8093,
    icon: <Cpu className="w-5 h-5" />,
    color: 'bg-purple-500',
    capabilities: ['代码生成', '代码审查', '编码规范检查', '代码优化']
  },
  {
    id: 'developer_flow',
    name: 'Developer Flow MCP',
    description: '开发者流程管理',
    port: 8094,
    icon: <Wrench className="w-5 h-5" />,
    color: 'bg-orange-500',
    capabilities: ['开发流程管理', '团队协作', '工作流编排', '质量门禁']
  },
  {
    id: 'test_manager',
    name: 'Test Manager MCP',
    description: '测试管理工作流',
    port: 8097,
    icon: <TestTube className="w-5 h-5" />,
    color: 'bg-red-500',
    capabilities: ['测试发现', '测试执行', '测试报告', '测试管理']
  },
  {
    id: 'release_manager',
    name: 'Release Manager MCP',
    description: '发布管理工作流',
    port: 8096,
    icon: <Rocket className="w-5 h-5" />,
    color: 'bg-indigo-500',
    capabilities: ['发布计划', '版本管理', '部署自动化', '回滚管理']
  },
  {
    id: 'operations_workflow',
    name: 'Operations Workflow MCP',
    description: '运维工作流',
    port: 8090,
    icon: <Monitor className="w-5 h-5" />,
    color: 'bg-teal-500',
    capabilities: ['系统监控', '日志分析', '性能优化', '故障处理']
  }
]

// 模拟性能数据
const performanceData = [
  { time: '00:00', cpu: 45, memory: 62, requests: 120 },
  { time: '04:00', cpu: 38, memory: 58, requests: 95 },
  { time: '08:00', cpu: 72, memory: 75, requests: 280 },
  { time: '12:00', cpu: 85, memory: 82, requests: 350 },
  { time: '16:00', cpu: 68, memory: 71, requests: 290 },
  { time: '20:00', cpu: 52, memory: 65, requests: 180 }
]

const serviceStatusData = [
  { name: '正常运行', value: 5, color: '#10b981' },
  { name: '警告', value: 1, color: '#f59e0b' },
  { name: '离线', value: 1, color: '#ef4444' }
]

function App() {
  const [services, setServices] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedService, setSelectedService] = useState(null)
  const [systemStats, setSystemStats] = useState({
    totalServices: 7,
    runningServices: 0,
    totalRequests: 0,
    avgResponseTime: 0
  })

  // 检查服务状态
  const checkServiceHealth = async (service) => {
    try {
      const response = await fetch(`http://localhost:${service.port}/api/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(5000) // 5秒超时
      })
      
      if (response.ok) {
        const data = await response.json()
        return {
          ...service,
          status: 'running',
          health: data,
          lastCheck: new Date().toISOString(),
          responseTime: Math.random() * 200 + 50 // 模拟响应时间
        }
      } else {
        return {
          ...service,
          status: 'error',
          error: `HTTP ${response.status}`,
          lastCheck: new Date().toISOString()
        }
      }
    } catch (error) {
      return {
        ...service,
        status: 'offline',
        error: error.message,
        lastCheck: new Date().toISOString()
      }
    }
  }

  // 检查所有服务
  const checkAllServices = async () => {
    setLoading(true)
    const servicePromises = MCP_SERVICES.map(service => checkServiceHealth(service))
    const results = await Promise.all(servicePromises)
    
    setServices(results)
    
    // 更新系统统计
    const runningCount = results.filter(s => s.status === 'running').length
    const totalRequests = results.reduce((sum, s) => sum + (s.health?.requests || 0), 0)
    const avgResponseTime = results
      .filter(s => s.responseTime)
      .reduce((sum, s, _, arr) => sum + s.responseTime / arr.length, 0)
    
    setSystemStats({
      totalServices: results.length,
      runningServices: runningCount,
      totalRequests,
      avgResponseTime: Math.round(avgResponseTime)
    })
    
    setLoading(false)
  }

  // 启动服务
  const startService = async (service) => {
    // 这里应该调用实际的启动API
    console.log(`启动服务: ${service.name}`)
    // 模拟启动过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    await checkAllServices()
  }

  // 停止服务
  const stopService = async (service) => {
    // 这里应该调用实际的停止API
    console.log(`停止服务: ${service.name}`)
    // 模拟停止过程
    await new Promise(resolve => setTimeout(resolve, 1000))
    await checkAllServices()
  }

  useEffect(() => {
    checkAllServices()
    // 每30秒自动刷新
    const interval = setInterval(checkAllServices, 30000)
    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'error':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />
      case 'offline':
        return <XCircle className="w-4 h-4 text-red-500" />
      default:
        return <RefreshCw className="w-4 h-4 text-gray-500 animate-spin" />
    }
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'running':
        return <Badge className="bg-green-100 text-green-800">运行中</Badge>
      case 'error':
        return <Badge className="bg-yellow-100 text-yellow-800">警告</Badge>
      case 'offline':
        return <Badge className="bg-red-100 text-red-800">离线</Badge>
      default:
        return <Badge className="bg-gray-100 text-gray-800">检查中</Badge>
    }
  }

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
        {/* 顶部导航栏 */}
        <header className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm border-b border-slate-200 dark:border-slate-700 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-4">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center"
                >
                  <Zap className="w-6 h-6 text-white" />
                </motion.div>
                <div>
                  <h1 className="text-xl font-bold text-slate-900 dark:text-white">PowerAutomation</h1>
                  <p className="text-sm text-slate-500 dark:text-slate-400">统一管理界面</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={checkAllServices}
                  disabled={loading}
                  className="flex items-center space-x-2"
                >
                  <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                  <span>刷新</span>
                </Button>
                
                <div className="flex items-center space-x-2 text-sm">
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-slate-600 dark:text-slate-300">{systemStats.runningServices}/{systemStats.totalServices} 服务运行中</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={
              <div className="space-y-8">
                {/* 系统概览卡片 */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                  >
                    <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white border-0">
                      <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-blue-100 text-sm font-medium">总服务数</p>
                            <p className="text-3xl font-bold">{systemStats.totalServices}</p>
                          </div>
                          <Server className="w-8 h-8 text-blue-200" />
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                  >
                    <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white border-0">
                      <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-green-100 text-sm font-medium">运行中服务</p>
                            <p className="text-3xl font-bold">{systemStats.runningServices}</p>
                          </div>
                          <Activity className="w-8 h-8 text-green-200" />
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                  >
                    <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white border-0">
                      <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-purple-100 text-sm font-medium">总请求数</p>
                            <p className="text-3xl font-bold">{systemStats.totalRequests.toLocaleString()}</p>
                          </div>
                          <BarChart3 className="w-8 h-8 text-purple-200" />
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                  >
                    <Card className="bg-gradient-to-r from-orange-500 to-orange-600 text-white border-0">
                      <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-orange-100 text-sm font-medium">平均响应时间</p>
                            <p className="text-3xl font-bold">{systemStats.avgResponseTime}ms</p>
                          </div>
                          <Zap className="w-8 h-8 text-orange-200" />
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                </div>

                {/* 主要内容区域 */}
                <Tabs defaultValue="services" className="space-y-6">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="services">服务管理</TabsTrigger>
                    <TabsTrigger value="monitoring">系统监控</TabsTrigger>
                    <TabsTrigger value="analytics">数据分析</TabsTrigger>
                  </TabsList>

                  <TabsContent value="services" className="space-y-6">
                    {/* 服务状态网格 */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                      {services.map((service, index) => (
                        <motion.div
                          key={service.id}
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: index * 0.1 }}
                        >
                          <Card className="hover:shadow-lg transition-all duration-300 cursor-pointer group"
                                onClick={() => setSelectedService(service)}>
                            <CardHeader className="pb-3">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                  <div className={`p-2 rounded-lg ${service.color} text-white`}>
                                    {service.icon}
                                  </div>
                                  <div>
                                    <CardTitle className="text-lg group-hover:text-blue-600 transition-colors">
                                      {service.name}
                                    </CardTitle>
                                    <CardDescription>{service.description}</CardDescription>
                                  </div>
                                </div>
                                {getStatusIcon(service.status)}
                              </div>
                            </CardHeader>
                            
                            <CardContent className="space-y-4">
                              <div className="flex items-center justify-between">
                                <span className="text-sm text-slate-600 dark:text-slate-400">状态</span>
                                {getStatusBadge(service.status)}
                              </div>
                              
                              <div className="flex items-center justify-between">
                                <span className="text-sm text-slate-600 dark:text-slate-400">端口</span>
                                <Badge variant="outline">{service.port}</Badge>
                              </div>
                              
                              {service.responseTime && (
                                <div className="flex items-center justify-between">
                                  <span className="text-sm text-slate-600 dark:text-slate-400">响应时间</span>
                                  <span className="text-sm font-medium">{Math.round(service.responseTime)}ms</span>
                                </div>
                              )}
                              
                              <div className="flex space-x-2 pt-2">
                                <Button
                                  size="sm"
                                  variant={service.status === 'running' ? 'destructive' : 'default'}
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    service.status === 'running' ? stopService(service) : startService(service)
                                  }}
                                  className="flex-1"
                                >
                                  {service.status === 'running' ? (
                                    <>
                                      <Pause className="w-4 h-4 mr-1" />
                                      停止
                                    </>
                                  ) : (
                                    <>
                                      <Play className="w-4 h-4 mr-1" />
                                      启动
                                    </>
                                  )}
                                </Button>
                                <Button size="sm" variant="outline" className="px-3">
                                  <Settings className="w-4 h-4" />
                                </Button>
                              </div>
                            </CardContent>
                          </Card>
                        </motion.div>
                      ))}
                    </div>
                  </TabsContent>

                  <TabsContent value="monitoring" className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      {/* 性能趋势图 */}
                      <Card>
                        <CardHeader>
                          <CardTitle>系统性能趋势</CardTitle>
                          <CardDescription>CPU、内存使用率和请求量</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={performanceData}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="time" />
                              <YAxis />
                              <Tooltip />
                              <Line type="monotone" dataKey="cpu" stroke="#3b82f6" strokeWidth={2} name="CPU %" />
                              <Line type="monotone" dataKey="memory" stroke="#10b981" strokeWidth={2} name="内存 %" />
                              <Line type="monotone" dataKey="requests" stroke="#f59e0b" strokeWidth={2} name="请求数" />
                            </LineChart>
                          </ResponsiveContainer>
                        </CardContent>
                      </Card>

                      {/* 服务状态分布 */}
                      <Card>
                        <CardHeader>
                          <CardTitle>服务状态分布</CardTitle>
                          <CardDescription>各服务运行状态统计</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                              <Pie
                                data={serviceStatusData}
                                cx="50%"
                                cy="50%"
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="value"
                                label={({ name, value }) => `${name}: ${value}`}
                              >
                                {serviceStatusData.map((entry, index) => (
                                  <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                              </Pie>
                              <Tooltip />
                            </PieChart>
                          </ResponsiveContainer>
                        </CardContent>
                      </Card>
                    </div>

                    {/* 系统资源使用情况 */}
                    <Card>
                      <CardHeader>
                        <CardTitle>系统资源使用情况</CardTitle>
                        <CardDescription>实时系统资源监控</CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                          <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span>CPU 使用率</span>
                              <span>68%</span>
                            </div>
                            <Progress value={68} className="h-2" />
                          </div>
                          <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span>内存使用率</span>
                              <span>74%</span>
                            </div>
                            <Progress value={74} className="h-2" />
                          </div>
                          <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span>磁盘使用率</span>
                              <span>45%</span>
                            </div>
                            <Progress value={45} className="h-2" />
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="analytics" className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      {/* API调用统计 */}
                      <Card>
                        <CardHeader>
                          <CardTitle>API调用统计</CardTitle>
                          <CardDescription>各服务API调用次数</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={[
                              { name: 'Requirements', calls: 1240 },
                              { name: 'Architecture', calls: 980 },
                              { name: 'Coding', calls: 1560 },
                              { name: 'Developer', calls: 890 },
                              { name: 'Test', calls: 2100 },
                              { name: 'Release', calls: 650 },
                              { name: 'Operations', calls: 1320 }
                            ]}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="name" />
                              <YAxis />
                              <Tooltip />
                              <Bar dataKey="calls" fill="#3b82f6" />
                            </BarChart>
                          </ResponsiveContainer>
                        </CardContent>
                      </Card>

                      {/* 错误率统计 */}
                      <Card>
                        <CardHeader>
                          <CardTitle>错误率趋势</CardTitle>
                          <CardDescription>系统错误率变化趋势</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={[
                              { time: '00:00', errorRate: 0.2 },
                              { time: '04:00', errorRate: 0.1 },
                              { time: '08:00', errorRate: 0.3 },
                              { time: '12:00', errorRate: 0.5 },
                              { time: '16:00', errorRate: 0.2 },
                              { time: '20:00', errorRate: 0.1 }
                            ]}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="time" />
                              <YAxis />
                              <Tooltip />
                              <Line type="monotone" dataKey="errorRate" stroke="#ef4444" strokeWidth={2} name="错误率 %" />
                            </LineChart>
                          </ResponsiveContainer>
                        </CardContent>
                      </Card>
                    </div>
                  </TabsContent>
                </Tabs>

                {/* 系统警告 */}
                {services.some(s => s.status === 'offline' || s.status === 'error') && (
                  <Alert className="border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-900/20">
                    <AlertTriangle className="h-4 w-4 text-yellow-600" />
                    <AlertTitle className="text-yellow-800 dark:text-yellow-200">系统警告</AlertTitle>
                    <AlertDescription className="text-yellow-700 dark:text-yellow-300">
                      检测到 {services.filter(s => s.status === 'offline').length} 个服务离线，
                      {services.filter(s => s.status === 'error').length} 个服务出现错误。
                      请检查服务状态并及时处理。
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            } />
          </Routes>
        </main>

        {/* 服务详情模态框 */}
        {selectedService && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
            onClick={() => setSelectedService(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white dark:bg-slate-800 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className={`p-3 rounded-lg ${selectedService.color} text-white`}>
                    {selectedService.icon}
                  </div>
                  <div>
                    <h2 className="text-xl font-bold">{selectedService.name}</h2>
                    <p className="text-slate-600 dark:text-slate-400">{selectedService.description}</p>
                  </div>
                </div>
                <Button variant="ghost" onClick={() => setSelectedService(null)}>
                  ×
                </Button>
              </div>

              <div className="space-y-6">
                <div>
                  <h3 className="font-semibold mb-3">服务状态</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex justify-between">
                      <span>状态:</span>
                      {getStatusBadge(selectedService.status)}
                    </div>
                    <div className="flex justify-between">
                      <span>端口:</span>
                      <Badge variant="outline">{selectedService.port}</Badge>
                    </div>
                    {selectedService.responseTime && (
                      <div className="flex justify-between">
                        <span>响应时间:</span>
                        <span>{Math.round(selectedService.responseTime)}ms</span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span>最后检查:</span>
                      <span className="text-sm text-slate-600">
                        {selectedService.lastCheck ? new Date(selectedService.lastCheck).toLocaleTimeString() : '-'}
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-3">服务能力</h3>
                  <div className="grid grid-cols-1 gap-2">
                    {selectedService.capabilities.map((capability, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <span className="text-sm">{capability}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {selectedService.health && (
                  <div>
                    <h3 className="font-semibold mb-3">健康信息</h3>
                    <pre className="bg-slate-100 dark:bg-slate-700 p-3 rounded text-sm overflow-x-auto">
                      {JSON.stringify(selectedService.health, null, 2)}
                    </pre>
                  </div>
                )}

                {selectedService.error && (
                  <div>
                    <h3 className="font-semibold mb-3 text-red-600">错误信息</h3>
                    <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded p-3">
                      <p className="text-red-700 dark:text-red-300">{selectedService.error}</p>
                    </div>
                  </div>
                )}

                <div className="flex space-x-3 pt-4 border-t">
                  <Button
                    variant={selectedService.status === 'running' ? 'destructive' : 'default'}
                    onClick={() => {
                      selectedService.status === 'running' ? stopService(selectedService) : startService(selectedService)
                      setSelectedService(null)
                    }}
                    className="flex-1"
                  >
                    {selectedService.status === 'running' ? '停止服务' : '启动服务'}
                  </Button>
                  <Button variant="outline" className="flex-1">
                    查看日志
                  </Button>
                  <Button variant="outline" className="flex-1">
                    配置管理
                  </Button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </div>
    </Router>
  )
}

export default App

