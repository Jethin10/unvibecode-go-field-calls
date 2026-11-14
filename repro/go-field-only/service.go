// service.go
package shop

type OrderService struct {
	store *OrderStore
}

func (o *OrderService) Place(id string, cents int) error {
	return o.store.Insert(id, cents) // through a field
}
