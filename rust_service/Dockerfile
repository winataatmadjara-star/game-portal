# Tahap Build
FROM rust:1.75-slim as builder
WORKDIR /app
COPY . .
RUN cargo build --release

# Tahap Runtime
FROM debian:bookworm-slim
WORKDIR /app
COPY --from=builder /app/target/release/nama_binary_rust ./app
# Sesuaikan port jika service Rust Anda berjalan di port tertentu (misal 8080)
EXPOSE 8080
CMD ["./app"]