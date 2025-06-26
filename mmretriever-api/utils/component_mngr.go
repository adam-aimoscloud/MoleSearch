package utils

import (
	"fmt"
)

type ComponentMngr struct {
}

type ComponentFactory interface {
	Config() interface{}
	SetConfig(config interface{})
	GetOrCreateInstance() (interface{}, error)
}

var allRegisteredComponentFactories map[string]ComponentFactory

func init() {
	allRegisteredComponentFactories = make(map[string]ComponentFactory)
}

func (mngr *ComponentMngr) RegisterComponentFactory(name string, componentFactory ComponentFactory) {
	if _, ok := allRegisteredComponentFactories[name]; ok {
		panic(fmt.Sprintf("componentFactory %s already registered", name))
	}
	allRegisteredComponentFactories[name] = componentFactory
}

func (mngr *ComponentMngr) GenerateConfigTemplate() interface{} {
	result := make(map[string]interface{})
	for name, componentFactory := range allRegisteredComponentFactories {
		result[name] = componentFactory.Config()
	}
	return result
}

func (mngr *ComponentMngr) GetComponentConfig(name string) interface{} {
	if cf, ok := allRegisteredComponentFactories[name]; ok {
		return cf.Config()
	}
	return nil
}

func (mngr *ComponentMngr) SetConfig(componentConfig interface{}) error {
	config := make(map[string]interface{})
	if cfg, ok := componentConfig.(map[string]interface{}); ok {
		config = cfg
	}
	for name, cfg := range config {
		if componentFactory, ok := allRegisteredComponentFactories[name]; ok {
			componentFactory.SetConfig(cfg)
		}
	}
	return nil
}

func (mngr *ComponentMngr) GetComponent(name string) (interface{}, error) {
	if cf, ok := allRegisteredComponentFactories[name]; ok {
		return cf.GetOrCreateInstance()
	}
	return nil, fmt.Errorf("component %s not found", name)
}
