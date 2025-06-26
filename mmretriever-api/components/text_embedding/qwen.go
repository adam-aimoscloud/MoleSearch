package text_embedding

import (
	"context"
	"fmt"
	"log"
	"mmretriever-api/pkg/dal"
	"time"

	openai "github.com/sashabaranov/go-openai"
)

type QwenConfig struct {
	DashscopeAPIKey string `json:"dashscope_api_key" yaml:"dashscope_api_key"`
	BaseURL         string `json:"base_url" yaml:"base_url"`
	Model           string `json:"model" yaml:"model"`
}

type QwenTextEmbedding struct {
	Config QwenConfig
}

func init() {
	registeredTextEmbeddingExtractor[TextEmbeddingExtractorTypeQwen] = &QwenTextEmbedding{}
	log.Printf("[TextEmbedding] Registered Qwen text embedding extractor")
}

func (q *QwenTextEmbedding) initialize(config *TextEmbeddingConfig) (err error) {
	log.Printf("[TextEmbedding][Qwen] Starting initialization...")

	q.Config = config.Qwen

	// Validate configuration with detailed logging
	if q.Config.DashscopeAPIKey == "" {
		log.Printf("[TextEmbedding][Qwen] ERROR: dashscope_api_key is missing")
		return fmt.Errorf("dashscope_api_key is required")
	}
	log.Printf("[TextEmbedding][Qwen] DashScope API key configured (length: %d)", len(q.Config.DashscopeAPIKey))

	if q.Config.BaseURL == "" {
		log.Printf("[TextEmbedding][Qwen] ERROR: base_url is missing")
		return fmt.Errorf("base_url is required")
	}
	log.Printf("[TextEmbedding][Qwen] Base URL configured: %s", q.Config.BaseURL)

	if q.Config.Model == "" {
		log.Printf("[TextEmbedding][Qwen] ERROR: model is missing")
		return fmt.Errorf("model is required")
	}
	log.Printf("[TextEmbedding][Qwen] Model configured: %s", q.Config.Model)

	log.Printf("[TextEmbedding][Qwen] Initialization completed successfully")
	return nil
}

func (q *QwenTextEmbedding) Infer(text string) (embeddings []dal.Embedding, err error) {
	startTime := time.Now()
	log.Printf("[TextEmbedding][Qwen] Starting inference for text (length: %d chars)", len(text))

	// Validate input
	if text == "" {
		log.Printf("[TextEmbedding][Qwen] WARNING: Empty text provided for inference")
		// Don't return error for empty text, let the API handle it
	}

	// Log text preview (first 100 characters)
	textPreview := text
	if len(textPreview) > 100 {
		textPreview = textPreview[:100] + "..."
	}
	log.Printf("[TextEmbedding][Qwen] Text preview: %s", textPreview)

	// Create OpenAI client configuration
	log.Printf("[TextEmbedding][Qwen] Creating OpenAI client configuration...")
	config := openai.DefaultConfig(q.Config.DashscopeAPIKey)
	config.BaseURL = q.Config.BaseURL

	log.Printf("[TextEmbedding][Qwen] Client config - Model: %s, Base URL: %s", q.Config.Model, q.Config.BaseURL)

	client := openai.NewClientWithConfig(config)
	log.Printf("[TextEmbedding][Qwen] OpenAI client created successfully")

	// Prepare embedding request
	log.Printf("[TextEmbedding][Qwen] Preparing embedding request...")
	embeddingRequest := openai.EmbeddingRequest{
		Model: openai.EmbeddingModel(q.Config.Model),
		Input: []string{text},
	}

	log.Printf("[TextEmbedding][Qwen] Request prepared - Model: %s, Input count: %d",
		string(embeddingRequest.Model), 1) // We know we're sending 1 text input

	// Create context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Send API request
	log.Printf("[TextEmbedding][Qwen] Sending embedding request...")
	apiCallStart := time.Now()

	rsp, err := client.CreateEmbeddings(ctx, embeddingRequest)
	apiCallDuration := time.Since(apiCallStart)

	if err != nil {
		log.Printf("[TextEmbedding][Qwen] ERROR: Failed to create embeddings (duration: %v): %v", apiCallDuration, err)
		return nil, fmt.Errorf("failed to create embeddings: %v", err)
	}

	log.Printf("[TextEmbedding][Qwen] API request completed successfully - Duration: %v", apiCallDuration)

	// Log response information
	log.Printf("[TextEmbedding][Qwen] Response received - Data count: %d", len(rsp.Data))

	// Log usage information if available
	if rsp.Usage.PromptTokens > 0 || rsp.Usage.TotalTokens > 0 {
		log.Printf("[TextEmbedding][Qwen] Token usage - Prompt: %d, Total: %d",
			rsp.Usage.PromptTokens, rsp.Usage.TotalTokens)
	}

	// Extract and validate embeddings
	log.Printf("[TextEmbedding][Qwen] Extracting embeddings...")
	if len(rsp.Data) == 0 {
		log.Printf("[TextEmbedding][Qwen] WARNING: No embedding data found in response")
		return nil, fmt.Errorf("no embedding data found in API response")
	}

	if len(rsp.Data) > 0 {
		originalEmbedding := rsp.Data[0].Embedding
		log.Printf("[TextEmbedding][Qwen] Original embedding dimension: %d (float32)", len(originalEmbedding))

		if len(originalEmbedding) == 0 {
			log.Printf("[TextEmbedding][Qwen] ERROR: Empty embedding vector received")
			return nil, fmt.Errorf("empty embedding vector received from API")
		}

		// Convert []float32 to []float64
		log.Printf("[TextEmbedding][Qwen] Converting embedding from float32 to float64...")
		embedding := make([]float64, len(originalEmbedding))
		nonZeroCount := 0
		for i, v := range originalEmbedding {
			embedding[i] = float64(v)
			if v != 0.0 {
				nonZeroCount++
			}
		}

		log.Printf("[TextEmbedding][Qwen] Successfully converted embedding - Dimension: %d (float64)", len(embedding))
		log.Printf("[TextEmbedding][Qwen] Embedding validation - Non-zero values: %d/%d", nonZeroCount, len(embedding))

		if nonZeroCount == 0 {
			log.Printf("[TextEmbedding][Qwen] WARNING: All embedding values are zero")
		}

		embeddings = []dal.Embedding{embedding}
	}

	totalDuration := time.Since(startTime)
	log.Printf("[TextEmbedding][Qwen] Inference completed successfully - Total duration: %v, API call: %v",
		totalDuration, apiCallDuration)

	return embeddings, nil
}
