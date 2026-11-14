package shop

type Handler struct {
	svc *OrderService
}

func NewHandler(svc *OrderService) *Handler { return &Handler{svc: svc} }

func (h *Handler) CreateOrder(id string, cents int) error {
	return h.svc.Place(id, cents)
}
