#!/bin/bash

# Script para rodar o IsCoolGPT
# Uso: ./rodar.sh

cd "$(dirname "$0")"

echo "🚀 Iniciando IsCoolGPT..."
echo ""

# Ativa o ambiente virtual
source venv/bin/activate

# Roda o servidor
python main.py

