package shop

type OrderService struct {
	store *OrderStore
}

func NewOrderService(st *OrderStore) *OrderService { return &OrderService{store: st} }

// Place persists through a struct field (the usual dependency-injection shape).
func (o *OrderService) Place(id string, cents int) error {
	return o.store.Insert(id, cents)
}

// PlaceDirect is the control: same call, receiver is a parameter.
func PlaceDirect(st *OrderStore, id string, cents int) error {
	return st.Insert(id, cents)
}
