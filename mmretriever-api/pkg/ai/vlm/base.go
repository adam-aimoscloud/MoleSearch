package vlm

import "fmt"

type VLMInference interface {
	Initialize(config interface{}) (err error)
	Image(imageBase64orURL string, prompt string) (text string, err error)
}

type VLMType string

const (
	QwenVLM = "qwen"
)

var registeredVLM = make(map[VLMType]VLMInference)

func NewVLM(vlmType VLMType) (VLMInference, error) {
	if vlm, ok := registeredVLM[vlmType]; ok {
		return vlm, nil
	}
	return nil, fmt.Errorf("unsupported vlm type: %s", vlmType)
}
