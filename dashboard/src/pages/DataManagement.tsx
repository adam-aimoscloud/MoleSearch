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
  Col,
  Progress,
  Modal,
  Tag
} from 'antd';
import { 
  PlusOutlined, 
  UploadOutlined, 
  FileTextOutlined, 
  PictureOutlined, 
  VideoCameraOutlined,
  ClearOutlined,
  PlayCircleOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  SyncOutlined
} from '@ant-design/icons';
import { ApiService } from '../services/api';
import { 
  InsertDataRequest, 
  AsyncInsertDataRequest, 
  AsyncBatchInsertRequest,
  AsyncTaskResponse,
  TaskStatusResponse,
  TaskStatus
} from '../types/api';
import FileUploadInput from '../components/FileUploadInput';
import TaskManager from '../components/TaskManager';
import { useTranslation } from 'react-i18next';

const { Title, Text } = Typography;
const { TabPane } = Tabs;
const { TextArea } = Input;

const DataManagement: React.FC = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [insertStats, setInsertStats] = useState<{ count: number; time: number } | null>(null);
  const [singleInsertForm] = Form.useForm();
  const [asyncSingleInsertForm] = Form.useForm();
  const [asyncBatchInsertForm] = Form.useForm();
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  
  // Async task monitoring
  const [monitoringTasks, setMonitoringTasks] = useState<Map<string, TaskStatus>>(new Map());
  const [taskModalVisible, setTaskModalVisible] = useState(false);
  const [currentTask, setCurrentTask] = useState<TaskStatus | null>(null);

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

  const handleAsyncSingleInsert = async (values: AsyncInsertDataRequest) => {
    try {
      setLoading(true);
      const response = await ApiService.asyncInsertData({
        text: values.text || undefined,
        image_url: values.image_url || undefined,
        video_url: values.video_url || undefined
      });
      
      if (response.success) {
        message.success(`${t('async_task_created')}: ${response.task_id}`);
        setRefreshTrigger(prev => prev + 1);
        
        // Start monitoring the task
        startTaskMonitoring(response.task_id);
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`${t('async_insert_failed')}: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAsyncBatchInsert = async (values: { batch_data: string }) => {
    try {
      setLoading(true);
      
      // Parse batch data
      const lines = values.batch_data.trim().split('\n').filter(line => line.trim());
      const batchData: AsyncInsertDataRequest[] = [];
      
      for (const line of lines) {
        try {
          const data = JSON.parse(line);
          batchData.push({
            text: data.text || undefined,
            image_url: data.image_url || undefined,
            video_url: data.video_url || undefined
          });
        } catch (e) {
          message.warning(`${t('skip_invalid_json_line')}: ${line}`);
        }
      }
      
      if (batchData.length === 0) {
        message.error(`${t('no_valid_data_to_insert')}`);
        return;
      }
      
      const response = await ApiService.asyncBatchInsertData({ data_list: batchData });
      
      if (response.success) {
        message.success(`${t('async_batch_task_created')}: ${response.task_id}`);
        setRefreshTrigger(prev => prev + 1);
        
        // Start monitoring the task
        startTaskMonitoring(response.task_id);
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`${t('async_batch_insert_failed')}: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const startTaskMonitoring = (taskId: string) => {
    const monitorTask = async () => {
      try {
        const response = await ApiService.getTaskStatus(taskId);
        if (response.success) {
          const taskStatus = response.task_status;
          setMonitoringTasks(prev => new Map(prev.set(taskId, taskStatus)));
          
          // Continue monitoring if task is not completed
          if (taskStatus.status === 'pending' || taskStatus.status === 'processing') {
            setTimeout(() => monitorTask(), 3000); // Check every 3 seconds
          } else {
            // Task completed, show result
            if (taskStatus.status === 'completed') {
              message.success(`${t('task_completed')}: ${taskStatus.message}`);
            } else if (taskStatus.status === 'failed') {
              message.error(`${t('task_failed')}: ${taskStatus.message}`);
            }
          }
        }
      } catch (error) {
        console.error('Task monitoring error:', error);
      }
    };
    
    monitorTask();
  };

  const showTaskDetails = (task: TaskStatus) => {
    setCurrentTask(task);
    setTaskModalVisible(true);
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
            <Form form={singleInsertForm} onFinish={handleSingleInsert} layout="vertical">
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
                <Space>
                  <Button 
                    type="primary" 
                    htmlType="submit" 
                    loading={loading}
                    icon={<PlusOutlined />}
                  >
                    {t('insert_data')}
                  </Button>
                  <Button 
                    onClick={() => {
                      singleInsertForm.resetFields();
                      message.success(t('form_cleared'));
                    }}
                    icon={<ClearOutlined />}
                  >
                    {t('clear_form')}
                  </Button>
                </Space>
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

        <TabPane 
          tab={
            <span>
              <PlayCircleOutlined />
              {t('async_single_insert')}
            </span>
          } 
          key="async_single"
        >
          <Card title={t('async_single_insert')}>
            <Alert
              message={t('async_insert_info')}
              description={t('async_insert_description')}
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            
            <Form form={asyncSingleInsertForm} onFinish={handleAsyncSingleInsert} layout="vertical">
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
                <Space>
                  <Button 
                    type="primary" 
                    htmlType="submit" 
                    loading={loading}
                    icon={<PlayCircleOutlined />}
                  >
                    {t('create_async_task')}
                  </Button>
                  <Button 
                    onClick={() => {
                      asyncSingleInsertForm.resetFields();
                      message.success(t('form_cleared'));
                    }}
                    icon={<ClearOutlined />}
                  >
                    {t('clear_form')}
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        <TabPane 
          tab={
            <span>
              <UploadOutlined />
              {t('async_batch_insert')}
            </span>
          } 
          key="async_batch"
        >
          <Card title={t('async_batch_insert')}>
            <Alert
              message={t('async_batch_insert_info')}
              description={t('async_batch_insert_description')}
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            
            <Form form={asyncBatchInsertForm} onFinish={handleAsyncBatchInsert} layout="vertical">
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
                    icon={<PlayCircleOutlined />}
                  >
                    {t('create_async_batch_task')}
                  </Button>
                  <Button 
                    onClick={() => {
                      asyncBatchInsertForm.resetFields();
                      const textarea = asyncBatchInsertForm.getFieldInstance('batch_data') as HTMLTextAreaElement;
                      if (textarea) {
                        textarea.value = sampleBatchData;
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

        <TabPane 
          tab={
            <span>
              <ClockCircleOutlined />
              {t('task_management')}
            </span>
          } 
          key="tasks"
        >
          <TaskManager refreshTrigger={refreshTrigger} />
        </TabPane>
      </Tabs>

      {/* Monitoring Tasks Display */}
      {monitoringTasks.size > 0 && (
        <Card title={t('monitoring_tasks')} style={{ marginTop: 16 }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            {Array.from(monitoringTasks.values()).map(task => (
              <Card 
                key={task.task_id} 
                size="small" 
                style={{ marginBottom: 8 }}
                extra={
                  <Button 
                    type="link" 
                    size="small"
                    onClick={() => showTaskDetails(task)}
                  >
                    {t('details')}
                  </Button>
                }
              >
                <Row gutter={16} align="middle">
                  <Col span={4}>
                    <Text code style={{ fontSize: '12px' }}>
                      {task.task_id.substring(0, 8)}...
                    </Text>
                  </Col>
                  <Col span={3}>
                    <Tag color={
                      task.status === 'pending' ? 'default' :
                      task.status === 'processing' ? 'processing' :
                      task.status === 'completed' ? 'success' : 'error'
                    }>
                      {task.status}
                    </Tag>
                  </Col>
                  <Col span={8}>
                    <Progress 
                      percent={task.progress} 
                      size="small"
                      status={task.status === 'failed' ? 'exception' : undefined}
                    />
                  </Col>
                  <Col span={9}>
                    <Text ellipsis style={{ maxWidth: 200 }}>
                      {task.message}
                    </Text>
                  </Col>
                </Row>
              </Card>
            ))}
          </Space>
        </Card>
      )}

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

      {/* Task Details Modal */}
      <Modal
        title={t('task_details')}
        open={taskModalVisible}
        onCancel={() => setTaskModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setTaskModalVisible(false)}>
            {t('close')}
          </Button>
        ]}
        width={600}
      >
        {currentTask && (
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Text strong>{t('task_id')}:</Text>
              <Text code style={{ marginLeft: 8 }}>
                {currentTask.task_id}
              </Text>
            </div>
            <div>
              <Text strong>{t('status')}:</Text>
              <Tag 
                color={
                  currentTask.status === 'pending' ? 'default' :
                  currentTask.status === 'processing' ? 'processing' :
                  currentTask.status === 'completed' ? 'success' : 'error'
                }
                style={{ marginLeft: 8 }}
              >
                {currentTask.status}
              </Tag>
            </div>
            <div>
              <Text strong>{t('progress')}:</Text>
              <Progress 
                percent={currentTask.progress} 
                size="small"
                style={{ marginLeft: 8, width: 200 }}
              />
            </div>
            <div>
              <Text strong>{t('message')}:</Text>
              <Text style={{ marginLeft: 8 }}>
                {currentTask.message}
              </Text>
            </div>
            <div>
              <Text strong>{t('created_at')}:</Text>
              <Text style={{ marginLeft: 8 }}>
                {new Date(currentTask.created_at).toLocaleString()}
              </Text>
            </div>
            {currentTask.started_at && (
              <div>
                <Text strong>{t('started_at')}:</Text>
                <Text style={{ marginLeft: 8 }}>
                  {new Date(currentTask.started_at).toLocaleString()}
                </Text>
              </div>
            )}
            {currentTask.completed_at && (
              <div>
                <Text strong>{t('completed_at')}:</Text>
                <Text style={{ marginLeft: 8 }}>
                  {new Date(currentTask.completed_at).toLocaleString()}
                </Text>
              </div>
            )}
            {currentTask.result && (
              <div>
                <Text strong>{t('result')}:</Text>
                <pre style={{ 
                  marginLeft: 8, 
                  backgroundColor: '#f5f5f5', 
                  padding: 8, 
                  borderRadius: 4,
                  fontSize: '12px'
                }}>
                  {JSON.stringify(currentTask.result, null, 2)}
                </pre>
              </div>
            )}
          </Space>
        )}
      </Modal>
    </div>
  );
};

export default DataManagement; 