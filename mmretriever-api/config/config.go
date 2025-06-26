package config

import (
	"os"

	"gopkg.in/yaml.v3"
)

type Config struct {
	Components map[string]interface{} `json:"components" yaml:"components"`
}

func (cfg *Config) LoadConfigFromYaml(configPath string) error {
	data, err := os.ReadFile(configPath)
	if err != nil {
		return err
	}
	cfg.Components = make(map[string]interface{})
	err = yaml.Unmarshal(data, cfg)
	return err
}

func (cfg *Config) GetComponents() interface{} {
	return cfg.Components
}
