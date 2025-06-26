package video_embedding

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"mmretriever-api/pkg/dal"
	"net/http"
	"time"
)

type QwenConfig struct {
	DashscopeAPIKey string `json:"dashscope_api_key" yaml:"dashscope_api_key"`
	BaseURL         string `json:"base_url" yaml:"base_url"`
	Model           string `json:"model" yaml:"model"`
}

type QwenVideoEmbedding struct {
	Config QwenConfig
}

func init() {
	registeredVideoEmbeddingExtractor[VideoEmbeddingExtractorTypeQwen] = &QwenVideoEmbedding{}
	log.Printf("[VideoEmbedding] Registered Qwen video embedding extractor")
}

func (q *QwenVideoEmbedding) initialize(config *VideoEmbeddingConfig) (err error) {
	log.Printf("[VideoEmbedding][Qwen] Starting initialization...")

	q.Config = config.Qwen

	// Validate configuration with detailed logging
	if q.Config.DashscopeAPIKey == "" {
		log.Printf("[VideoEmbedding][Qwen] ERROR: dashscope_api_key is missing")
		return fmt.Errorf("dashscope_api_key is required")
	}
	log.Printf("[VideoEmbedding][Qwen] DashScope API key configured (length: %d)", len(q.Config.DashscopeAPIKey))

	if q.Config.BaseURL == "" {
		log.Printf("[VideoEmbedding][Qwen] ERROR: base_url is missing")
		return fmt.Errorf("base_url is required")
	}
	log.Printf("[VideoEmbedding][Qwen] Base URL configured: %s", q.Config.BaseURL)

	if q.Config.Model == "" {
		log.Printf("[VideoEmbedding][Qwen] ERROR: model is missing")
		return fmt.Errorf("model is required")
	}
	log.Printf("[VideoEmbedding][Qwen] Model configured: %s", q.Config.Model)

	log.Printf("[VideoEmbedding][Qwen] Initialization completed successfully")
	return nil
}

func (q *QwenVideoEmbedding) Infer(videoURL string) (embeddings []dal.Embedding, err error) {
	startTime := time.Now()
	log.Printf("[VideoEmbedding][Qwen] Starting inference for video URL: %s", videoURL)

	// Validate input
	if videoURL == "" {
		log.Printf("[VideoEmbedding][Qwen] ERROR: Empty video URL provided")
		return nil, fmt.Errorf("video URL cannot be empty")
	}

	// Prepare request body
	log.Printf("[VideoEmbedding][Qwen] Preparing request body...")
	reqBody := map[string]interface{}{
		"model": q.Config.Model,
		"input": map[string]interface{}{
			"contents": []map[string]interface{}{
				{
					"video": videoURL,
				},
			},
		},
		"parameters": map[string]interface{}{},
	}

	// Log request configuration (without sensitive data)
	log.Printf("[VideoEmbedding][Qwen] Request config - Model: %s, Base URL: %s", q.Config.Model, q.Config.BaseURL)

	// Create HTTP request
	log.Printf("[VideoEmbedding][Qwen] Creating HTTP request...")
	req, err := http.NewRequest("POST", q.Config.BaseURL, nil)
	if err != nil {
		log.Printf("[VideoEmbedding][Qwen] ERROR: Failed to create HTTP request: %v", err)
		return nil, fmt.Errorf("failed to create request: %v", err)
	}

	// Set headers
	req.Header.Set("Authorization", "Bearer "+q.Config.DashscopeAPIKey)
	req.Header.Set("Content-Type", "application/json")
	log.Printf("[VideoEmbedding][Qwen] HTTP headers set successfully")

	// Marshal request body
	log.Printf("[VideoEmbedding][Qwen] Marshaling request body...")
	reqBodyBytes, err := json.Marshal(reqBody)
	if err != nil {
		log.Printf("[VideoEmbedding][Qwen] ERROR: Failed to marshal request body: %v", err)
		return nil, fmt.Errorf("failed to marshal request body: %v", err)
	}
	log.Printf("[VideoEmbedding][Qwen] Request body size: %d bytes", len(reqBodyBytes))

	req.Body = io.NopCloser(bytes.NewReader(reqBodyBytes))

	// Send request
	log.Printf("[VideoEmbedding][Qwen] Sending HTTP request...")
	client := &http.Client{
		Timeout: 30 * time.Second, // Add timeout for better error handling
	}

	apiCallStart := time.Now()
	resp, err := client.Do(req)
	apiCallDuration := time.Since(apiCallStart)

	if err != nil {
		log.Printf("[VideoEmbedding][Qwen] ERROR: Failed to send request (duration: %v): %v", apiCallDuration, err)
		return nil, fmt.Errorf("failed to send request: %v", err)
	}
	defer resp.Body.Close()

	log.Printf("[VideoEmbedding][Qwen] HTTP request completed - Status: %s, Duration: %v", resp.Status, apiCallDuration)

	// Check response status
	if resp.StatusCode != http.StatusOK {
		log.Printf("[VideoEmbedding][Qwen] WARNING: Non-200 status code received: %d", resp.StatusCode)
	}

	// Read response
	log.Printf("[VideoEmbedding][Qwen] Reading response body...")
	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Printf("[VideoEmbedding][Qwen] ERROR: Failed to read response body: %v", err)
		return nil, fmt.Errorf("failed to read response body: %v", err)
	}
	log.Printf("[VideoEmbedding][Qwen] Response body size: %d bytes", len(respBody))

	// Log response for debugging (first 200 characters)
	responsePreview := string(respBody)
	if len(responsePreview) > 200 {
		responsePreview = responsePreview[:200] + "..."
	}
	log.Printf("[VideoEmbedding][Qwen] Response preview: %s", responsePreview)

	// Parse response
	log.Printf("[VideoEmbedding][Qwen] Parsing response JSON...")
	var result struct {
		Output struct {
			Embeddings []struct {
				Embedding []float64 `json:"embedding"`
			} `json:"embeddings"`
		} `json:"output"`
		Usage struct {
			InputTokens  int `json:"input_tokens"`
			OutputTokens int `json:"output_tokens"`
			TotalTokens  int `json:"total_tokens"`
		} `json:"usage,omitempty"`
	}

	if err := json.Unmarshal(respBody, &result); err != nil {
		log.Printf("[VideoEmbedding][Qwen] ERROR: Failed to unmarshal response: %v", err)
		log.Printf("[VideoEmbedding][Qwen] Raw response: %s", string(respBody))
		return nil, fmt.Errorf("failed to unmarshal response: %v", err)
	}

	// Log usage information if available
	if result.Usage.TotalTokens > 0 {
		log.Printf("[VideoEmbedding][Qwen] Token usage - Input: %d, Output: %d, Total: %d",
			result.Usage.InputTokens, result.Usage.OutputTokens, result.Usage.TotalTokens)
	}

	// Extract embeddings
	log.Printf("[VideoEmbedding][Qwen] Extracting embeddings...")
	if len(result.Output.Embeddings) == 0 {
		log.Printf("[VideoEmbedding][Qwen] WARNING: No embeddings found in response")
		return nil, fmt.Errorf("no embeddings found in API response")
	}

	if len(result.Output.Embeddings) > 0 {
		embedding := result.Output.Embeddings[0].Embedding
		log.Printf("[VideoEmbedding][Qwen] Successfully extracted embedding - Dimension: %d", len(embedding))

		// Validate embedding
		if len(embedding) == 0 {
			log.Printf("[VideoEmbedding][Qwen] ERROR: Empty embedding vector received")
			return nil, fmt.Errorf("empty embedding vector received from API")
		}

		// Check for non-zero values
		nonZeroCount := 0
		for _, val := range embedding {
			if val != 0.0 {
				nonZeroCount++
			}
		}
		log.Printf("[VideoEmbedding][Qwen] Embedding validation - Non-zero values: %d/%d", nonZeroCount, len(embedding))

		embeddings = []dal.Embedding{embedding}
	}

	totalDuration := time.Since(startTime)
	log.Printf("[VideoEmbedding][Qwen] Inference completed successfully - Total duration: %v, API call: %v",
		totalDuration, apiCallDuration)

	return embeddings, nil
}
