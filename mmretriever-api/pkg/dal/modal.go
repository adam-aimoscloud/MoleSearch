package dal

type Embedding []float64

type TextEmbedding struct {
	Chunk string `json:"chunk"`
	Embedding Embedding `json:"embedding"`
}

type IndexParam struct {
	Texts []string `json:"texts"`
	TextEmbeddings []Embedding `json:"text_embeddings"`
	ImageEmbeddings []ImageEmbedding `json:"image_embeddings"`
}
type ImageEmbedding struct {
	ImageURL string `json:"image_url"`
	ImageBase64 string `json:"image_base64"`
	Embedding Embedding `json:"embedding"`
}

type TextModal struct {
	Text string `json:"text"`
	Embeddings []TextEmbedding `json:"embeddings"`
}

type ImageModal struct {
	ImageURL string `json:"image_url"`
	ImageBase64 string `json:"image_base64"`
	Text string `json:"text"`
	ImageEmbedding ImageEmbedding `json:"image_embedding"`
	TextEmbedding TextEmbedding `json:"text_embedding"`   // image caption or description embedding
}

type VideoModal struct {
