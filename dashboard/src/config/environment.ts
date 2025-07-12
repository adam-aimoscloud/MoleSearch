// Environment Configuration
export interface EnvironmentConfig {
  apiBaseUrl: string;
  environment: string;
  isDevelopment: boolean;
  isProduction: boolean;
  isTest: boolean;
}

// Environment variable configuration interface
export interface EnvVarConfig {
  description: string;
  examples?: string[];
  values?: string[];
  default: string;
}

// Get environment configuration
export const getEnvironmentConfig = (): EnvironmentConfig => {
  const environment = process.env.NODE_ENV || 'development';
  const apiBaseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';
  
  return {
    apiBaseUrl,
    environment,
    isDevelopment: environment === 'development',
    isProduction: environment === 'production',
    isTest: environment === 'test',
  };
};

// Export current environment configuration
export const envConfig = getEnvironmentConfig();

// Environment variables documentation
export const ENVIRONMENT_VARIABLES: Record<string, EnvVarConfig> = {
  REACT_APP_API_BASE_URL: {
    description: 'Backend API base URL',
    examples: [
      'http://localhost:8000/api/v1 (development)',
      '/api/v1 (production, same domain)',
      'https://api.example.com/api/v1 (production, different domain)',
    ],
    default: 'http://localhost:8000/api/v1',
  },
  NODE_ENV: {
    description: 'Environment type',
    values: ['development', 'production', 'test'],
    default: 'development',
  },
};

// Log environment configuration
console.log('Environment Configuration:', {
  environment: envConfig.environment,
  apiBaseUrl: envConfig.apiBaseUrl,
  isDevelopment: envConfig.isDevelopment,
  isProduction: envConfig.isProduction,
}); 