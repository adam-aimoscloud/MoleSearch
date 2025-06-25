package text_embedding

import (
	"fmt"
	"mmretriever-api/pkg/dal"
)

// TextEmbeddingExtractor is the interface for extracting embeddings from text
type TextEmbeddingExtractor interface {
	Initialize(config interface{}) (err error)
	Infer(text string) (embeddings []dal.Embedding, err error)
}

type TextEmbeddingExtractorType string

const (
	TextEmbeddingExtractorTypeQwen = "qwen"
)

type TextEmbeddingConfig struct {
	EmbeddingType TextEmbeddingExtractorType
	Config        interface{}
}

var registeredTextEmbeddingExtractor = make(map[TextEmbeddingExtractorType]TextEmbeddingExtractor)

func NewTextEmbeddingExtractor(config *TextEmbeddingConfig) (TextEmbeddingExtractor, error) {
	if textEmbeddingExtractor, ok := registeredTextEmbeddingExtractor[config.EmbeddingType]; ok {
		if err := textEmbeddingExtractor.Initialize(config.Config); err != nil {
			return nil, err
		}
		return textEmbeddingExtractor, nil
	}
	return nil, fmt.Errorf("unsupported text embedding extractor type: %s", config.EmbeddingType)
}
