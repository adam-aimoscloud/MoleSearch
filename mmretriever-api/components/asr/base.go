package asr

import "fmt"

type ASR interface {
	Initialize(config interface{}) (err error)
	Infer(audioBase64orURL string) (text string, err error)
}

type ASRType string

const (
	ASRTypeQwen = "qwen"
)

var registeredASR map[ASRType]ASR

func NewASR(asrType ASRType) (ASR, error) {
	if asr, ok := registeredASR[asrType]; ok {
		return asr, nil
	}
	return nil, fmt.Errorf("unsupported asr type: %s", asrType)
}
