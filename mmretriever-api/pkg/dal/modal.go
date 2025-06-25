package dal

type Embedding []float64

type IndexParam struct {
	Texts           []string    `json:"texts"`
	TextEmbeddings  []Embedding `json:"text_embeddings"`
	ImageEmbeddings []Embedding `json:"image_embeddings"`
}

type MultiModalData struct {
	Text          string     `json:"text"`
	ImageB64orURL string     `json:"image_b64_or_url"`
	VideoB64orURL string     `json:"video_b64_or_url"`
	IndexParam    IndexParam `json:"index_param"`
}
