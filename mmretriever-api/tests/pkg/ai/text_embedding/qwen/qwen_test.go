package qwen

import (
	"mmretriever-api/config"
	"mmretriever-api/pkg/ai/text_embedding"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// setupTestConfig create test config file
func setupTestConfig(t *testing.T) (string, func()) {
	// create temporary config file
	tmpDir := t.TempDir()
	configPath := filepath.Join(tmpDir, "test.yaml")

	configContent := `embedding:
  embedding_type: "qwen"
  qwen:
    dashscope_api_key: "test-api-key"
    base_url: "https://test.example.com"
    model: "test-model"
`

	err := os.WriteFile(configPath, []byte(configContent), 0644)
	require.NoError(t, err)

	// return cleanup function
	cleanup := func() {
		os.RemoveAll(tmpDir)
	}

	return configPath, cleanup
}

// setupRealConfig load real .env.yaml config file
func setupRealConfig() (text_embedding.QwenConfig, error) {
	cfg := config.NewConfig()

	configPath := "../../../../../.env.yaml"

	if err := cfg.LoadConfigFromYaml(configPath); err != nil {
		return text_embedding.QwenConfig{}, err
	}

	return cfg.GetQwenConfig(), nil
}

func TestQwenTextEmbedding_Initialize_FromConfig(t *testing.T) {
	tests := []struct {
		name       string
		configYaml string
		wantErr    bool
		errMsg     string
	}{
		{
			name: "valid config",
			configYaml: `embedding:
  embedding_type: "qwen"
  qwen:
    dashscope_api_key: "test-api-key"
    base_url: "https://test.example.com"
    model: "test-model"`,
			wantErr: false,
		},
		{
			name: "missing api key",
			configYaml: `embedding:
  embedding_type: "qwen"
  qwen:
    dashscope_api_key: ""
    base_url: "https://test.example.com"
    model: "test-model"`,
			wantErr: true,
			errMsg:  "dashscope_api_key is required",
		},
		{
			name: "missing base url",
			configYaml: `embedding:
  embedding_type: "qwen"
  qwen:
    dashscope_api_key: "test-api-key"
    base_url: ""
    model: "test-model"`,
			wantErr: true,
			errMsg:  "base_url is required",
		},
		{
			name: "missing model",
			configYaml: `embedding:
  embedding_type: "qwen"
  qwen:
    dashscope_api_key: "test-api-key"
    base_url: "https://test.example.com"
    model: ""`,
			wantErr: true,
			errMsg:  "model is required",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// create temporary config file
			tmpDir := t.TempDir()
			configPath := filepath.Join(tmpDir, "test.yaml")
			err := os.WriteFile(configPath, []byte(tt.configYaml), 0644)
			require.NoError(t, err)

			// load config
			cfg := config.NewConfig()
			err = cfg.LoadConfigFromYaml(configPath)
			require.NoError(t, err)

			qwenConfig := cfg.GetQwenConfig()

			// test initialize
			qe := &text_embedding.QwenTextEmbedding{}
			err = qe.Initialize(qwenConfig)

			if tt.wantErr {
				assert.Error(t, err)
				assert.Equal(t, tt.errMsg, err.Error())
			} else {
				assert.NoError(t, err)
				assert.Equal(t, qwenConfig, qe.Config)
			}
		})
	}
}

func TestQwenTextEmbedding_LoadFromYamlConfig(t *testing.T) {
	configPath, cleanup := setupTestConfig(t)
	defer cleanup()

	// load config
	cfg := config.NewConfig()
	err := cfg.LoadConfigFromYaml(configPath)
	require.NoError(t, err)

	qwenConfig := cfg.GetQwenConfig()

	// check config values
	assert.Equal(t, "test-api-key", qwenConfig.DashscopeAPIKey)
	assert.Equal(t, "https://test.example.com", qwenConfig.BaseURL)
	assert.Equal(t, "test-model", qwenConfig.Model)

	// test initialize
	qe := &text_embedding.QwenTextEmbedding{}
	err = qe.Initialize(qwenConfig)
	assert.NoError(t, err)
	assert.Equal(t, qwenConfig, qe.Config)
}

func TestQwenTextEmbedding_TextEmbedding_WithRealConfig(t *testing.T) {
	// try to load real config
	realConfig, err := setupRealConfig()
	if err != nil {
		t.Skip("Cannot load .env.yaml, skipping integration test:", err)
	}

	// if API Key is default value, skip test
	if realConfig.DashscopeAPIKey == "your_dashscope_api_key_here" || realConfig.DashscopeAPIKey == "" {
		t.Skip("Real API key not configured, skipping integration test")
	}

	qe := &text_embedding.QwenTextEmbedding{}
	err = qe.Initialize(realConfig)
	require.NoError(t, err)

	tests := []struct {
		name string
		text string
	}{
		{
			name: "simple text",
			text: "Hello, world!",
		},
		{
			name: "chinese text",
			text: "你好世界",
		},
		{
			name: "longer text",
			text: "This is a longer text for testing embedding generation. It contains multiple sentences and should be properly processed by the embedding model.",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			embeddings, err := qe.Infer(tt.text)

			assert.NoError(t, err)
			assert.NotEmpty(t, embeddings)
			assert.Len(t, embeddings, 1)

			// check embedding is not empty and contains values
			embedding := embeddings[0]
			assert.NotEmpty(t, embedding)
			assert.Greater(t, len(embedding), 0)

			// check embedding contains non-zero values
			hasNonZero := false
			for _, val := range embedding {
				if val != 0 {
					hasNonZero = true
					break
				}
			}
			assert.True(t, hasNonZero, "Embedding should contain non-zero values")
		})
	}
}

func TestQwenTextEmbedding_TextEmbedding_WithInvalidConfig(t *testing.T) {
	// use invalid config
	invalidConfigYaml := `embedding:
  embedding_type: "qwen"
  qwen:
    dashscope_api_key: "invalid-key"
    base_url: "https://invalid.example.com"
    model: "invalid-model"`

	tmpDir := t.TempDir()
	configPath := filepath.Join(tmpDir, "invalid.yaml")
	err := os.WriteFile(configPath, []byte(invalidConfigYaml), 0644)
	require.NoError(t, err)

	cfg := config.NewConfig()
	err = cfg.LoadConfigFromYaml(configPath)
	require.NoError(t, err)

	qwenConfig := cfg.GetQwenConfig()

	qe := &text_embedding.QwenTextEmbedding{}
	err = qe.Initialize(qwenConfig)
	require.NoError(t, err)

	_, err = qe.Infer("test text")
	assert.Error(t, err, "Should return error with invalid config")
}

// BenchmarkQwenEmbedding_TextEmbedding_WithConfig performance test
func BenchmarkQwenEmbedding_TextEmbedding_WithConfig(b *testing.B) {
	realConfig, err := setupRealConfig()
	if err != nil || realConfig.DashscopeAPIKey == "your_dashscope_api_key_here" || realConfig.DashscopeAPIKey == "" {
		b.Skip("Real API key not configured, skipping benchmark")
	}

	qe := &text_embedding.QwenTextEmbedding{}
	err = qe.Initialize(realConfig)
	require.NoError(b, err)

	text := "This is a test text for benchmarking embedding generation performance."

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := qe.Infer(text)
		if err != nil {
			b.Fatal(err)
		}
	}
}
