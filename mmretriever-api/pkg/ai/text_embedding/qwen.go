package text_embedding

import (
	"context"
	"fmt"
	"mmretriever-api/pkg/dal"

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
}

func (q *QwenTextEmbedding) Initialize(config interface{}) (err error) {
	q.Config = config.(QwenConfig)
	if q.Config.DashscopeAPIKey == "" {
		return fmt.Errorf("dashscope_api_key is required")
	}
	if q.Config.BaseURL == "" {
		return fmt.Errorf("base_url is required")
	}
	if q.Config.Model == "" {
		return fmt.Errorf("model is required")
	}
	return nil
}

func (q *QwenTextEmbedding) Infer(text string) (embeddings []dal.Embedding, err error) {
	config := openai.DefaultConfig(q.Config.DashscopeAPIKey)
	config.BaseURL = q.Config.BaseURL
	client := openai.NewClientWithConfig(config)

	response, err := client.CreateEmbeddings(context.Background(), openai.EmbeddingRequest{
		Model: openai.EmbeddingModel(q.Config.Model),
		Input: []string{text},
	})
	if err != nil {
		return nil, err
	}

	if len(response.Data) > 0 {
		// Convert []float32 to []float64
		embedding := make([]float64, len(response.Data[0].Embedding))
		for i, v := range response.Data[0].Embedding {
			embedding[i] = float64(v)
		}
		embeddings = []dal.Embedding{
			embedding,
		}
	}
	return embeddings, nil
}
