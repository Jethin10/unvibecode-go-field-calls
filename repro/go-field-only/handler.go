// handler.go
package shop

type Handler struct {
	svc *OrderService
}

func (h *Handler) CreateOrder(id string, cents int) error {
	return h.svc.Place(id, cents) // through a field
}
