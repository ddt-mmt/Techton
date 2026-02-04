# Stage 1: Build k6 with LDAP extension
FROM golang:1.25-alpine as builder
ENV GOPROXY=https://proxy.golang.org,direct
WORKDIR /go/src/app

# Install git and build tools
RUN apk add --no-cache git make build-base

# Install xk6 (Latest version requires Go 1.25, which we have)
RUN go install go.k6.io/xk6/cmd/xk6@latest

# Build k6 with xk6-ldap
# We use --replace to force using the correct module path if needed, 
# but first let's try standard build with env vars
ENV CGO_ENABLED=0
RUN xk6 build v0.50.0 --with github.com/kressnick25/xk6-ldap

# Stage 2: Final lightweight image
FROM alpine:latest
RUN apk add --no-cache ca-certificates

# Copy k6 binary from builder
COPY --from=builder /go/src/app/k6 /usr/bin/k6

# Create workspace
WORKDIR /tests
ENTRYPOINT ["k6"]