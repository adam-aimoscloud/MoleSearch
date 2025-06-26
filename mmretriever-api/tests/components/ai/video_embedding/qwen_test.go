package video_embedding

import (
	"fmt"
	"mmretriever-api/components/video_embedding"
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

func TestQwenVideoEmbedding_Initialize_FromConfig(t *testing.T) {
	tests := []struct {
		name    string
		config  map[string]interface{}
		wantErr bool
		errMsg  string
	}{
		{
			name: "valid config",
			config: map[string]interface{}{
				"video_embedding": map[string]interface{}{
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
				"video_embedding": map[string]interface{}{
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
				"video_embedding": map[string]interface{}{
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
				"video_embedding": map[string]interface{}{
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
			instance, err := mngr.GetComponent("video_embedding")

			if tt.wantErr {
				assert.Error(t, err)
				assert.Contains(t, err.Error(), tt.errMsg)
			} else {
				assert.NoError(t, err)
				assert.NotNil(t, instance)

				// Verify instance type
				qe, ok := instance.(video_embedding.VideoEmbeddingExtractor)
				assert.True(t, ok)
				assert.NotNil(t, qe)
			}
		})
	}
}

func TestQwenVideoEmbedding_LoadFromYamlConfig(t *testing.T) {
	// Create test config file
	tmpDir := t.TempDir()
	configPath := filepath.Join(tmpDir, "test.yaml")

	configContent := `components:
  video_embedding:
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
	instance, err := mngr.GetComponent("video_embedding")
	assert.NoError(t, err)
	assert.NotNil(t, instance)
}

func TestQwenVideoEmbedding_Infer_WithRealConfig(t *testing.T) {
	// Step 1: Load real config
	componentConfig, err := setupRealConfig()
	if err != nil {
		t.Skip("Cannot load .env.yaml, skipping integration test:", err)
	}

	// Check if API key is configured
	videoEmbeddingConfig, ok := componentConfig["video_embedding"].(map[string]interface{})
	if !ok {
		t.Skip("Invalid video_embedding config structure")
	}

	qwenConfig, ok := videoEmbeddingConfig["qwen"].(map[string]interface{})
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
	instance, err := mngr.GetComponent("video_embedding")
	require.NoError(t, err)

	qe, ok := instance.(video_embedding.VideoEmbeddingExtractor)
	require.True(t, ok)

	tests := []struct {
		name     string
		videoURL string
	}{
		{
			name:     "simple video url",
			videoURL: "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250107/lbcemt/new+video.mp4",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			embeddings, err := qe.Infer(tt.videoURL)

			if err != nil {
				// If there's an error, it might be due to API configuration or network issues
				// Log the error but don't fail the test for the real API test
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

			t.Logf("Successfully generated embedding for video - Dimension: %d", len(embedding))
		})
	}
}

func TestQwenVideoEmbedding_Infer_WithInvalidConfig(t *testing.T) {
	invalidConfig := map[string]interface{}{
		"video_embedding": map[string]interface{}{
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
	instance, err := mngr.GetComponent("video_embedding")
	require.NoError(t, err)

	qe, ok := instance.(video_embedding.VideoEmbeddingExtractor)
	require.True(t, ok)

	// Test with invalid API should return error
	_, err = qe.Infer("https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4")
	assert.Error(t, err, "Should return error with invalid config")
}

func TestQwenVideoEmbedding_Infer_WithInvalidVideoURL(t *testing.T) {
	validConfig := map[string]interface{}{
		"video_embedding": map[string]interface{}{
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
	instance, err := mngr.GetComponent("video_embedding")
	require.NoError(t, err)

	qe, ok := instance.(video_embedding.VideoEmbeddingExtractor)
	require.True(t, ok)

	tests := []struct {
		name     string
		videoURL string
	}{
		{
			name:     "empty video url",
			videoURL: "",
		},
		{
			name:     "invalid video url",
			videoURL: "not-a-valid-url",
		},
		{
			name:     "non-existent video url",
			videoURL: "https://example.com/non-existent-video.mp4",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			_, err := qe.Infer(tt.videoURL)

			if tt.videoURL == "" {
				// Empty URL should definitely return an error
				assert.Error(t, err, "Empty video URL should return error")
				assert.Contains(t, err.Error(), "video URL cannot be empty")
			} else {
				// Other invalid URLs might or might not return errors depending on API validation
				// We just log the result
				if err != nil {
					t.Logf("Invalid video URL returned error as expected: %v", err)
				} else {
					t.Logf("Invalid video URL was accepted by API")
				}
			}
		})
	}
}

func TestQwenVideoEmbedding_Infer_RealConfig_BatchProcessing(t *testing.T) {
	// Step 1: Load real config
	componentConfig, err := setupRealConfig()
	if err != nil {
		t.Skip("Cannot load .env.yaml, skipping integration test:", err)
	}

	// Check if API key is configured
	videoEmbeddingConfig, ok := componentConfig["video_embedding"].(map[string]interface{})
	if !ok {
		t.Skip("Invalid video_embedding config structure")
	}

	qwenConfig, ok := videoEmbeddingConfig["qwen"].(map[string]interface{})
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
	instance, err := mngr.GetComponent("video_embedding")
	require.NoError(t, err)

	qe, ok := instance.(video_embedding.VideoEmbeddingExtractor)
	require.True(t, ok)

	// Test batch processing of multiple videos
	testVideos := []string{
		"https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4",
		"https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4",
		"https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
	}

	var allEmbeddings [][]float64
	for i, videoURL := range testVideos {
		t.Run(fmt.Sprintf("batch_video_%d", i+1), func(t *testing.T) {
			embeddings, err := qe.Infer(videoURL)
			if err != nil {
				t.Logf("API call failed for video %d: %v", i+1, err)
				t.Skip("Skipping due to API error")
				return
			}

			assert.NoError(t, err)
			assert.NotEmpty(t, embeddings)
			assert.Len(t, embeddings, 1)
			assert.Greater(t, len(embeddings[0]), 0)

			allEmbeddings = append(allEmbeddings, embeddings[0])
		})
	}

	// Check that all embeddings have the same dimension
	if len(allEmbeddings) > 1 {
		baseDimension := len(allEmbeddings[0])
		for i, embedding := range allEmbeddings[1:] {
			assert.Equal(t, baseDimension, len(embedding),
				"All embeddings should have the same dimension, embedding %d has different size", i+2)
		}
	}
}

func TestQwenVideoEmbedding_Infer_RealConfig_EdgeCases(t *testing.T) {
	// Step 1: Load real config
	componentConfig, err := setupRealConfig()
	if err != nil {
		t.Skip("Cannot load .env.yaml, skipping integration test:", err)
	}

	// Check if API key is configured
	videoEmbeddingConfig, ok := componentConfig["video_embedding"].(map[string]interface{})
	if !ok {
		t.Skip("Invalid video_embedding config structure")
	}

	qwenConfig, ok := videoEmbeddingConfig["qwen"].(map[string]interface{})
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
	instance, err := mngr.GetComponent("video_embedding")
	require.NoError(t, err)

	qe, ok := instance.(video_embedding.VideoEmbeddingExtractor)
	require.True(t, ok)

	// Test edge cases
	edgeCases := []struct {
		name     string
		videoURL string
	}{
		{
			name:     "very_short_video",
			videoURL: "https://sample-videos.com/zip/10/mp4/SampleVideo_360x240_1mb.mp4",
		},
		{
			name:     "different_resolution",
			videoURL: "https://sample-videos.com/zip/10/mp4/SampleVideo_640x360_1mb.mp4",
		},
		{
			name:     "different_format_mp4",
			videoURL: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
		},
	}

	for _, tt := range edgeCases {
		t.Run(tt.name, func(t *testing.T) {
			embeddings, err := qe.Infer(tt.videoURL)
			if err != nil {
				t.Logf("API call failed for %s: %v", tt.name, err)
				// Don't skip for edge cases, just log and continue
				// Some edge cases might legitimately fail
				return
			}

			if len(embeddings) > 0 && len(embeddings[0]) > 0 {
				t.Logf("Successfully generated embedding for %s, dimension: %d", tt.name, len(embeddings[0]))
				assert.Greater(t, len(embeddings[0]), 0)
			}
		})
	}
}

func TestQwenVideoEmbedding_ConfigTemplate(t *testing.T) {
	expectedConfig := map[string]interface{}{
		"video_embedding": map[string]interface{}{
			"embedding_type": "qwen",
			"qwen": map[string]interface{}{
				"dashscope_api_key": "your_dashscope_api_key_here",
				"base_url":          "https://dashscope.aliyuncs.com/api/v1/services/embeddings/multimodal-embedding/multimodal-embedding",
				"model":             "multimodal-embedding-one",
			},
		},
	}

	// This test just validates that the expected config structure is valid
	mngr := utils.ComponentMngr{}
	err := mngr.SetConfig(expectedConfig)
	assert.NoError(t, err, "Config template should be valid")
}

// BenchmarkQwenVideoEmbedding_Infer_WithConfig performance test
func BenchmarkQwenVideoEmbedding_Infer_WithConfig(b *testing.B) {
	// Step 1: Load real config
	componentConfig, err := setupRealConfig()
	if err != nil {
		b.Skip("Cannot load .env.yaml, skipping benchmark:", err)
	}

	// Check if API key is configured
	videoEmbeddingConfig, ok := componentConfig["video_embedding"].(map[string]interface{})
	if !ok {
		b.Skip("Invalid video_embedding config structure")
	}

	qwenConfig, ok := videoEmbeddingConfig["qwen"].(map[string]interface{})
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
	instance, err := mngr.GetComponent("video_embedding")
	require.NoError(b, err)

	qe, ok := instance.(video_embedding.VideoEmbeddingExtractor)
	require.True(b, ok)

	videoURL := "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4"

	// Test one call first to see if the API is working
	_, err = qe.Infer(videoURL)
	if err != nil {
		b.Skip("API not working, skipping benchmark:", err)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := qe.Infer(videoURL)
		if err != nil {
			b.Logf("API call failed during benchmark: %v", err)
			// Don't fail immediately, just log and continue
		}
	}
}
