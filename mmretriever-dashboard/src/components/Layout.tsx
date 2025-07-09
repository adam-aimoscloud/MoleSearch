import React, { useState } from 'react';
import { Layout, Menu, theme, Select } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  SearchOutlined,
  DatabaseOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

const { Header, Sider, Content } = Layout;

interface LayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<LayoutProps> = ({ children }) => {
  const [collapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();
  const { i18n, t } = useTranslation();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: t('dashboard'),
    },
    {
      key: '/search',
      icon: <SearchOutlined />,
      label: t('search'),
    },
    {
      key: '/data',
      icon: <DatabaseOutlined />,
      label: t('data'),
    },
    {
      key: '/status',
      icon: <SettingOutlined />,
      label: t('status'),
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        theme="dark"
      >
        <div className="logo">
          {collapsed ? 'MM' : 'MMRetriever'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: 0, background: colorBgContainer, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            height: '100%',
            paddingLeft: 16,
            fontSize: 18,
            fontWeight: 'bold'
          }}>
            MMRetriever API Dashboard
          </div>
          <div style={{ paddingRight: 24 }}>
            <Select
              value={i18n.language}
              onChange={lng => i18n.changeLanguage(lng)}
              style={{ width: 100 }}
              options={[
                { value: 'zh', label: '中文' },
                { value: 'en', label: 'English' }
              ]}
            />
          </div>
        </Header>
        <Content
          style={{
            margin: '24px 16px',
            padding: 24,
            minHeight: 280,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
          }}
        >
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout; 