package embedding

import (
	"fmt"
	"mmretriever-api/pkg/dal"
)

// EmbeddingExtractor is the interface for extracting embeddings from text and image
type EmbeddingExtractor interface {
	Initialize(config interface{}) (err error)
	TextEmbedding(text string) (embeddings []dal.Embedding, err error)
	ImageEmbedding(imageB64orURL string) (embedding dal.Embedding, err error)
}

type EmbeddingExtractorType string

const (
	EmbeddingExtractorTypeQwen = "qwen"
)

var registeredEmbeddingExtractor = make(map[EmbeddingExtractorType]EmbeddingExtractor)

func NewEmbeddingExtractor(embeddingExtractorType EmbeddingExtractorType) (EmbeddingExtractor, error) {
	if embeddingExtractor, ok := registeredEmbeddingExtractor[embeddingExtractorType]; ok {
		return embeddingExtractor, nil
	}
	return nil, fmt.Errorf("unsupported embedding extractor type: %s", embeddingExtractorType)
}
