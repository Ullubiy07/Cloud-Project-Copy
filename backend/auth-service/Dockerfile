# Build stage
FROM golang:1.25-alpine AS builder

WORKDIR /app

# Install git for fetching dependencies
RUN apk add --no-cache git

COPY go.mod go.sum ./
RUN go mod download

COPY . .

# Build the application
# CGO_ENABLED=0 creates a statically linked binary
RUN CGO_ENABLED=0 GOOS=linux go build -o auth-service cmd/auth/main.go

# Run stage
FROM alpine:latest

WORKDIR /root/

# Install ca-certificates for HTTPS calls
RUN apk --no-cache add ca-certificates

COPY --from=builder /app/auth-service .

# Expose the application port
EXPOSE 3000

CMD ["./auth-service"]
