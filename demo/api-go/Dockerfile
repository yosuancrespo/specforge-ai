FROM golang:1.23-alpine

WORKDIR /app

COPY go.mod ./
COPY cmd ./cmd

RUN go build -o /specforge-demo-api ./cmd/server

EXPOSE 8080

CMD ["/specforge-demo-api"]

