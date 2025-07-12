import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Card, message, Typography } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const { Title, Text } = Typography;

interface LoginForm {
  username: string;
  password: string;
}

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated } = useAuth();

  // If user is authenticated, redirect to home page
  useEffect(() => {
    if (isAuthenticated) {
      console.log('Login: redirect to home page');
      navigate('/', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  // debug information
  useEffect(() => {
    console.log('Login: page loaded');
    console.log('Login: current path:', location.pathname);
    console.log('Login: authentication status:', isAuthenticated);
    console.log('Login: source path:', location.state?.from?.pathname);
  }, [location, isAuthenticated]);

  const onFinish = async (values: LoginForm) => {
    console.log('Login: start login process', values.username);
    setLoading(true);
    
    try {
      const success = await login(values.username, values.password);
      
      if (success) {
        console.log('Login: login successful, redirect to home page');
        message.success('Login successful!');
        
        // use setTimeout to ensure the status is updated before redirecting
        setTimeout(() => {
          console.log('Login: redirect to home page');
          const returnPath = location.state?.from?.pathname || '/';
          navigate(returnPath, { replace: true });
        }, 100);
      } else {
        console.log('Login: login failed');
        message.error('Login failed, please check username and password');
      }
    } catch (error: any) {
      console.error('Login: login error:', error);
      message.error(error.response?.data?.detail || 'Login failed, please check username and password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Card
        style={{
          width: 400,
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
          borderRadius: '12px'
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <Title level={2} style={{ color: '#1890ff', marginBottom: '8px' }}>
            MoleRetriever
          </Title>
          <Text type="secondary">Multimodal Search System</Text>
        </div>

        <Form
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          layout="vertical"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: 'Please enter username!' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Username"
              size="large"
              style={{ borderRadius: '6px' }}
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Please enter password!' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Password"
              size="large"
              style={{ borderRadius: '6px' }}
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              size="large"
              style={{
                width: '100%',
                borderRadius: '6px',
                height: '40px'
              }}
            >
              Login
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Login; 