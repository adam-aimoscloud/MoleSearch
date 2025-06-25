package transformer

import (
	"fmt"
	"mmretriever-api/pkg/ai/asr"
	"mmretriever-api/pkg/ai/embedding"
	"mmretriever-api/pkg/ai/vlm"
	"mmretriever-api/pkg/dal"
)

type Transformer interface {
	Initialize(embeddingExtractor embedding.EmbeddingExtractor, vlm vlm.VLMInference, asr asr.ASR) (err error)
	MultiModal(multiModalData dal.MultiModalData) (indexParam dal.IndexParam, err error)
}

type TransformerType string

const (
	TransformerTypeDefault = "default"
	TransformerTypeDify    = "dify"
)

var registeredTransformers = make(map[TransformerType]Transformer)

func NewTransformer(transformerType TransformerType) (Transformer, error) {
	if transformer, ok := registeredTransformers[transformerType]; ok {
		return transformer, nil
	}
	return nil, fmt.Errorf("unsurported transformer type: %s", transformerType)
}
