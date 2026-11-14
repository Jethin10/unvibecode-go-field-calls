package shop

type OrderStore struct{ rows map[string]int }

func NewOrderStore() *OrderStore { return &OrderStore{rows: map[string]int{}} }

func (s *OrderStore) Insert(id string, cents int) error {
	s.rows[id] = cents
	return nil
}
