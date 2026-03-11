package main

import (
	"context"
	"log"
	"net/http"
	"time"

	"auth/internal/config"
	"auth/internal/handler"
	"auth/internal/store/pgstore"
	"auth/internal/token"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/jackc/pgx/v5/pgxpool"
	httpSwagger "github.com/swaggo/http-swagger/v2"

	_ "auth/docs"
)

// @title Auth Service API
// @version 1.0
// @description Authentication service.
// @host localhost:3000
// @BasePath /
func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	dbpool, err := pgxpool.New(context.Background(), cfg.DatabaseURL)
	if err != nil {
		log.Fatalf("Unable to connect to database: %v", err)
	}
	defer dbpool.Close()

	userStore := pgstore.New(dbpool)
	tokenService := token.NewTokenService(cfg.JWTSecret, "auth-service", 24*time.Hour)
	authHandler := handler.NewAuthHandler(userStore, tokenService)

	r := chi.NewRouter()
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)

	r.Post("/auth/register", authHandler.Register)
	r.Post("/auth/login", authHandler.Login)

	// Swagger documentation
	r.Get("/swagger/*", httpSwagger.Handler(
		httpSwagger.URL("http://localhost:3000/swagger/doc.json"),
	))

	log.Printf("Starting server on port %s", cfg.Port)
	if err := http.ListenAndServe(":"+cfg.Port, r); err != nil {
		log.Panic(err)
	}
}
