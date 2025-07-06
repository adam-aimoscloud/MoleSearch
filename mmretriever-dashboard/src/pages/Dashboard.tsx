import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Typography, Space, Alert } from 'antd';
import { 
  SearchOutlined, 
  DatabaseOutlined, 
  CheckCircleOutlined,
  ExclamationCircleOutlined 
} from '@ant-design/icons';
import { ApiService } from '../services/api';
import { StatusResponse } from '../types/api';

const { Title, Text } = Typography;

const Dashboard: React.FC = () => {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 30000); // 每30秒刷新一次
    return () => clearInterval(interval);
  }, []);

  const loadStatus = async () => {
    try {
      setLoading(true);
      const statusData = await ApiService.getStatus();
      setStatus(statusData);
      setError(null);
    } catch (err) {
      setError('无法连接到API服务器');
      console.error('Status load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getServiceStatus = () => {
    if (!status) return 'unknown';
    if (status.success && status.status.initialized) return 'online';
    return 'offline';
  };

  const serviceStatus = getServiceStatus();

  return (
    <div>
      <Title level={2}>系统仪表板</Title>
      
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
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="服务状态"
              value={serviceStatus === 'online' ? '在线' : '离线'}
              prefix={
                serviceStatus === 'online' ? 
                <CheckCircleOutlined style={{ color: '#52c41a' }} /> : 
                <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
              }
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
              loading={loading}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="系统信息">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text>
                <strong>初始化状态:</strong> {status?.status.initialized ? '已完成' : '未完成'}
              </Text>
              <Text>
                <strong>MMExtractor状态:</strong> {status?.status.mm_extractor ? '正常' : '异常'}
              </Text>
              <Text>
                <strong>搜索引擎状态:</strong> {status?.status.search_engine ? '正常' : '异常'}
              </Text>
              <Text>
                <strong>Elasticsearch连接:</strong> {status?.status.search_engine_connected ? '正常' : '异常'}
              </Text>
            </Space>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="快速操作">
            <Space wrap>
              <Text>点击左侧菜单进行以下操作：</Text>
              <ul>
                <li><Text strong>搜索管理</Text> - 测试文本、图像、视频搜索功能</li>
                <li><Text strong>数据管理</Text> - 插入和管理多模态数据</li>
                <li><Text strong>系统状态</Text> - 查看详细的系统状态信息</li>
              </ul>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 