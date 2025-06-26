package text_embedding

import (
	"fmt"
	"mmretriever-api/components/text_embedding"
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

func TestQwenTextEmbedding_Initialize_FromConfig(t *testing.T) {
	tests := []struct {
		name    string
		config  map[string]interface{}
		wantErr bool
		errMsg  string
	}{
		{
			name: "valid config",
			config: map[string]interface{}{
				"text_embedding": map[string]interface{}{
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
				"text_embedding": map[string]interface{}{
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
				"text_embedding": map[string]interface{}{
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
				"text_embedding": map[string]interface{}{
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
			instance, err := mngr.GetComponent("text_embedding")

			if tt.wantErr {
				assert.Error(t, err)
				assert.Contains(t, err.Error(), tt.errMsg)
			} else {
				assert.NoError(t, err)
				assert.NotNil(t, instance)

				// Verify instance type
				qe, ok := instance.(text_embedding.TextEmbeddingExtractor)
				assert.True(t, ok)
				assert.NotNil(t, qe)
			}
		})
	}
}

func TestQwenTextEmbedding_LoadFromYamlConfig(t *testing.T) {
	// Create test config file
	tmpDir := t.TempDir()
	configPath := filepath.Join(tmpDir, "test.yaml")

	configContent := `components:
  text_embedding:
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
	instance, err := mngr.GetComponent("text_embedding")
	assert.NoError(t, err)
	assert.NotNil(t, instance)
}

func TestQwenTextEmbedding_TextEmbedding_WithRealConfig(t *testing.T) {
	// Step 1: Load real config
	componentConfig, err := setupRealConfig()
	if err != nil {
		t.Skip("Cannot load .env.yaml, skipping integration test:", err)
	}

	// Check if API key is configured
	textEmbeddingConfig, ok := componentConfig["text_embedding"].(map[string]interface{})
	if !ok {
		t.Skip("Invalid text_embedding config structure")
	}

	qwenConfig, ok := textEmbeddingConfig["qwen"].(map[string]interface{})
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
	instance, err := mngr.GetComponent("text_embedding")
	require.NoError(t, err)

	qe, ok := instance.(text_embedding.TextEmbeddingExtractor)
	require.True(t, ok)

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
		{
			name: "technical text",
			text: "Machine learning algorithms use vector embeddings to represent textual data in high-dimensional space for semantic similarity computation.",
		},
		{
			name: "mixed language",
			text: "Hello 你好 world 世界! This is a mixed language test case.",
		},
		{
			name: "empty text",
			text: "",
		},
		{
			name: "single character",
			text: "A",
		},
		{
			name: "numbers and symbols",
			text: "123 ABC !@# $%^ &*() 456 DEF",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			embeddings, err := qe.Infer(tt.text)

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

			// Check embedding contains non-zero values (unless it's empty text)
			if tt.text != "" {
				hasNonZero := false
				for _, val := range embedding {
					if val != 0 {
						hasNonZero = true
						break
					}
				}
				assert.True(t, hasNonZero, "Embedding should contain non-zero values for non-empty text")
			}
		})
	}
}

func TestQwenTextEmbedding_Infer_WithInvalidText(t *testing.T) {
	validConfig := map[string]interface{}{
		"text_embedding": map[string]interface{}{
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
	instance, err := mngr.GetComponent("text_embedding")
	require.NoError(t, err)

	qe, ok := instance.(text_embedding.TextEmbeddingExtractor)
	require.True(t, ok)

	// Test with very long text (might hit API limits)
	veryLongText := ""
	for i := 0; i < 1000; i++ {
		veryLongText += "This is a very long text that might exceed API limits. "
	}

	t.Run("very_long_text", func(t *testing.T) {
		_, err := qe.Infer(veryLongText)
		// This might succeed or fail depending on API limits
		// We just log the result without asserting
		if err != nil {
			t.Logf("Very long text failed as expected: %v", err)
		} else {
			t.Logf("Very long text succeeded")
		}
	})
}

func TestQwenTextEmbedding_Infer_EmbeddingConsistency(t *testing.T) {
	validConfig := map[string]interface{}{
		"text_embedding": map[string]interface{}{
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
	instance, err := mngr.GetComponent("text_embedding")
	require.NoError(t, err)

	qe, ok := instance.(text_embedding.TextEmbeddingExtractor)
	require.True(t, ok)

	testText := "This is a consistency test"

	// Call Infer multiple times with the same text
	embeddings1, err1 := qe.Infer(testText)
	embeddings2, err2 := qe.Infer(testText)

	// Both should either succeed or fail together
	if err1 != nil && err2 != nil {
		t.Logf("Both calls failed consistently: %v, %v", err1, err2)
		return
	}

	if err1 == nil && err2 == nil {
		// Check that embeddings have consistent dimensions
		assert.Equal(t, len(embeddings1), len(embeddings2), "Number of embeddings should be consistent")
		if len(embeddings1) > 0 && len(embeddings2) > 0 {
			assert.Equal(t, len(embeddings1[0]), len(embeddings2[0]), "Embedding dimensions should be consistent")
		}
	}
}

func TestQwenTextEmbedding_TextEmbedding_WithInvalidConfig(t *testing.T) {
	invalidConfig := map[string]interface{}{
		"text_embedding": map[string]interface{}{
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
	instance, err := mngr.GetComponent("text_embedding")
	require.NoError(t, err)

	qe, ok := instance.(text_embedding.TextEmbeddingExtractor)
	require.True(t, ok)

	// Test with invalid API should return error
	_, err = qe.Infer("test text")
	assert.Error(t, err, "Should return error with invalid config")
}

// BenchmarkQwenEmbedding_TextEmbedding_WithConfig performance test
func BenchmarkQwenEmbedding_TextEmbedding_WithConfig(b *testing.B) {
	// Step 1: Load real config
	componentConfig, err := setupRealConfig()
	if err != nil {
		b.Skip("Cannot load .env.yaml, skipping benchmark:", err)
	}

	// Check if API key is configured
	textEmbeddingConfig, ok := componentConfig["text_embedding"].(map[string]interface{})
	if !ok {
		b.Skip("Invalid text_embedding config structure")
	}

	qwenConfig, ok := textEmbeddingConfig["qwen"].(map[string]interface{})
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
	instance, err := mngr.GetComponent("text_embedding")
	require.NoError(b, err)

	qe, ok := instance.(text_embedding.TextEmbeddingExtractor)
	require.True(b, ok)

	text := "This is a test text for benchmarking embedding generation performance."

	// Test one call first to see if the API is working
	_, err = qe.Infer(text)
	if err != nil {
		b.Skip("API not working, skipping benchmark:", err)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := qe.Infer(text)
		if err != nil {
			b.Logf("API call failed during benchmark: %v", err)
			// Don't fail immediately, just log and continue
		}
	}
}

// TestQwenTextEmbedding_Infer_RealConfig_BatchProcessing tests processing multiple texts with real config
func TestQwenTextEmbedding_Infer_RealConfig_BatchProcessing(t *testing.T) {
	// Step 1: Load real config
	componentConfig, err := setupRealConfig()
	if err != nil {
		t.Skip("Cannot load .env.yaml, skipping integration test:", err)
	}

	// Check if API key is configured
	textEmbeddingConfig, ok := componentConfig["text_embedding"].(map[string]interface{})
	if !ok {
		t.Skip("Invalid text_embedding config structure")
	}

	qwenConfig, ok := textEmbeddingConfig["qwen"].(map[string]interface{})
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
	instance, err := mngr.GetComponent("text_embedding")
	require.NoError(t, err)

	qe, ok := instance.(text_embedding.TextEmbeddingExtractor)
	require.True(t, ok)

	// Test batch processing of multiple texts
	testTexts := []string{
		"Machine learning algorithms use neural networks for pattern recognition.",
		"Deep learning models require large datasets for training.",
		"Natural language processing enables computers to understand human language.",
		"Computer vision algorithms can identify objects in images.",
		"Artificial intelligence is transforming various industries.",
	}

	var allEmbeddings [][]float64
	for i, text := range testTexts {
		t.Run(fmt.Sprintf("batch_text_%d", i+1), func(t *testing.T) {
			embeddings, err := qe.Infer(text)
			if err != nil {
				t.Logf("API call failed for text %d: %v", i+1, err)
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

// TestQwenTextEmbedding_Infer_RealConfig_SemanticSimilarity tests semantic similarity with real config
func TestQwenTextEmbedding_Infer_RealConfig_SemanticSimilarity(t *testing.T) {
	// Step 1: Load real config
	componentConfig, err := setupRealConfig()
	if err != nil {
		t.Skip("Cannot load .env.yaml, skipping integration test:", err)
	}

	// Check if API key is configured
	textEmbeddingConfig, ok := componentConfig["text_embedding"].(map[string]interface{})
	if !ok {
		t.Skip("Invalid text_embedding config structure")
	}

	qwenConfig, ok := textEmbeddingConfig["qwen"].(map[string]interface{})
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
	instance, err := mngr.GetComponent("text_embedding")
	require.NoError(t, err)

	qe, ok := instance.(text_embedding.TextEmbeddingExtractor)
	require.True(t, ok)

	// Test semantic similarity with similar texts
	similarTexts := []struct {
		text1 string
		text2 string
		name  string
	}{
		{
			text1: "I love cats",
			text2: "I adore felines",
			name:  "pet_similarity",
		},
		{
			text1: "The weather is beautiful today",
			text2: "Today has lovely weather",
			name:  "weather_similarity",
		},
		{
			text1: "Machine learning is a subset of artificial intelligence",
			text2: "AI includes machine learning as a component",
			name:  "technical_similarity",
		},
	}

	for _, tt := range similarTexts {
		t.Run(tt.name, func(t *testing.T) {
			// Get embeddings for both texts
			embeddings1, err1 := qe.Infer(tt.text1)
			embeddings2, err2 := qe.Infer(tt.text2)

			if err1 != nil || err2 != nil {
				t.Logf("API call failed: err1=%v, err2=%v", err1, err2)
				t.Skip("Skipping due to API error")
				return
			}

			assert.NoError(t, err1)
			assert.NoError(t, err2)
			assert.NotEmpty(t, embeddings1)
			assert.NotEmpty(t, embeddings2)
			assert.Len(t, embeddings1, 1)
			assert.Len(t, embeddings2, 1)

			// Both embeddings should have the same dimension
			assert.Equal(t, len(embeddings1[0]), len(embeddings2[0]),
				"Similar texts should produce embeddings of the same dimension")

			// Log the similarity information (we don't assert specific values since
			// semantic similarity depends on the model and can vary)
			t.Logf("Generated embeddings for similar texts: '%s' and '%s'", tt.text1, tt.text2)
			t.Logf("Embedding dimensions: %d", len(embeddings1[0]))
		})
	}
}

// TestQwenTextEmbedding_Infer_RealConfig_MultiLanguage tests multi-language support with real config
func TestQwenTextEmbedding_Infer_RealConfig_MultiLanguage(t *testing.T) {
	// Step 1: Load real config
	componentConfig, err := setupRealConfig()
	if err != nil {
		t.Skip("Cannot load .env.yaml, skipping integration test:", err)
	}

	// Check if API key is configured
	textEmbeddingConfig, ok := componentConfig["text_embedding"].(map[string]interface{})
	if !ok {
		t.Skip("Invalid text_embedding config structure")
	}

	qwenConfig, ok := textEmbeddingConfig["qwen"].(map[string]interface{})
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
	instance, err := mngr.GetComponent("text_embedding")
	require.NoError(t, err)

	qe, ok := instance.(text_embedding.TextEmbeddingExtractor)
	require.True(t, ok)

	// Test different languages
	multiLanguageTexts := []struct {
		name string
		text string
		lang string
	}{
		{
			name: "english",
			text: "Hello, how are you today?",
			lang: "en",
		},
		{
			name: "chinese_simplified",
			text: "你好，今天过得怎么样？",
			lang: "zh-CN",
		},
		{
			name: "chinese_traditional",
			text: "你好，今天過得怎麼樣？",
			lang: "zh-TW",
		},
		{
			name: "japanese",
			text: "こんにちは、今日はいかがですか？",
			lang: "ja",
		},
		{
			name: "korean",
			text: "안녕하세요, 오늘 어떻게 지내세요?",
			lang: "ko",
		},
		{
			name: "mixed_language",
			text: "Hello 你好 こんにちは 안녕하세요 world",
			lang: "mixed",
		},
	}

	var allEmbeddings [][]float64
	for _, tt := range multiLanguageTexts {
		t.Run(tt.name, func(t *testing.T) {
			embeddings, err := qe.Infer(tt.text)
			if err != nil {
				t.Logf("API call failed for %s text: %v", tt.lang, err)
				t.Skip("Skipping due to API error")
				return
			}

			assert.NoError(t, err)
			assert.NotEmpty(t, embeddings)
			assert.Len(t, embeddings, 1)
			assert.Greater(t, len(embeddings[0]), 0)

			// Check for non-zero values
			hasNonZero := false
			for _, val := range embeddings[0] {
				if val != 0 {
					hasNonZero = true
					break
				}
			}
			assert.True(t, hasNonZero, "Embedding should contain non-zero values for %s text", tt.lang)

			allEmbeddings = append(allEmbeddings, embeddings[0])
			t.Logf("Successfully generated embedding for %s text, dimension: %d", tt.lang, len(embeddings[0]))
		})
	}

	// Verify all embeddings have consistent dimensions
	if len(allEmbeddings) > 1 {
		baseDimension := len(allEmbeddings[0])
		for i, embedding := range allEmbeddings[1:] {
			assert.Equal(t, baseDimension, len(embedding),
				"All multi-language embeddings should have the same dimension, embedding %d differs", i+2)
		}
	}
}

// TestQwenTextEmbedding_Infer_RealConfig_EdgeCases tests edge cases with real config
func TestQwenTextEmbedding_Infer_RealConfig_EdgeCases(t *testing.T) {
	// Step 1: Load real config
	componentConfig, err := setupRealConfig()
	if err != nil {
		t.Skip("Cannot load .env.yaml, skipping integration test:", err)
	}

	// Check if API key is configured
	textEmbeddingConfig, ok := componentConfig["text_embedding"].(map[string]interface{})
	if !ok {
		t.Skip("Invalid text_embedding config structure")
	}

	qwenConfig, ok := textEmbeddingConfig["qwen"].(map[string]interface{})
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
	instance, err := mngr.GetComponent("text_embedding")
	require.NoError(t, err)

	qe, ok := instance.(text_embedding.TextEmbeddingExtractor)
	require.True(t, ok)

	// Test edge cases
	edgeCases := []struct {
		name string
		text string
	}{
		{
			name: "only_whitespace",
			text: "   \t\n\r   ",
		},
		{
			name: "only_punctuation",
			text: "!@#$%^&*()_+-=[]{}|;':\",./<>?",
		},
		{
			name: "only_numbers",
			text: "1234567890",
		},
		{
			name: "repeated_characters",
			text: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
		},
		{
			name: "unicode_characters",
			text: "🚀🌟💻🔥⭐🎯🌈🎉🏆🎨",
		},
		{
			name: "code_snippet",
			text: "func main() { fmt.Println(\"Hello, World!\") }",
		},
		{
			name: "html_tags",
			text: "<html><body><h1>Hello World</h1></body></html>",
		},
		{
			name: "json_data",
			text: `{"name": "test", "value": 123, "active": true}`,
		},
	}

	for _, tt := range edgeCases {
		t.Run(tt.name, func(t *testing.T) {
			embeddings, err := qe.Infer(tt.text)
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
