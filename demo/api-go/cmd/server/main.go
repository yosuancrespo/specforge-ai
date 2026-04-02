package main

import (
	"encoding/json"
	"log"
	"net/http"
	"strings"
	"sync"
	"time"
)

type OrderItem struct {
	SKU      string `json:"sku"`
	Quantity int    `json:"quantity"`
}

type CreateOrderRequest struct {
	CustomerID string      `json:"customer_id"`
	Items      []OrderItem `json:"items"`
	Amount     float64     `json:"amount"`
	Discount   float64     `json:"discount"`
	Currency   string      `json:"currency"`
}

type Order struct {
	ID         string      `json:"id"`
	CustomerID string      `json:"customer_id"`
	Items      []OrderItem `json:"items"`
	Amount     float64     `json:"amount"`
	Discount   float64     `json:"discount"`
	Currency   string      `json:"currency"`
	Status     string      `json:"status"`
	CreatedAt  time.Time   `json:"created_at"`
}

type Summary struct {
	OrderID    string  `json:"order_id"`
	Amount     float64 `json:"amount"`
	Discount   float64 `json:"discount"`
	FinalTotal float64 `json:"final_total"`
}

var (
	orderStore = map[string]Order{}
	storeMu    sync.RWMutex
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/health", handleHealth)
	mux.HandleFunc("/orders", handleCreateOrder)
	mux.HandleFunc("/orders/", handleOrderRoutes)

	log.Println("SpecForge demo API listening on :8080")
	if err := http.ListenAndServe(":8080", mux); err != nil {
		log.Fatal(err)
	}
}

func handleHealth(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
}

func handleCreateOrder(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.NotFound(w, r)
		return
	}

	var payload CreateOrderRequest
	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid json body"})
		return
	}

	if payload.CustomerID == "" || payload.Currency == "" {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "customer_id and currency are required"})
		return
	}

	// Seeded defects:
	// - Missing validation for empty items
	// - Missing validation for non-positive amount
	// - Missing validation for discount > amount
	orderID := time.Now().UTC().Format("20060102150405.000000")
	order := Order{
		ID:         "ord-" + strings.ReplaceAll(orderID, ".", ""),
		CustomerID: payload.CustomerID,
		Items:      payload.Items,
		Amount:     payload.Amount,
		Discount:   payload.Discount,
		Currency:   payload.Currency,
		Status:     "draft",
		CreatedAt:  time.Now().UTC(),
	}

	storeMu.Lock()
	orderStore[order.ID] = order
	storeMu.Unlock()

	writeJSON(w, http.StatusCreated, order)
}

func handleOrderRoutes(w http.ResponseWriter, r *http.Request) {
	path := strings.TrimPrefix(r.URL.Path, "/orders/")
	parts := strings.Split(path, "/")
	if len(parts) == 0 || parts[0] == "" {
		http.NotFound(w, r)
		return
	}

	orderID := parts[0]
	order, ok := getOrder(orderID)
	if !ok {
		writeJSON(w, http.StatusNotFound, map[string]string{"error": "order not found"})
		return
	}

	if len(parts) == 1 && r.Method == http.MethodGet {
		writeJSON(w, http.StatusOK, order)
		return
	}

	if len(parts) == 2 && parts[1] == "summary" && r.Method == http.MethodGet {
		summary := Summary{
			OrderID:    order.ID,
			Amount:     order.Amount,
			Discount:   order.Discount,
			FinalTotal: order.Amount + order.Discount, // Seeded defect: should subtract.
		}
		writeJSON(w, http.StatusOK, summary)
		return
	}

	if len(parts) == 2 && parts[1] == "status" && r.Method == http.MethodPost {
		var payload map[string]string
		if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
			writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid status body"})
			return
		}
		order.Status = payload["status"] // Seeded defect: no transition guard.
		storeMu.Lock()
		orderStore[order.ID] = order
		storeMu.Unlock()
		writeJSON(w, http.StatusOK, order)
		return
	}

	http.NotFound(w, r)
}

func getOrder(orderID string) (Order, bool) {
	storeMu.RLock()
	defer storeMu.RUnlock()
	order, ok := orderStore[orderID]
	return order, ok
}

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("content-type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(payload)
}

