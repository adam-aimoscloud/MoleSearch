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

const { Title, Text } = Typography;
const { TabPane } = Tabs;
const { TextArea } = Input;

const DataManagement: React.FC = () => {
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
        message.success(`数据插入成功！处理时间: ${response.processing_time?.toFixed(3)} 秒`);
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`插入失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleBatchInsert = async (values: { batch_data: string }) => {
    try {
      setLoading(true);
      
      // 解析批量数据
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
          message.warning(`跳过无效的JSON行: ${line}`);
        }
      }
      
      if (batchData.length === 0) {
        message.error('没有有效的数据需要插入');
        return;
      }
      
      const response = await ApiService.batchInsertData({ data: batchData });
      
      if (response.success) {
        setInsertStats({ 
          count: response.inserted_count || batchData.length, 
          time: response.processing_time || 0 
        });
        message.success(`批量插入成功！插入 ${response.inserted_count} 条数据，处理时间: ${response.processing_time?.toFixed(3)} 秒`);
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`批量插入失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const sampleBatchData = `{"text": "人工智能是现代科技的重要分支", "image_url": "", "video_url": ""}
{"text": "机器学习通过数据训练模型来做出预测", "image_url": "", "video_url": ""}
{"text": "深度学习使用神经网络处理复杂数据", "image_url": "", "video_url": ""}`;

  return (
    <div>
      <Title level={2}>数据管理</Title>
      
      <Alert
        message="数据插入说明"
        description="支持插入文本、图像、视频数据。至少需要提供一种类型的内容。图像和视频支持直接输入URL或上传本地文件。"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />
      
      <Tabs defaultActiveKey="single">
        <TabPane 
          tab={
            <span>
              <PlusOutlined />
              单条插入
            </span>
          } 
          key="single"
        >
          <Card title="单条数据插入">
            <Form onFinish={handleSingleInsert} layout="vertical">
              <Row gutter={16}>
                <Col span={24}>
                  <Form.Item
                    name="text"
                    label={
                      <span>
                        <FileTextOutlined /> 文本内容
                      </span>
                    }
                  >
                    <TextArea 
                      placeholder="请输入文本内容（可选）"
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
                        <PictureOutlined /> 图像URL
                      </span>
                    }
                  >
                    <FileUploadInput
                      placeholder="请输入图像URL或上传图像文件"
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
                        <VideoCameraOutlined /> 视频URL
                      </span>
                    }
                  >
                    <FileUploadInput
                      placeholder="请输入视频URL或上传视频文件"
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
                  插入数据
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        <TabPane 
          tab={
            <span>
              <UploadOutlined />
              批量插入
            </span>
          } 
          key="batch"
        >
          <Card title="批量数据插入">
            <Alert
              message="批量插入格式"
              description="每行一个JSON对象，包含text、image_url、video_url字段。至少需要提供一种类型的内容。"
              type="warning"
              showIcon
              style={{ marginBottom: 16 }}
            />
            
            <Form onFinish={handleBatchInsert} layout="vertical">
              <Form.Item
                name="batch_data"
                label="批量数据（JSON格式）"
                rules={[{ required: true, message: '请输入批量数据' }]}
                initialValue={sampleBatchData}
              >
                <TextArea 
                  placeholder="请输入批量数据，每行一个JSON对象"
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
                    批量插入
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
                    加载示例数据
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>
      </Tabs>

      {insertStats && (
        <Card title="插入统计" style={{ marginTop: 16 }}>
          <Space direction="vertical">
            <Text>插入数据条数: {insertStats.count}</Text>
            <Text>处理时间: {insertStats.time.toFixed(3)} 秒</Text>
          </Space>
        </Card>
      )}

      <Divider />

      <Card title="数据格式说明">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Text strong>单条数据格式：</Text>
          <Text code>
            {`{
  "text": "文本内容",
  "image_url": "图像URL地址",
  "video_url": "视频URL地址"
}`}
          </Text>
          
          <Text strong>批量数据格式：</Text>
          <Text code>
            {`{"text": "第一条数据", "image_url": "", "video_url": ""}
{"text": "第二条数据", "image_url": "", "video_url": ""}
{"text": "第三条数据", "image_url": "", "video_url": ""}`}
          </Text>
          
          <Text type="secondary">
            注意：至少需要提供text、image_url、video_url中的一种内容。
          </Text>
        </Space>
      </Card>
    </div>
  );
};

export default DataManagement; 