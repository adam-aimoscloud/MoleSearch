import React, { useState, useEffect, useCallback } from 'react';
import { 
  Card, 
  Tabs, 
  Form, 
  Input, 
  Button, 
  List, 
  Typography, 
  Space, 
  Tag, 
  message,
  Alert,
  Pagination
} from 'antd';
import { SearchOutlined, FileTextOutlined, PictureOutlined, VideoCameraOutlined, DatabaseOutlined } from '@ant-design/icons';
import { ApiService } from '../services/api';
import { SearchResultItem, DataListItem } from '../types/api';
import FileUploadInput from '../components/FileUploadInput';
import { useTranslation } from 'react-i18next';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

const Search: React.FC = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [searchStats, setSearchStats] = useState<{ total: number; queryTime: number } | null>(null);
  
  // 全量数据状态
  const [dataList, setDataList] = useState<DataListItem[]>([]);
  const [dataLoading, setDataLoading] = useState(false);
  const [dataPagination, setDataPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });

  const handleTextSearch = async (values: { query: string; top_k: number }) => {
    try {
      setLoading(true);
      const response = await ApiService.searchText({
        query: values.query,
        top_k: values.top_k || 10
      });
      
      if (response.success) {
        setResults(response.results);
        setSearchStats({ total: response.total, queryTime: response.query_time });
        message.success(`${t('found')} ${response.total} ${t('results')}, ${t('query_time')}: ${response.query_time.toFixed(3)} ${t('seconds')}`);
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`${t('search_failed')}: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleImageSearch = async (values: { image_url: string; top_k: number }) => {
    try {
      setLoading(true);
      const response = await ApiService.searchImage({
        image_url: values.image_url,
        top_k: values.top_k || 10
      });
      
      if (response.success) {
        setResults(response.results);
        setSearchStats({ total: response.total, queryTime: response.query_time });
        message.success(`${t('found')} ${response.total} ${t('results')}, ${t('query_time')}: ${response.query_time.toFixed(3)} ${t('seconds')}`);
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`${t('search_failed')}: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleVideoSearch = async (values: { video_url: string; top_k: number }) => {
    try {
      setLoading(true);
      const response = await ApiService.searchVideo({
        video_url: values.video_url,
        top_k: values.top_k || 10
      });
      
      if (response.success) {
        setResults(response.results);
        setSearchStats({ total: response.total, queryTime: response.query_time });
        message.success(`${t('found')} ${response.total} ${t('results')}, ${t('query_time')}: ${response.query_time.toFixed(3)} ${t('seconds')}`);
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`${t('search_failed')}: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleMultimodalSearch = async (values: { 
    text?: string; 
    image_url?: string; 
    video_url?: string; 
    top_k: number 
  }) => {
    try {
      setLoading(true);
      const response = await ApiService.searchMultimodal({
        text: values.text || undefined,
        image_url: values.image_url || undefined,
        video_url: values.video_url || undefined,
        top_k: values.top_k || 10
      });
      
      if (response.success) {
        setResults(response.results);
        setSearchStats({ total: response.total, queryTime: response.query_time });
        message.success(`${t('found')} ${response.total} ${t('results')}, ${t('query_time')}: ${response.query_time.toFixed(3)} ${t('seconds')}`);
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`${t('search_failed')}: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Load all data
  const loadDataList = useCallback(async (page: number = 1, pageSize: number = 10) => {
    try {
      setDataLoading(true);
      const response = await ApiService.listData({
        page,
        page_size: pageSize
      });
      
      if (response.success) {
        setDataList(response.items);
        setDataPagination({
          current: page,
          pageSize,
          total: response.total
        });
        message.success(`${t('loaded')} ${response.items.length} ${t('data_items')}, ${t('total')}: ${response.total}`);
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`${t('data_load_failed')}: ${error.response?.data?.detail || error.message}`);
    } finally {
      setDataLoading(false);
    }
  }, [t]);

  // Load first page data when page loads
  useEffect(() => {
    loadDataList();
  }, [loadDataList]);

  const renderResultItem = (item: SearchResultItem, index: number) => (
    <List.Item>
      <Card size="small" style={{ width: '100%' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Space>
            <Tag color="blue">#{index + 1}</Tag>
            <Tag color="green">Score: {item.score.toFixed(3)}</Tag>
            <Text strong>ID: {item.id}</Text>
          </Space>
          
          {item.text && (
            <div>
              <Text strong>Text content:</Text>
              <Text>{item.text}</Text>
            </div>
          )}
          
          {item.image_url && (
            <div>
              <Text strong>Image:</Text>
              <div>
                <img src={item.image_url} alt="Search result" style={{ maxWidth: 160, maxHeight: 120, borderRadius: 4, border: '1px solid #eee' }} />
              </div>
            </div>
          )}
          
          {item.video_url && (
            <div>
              <Text strong>Video:</Text>
              <div>
                <video src={item.video_url} controls style={{ maxWidth: 240, maxHeight: 160, borderRadius: 4, border: '1px solid #eee' }} />
              </div>
            </div>
          )}
          
          {item.image_text && (
            <div>
              <Text strong>Image text:</Text>
              <Text type="secondary">{item.image_text}</Text>
            </div>
          )}
          
          {item.video_text && (
            <div>
              <Text strong>Video text:</Text>
              <Text type="secondary">{item.video_text}</Text>
            </div>
          )}
        </Space>
      </Card>
    </List.Item>
  );

  const renderDataItem = (item: DataListItem, index: number) => (
    <List.Item>
      <Card size="small" style={{ width: '100%' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Space>
            <Tag color="blue">#{index + 1}</Tag>
            <Text strong>ID: {item.id}</Text>
          </Space>
          
          {item.text && (
            <div>
              <Text strong>Text content:</Text>
              <Text>{item.text}</Text>
            </div>
          )}
          
          {item.image_url && (
            <div>
              <Text strong>Image:</Text>
              <div>
                <img src={item.image_url} alt="Data item" style={{ maxWidth: 160, maxHeight: 120, borderRadius: 4, border: '1px solid #eee' }} />
              </div>
            </div>
          )}
          
          {item.video_url && (
            <div>
              <Text strong>Video:</Text>
              <div>
                <video src={item.video_url} controls style={{ maxWidth: 240, maxHeight: 160, borderRadius: 4, border: '1px solid #eee' }} />
              </div>
            </div>
          )}
          
          {item.image_text && (
            <div>
              <Text strong>Image text:</Text>
              <Text type="secondary">{item.image_text}</Text>
            </div>
          )}
          
          {item.video_text && (
            <div>
              <Text strong>Video text:</Text>
              <Text type="secondary">{item.video_text}</Text>
            </div>
          )}
        </Space>
      </Card>
    </List.Item>
  );

  return (
    <div>
      <Title level={2}>{t('search_management')}</Title>
      
      <Tabs defaultActiveKey="text">
        <TabPane 
          tab={
            <span>
              <FileTextOutlined />
              {t('text_search')}
            </span>
          } 
          key="text"
        >
          <Card title={t('text_search')} style={{ marginBottom: 16 }}>
            <Form onFinish={handleTextSearch} layout="vertical">
              <Form.Item
                name="query"
                label={t('search_query')}
                rules={[{ required: true, message: t('search_query') }]}
              >
                <Input.TextArea 
                  placeholder={t('text_content')}
                  rows={3}
                />
              </Form.Item>
              
              <Form.Item
                name="top_k"
                label={t('result_count')}
                initialValue={10}
              >
                <Input type="number" min={1} max={100} />
              </Form.Item>
              
              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  loading={loading}
                  icon={<SearchOutlined />}
                >
                  {t('start_search')}
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        <TabPane 
          tab={
            <span>
              <PictureOutlined />
              {t('image_search')}
            </span>
          } 
          key="image"
        >
          <Card title={t('image_search')} style={{ marginBottom: 16 }}>
            <Form onFinish={handleImageSearch} layout="vertical">
              <Form.Item
                name="image_url"
                label={t('image') + 'URL'}
                rules={[{ required: true, message: t('image') + 'URL' }]}
              >
                <FileUploadInput
                  placeholder={t('image') + 'URL'}
                  accept="image/*"
                  fileType="image"
                />
              </Form.Item>
              
              <Form.Item
                name="top_k"
                label={t('result_count')}
                initialValue={10}
              >
                <Input type="number" min={1} max={100} />
              </Form.Item>
              
              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  loading={loading}
                  icon={<SearchOutlined />}
                >
                  {t('start_search')}
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        <TabPane 
          tab={
            <span>
              <VideoCameraOutlined />
              {t('video_search')}
            </span>
          } 
          key="video"
        >
          <Card title={t('video_search')} style={{ marginBottom: 16 }}>
            <Form onFinish={handleVideoSearch} layout="vertical">
              <Form.Item
                name="video_url"
                label={t('video') + 'URL'}
                rules={[{ required: true, message: t('video') + 'URL' }]}
              >
                <FileUploadInput
                  placeholder={t('video') + 'URL'}
                  accept="video/*"
                  fileType="video"
                />
              </Form.Item>
              
              <Form.Item
                name="top_k"
                label={t('result_count')}
                initialValue={10}
              >
                <Input type="number" min={1} max={100} />
              </Form.Item>
              
              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  loading={loading}
                  icon={<SearchOutlined />}
                >
                  {t('start_search')}
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        <TabPane 
          tab={
            <span>
              <SearchOutlined />
              {t('multimodal_search')}
            </span>
          } 
          key="multimodal"
        >
          <Card title={t('multimodal_search')} style={{ marginBottom: 16 }}>
            <Alert
              message={t('multimodal_search') + t('info')}
              description={t('multimodal_search') + t('info')}
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            
            <Form onFinish={handleMultimodalSearch} layout="vertical">
              <Form.Item
                name="text"
                label={t('text_content') + '（' + t('optional') + '）'}
              >
                <Input.TextArea 
                  placeholder={t('text_content')}
                  rows={2}
                />
              </Form.Item>
              
              <Form.Item
                name="image_url"
                label={t('image') + 'URL（' + t('optional') + '）'}
              >
                <FileUploadInput
                  placeholder={t('image') + 'URL'}
                  accept="image/*"
                  fileType="image"
                />
              </Form.Item>
              
              <Form.Item
                name="video_url"
                label={t('video') + 'URL（' + t('optional') + '）'}
              >
                <FileUploadInput
                  placeholder={t('video') + 'URL'}
                  accept="video/*"
                  fileType="video"
                />
              </Form.Item>
              
              <Form.Item
                name="top_k"
                label={t('result_count')}
                initialValue={10}
              >
                <Input type="number" min={1} max={100} />
              </Form.Item>
              
              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  loading={loading}
                  icon={<SearchOutlined />}
                >
                  {t('start_search')}
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        <TabPane 
          tab={
            <span>
              <DatabaseOutlined />
              {t('all_data')}
            </span>
          } 
          key="data"
        >
          <Card title={t('all_data')} style={{ marginBottom: 16 }}>
            <Alert
              message={t('all_data') + t('info')}
              description={t('all_data') + t('info')}
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            
            <Space style={{ marginBottom: 16 }}>
              <Button 
                type="primary" 
                onClick={() => loadDataList(dataPagination.current, dataPagination.pageSize)}
                loading={dataLoading}
                icon={<DatabaseOutlined />}
              >
                {t('refresh')}
              </Button>
              <Text>{t('total', { count: dataPagination.total })}</Text>
            </Space>
          </Card>
        </TabPane>
      </Tabs>

      {searchStats && (
        <Card title={t('search_stats')} style={{ marginBottom: 16 }}>
          <Space>
            <Text>{t('found')} <Text strong>{searchStats.total}</Text> {t('results')}</Text>
            <Text>{t('query_time')}: <Text strong>{searchStats.queryTime.toFixed(3)}</Text> {t('seconds')}</Text>
          </Space>
        </Card>
      )}

      {results.length > 0 && (
        <Card title={t('search_results')}>
          <List
            dataSource={results}
            renderItem={renderResultItem}
            loading={loading}
          />
        </Card>
      )}

      {dataList.length > 0 && (
        <Card title={t('all_data')}>
          <List
            dataSource={dataList}
            renderItem={renderDataItem}
            loading={dataLoading}
          />
          <div style={{ textAlign: 'center', marginTop: 16 }}>
            <Pagination
              current={dataPagination.current}
              pageSize={dataPagination.pageSize}
              total={dataPagination.total}
              showSizeChanger
              showQuickJumper
              showTotal={(total, range) => `${t('page_range', { start: range[0], end: range[1], total: total })}`}
              onChange={(page, pageSize) => {
                loadDataList(page, pageSize);
              }}
              onShowSizeChange={(current, size) => {
                loadDataList(1, size);
              }}
            />
          </div>
        </Card>
      )}
    </div>
  );
};

export default Search; 