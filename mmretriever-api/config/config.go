package config

import (
	"mmretriever-api/pkg/ai/text_embedding"
	"os"

	"gopkg.in/yaml.v3"
)

type Config struct {
	TextEmbedding TextEmbeddingConfig `yaml:"embedding"`
}

type TextEmbeddingConfig struct {
	EmbeddingType string                    `yaml:"embedding_type" json:"embedding_type"`
	Qwen          text_embedding.QwenConfig `yaml:"qwen" json:"qwen"`
}

func NewConfig() *Config {
	return &Config{}
}

func (cfg *Config) LoadConfigFromYaml(configPath string) (err error) {
	data, err := os.ReadFile(configPath)
	if err != nil {
		return err
	}
	return yaml.Unmarshal(data, cfg)
}

func (cfg *Config) GetTextEmbeddingConfig() *TextEmbeddingConfig {
	return &TextEmbeddingConfig{
		EmbeddingType: cfg.TextEmbedding.EmbeddingType,
		Qwen:          cfg.TextEmbedding.Qwen,
	}
}

func (cfg *Config) GetQwenConfig() text_embedding.QwenConfig {
	return cfg.TextEmbedding.Qwen
}
