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
  placeholder = "Enter URL or upload file",
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
        message.success('File uploaded successfully');
        onChange?.(data.file_url);
      } else {
        message.error(`Upload failed: ${data.message}`);
      }
    } catch (error: any) {
      message.error(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const uploadProps = {
    showUploadList: false,
    beforeUpload: (file: File) => {
      handleUpload(file);
      return false; // Prevent default upload behavior
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
          title="Upload file"
        >
          Upload
        </Button>
      </Upload>
    </Space.Compact>
  );
};

export default FileUploadInput; 