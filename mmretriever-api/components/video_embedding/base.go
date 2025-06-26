package video_embedding

import (
	"encoding/json"
	"fmt"
	"mmretriever-api/pkg/dal"
	"mmretriever-api/utils"
)

func init() {
	mngr := utils.ComponentMngr{}
	factory = &VideoEmbeddingExtractorFactory{}
	mngr.RegisterComponentFactory("video_embedding", factory)
}

// ================= VideoEmbeddingExtractorFactory Implementation
type VideoEmbeddingExtractorFactory struct {
	cfg VideoEmbeddingConfig
}

func (f *VideoEmbeddingExtractorFactory) Config() interface{} {
	return f.cfg
}

func (f *VideoEmbeddingExtractorFactory) SetConfig(cfg interface{}) {
	if cfg == nil {
		return
	}
	// Convert config using JSON marshaling/unmarshaling
	if jsonData, err := json.Marshal(cfg); err == nil {
		var tempConfig VideoEmbeddingConfig
		if err := json.Unmarshal(jsonData, &tempConfig); err == nil {
			f.cfg = tempConfig
		}
	}
}

func (f *VideoEmbeddingExtractorFactory) GetOrCreateInstance() (interface{}, error) {
	return newVideoEmbeddingExtractor(&f.cfg)
}

var factory *VideoEmbeddingExtractorFactory

func GetVideoEmbeddingExtractorFactory() *VideoEmbeddingExtractorFactory {
	return factory
}

// ===================== VideoEmbeddingExtractor Implementation
// VideoEmbeddingExtractor is the interface for extracting embeddings from videos
type VideoEmbeddingExtractor interface {
	initialize(config *VideoEmbeddingConfig) (err error)
	Infer(videoURL string) (embeddings []dal.Embedding, err error)
}

type VideoEmbeddingExtractorType string

const (
	VideoEmbeddingExtractorTypeQwen = "qwen"
)

type VideoEmbeddingConfig struct {
	EmbeddingType VideoEmbeddingExtractorType `json:"embedding_type" yaml:"embedding_type"`
	Qwen          QwenConfig                  `json:"qwen" yaml:"qwen"`
}

var registeredVideoEmbeddingExtractor = make(map[VideoEmbeddingExtractorType]VideoEmbeddingExtractor)

func newVideoEmbeddingExtractor(config *VideoEmbeddingConfig) (VideoEmbeddingExtractor, error) {
	if videoEmbeddingExtractor, ok := registeredVideoEmbeddingExtractor[config.EmbeddingType]; ok {
		if err := videoEmbeddingExtractor.initialize(config); err != nil {
			return nil, err
		}
		return videoEmbeddingExtractor, nil
	}
	return nil, fmt.Errorf("unsupported video embedding extractor type: %s", config.EmbeddingType)
}
