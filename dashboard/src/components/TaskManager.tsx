import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Tag, 
  Progress, 
  Button, 
  Space, 
  Typography, 
  Tooltip,
  Badge,
  Alert
} from 'antd';
import { 
  ReloadOutlined, 
  ClockCircleOutlined, 
  CheckCircleOutlined, 
  ExclamationCircleOutlined,
  SyncOutlined,
  PlayCircleOutlined
} from '@ant-design/icons';
import { ApiService } from '../services/api';
import { TaskStatus } from '../types/api';
import { useTranslation } from 'react-i18next';

const { Title, Text } = Typography;

interface TaskManagerProps {
  refreshTrigger?: number;
}

const TaskManager: React.FC<TaskManagerProps> = ({ refreshTrigger }) => {
  const { t } = useTranslation();
  const [tasks, setTasks] = useState<TaskStatus[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTasks();
  }, [refreshTrigger]);

  const loadTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await ApiService.getPendingTasks();
      if (response.success) {
        setTasks(response.tasks);
      } else {
        setError(response.message);
      }
    } catch (err: any) {
      setError('Failed to load pending tasks');
      console.error('Task load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'default';
      case 'processing':
        return 'processing';
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <ClockCircleOutlined />;
      case 'processing':
        return <SyncOutlined spin />;
      case 'completed':
        return <CheckCircleOutlined />;
      case 'failed':
        return <ExclamationCircleOutlined />;
      default:
        return <ClockCircleOutlined />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return t('pending');
      case 'processing':
        return t('processing');
      case 'completed':
        return t('completed');
      case 'failed':
        return t('failed');
      default:
        return status;
    }
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const columns = [
    {
      title: t('task_id'),
      dataIndex: 'task_id',
      key: 'task_id',
      width: 200,
      render: (text: string) => (
        <Text code style={{ fontSize: '12px' }}>
          {text.substring(0, 8)}...
        </Text>
      )
    },
    {
      title: t('status'),
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => (
        <Tag color={getStatusColor(status)} icon={getStatusIcon(status)}>
          {getStatusText(status)}
        </Tag>
      )
    },
    {
      title: t('progress'),
      dataIndex: 'progress',
      key: 'progress',
      width: 200,
      render: (progress: number, record: TaskStatus) => (
        <Progress 
          percent={progress} 
          size="small" 
          status={record.status === 'failed' ? 'exception' : undefined}
        />
      )
    },
    {
      title: t('message'),
      dataIndex: 'message',
      key: 'message',
      render: (text: string) => (
        <Tooltip title={text}>
          <Text ellipsis style={{ maxWidth: 200 }}>
            {text}
          </Text>
        </Tooltip>
      )
    },
    {
      title: t('created_at'),
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (text: string) => formatDateTime(text)
    },
    {
      title: t('duration'),
      key: 'duration',
      width: 100,
      render: (record: TaskStatus) => {
        const start = record.started_at ? new Date(record.started_at) : new Date(record.created_at);
        const end = record.completed_at ? new Date(record.completed_at) : new Date();
        const duration = Math.round((end.getTime() - start.getTime()) / 1000);
        return `${duration}s`;
      }
    },
    {
      title: t('actions'),
      key: 'actions',
      width: 100,
      render: (record: TaskStatus) => (
        <Space>
          {record.status === 'completed' && record.result && (
            <Tooltip title={t('view_result')}>
              <Button 
                type="link" 
                size="small"
                icon={<CheckCircleOutlined />}
              >
                {t('result')}
              </Button>
            </Tooltip>
          )}
        </Space>
      )
    }
  ];

  // Only show pending tasks
  const pendingTasks = tasks.filter(task => task.status === 'pending');

  return (
    <div>
      <Card 
        title={
          <Space>
            <PlayCircleOutlined />
            {t('task_management')}
          </Space>
        }
        extra={
          <Button 
            icon={<ReloadOutlined />} 
            onClick={loadTasks}
            loading={loading}
          >
            {t('refresh')}
          </Button>
        }
      >
        {error && (
          <Alert
            message={error}
            type="error"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}

        <Space direction="vertical" style={{ width: '100%' }}>
          {/* Pending Tasks */}
          <div>
            <Title level={4}>
              <Badge count={pendingTasks.length} showZero>
                {t('pending_tasks')}
              </Badge>
            </Title>
            <Table
              dataSource={pendingTasks}
              columns={columns}
              rowKey="task_id"
              pagination={false}
              size="small"
              loading={loading}
            />
          </div>
        </Space>
      </Card>
    </div>
  );
};

export default TaskManager; 