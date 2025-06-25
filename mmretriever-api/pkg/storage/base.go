package storage

import "fmt"

type Storage interface {
	Initialize(config interface{}) (err error)
	Save(fileB64orURL string, fileName string) (url string, err error)
	GetURL(fileNameorURL string) (url string, err error)
}

type StorageType string

const (
	StorageTypeOSSAliyun = "oss-aliyun"
)

var registeredStorage = make(map[StorageType]Storage)

func NewStorage(storageType StorageType) (Storage, error) {
	if storage, ok := registeredStorage[storageType]; ok {
		return storage, nil
	}
	return nil, fmt.Errorf("unsupported storage type: %s", storageType)
}
