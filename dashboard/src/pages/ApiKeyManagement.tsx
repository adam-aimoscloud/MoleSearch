import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Button, 
  Table, 
  Modal, 
  Form, 
  Input, 
  Typography, 
  Space, 
  message,
  Tag,
  Tooltip,
  Alert,
  Divider,
  Row,
  Col,
  Popconfirm
} from 'antd';
import { 
  PlusOutlined, 
  DeleteOutlined, 
  CopyOutlined,
  KeyOutlined,
  ClockCircleOutlined,
  EyeOutlined,
  EyeInvisibleOutlined
} from '@ant-design/icons';
import { ApiService } from '../services/api';
import { ApiKeyInfo, CreateApiKeyRequest } from '../types/api';
import { useTranslation } from 'react-i18next';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

const ApiKeyManagement: React.FC = () => {
  const { t } = useTranslation();
  const [apiKeys, setApiKeys] = useState<ApiKeyInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [showKey, setShowKey] = useState<string | null>(null);

  useEffect(() => {
    loadApiKeys();
  }, []);

  const loadApiKeys = async () => {
    try {
      setLoading(true);
      const response = await ApiService.listApiKeys();
      if (response.success) {
        setApiKeys(response.api_keys);
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`Failed to load API keys: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateApiKey = async (values: CreateApiKeyRequest) => {
    try {
      setLoading(true);
      const response = await ApiService.createApiKey(values);
      if (response.success) {
        message.success('API key created successfully');
        setModalVisible(false);
        form.resetFields();
        loadApiKeys();
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`Failed to create API key: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteApiKey = async (keyId: string) => {
    try {
      const response = await ApiService.deleteApiKey(keyId);
      if (response.success) {
        message.success('API key deleted successfully');
        loadApiKeys();
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`Failed to delete API key: ${error.response?.data?.detail || error.message}`);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    message.success('Copied to clipboard');
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusTag = (apiKey: ApiKeyInfo) => {
    if (apiKey.expires_at) {
      const expiresAt = new Date(apiKey.expires_at);
      const now = new Date();
      if (now > expiresAt) {
        return <Tag color="red">Expired</Tag>;
      } else if (expiresAt.getTime() - now.getTime() < 7 * 24 * 60 * 60 * 1000) {
        return <Tag color="orange">Expiring Soon</Tag>;
      }
    }
    return <Tag color="green">Active</Tag>;
  };

  const columns = [
    {
      title: t('name'),
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <Text strong>{text}</Text>
    },
    {
      title: t('api_key'),
      dataIndex: 'key',
      key: 'key',
      render: (text: string, record: ApiKeyInfo) => (
        <Space>
          <Text code style={{ fontSize: '12px' }}>
            {showKey === record.key_id ? text : `${text.substring(0, 8)}...`}
          </Text>
          <Button
            type="text"
            size="small"
            icon={showKey === record.key_id ? <EyeInvisibleOutlined /> : <EyeOutlined />}
            onClick={() => setShowKey(showKey === record.key_id ? null : record.key_id)}
          />
          <Button
            type="text"
            size="small"
            icon={<CopyOutlined />}
            onClick={() => copyToClipboard(text)}
          />
        </Space>
      )
    },
    {
      title: t('status'),
      key: 'status',
      render: (record: ApiKeyInfo) => getStatusTag(record)
    },
    {
      title: t('created_at'),
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text: string) => formatDateTime(text)
    },
    {
      title: t('expires_at'),
      dataIndex: 'expires_at',
      key: 'expires_at',
      render: (text: string) => text ? formatDateTime(text) : t('never')
    },
    {
      title: t('last_used_at'),
      dataIndex: 'last_used_at',
      key: 'last_used_at',
      render: (text: string) => text ? formatDateTime(text) : t('never')
    },
    {
      title: t('actions'),
      key: 'actions',
      render: (record: ApiKeyInfo) => (
        <Popconfirm
          title={t('delete_api_key_confirm')}
          onConfirm={() => handleDeleteApiKey(record.key_id)}
          okText={t('yes')}
          cancelText={t('no')}
        >
          <Button 
            type="text" 
            danger 
            icon={<DeleteOutlined />}
            size="small"
          >
            {t('delete')}
          </Button>
        </Popconfirm>
      )
    }
  ];

  const curlExample = (apiKey: string) => `curl -X POST "http://localhost:8000/api/v1/search/text" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer ${apiKey}" \\
  -d '{
    "query": "artificial intelligence",
    "top_k": 10
  }'`;

  return (
    <div>
      <Title level={2}>
        <KeyOutlined /> {t('api_key_management')}
      </Title>

      <Card 
        title={t('api_keys')}
        extra={
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={() => setModalVisible(true)}
          >
            {t('create_api_key')}
          </Button>
        }
      >
        <Alert
          message={t('api_key_info')}
          description={t('api_key_description')}
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />

        <Table
          dataSource={apiKeys}
          columns={columns}
          rowKey="key_id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* Create API Key Modal */}
      <Modal
        title={t('create_api_key')}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateApiKey}
          initialValues={{
            expires_in_days: undefined,
            permissions: []
          }}
        >
          <Form.Item
            name="name"
            label={t('api_key_name')}
            rules={[{ required: true, message: t('api_key_name_required') }]}
          >
            <Input placeholder={t('enter_api_key_name')} />
          </Form.Item>

          <Form.Item
            name="expires_in_days"
            label={t('expiration_days')}
          >
            <Input 
              type="number" 
              placeholder={t('leave_empty_for_permanent')}
              min={1}
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={loading}
                icon={<PlusOutlined />}
              >
                {t('create')}
              </Button>
              <Button 
                onClick={() => {
                  setModalVisible(false);
                  form.resetFields();
                }}
              >
                {t('cancel')}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Usage Examples */}
      <Card title={t('usage_examples')} style={{ marginTop: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>{t('curl_example')}:</Text>
            <Paragraph>
              <pre style={{ background: '#f5f5f5', padding: 8, borderRadius: 4, fontSize: 13, margin: 0 }}>
                {apiKeys.length > 0 ? curlExample(apiKeys[0].key) : `curl -X POST "http://localhost:8000/api/v1/search/text" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "query": "artificial intelligence",
    "top_k": 10
  }'`}
              </pre>
            </Paragraph>
          </div>

          <Divider />

          <div>
            <Text strong>{t('python_example')}:</Text>
            <Paragraph>
              <Text code>
                {`import requests

api_key = "YOUR_API_KEY"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

response = requests.post(
    "http://localhost:8000/api/v1/search/text",
    headers=headers,
    json={
        "query": "artificial intelligence",
        "top_k": 10
    }
)

print(response.json())`}
              </Text>
            </Paragraph>
          </div>

          <Divider />

          <div>
            <Text strong>{t('javascript_example')}:</Text>
            <Paragraph>
              <Text code>
                {`const apiKey = "YOUR_API_KEY";

fetch("http://localhost:8000/api/v1/search/text", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": \`Bearer \${apiKey}\`
  },
  body: JSON.stringify({
    query: "artificial intelligence",
    top_k: 10
  })
})
.then(response => response.json())
.then(data => console.log(data));`}
              </Text>
            </Paragraph>
          </div>
        </Space>
      </Card>
    </div>
  );
};

export default ApiKeyManagement; 