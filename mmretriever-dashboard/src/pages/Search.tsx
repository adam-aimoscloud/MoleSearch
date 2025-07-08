import React, { useState, useEffect } from 'react';
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
  Spin,
  Alert,
  Pagination
} from 'antd';
import { SearchOutlined, FileTextOutlined, PictureOutlined, VideoCameraOutlined, DatabaseOutlined } from '@ant-design/icons';
import { ApiService } from '../services/api';
import { SearchResponse, SearchResultItem, DataListResponse, DataListItem } from '../types/api';
import FileUploadInput from '../components/FileUploadInput';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

const Search: React.FC = () => {
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
        message.success(`找到 ${response.total} 个结果，耗时 ${response.query_time.toFixed(3)} 秒`);
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`搜索失败: ${error.response?.data?.detail || error.message}`);
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
        message.success(`找到 ${response.total} 个结果，耗时 ${response.query_time.toFixed(3)} 秒`);
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`搜索失败: ${error.response?.data?.detail || error.message}`);
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
        message.success(`找到 ${response.total} 个结果，耗时 ${response.query_time.toFixed(3)} 秒`);
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`搜索失败: ${error.response?.data?.detail || error.message}`);
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
        message.success(`找到 ${response.total} 个结果，耗时 ${response.query_time.toFixed(3)} 秒`);
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`搜索失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 全量数据查询
  const loadDataList = async (page: number = 1, pageSize: number = 10) => {
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
        message.success(`加载了 ${response.items.length} 条数据，共 ${response.total} 条`);
      } else {
        message.error(response.message);
      }
    } catch (error: any) {
      message.error(`数据加载失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      setDataLoading(false);
    }
  };

  // 页面加载时自动加载第一页数据
  useEffect(() => {
    loadDataList();
  }, []);

  const renderResultItem = (item: SearchResultItem, index: number) => (
    <List.Item>
      <Card size="small" style={{ width: '100%' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Space>
            <Tag color="blue">#{index + 1}</Tag>
            <Tag color="green">得分: {item.score.toFixed(3)}</Tag>
            <Text strong>ID: {item.id}</Text>
          </Space>
          
          {item.text && (
            <div>
              <Text strong>文本内容:</Text>
              <Text>{item.text}</Text>
            </div>
          )}
          
          {item.image_url && (
            <div>
              <Text strong>图像:</Text>
              <div>
                <img src={item.image_url} alt="图片" style={{ maxWidth: 160, maxHeight: 120, borderRadius: 4, border: '1px solid #eee' }} />
              </div>
            </div>
          )}
          
          {item.video_url && (
            <div>
              <Text strong>视频:</Text>
              <div>
                <video src={item.video_url} controls style={{ maxWidth: 240, maxHeight: 160, borderRadius: 4, border: '1px solid #eee' }} />
              </div>
            </div>
          )}
          
          {item.image_text && (
            <div>
              <Text strong>图像文本:</Text>
              <Text type="secondary">{item.image_text}</Text>
            </div>
          )}
          
          {item.video_text && (
            <div>
              <Text strong>视频文本:</Text>
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
              <Text strong>文本内容:</Text>
              <Text>{item.text}</Text>
            </div>
          )}
          
          {item.image_url && (
            <div>
              <Text strong>图像:</Text>
              <div>
                <img src={item.image_url} alt="图片" style={{ maxWidth: 160, maxHeight: 120, borderRadius: 4, border: '1px solid #eee' }} />
              </div>
            </div>
          )}
          
          {item.video_url && (
            <div>
              <Text strong>视频:</Text>
              <div>
                <video src={item.video_url} controls style={{ maxWidth: 240, maxHeight: 160, borderRadius: 4, border: '1px solid #eee' }} />
              </div>
            </div>
          )}
          
          {item.image_text && (
            <div>
              <Text strong>图像文本:</Text>
              <Text type="secondary">{item.image_text}</Text>
            </div>
          )}
          
          {item.video_text && (
            <div>
              <Text strong>视频文本:</Text>
              <Text type="secondary">{item.video_text}</Text>
            </div>
          )}
        </Space>
      </Card>
    </List.Item>
  );

  return (
    <div>
      <Title level={2}>搜索管理</Title>
      
      <Tabs defaultActiveKey="text">
        <TabPane 
          tab={
            <span>
              <FileTextOutlined />
              文本搜索
            </span>
          } 
          key="text"
        >
          <Card title="文本搜索" style={{ marginBottom: 16 }}>
            <Form onFinish={handleTextSearch} layout="vertical">
              <Form.Item
                name="query"
                label="搜索查询"
                rules={[{ required: true, message: '请输入搜索查询' }]}
              >
                <Input.TextArea 
                  placeholder="请输入要搜索的文本内容"
                  rows={3}
                />
              </Form.Item>
              
              <Form.Item
                name="top_k"
                label="返回结果数量"
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
                  开始搜索
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        <TabPane 
          tab={
            <span>
              <PictureOutlined />
              图像搜索
            </span>
          } 
          key="image"
        >
          <Card title="图像搜索" style={{ marginBottom: 16 }}>
            <Form onFinish={handleImageSearch} layout="vertical">
              <Form.Item
                name="image_url"
                label="图像URL"
                rules={[{ required: true, message: '请输入图像URL' }]}
              >
                <FileUploadInput
                  placeholder="请输入图像URL或上传图像文件"
                  accept="image/*"
                  fileType="image"
                />
              </Form.Item>
              
              <Form.Item
                name="top_k"
                label="返回结果数量"
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
                  开始搜索
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        <TabPane 
          tab={
            <span>
              <VideoCameraOutlined />
              视频搜索
            </span>
          } 
          key="video"
        >
          <Card title="视频搜索" style={{ marginBottom: 16 }}>
            <Form onFinish={handleVideoSearch} layout="vertical">
              <Form.Item
                name="video_url"
                label="视频URL"
                rules={[{ required: true, message: '请输入视频URL' }]}
              >
                <FileUploadInput
                  placeholder="请输入视频URL或上传视频文件"
                  accept="video/*"
                  fileType="video"
                />
              </Form.Item>
              
              <Form.Item
                name="top_k"
                label="返回结果数量"
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
                  开始搜索
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        <TabPane 
          tab={
            <span>
              <SearchOutlined />
              多模态搜索
            </span>
          } 
          key="multimodal"
        >
          <Card title="多模态搜索" style={{ marginBottom: 16 }}>
            <Alert
              message="多模态搜索说明"
              description="可以同时使用文本、图像、视频进行搜索，至少需要提供一种类型的输入。支持直接输入URL或上传本地文件。"
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            
            <Form onFinish={handleMultimodalSearch} layout="vertical">
              <Form.Item
                name="text"
                label="文本查询（可选）"
              >
                <Input.TextArea 
                  placeholder="请输入文本查询"
                  rows={2}
                />
              </Form.Item>
              
              <Form.Item
                name="image_url"
                label="图像URL（可选）"
              >
                <FileUploadInput
                  placeholder="请输入图像URL或上传图像文件"
                  accept="image/*"
                  fileType="image"
                />
              </Form.Item>
              
              <Form.Item
                name="video_url"
                label="视频URL（可选）"
              >
                <FileUploadInput
                  placeholder="请输入视频URL或上传视频文件"
                  accept="video/*"
                  fileType="video"
                />
              </Form.Item>
              
              <Form.Item
                name="top_k"
                label="返回结果数量"
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
                  开始搜索
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        <TabPane 
          tab={
            <span>
              <DatabaseOutlined />
              全量数据
            </span>
          } 
          key="data"
        >
          <Card title="全量数据查看" style={{ marginBottom: 16 }}>
            <Alert
              message="全量数据查看说明"
              description="查看系统中的所有数据，支持分页浏览。数据按插入时间倒序排列。"
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
                刷新数据
              </Button>
              <Text>共 {dataPagination.total} 条数据</Text>
            </Space>
          </Card>
        </TabPane>
      </Tabs>

      {searchStats && (
        <Card title="搜索结果统计" style={{ marginBottom: 16 }}>
          <Space>
            <Text>找到 <Text strong>{searchStats.total}</Text> 个结果</Text>
            <Text>查询耗时 <Text strong>{searchStats.queryTime.toFixed(3)}</Text> 秒</Text>
          </Space>
        </Card>
      )}

      {results.length > 0 && (
        <Card title="搜索结果">
          <List
            dataSource={results}
            renderItem={renderResultItem}
            loading={loading}
          />
        </Card>
      )}

      {dataList.length > 0 && (
        <Card title="全量数据">
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
              showTotal={(total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`}
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