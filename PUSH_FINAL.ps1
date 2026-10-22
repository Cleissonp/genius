# ============================================
# Script Final: Push para GitHub - Genius Neon
# ============================================
# Execute este script NO SEU PowerShell!

Write-Host "🚀 Genius Neon — Push Final para GitHub" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""

# Variáveis
$username = "Cleissonp"
$repo = "genius"

# Ir para pasta do projeto
cd C:\Users\Cleisson\Documents\Arduino\Genius

Write-Host "1️⃣  Verificando git..." -ForegroundColor Cyan
git --version
Write-Host ""

Write-Host "2️⃣  Verificando status do repositório..." -ForegroundColor Cyan
git status
Write-Host ""

Write-Host "3️⃣  Configurando credenciais..." -ForegroundColor Cyan
git config --global credential.helper wincred
Write-Host "   ✓ Credential helper: wincred" -ForegroundColor Green
Write-Host ""

Write-Host "4️⃣  Configurando branch..." -ForegroundColor Cyan
git branch -M main
Write-Host "   ✓ Branch: main" -ForegroundColor Green
Write-Host ""

Write-Host "5️⃣  Configurando remote..." -ForegroundColor Cyan
git remote remove origin 2>$null
git remote add origin "https://github.com/${username}/${repo}.git"
Write-Host "   ✓ Remote: https://github.com/${username}/${repo}" -ForegroundColor Green
git remote -v
Write-Host ""

Write-Host "6️⃣  FAZENDO PUSH..." -ForegroundColor Yellow
Write-Host "   Quando pedir autenticação:" -ForegroundColor Yellow
Write-Host "   - Username: Cleissonp" -ForegroundColor Gray
Write-Host "   - Password: (cole o token ou deixa a janela fazer)" -ForegroundColor Gray
Write-Host ""

# Fazer push
git push -u origin main

Write-Host ""
if ($LASTEXITCODE -eq 0) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Host "✅ SUCESSO! Push concluído!" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Host ""
    Write-Host "📍 Repositório: https://github.com/${username}/${repo}" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✓ Firmware + Cliente Python + Documentação" -ForegroundColor Green
    Write-Host "✓ 15 Testes unitários" -ForegroundColor Green
    Write-Host "✓ 7 Documentos de deploy" -ForegroundColor Green
} else {
    Write-Host "❌ Erro no push" -ForegroundColor Red
    Write-Host "Código: $LASTEXITCODE" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Pressione Enter para fechar..." -ForegroundColor Gray
Read-Host
