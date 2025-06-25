package searchengine

import (
	"fmt"
	"mmretriever-api/pkg/dal"
)

type SearchEngine interface {
	Initialize(config interface{}) (err error)
	Add(dal.MultiModalData) (err error)
	Search(dal.MultiModalData) (results []dal.MultiModalData, err error)
}

type SearchEngineType string

const (
	SearchEngineTypeES = "elasticsearch"
)

var registeredSearchEngine = make(map[SearchEngineType]SearchEngine)

func NewSearchEngine(searchEngineType SearchEngineType) (SearchEngine, error) {
	if searchEngine, ok := registeredSearchEngine[searchEngineType]; ok {
		return searchEngine, nil
	}
	return nil, fmt.Errorf("unsupported search engine type: %s", searchEngineType)
}
