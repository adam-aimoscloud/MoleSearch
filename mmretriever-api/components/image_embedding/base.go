package image_embedding

import (
	"encoding/json"
	"fmt"
	"mmretriever-api/pkg/dal"
	"mmretriever-api/utils"
)

func init() {
	mngr := utils.ComponentMngr{}
	factory = &ImageEmbeddingExtractorFactory{}
	mngr.RegisterComponentFactory("image_embedding", factory)
}

// ================= ImageEmbeddingExtractorFactory Implementation
type ImageEmbeddingExtractorFactory struct {
	cfg ImageEmbeddingConfig
}

func (f *ImageEmbeddingExtractorFactory) Config() interface{} {
	return f.cfg
}

func (f *ImageEmbeddingExtractorFactory) SetConfig(cfg interface{}) {
	if cfg == nil {
		return
	}
	// Convert config using JSON marshaling/unmarshaling
	if jsonData, err := json.Marshal(cfg); err == nil {
		var tempConfig ImageEmbeddingConfig
		if err := json.Unmarshal(jsonData, &tempConfig); err == nil {
			f.cfg = tempConfig
		}
	}
}

func (f *ImageEmbeddingExtractorFactory) GetOrCreateInstance() (interface{}, error) {
	return newImageEmbeddingExtractor(&f.cfg)
}

var factory *ImageEmbeddingExtractorFactory

func GetImageEmbeddingExtractorFactory() *ImageEmbeddingExtractorFactory {
	return factory
}

// ===================== ImageEmbeddingExtractor Implementation
// ImageEmbeddingExtractor is the interface for extracting embeddings from images
type ImageEmbeddingExtractor interface {
	initialize(config *ImageEmbeddingConfig) (err error)
	Infer(imageURL string) (embeddings []dal.Embedding, err error)
}

type ImageEmbeddingExtractorType string

const (
	ImageEmbeddingExtractorTypeQwen = "qwen"
)

type ImageEmbeddingConfig struct {
	EmbeddingType ImageEmbeddingExtractorType `json:"embedding_type" yaml:"embedding_type"`
	Qwen          QwenConfig                  `json:"qwen" yaml:"qwen"`
}

var registeredImageEmbeddingExtractor = make(map[ImageEmbeddingExtractorType]ImageEmbeddingExtractor)

func newImageEmbeddingExtractor(config *ImageEmbeddingConfig) (ImageEmbeddingExtractor, error) {
	if imageEmbeddingExtractor, ok := registeredImageEmbeddingExtractor[config.EmbeddingType]; ok {
		if err := imageEmbeddingExtractor.initialize(config); err != nil {
			return nil, err
		}
		return imageEmbeddingExtractor, nil
	}
	return nil, fmt.Errorf("unsupported image embedding extractor type: %s", config.EmbeddingType)
}
