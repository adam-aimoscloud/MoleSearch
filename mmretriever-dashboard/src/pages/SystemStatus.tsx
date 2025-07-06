import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Typography, 
  Space, 
  Tag, 
  Alert,
  Button,
  Descriptions,
  Divider,
  Statistic
} from 'antd';
import { 
  CheckCircleOutlined, 
  ExclamationCircleOutlined,
  ReloadOutlined,
  DatabaseOutlined,
  SearchOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { ApiService } from '../services/api';
import { StatusResponse, HealthResponse } from '../types/api';

const { Title, Text } = Typography;

const SystemStatus: React.FC = () => {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [statusData, healthData] = await Promise.all([
        ApiService.getStatus(),
        ApiService.getHealth()
      ]);
      
      setStatus(statusData);
      setHealth(healthData);
    } catch (err: any) {
      setError('无法连接到API服务器');
      console.error('Status load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 30000); // 每30秒刷新一次
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: boolean) => status ? 'green' : 'red';
  const getStatusIcon = (status: boolean) => 
    status ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />;

  const getOverallStatus = () => {
    if (!status) return 'unknown';
    if (status.success && 
        status.status.initialized && 
        status.status.mm_extractor && 
        status.status.search_engine && 
        status.status.search_engine_connected) {
      return 'healthy';
    }
    return 'warning';
  };

  const overallStatus = getOverallStatus();

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Title level={2}>系统状态</Title>
        <Button 
          icon={<ReloadOutlined />} 
          onClick={loadStatus}
          loading={loading}
        >
          刷新状态
        </Button>
      </Space>

      {error && (
        <Alert
          message="连接错误"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card title="整体状态">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Space>
                <Tag 
                  color={overallStatus === 'healthy' ? 'green' : overallStatus === 'warning' ? 'orange' : 'red'}
                  icon={overallStatus === 'healthy' ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}
                >
                  {overallStatus === 'healthy' ? '系统正常' : overallStatus === 'warning' ? '部分异常' : '系统异常'}
                </Tag>
                <Text>最后更新: {new Date().toLocaleString()}</Text>
              </Space>
              
              {health && (
                <Text>
                  <strong>健康检查:</strong> {health.status}
                </Text>
              )}
            </Space>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="初始化状态"
              value={status?.status.initialized ? '已完成' : '未完成'}
              prefix={getStatusIcon(status?.status.initialized || false)}
              valueStyle={{ color: getStatusColor(status?.status.initialized || false) }}
              loading={loading}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="MMExtractor"
              value={status?.status.mm_extractor ? '正常' : '异常'}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: getStatusColor(status?.status.mm_extractor || false) }}
              loading={loading}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="搜索引擎"
              value={status?.status.search_engine ? '正常' : '异常'}
              prefix={<SearchOutlined />}
              valueStyle={{ color: getStatusColor(status?.status.search_engine || false) }}
              loading={loading}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="ES连接"
              value={status?.status.search_engine_connected ? '正常' : '异常'}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: getStatusColor(status?.status.search_engine_connected || false) }}
              loading={loading}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="详细状态信息">
            <Descriptions bordered column={2}>
              <Descriptions.Item label="服务状态">
                <Tag color={status?.success ? 'green' : 'red'}>
                  {status?.success ? '正常' : '异常'}
                </Tag>
              </Descriptions.Item>
              
              <Descriptions.Item label="初始化状态">
                <Tag color={getStatusColor(status?.status.initialized || false)}>
                  {status?.status.initialized ? '已完成' : '未完成'}
                </Tag>
              </Descriptions.Item>
              
              <Descriptions.Item label="MMExtractor状态">
                <Tag color={getStatusColor(status?.status.mm_extractor || false)}>
                  {status?.status.mm_extractor ? '正常' : '异常'}
                </Tag>
              </Descriptions.Item>
              
              <Descriptions.Item label="搜索引擎状态">
                <Tag color={getStatusColor(status?.status.search_engine || false)}>
                  {status?.status.search_engine ? '正常' : '异常'}
                </Tag>
              </Descriptions.Item>
              
              <Descriptions.Item label="ES连接状态">
                <Tag color={getStatusColor(status?.status.search_engine_connected || false)}>
                  {status?.status.search_engine_connected ? '正常' : '异常'}
                </Tag>
              </Descriptions.Item>
              
              <Descriptions.Item label="健康检查">
                <Tag color={health?.status === 'healthy' ? 'green' : 'red'}>
                  {health?.status || '未知'}
                </Tag>
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="系统组件">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>FastAPI服务器</Text>
                <Tag color="green" style={{ marginLeft: 8 }}>运行中</Tag>
              </div>
              
              <div>
                <Text strong>Elasticsearch</Text>
                <Tag color={getStatusColor(status?.status.search_engine_connected || false)} style={{ marginLeft: 8 }}>
                  {status?.status.search_engine_connected ? '已连接' : '未连接'}
                </Tag>
              </div>
              
              <div>
                <Text strong>MMExtractor插件</Text>
                <Tag color={getStatusColor(status?.status.mm_extractor || false)} style={{ marginLeft: 8 }}>
                  {status?.status.mm_extractor ? '已加载' : '未加载'}
                </Tag>
              </div>
              
              <div>
                <Text strong>搜索服务</Text>
                <Tag color={getStatusColor(status?.status.search_engine || false)} style={{ marginLeft: 8 }}>
                  {status?.status.search_engine ? '可用' : '不可用'}
                </Tag>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>

      <Divider />

      <Card title="故障排除">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Alert
            message="常见问题"
            description="如果系统状态显示异常，请检查以下项目："
            type="info"
            showIcon
          />
          
          <ul>
            <li><Text strong>Elasticsearch连接失败:</Text> 检查ES服务是否启动，端口9200是否可访问</li>
            <li><Text strong>MMExtractor初始化失败:</Text> 检查配置文件是否正确，API密钥是否有效</li>
            <li><Text strong>搜索服务异常:</Text> 检查ES索引是否存在，数据是否已插入</li>
            <li><Text strong>API响应缓慢:</Text> 检查网络连接，服务器资源使用情况</li>
          </ul>
          
          <Text type="secondary">
            如需更多帮助，请查看服务器日志或联系系统管理员。
          </Text>
        </Space>
      </Card>
    </div>
  );
};

export default SystemStatus; 