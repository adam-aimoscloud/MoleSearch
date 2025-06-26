package text_embedding

import (
	"encoding/json"
	"fmt"
	"mmretriever-api/pkg/dal"
	"mmretriever-api/utils"
)

func init() {
	mngr := utils.ComponentMngr{}
	factory = &TextEmbeddingExtractorFactory{}
	mngr.RegisterComponentFactory("text_embedding", factory)
}

// ================= TextEmbeddingExtractorFactory Implementation
type TextEmbeddingExtractorFactory struct {
	cfg TextEmbeddingConfig
}

func (f *TextEmbeddingExtractorFactory) Config() interface{} {
	return f.cfg
}

func (f *TextEmbeddingExtractorFactory) SetConfig(cfg interface{}) {
	if cfg == nil {
		return
	}
	// Convert config using JSON marshaling/unmarshaling
	if jsonData, err := json.Marshal(cfg); err == nil {
		var tempConfig TextEmbeddingConfig
		if err := json.Unmarshal(jsonData, &tempConfig); err == nil {
			f.cfg = tempConfig
		}
	}
}

func (f *TextEmbeddingExtractorFactory) GetOrCreateInstance() (interface{}, error) {
	return newTextEmbeddingExtractor(&f.cfg)
}

var factory *TextEmbeddingExtractorFactory

func GetTextEmbeddingExtractorFactory() *TextEmbeddingExtractorFactory {
	return factory
}

// ===================== TextEmbeddingExtractor Implementation
// TextEmbeddingExtractor is the interface for extracting embeddings from text
type TextEmbeddingExtractor interface {
	initialize(config *TextEmbeddingConfig) (err error)
	Infer(text string) (embeddings []dal.Embedding, err error)
}

type TextEmbeddingExtractorType string

const (
	TextEmbeddingExtractorTypeQwen = "qwen"
)

type TextEmbeddingConfig struct {
	EmbeddingType TextEmbeddingExtractorType `json:"embedding_type" yaml:"embedding_type"`
	Qwen          QwenConfig                 `json:"qwen" yaml:"qwen"`
}

var registeredTextEmbeddingExtractor = make(map[TextEmbeddingExtractorType]TextEmbeddingExtractor)

func newTextEmbeddingExtractor(config *TextEmbeddingConfig) (TextEmbeddingExtractor, error) {
	if textEmbeddingExtractor, ok := registeredTextEmbeddingExtractor[config.EmbeddingType]; ok {
		if err := textEmbeddingExtractor.initialize(config); err != nil {
			return nil, err
		}
		return textEmbeddingExtractor, nil
	}
	return nil, fmt.Errorf("unsupported text embedding extractor type: %s", config.EmbeddingType)
}
