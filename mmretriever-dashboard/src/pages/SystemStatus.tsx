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
import { useTranslation } from 'react-i18next';

const { Title, Text } = Typography;

const SystemStatus: React.FC = () => {
  const { t } = useTranslation();
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
      setError('Cannot connect to API server');
      console.error('Status load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 30000); // Refresh every 30 seconds
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
        <Title level={2}>{t('status')}</Title>
        <Button icon={<ReloadOutlined />} onClick={loadStatus} loading={loading}>{t('refresh')}</Button>
      </Space>

      {error && (
        <Alert
          message={t('error')}
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card title={t('overallStatus')}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Space>
                <Tag 
                  color={overallStatus === 'healthy' ? 'green' : overallStatus === 'warning' ? 'orange' : 'red'}
                  icon={overallStatus === 'healthy' ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}
                >
                  {overallStatus === 'healthy' ? t('systemHealthy') : overallStatus === 'warning' ? t('systemWarning') : t('systemError')}
                </Tag>
                <Text>{t('lastUpdated')}: {new Date().toLocaleString()}</Text>
              </Space>
              
              {health && (
                <Text>
                  <strong>{t('healthCheck')}:</strong> {health.status}
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
              title={t('initializationStatus')}
              value={status?.status.initialized ? t('completed') : t('notCompleted')}
              prefix={getStatusIcon(status?.status.initialized || false)}
              valueStyle={{ color: getStatusColor(status?.status.initialized || false) }}
              loading={loading}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('mmExtractor')}
              value={status?.status.mm_extractor ? t('normal') : t('abnormal')}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: getStatusColor(status?.status.mm_extractor || false) }}
              loading={loading}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('searchEngine')}
              value={status?.status.search_engine ? t('normal') : t('abnormal')}
              prefix={<SearchOutlined />}
              valueStyle={{ color: getStatusColor(status?.status.search_engine || false) }}
              loading={loading}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('esConnection')}
              value={status?.status.search_engine_connected ? t('normal') : t('abnormal')}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: getStatusColor(status?.status.search_engine_connected || false) }}
              loading={loading}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title={t('detailedStatus')}>
            <Descriptions bordered column={2}>
              <Descriptions.Item label={t('serviceStatus')}>
                <Tag color={status?.success ? 'green' : 'red'}>
                  {status?.success ? t('normal') : t('abnormal')}
                </Tag>
              </Descriptions.Item>
              
              <Descriptions.Item label={t('initializationStatus')}>
                <Tag color={getStatusColor(status?.status.initialized || false)}>
                  {status?.status.initialized ? t('completed') : t('notCompleted')}
                </Tag>
              </Descriptions.Item>
              
              <Descriptions.Item label={t('mmExtractorStatus')}>
                <Tag color={getStatusColor(status?.status.mm_extractor || false)}>
                  {status?.status.mm_extractor ? t('normal') : t('abnormal')}
                </Tag>
              </Descriptions.Item>
              
              <Descriptions.Item label={t('searchEngineStatus')}>
                <Tag color={getStatusColor(status?.status.search_engine || false)}>
                  {status?.status.search_engine ? t('normal') : t('abnormal')}
                </Tag>
              </Descriptions.Item>
              
              <Descriptions.Item label={t('esConnectionStatus')}>
                <Tag color={getStatusColor(status?.status.search_engine_connected || false)}>
                  {status?.status.search_engine_connected ? t('normal') : t('abnormal')}
                </Tag>
              </Descriptions.Item>
              
              <Descriptions.Item label={t('healthCheck')}>
                <Tag color={health?.status === 'healthy' ? 'green' : 'red'}>
                  {health?.status || t('unknown')}
                </Tag>
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title={t('systemComponents')}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>{t('fastApiServer')}</Text>
                <Tag color="green" style={{ marginLeft: 8 }}>{t('running')}</Tag>
              </div>
              
              <div>
                <Text strong>{t('elasticsearch')}</Text>
                <Tag color={getStatusColor(status?.status.search_engine_connected || false)} style={{ marginLeft: 8 }}>
                  {status?.status.search_engine_connected ? t('connected') : t('disconnected')}
                </Tag>
              </div>
              
              <div>
                <Text strong>{t('mmExtractorPlugin')}</Text>
                <Tag color={getStatusColor(status?.status.mm_extractor || false)} style={{ marginLeft: 8 }}>
                  {status?.status.mm_extractor ? t('loaded') : t('unloaded')}
                </Tag>
              </div>
              
              <div>
                <Text strong>{t('searchService')}</Text>
                <Tag color={getStatusColor(status?.status.search_engine || false)} style={{ marginLeft: 8 }}>
                  {status?.status.search_engine ? t('available') : t('unavailable')}
                </Tag>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>

      <Divider />

      <Card title={t('troubleshooting')}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Alert
            message={t('commonIssues')}
            description={t('checkItems')}
            type="info"
            showIcon
          />
          
          <ul>
            <li><Text strong>{t('esConnectionFailed')}:</Text> {t('checkEsService')}</li>
            <li><Text strong>{t('mmExtractorFailed')}:</Text> {t('checkConfigFile')}</li>
            <li><Text strong>{t('searchServiceFailed')}:</Text> {t('checkEsIndex')}</li>
            <li><Text strong>{t('apiSlow')}:</Text> {t('checkNetwork')}</li>
          </ul>
          
          <Text type="secondary">
            {t('moreHelp')}
          </Text>
        </Space>
      </Card>
    </div>
  );
};

export default SystemStatus; 