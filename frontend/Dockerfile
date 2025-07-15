# frontend/Dockerfile

FROM oven/bun:1.0 AS builder
WORKDIR /app
COPY . .
RUN bun install
RUN bun run build

FROM oven/bun:1.0 AS runner
WORKDIR /app
COPY --from=builder /app .
EXPOSE 3000
CMD ["bun", "run", "start"]
