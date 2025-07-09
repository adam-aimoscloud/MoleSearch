import React, { useState } from 'react';
import { 
  Card, 
  Tabs, 
  Form, 
  Input, 
  Button, 
  Typography, 
  Space, 
  message,
  Alert,
  Divider,
  Row,
  Col
} from 'antd';
import { 
  PlusOutlined, 
  UploadOutlined, 
  FileTextOutlined, 
  PictureOutlined, 
  VideoCameraOutlined 
} from '@ant-design/icons';
import { ApiService } from '../services/api';
import { InsertDataRequest } from '../types/api';
import FileUploadInput from '../components/FileUploadInput';
import { useTranslation } from 'react-i18next';

const { Title, Text } = Typography;
const { TabPane } = Tabs;
const { TextArea } = Input;

const DataManagement: React.FC = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [insertStats, setInsertStats] = useState<{ count: number; time: number } | null>(null);

  const handleSingleInsert = async (values: InsertDataRequest) => {
    try {
      setLoading(true);
      const response = await ApiService.insertData({
        text: values.text || '',
        image_url: values.image_url || '',
        video_url: values.video_url || ''
      });
      
      if (response.success) {
        setInsertStats({ 
          count: response.inserted_count || 1, 
          time: response.processing_time || 0 
        });
        message.success(`${t('data')} ${t('insert_success')}: ${response.processing_time?.toFixed(3)} ${t('second')}`);
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`${t('insert_failed')}: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleBatchInsert = async (values: { batch_data: string }) => {
    try {
      setLoading(true);
      
      // Parse batch data
      const lines = values.batch_data.trim().split('\n').filter(line => line.trim());
      const batchData: InsertDataRequest[] = [];
      
      for (const line of lines) {
        try {
          const data = JSON.parse(line);
          batchData.push({
            text: data.text || '',
            image_url: data.image_url || '',
            video_url: data.video_url || ''
          });
        } catch (e) {
          message.warning(`${t('skip_invalid_json_line')}: ${line}`);
        }
      }
      
      if (batchData.length === 0) {
        message.error(`${t('no_valid_data_to_insert')}`);
        return;
      }
      
      const response = await ApiService.batchInsertData({ data: batchData });
      
      if (response.success) {
        setInsertStats({ 
          count: response.inserted_count || batchData.length, 
          time: response.processing_time || 0 
        });
        message.success(`${t('batch_insert_success')}: ${response.inserted_count} ${t('data')}, ${t('processing_time')}: ${response.processing_time?.toFixed(3)} ${t('second')}`);
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`${t('batch_insert_failed')}: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const sampleBatchData = `{"text": "Artificial intelligence is an important branch of modern technology", "image_url": "", "video_url": ""}
{"text": "Machine learning uses data training models to make predictions", "image_url": "", "video_url": ""}
{"text": "Deep learning uses neural networks to process complex data", "image_url": "", "video_url": ""}`;

  return (
    <div>
      <Title level={2}>{t('data_management')}</Title>
      
      <Tabs defaultActiveKey="single">
        <TabPane 
          tab={
            <span>
              <PlusOutlined />
              {t('single_insert')}
            </span>
          } 
          key="single"
        >
          <Card title={t('single_insert')}>
            <Form onFinish={handleSingleInsert} layout="vertical">
              <Row gutter={16}>
                <Col span={24}>
                  <Form.Item
                    name="text"
                    label={
                      <span>
                        <FileTextOutlined /> {t('text_content')}
                      </span>
                    }
                  >
                    <TextArea 
                      placeholder={t('text_content') + t('optional')}
                      rows={4}
                    />
                  </Form.Item>
                </Col>
              </Row>
              
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="image_url"
                    label={
                      <span>
                        <PictureOutlined /> {t('image')}
                      </span>
                    }
                  >
                    <FileUploadInput
                      placeholder={t('image') + t('url')}
                      accept="image/*"
                      fileType="image"
                    />
                  </Form.Item>
                </Col>
                
                <Col span={12}>
                  <Form.Item
                    name="video_url"
                    label={
                      <span>
                        <VideoCameraOutlined /> {t('video')}
                      </span>
                    }
                  >
                    <FileUploadInput
                      placeholder={t('video') + t('url')}
                      accept="video/*"
                      fileType="video"
                    />
                  </Form.Item>
                </Col>
              </Row>
              
              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  loading={loading}
                  icon={<PlusOutlined />}
                >
                  {t('insert_data')}
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        <TabPane 
          tab={
            <span>
              <UploadOutlined />
              {t('batch_insert')}
            </span>
          } 
          key="batch"
        >
          <Card title={t('batch_insert')}>
            <Alert
              message={t('batch_insert') + t('info')}
              description={t('batch_insert') + t('info')}
              type="warning"
              showIcon
              style={{ marginBottom: 16 }}
            />
            
            <Form onFinish={handleBatchInsert} layout="vertical">
              <Form.Item
                name="batch_data"
                label={t('batch_insert') + t('json_format')}
                rules={[{ required: true, message: t('batch_insert') + t('json_format') }]}
                initialValue={sampleBatchData}
              >
                <TextArea 
                  placeholder={t('batch_insert') + t('json_format')}
                  rows={10}
                />
              </Form.Item>
              
              <Form.Item>
                <Space>
                  <Button 
                    type="primary" 
                    htmlType="submit" 
                    loading={loading}
                    icon={<UploadOutlined />}
                  >
                    {t('batch_insert')}
                  </Button>
                  <Button 
                    onClick={() => {
                      const form = document.querySelector('form');
                      if (form) {
                        const textarea = form.querySelector('textarea');
                        if (textarea) {
                          (textarea as HTMLTextAreaElement).value = sampleBatchData;
                        }
                      }
                    }}
                  >
                    {t('load_sample')}
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>
      </Tabs>

      {insertStats && (
        <Card title={t('insert_stats')} style={{ marginTop: 16 }}>
          <Space direction="vertical">
            <Text>{t('inserted_data_count')}: {insertStats.count}</Text>
            <Text>{t('processing_time')}: {insertStats.time.toFixed(3)} {t('second')}</Text>
          </Space>
        </Card>
      )}

      <Divider />

      <Card title={t('data_format_description')}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Text strong>{t('single_data_format')}:</Text>
          <Text code>
            {`{
  "text": "Text content",
  "image_url": "Image URL address",
  "video_url": "Video URL address"
}`}
          </Text>
          
          <Text strong>{t('batch_data_format')}:</Text>
          <Text code>
            {`{"text": "First data", "image_url": "", "video_url": ""}
{"text": "Second data", "image_url": "", "video_url": ""}
{"text": "Third data", "image_url": "", "video_url": ""}`}
          </Text>
          
          <Text type="secondary">
            {t('note')}: {t('at_least_one_type_of_content_is_required')}.
          </Text>
        </Space>
      </Card>
    </div>
  );
};

export default DataManagement; 