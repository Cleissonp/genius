# Script para fazer push para GitHub
# Execute este arquivo no PowerShell (clique direito > Run with PowerShell)

Write-Host "🚀 Genius — Push para GitHub" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""

# Ir para a pasta do projeto
cd C:\Users\Cleisson\Documents\Arduino\Genius

# Configurar branch main
Write-Host "1️⃣  Configurando branch..." -ForegroundColor Cyan
git branch -M main

# Remover remote antigo (se existir)
git remote remove origin 2>$null

# Adicionar remote
Write-Host "2️⃣  Adicionando remote..." -ForegroundColor Cyan
git remote add origin "https://github.com/Cleissonp/genius.git"

# Fazer push
Write-Host "3️⃣  Fazendo push para GitHub..." -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  Será pedido seu usuário e token" -ForegroundColor Yellow
Write-Host "   Usuário: Cleissonp" -ForegroundColor Gray
Write-Host "   Token: (cole seu github_pat_...)" -ForegroundColor Gray
Write-Host ""

git push -u origin main

Write-Host ""
Write-Host "✅ Push concluído!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Seu repositório: https://github.com/Cleissonp/genius" -ForegroundColor Cyan
