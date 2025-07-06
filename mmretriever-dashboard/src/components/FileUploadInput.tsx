import React, { useState } from 'react';
import { Input, Button, Upload, message, Space } from 'antd';
import { UploadOutlined, LinkOutlined } from '@ant-design/icons';
import { ApiService } from '../services/api';

interface FileUploadInputProps {
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  accept?: string;
  fileType?: string;
  label?: string;
}

const FileUploadInput: React.FC<FileUploadInputProps> = ({
  value,
  onChange,
  placeholder = "请输入URL或上传文件",
  accept = "*/*",
  fileType,
  label
}) => {
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (file: File) => {
    try {
      setUploading(true);
      
      const formData = new FormData();
      formData.append('file', file);
      if (fileType) {
        formData.append('file_type', fileType);
      }

      const response = await fetch('/api/v1/files/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        message.success('文件上传成功');
        onChange?.(data.file_url);
      } else {
        message.error(`上传失败: ${data.message}`);
      }
    } catch (error: any) {
      message.error(`上传失败: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const uploadProps = {
    showUploadList: false,
    beforeUpload: (file: File) => {
      handleUpload(file);
      return false; // 阻止默认上传行为
    },
    accept,
  };

  return (
    <Space.Compact style={{ width: '100%' }}>
      <Input
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder={placeholder}
        addonBefore={label && <span>{label}</span>}
        style={{ flex: 1 }}
      />
      <Upload {...uploadProps}>
        <Button 
          icon={<UploadOutlined />} 
          loading={uploading}
          title="上传文件"
        >
          上传
        </Button>
      </Upload>
    </Space.Compact>
  );
};

export default FileUploadInput; 