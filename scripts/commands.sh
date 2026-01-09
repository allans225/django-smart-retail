#!/bin/sh

# O shell irá encerrar a execução do script quando um comando falhar
# The shell will exit the script execution when a command fails
set -e

# Executa o script de espera antes de qualquer coisa
# Run the wait script before anything else
wait_psql.sh

collectstatic.sh
makemigrations.sh
migrate.sh
runserver.sh
