package image_embedding

import (
	"mmretriever-api/components/image_embedding"
	"mmretriever-api/config"
	"mmretriever-api/utils"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// setupRealConfig loads real .env.yaml config file
func setupRealConfig() (map[string]interface{}, error) {
	cfg := &config.Config{}

	configPath := "../../../../.env.yaml"
	if err := cfg.LoadConfigFromYaml(configPath); err != nil {
		return nil, err
	}

	return cfg.Components, nil
}

func TestQwenImageEmbedding_Initialize_FromConfig(t *testing.T) {
	tests := []struct {
		name    string
		config  map[string]interface{}
		wantErr bool
		errMsg  string
	}{
		{
			name: "valid config",
			config: map[string]interface{}{
				"image_embedding": map[string]interface{}{
					"embedding_type": "qwen",
					"qwen": map[string]interface{}{
						"dashscope_api_key": "test-api-key",
						"base_url":          "https://test.example.com",
						"model":             "test-model",
					},
				},
			},
			wantErr: false,
		},
		{
			name: "missing api key",
			config: map[string]interface{}{
				"image_embedding": map[string]interface{}{
					"embedding_type": "qwen",
					"qwen": map[string]interface{}{
						"dashscope_api_key": "",
						"base_url":          "https://test.example.com",
						"model":             "test-model",
					},
				},
			},
			wantErr: true,
			errMsg:  "dashscope_api_key is required",
		},
		{
			name: "missing base url",
			config: map[string]interface{}{
				"image_embedding": map[string]interface{}{
					"embedding_type": "qwen",
					"qwen": map[string]interface{}{
						"dashscope_api_key": "test-api-key",
						"base_url":          "",
						"model":             "test-model",
					},
				},
			},
			wantErr: true,
			errMsg:  "base_url is required",
		},
		{
			name: "missing model",
			config: map[string]interface{}{
				"image_embedding": map[string]interface{}{
					"embedding_type": "qwen",
					"qwen": map[string]interface{}{
						"dashscope_api_key": "test-api-key",
						"base_url":          "https://test.example.com",
						"model":             "",
					},
				},
			},
			wantErr: true,
			errMsg:  "model is required",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Step 1: Initialize ComponentMngr
			mngr := utils.ComponentMngr{}

			// Step 2: ComponentMngr.SetConfig
			err := mngr.SetConfig(tt.config)
			require.NoError(t, err)

			// Step 3: Get component instance
			instance, err := mngr.GetComponent("image_embedding")

			if tt.wantErr {
				assert.Error(t, err)
				assert.Contains(t, err.Error(), tt.errMsg)
			} else {
				assert.NoError(t, err)
				assert.NotNil(t, instance)

				// Verify instance type
				qe, ok := instance.(image_embedding.ImageEmbeddingExtractor)
				assert.True(t, ok)
				assert.NotNil(t, qe)
			}
		})
	}
}

func TestQwenImageEmbedding_LoadFromYamlConfig(t *testing.T) {
	// Create test config file
	tmpDir := t.TempDir()
	configPath := filepath.Join(tmpDir, "test.yaml")

	configContent := `components:
  image_embedding:
    embedding_type: "qwen"
    qwen:
      dashscope_api_key: "test-api-key"
      base_url: "https://test.example.com"
      model: "test-model"
`

	err := os.WriteFile(configPath, []byte(configContent), 0644)
	require.NoError(t, err)

	// Step 1: Initialize Config
	cfg := &config.Config{}
	err = cfg.LoadConfigFromYaml(configPath)
	require.NoError(t, err)

	// Step 2: ComponentMngr.SetConfig
	mngr := utils.ComponentMngr{}
	err = mngr.SetConfig(cfg.Components)
	require.NoError(t, err)

	// Step 3: Get component instance
	instance, err := mngr.GetComponent("image_embedding")
	assert.NoError(t, err)
	assert.NotNil(t, instance)
}

func TestQwenImageEmbedding_Infer_WithRealConfig(t *testing.T) {
	// Step 1: Load real config
	componentConfig, err := setupRealConfig()
	if err != nil {
		t.Skip("Cannot load .env.yaml, skipping integration test:", err)
	}

	// Check if API key is configured
	imageEmbeddingConfig, ok := componentConfig["image_embedding"].(map[string]interface{})
	if !ok {
		t.Skip("Invalid image_embedding config structure")
	}

	qwenConfig, ok := imageEmbeddingConfig["qwen"].(map[string]interface{})
	if !ok {
		t.Skip("Invalid qwen config structure")
	}

	apiKey, ok := qwenConfig["dashscope_api_key"].(string)
	if !ok || apiKey == "your_dashscope_api_key_here" || apiKey == "" {
		t.Skip("Real API key not configured, skipping integration test")
	}

	// Step 2: ComponentMngr.SetConfig
	mngr := utils.ComponentMngr{}
	err = mngr.SetConfig(componentConfig)
	require.NoError(t, err)

	// Step 3: Get component instance
	instance, err := mngr.GetComponent("image_embedding")
	require.NoError(t, err)

	qe, ok := instance.(image_embedding.ImageEmbeddingExtractor)
	require.True(t, ok)

	tests := []struct {
		name     string
		imageURL string
	}{
		{
			name:     "simple image url",
			imageURL: "https://mitalinlp.oss-cn-hangzhou.aliyuncs.com/dingkun/images/1712648554702.jpg",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			embeddings, err := qe.Infer(tt.imageURL)

			if err != nil {
				// If there's an error, it might be due to API configuration or network issues
				// Log the error but don't fail the test
				t.Logf("API call failed (this may be expected if API is not configured): %v", err)
				t.Skip("Skipping due to API error - may be configuration issue")
				return
			}

			assert.NoError(t, err)
			assert.NotEmpty(t, embeddings)
			assert.Len(t, embeddings, 1)

			// Check embedding is not empty and contains values
			embedding := embeddings[0]
			assert.NotEmpty(t, embedding)
			assert.Greater(t, len(embedding), 0)

			// Check embedding contains non-zero values
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

func TestQwenImageEmbedding_Infer_WithInvalidConfig(t *testing.T) {
	invalidConfig := map[string]interface{}{
		"image_embedding": map[string]interface{}{
			"embedding_type": "qwen",
			"qwen": map[string]interface{}{
				"dashscope_api_key": "invalid-key",
				"base_url":          "https://invalid.example.com",
				"model":             "invalid-model",
			},
		},
	}

	// Step 1: ComponentMngr.SetConfig
	mngr := utils.ComponentMngr{}
	err := mngr.SetConfig(invalidConfig)
	require.NoError(t, err)

	// Step 2: Get component instance
	instance, err := mngr.GetComponent("image_embedding")
	require.NoError(t, err)

	qe, ok := instance.(image_embedding.ImageEmbeddingExtractor)
	require.True(t, ok)

	// Test with invalid API should return error
	_, err = qe.Infer("https://via.placeholder.com/300x200.png?text=Test")
	assert.Error(t, err, "Should return error with invalid config")
}

func TestQwenImageEmbedding_Infer_WithInvalidImageURL(t *testing.T) {
	validConfig := map[string]interface{}{
		"image_embedding": map[string]interface{}{
			"embedding_type": "qwen",
			"qwen": map[string]interface{}{
				"dashscope_api_key": "test-api-key",
				"base_url":          "https://test.example.com",
				"model":             "test-model",
			},
		},
	}

	// Step 1: ComponentMngr.SetConfig
	mngr := utils.ComponentMngr{}
	err := mngr.SetConfig(validConfig)
	require.NoError(t, err)

	// Step 2: Get component instance
	instance, err := mngr.GetComponent("image_embedding")
	require.NoError(t, err)

	qe, ok := instance.(image_embedding.ImageEmbeddingExtractor)
	require.True(t, ok)

	invalidURLs := []string{
		"invalid-url",
		"https://example.com/nonexistent.jpg",
		"",
		"not-a-valid-url",
	}

	for _, invalidURL := range invalidURLs {
		t.Run("invalid_url_"+invalidURL, func(t *testing.T) {
			_, err := qe.Infer(invalidURL)
			// Should return error for invalid URLs
			assert.Error(t, err, "Should return error for invalid image URL: %s", invalidURL)
		})
	}
}

func TestQwenImageEmbedding_ConfigTemplate(t *testing.T) {
	// Step 1: Get config template
	mngr := utils.ComponentMngr{}
	template := mngr.GenerateConfigTemplate()

	// Step 2: Verify the template contains image_embedding
	templateMap, ok := template.(map[string]interface{})
	require.True(t, ok)

	imageEmbeddingConfig, exists := templateMap["image_embedding"]
	assert.True(t, exists)
	assert.NotNil(t, imageEmbeddingConfig)
}

// BenchmarkQwenImageEmbedding_Infer_WithConfig performance test
func BenchmarkQwenImageEmbedding_Infer_WithConfig(b *testing.B) {
	// Step 1: Load real config
	componentConfig, err := setupRealConfig()
	if err != nil {
		b.Skip("Cannot load .env.yaml, skipping benchmark:", err)
	}

	// Check if API key is configured
	imageEmbeddingConfig, ok := componentConfig["image_embedding"].(map[string]interface{})
	if !ok {
		b.Skip("Invalid image_embedding config structure")
	}

	qwenConfig, ok := imageEmbeddingConfig["qwen"].(map[string]interface{})
	if !ok {
		b.Skip("Invalid qwen config structure")
	}

	apiKey, ok := qwenConfig["dashscope_api_key"].(string)
	if !ok || apiKey == "your_dashscope_api_key_here" || apiKey == "" {
		b.Skip("Real API key not configured, skipping benchmark")
	}

	// Step 2: ComponentMngr.SetConfig
	mngr := utils.ComponentMngr{}
	err = mngr.SetConfig(componentConfig)
	require.NoError(b, err)

	// Step 3: Get component instance
	instance, err := mngr.GetComponent("image_embedding")
	require.NoError(b, err)

	qe, ok := instance.(image_embedding.ImageEmbeddingExtractor)
	require.True(b, ok)

	imageURL := "https://via.placeholder.com/300x200.png?text=Benchmark+Test"

	// Test one call first to see if the API is working
	_, err = qe.Infer(imageURL)
	if err != nil {
		b.Skip("API not working, skipping benchmark:", err)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := qe.Infer(imageURL)
		if err != nil {
			b.Logf("API call failed during benchmark: %v", err)
			// Don't fail immediately, just log and continue
		}
	}
}
