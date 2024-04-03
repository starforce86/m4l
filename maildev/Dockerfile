# syntax=docker/dockerfile:1.5

ARG NODE_VERSION=16.17.1

FROM node:${NODE_VERSION}-alpine AS install-maildev

RUN mkdir -p /usr/local/lib/node_modules && chown -R node:node /usr/local

USER node

ARG MAILDEV_VERSION=2.0.5

RUN --mount=type=cache,target=/home/node/.npm,uid=1000,gid=1000 \
    npm i -g maildev@${MAILDEV_VERSION}

###############################################################################

FROM golang:1.20-alpine AS build-healthcheck

WORKDIR /build

COPY <<EOF ./http_healthcheck.go
package main
import (
	"net/http"
	"os"
)
func main() {
	_, err := http.Get(os.Args[1])
	if err != nil { os.Exit(1) }
}
EOF

RUN go build -o http_healthcheck ./http_healthcheck.go

###############################################################################

FROM install-maildev AS run-maildev

EXPOSE 1025
EXPOSE 1080

COPY --chown=node:node --from=build-healthcheck /build/http_healthcheck /usr/local/bin/
RUN chmod +x /usr/local/bin/http_healthcheck
HEALTHCHECK --interval=2s --timeout=5s --start-period=5s --retries=10 \
    CMD [ "http_healthcheck", "http://localhost:1080/" ]

CMD ["maildev"]
