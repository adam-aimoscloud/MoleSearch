import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Search from './pages/Search';
import DataManagement from './pages/DataManagement';
import SystemStatus from './pages/SystemStatus';
import './App.css';

const App: React.FC = () => {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/search" element={<Search />} />
            <Route path="/data" element={<DataManagement />} />
            <Route path="/status" element={<SystemStatus />} />
          </Routes>
        </Layout>
      </Router>
    </ConfigProvider>
  );
};

export default App; 