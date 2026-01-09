#!/bin/sh

echo "🟡 Aguardando o PostgreSQL iniciar em $POSTGRES_HOST:$POSTGRES_PORT..."

# O comando pg_isready vem no pacote postgresql-client
while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
  echo "⏳ PostgreSQL ainda não está pronto - aguardando 2 segundos..."
  sleep 2
done

echo "✅ PostgreSQL iniciado e aceitando conexões!"
