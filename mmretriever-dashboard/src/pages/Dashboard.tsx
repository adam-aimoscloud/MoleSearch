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
import { useTranslation } from 'react-i18next';

const { Title, Text } = Typography;

const Dashboard: React.FC = () => {
  const { t } = useTranslation();
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
      <Title level={2}>{t('dashboard')}</Title>
      
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
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('service_status')}
              value={serviceStatus === 'online' ? t('online') : t('offline')}
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
              title={t('mm_extractor')}
              value={status?.status.mm_extractor ? t('success') : t('error')}
              prefix={<DatabaseOutlined />}
              loading={loading}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('search_engine')}
              value={status?.status.search_engine ? t('success') : t('error')}
              prefix={<SearchOutlined />}
              loading={loading}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('es_connection')}
              value={status?.status.search_engine_connected ? t('success') : t('error')}
              prefix={<DatabaseOutlined />}
              loading={loading}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title={t('system_info')}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text>
                <strong>{t('init_status')}:</strong> {status?.status.initialized ? t('success') : t('error')}
              </Text>
              <Text>
                <strong>{t('mm_extractor')}:</strong> {status?.status.mm_extractor ? t('success') : t('error')}
              </Text>
              <Text>
                <strong>{t('search_engine')}:</strong> {status?.status.search_engine ? t('success') : t('error')}
              </Text>
              <Text>
                <strong>{t('es_connection')}:</strong> {status?.status.search_engine_connected ? t('success') : t('error')}
              </Text>
            </Space>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title={t('quick_actions')}>
            <Space wrap>
              <Text>{t('operation')}:</Text>
              <ul>
                <li><Text strong>{t('search')}</Text> - {t('text_search')}, {t('image_search')}, {t('video_search')}</li>
                <li><Text strong>{t('data')}</Text> - {t('insert_data')}, {t('batch_insert')}</li>
                <li><Text strong>{t('status')}</Text> - {t('system_info')}</li>
              </ul>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 