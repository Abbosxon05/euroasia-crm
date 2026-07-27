$ghZip = "$env:TEMP\gh.zip"
$ghDir = "$env:TEMP\gh_cli"
$ghExe = "$ghDir\gh_2.96.0_windows_amd64\bin\gh.exe"
$repoDir = "C:\Users\Abbosxon\Downloads\euro asia"

Write-Host "=== GitHub CLI yuklanmoqda ===" -ForegroundColor Cyan
Invoke-WebRequest -Uri "https://github.com/cli/cli/releases/download/v2.96.0/gh_2.96.0_windows_amd64.zip" -OutFile $ghZip -UseBasicParsing
Write-Host "OK - Yuklab olindi!" -ForegroundColor Green

Expand-Archive -Path $ghZip -DestinationPath $ghDir -Force
Write-Host "OK - Chiqarildi!" -ForegroundColor Green

Write-Host ""
Write-Host "=== GitHub Login ===" -ForegroundColor Cyan
Write-Host "Brauzer ochiladi, GitHub-ga kirib tasdiqlang..." -ForegroundColor Yellow
& $ghExe auth login --web --git-protocol https

Write-Host ""
Write-Host "=== Repo yaratilmoqda ===" -ForegroundColor Cyan
Set-Location $repoDir
& $ghExe repo create Abbosxon05/euroasia-crm --public --description "EuroAsia Education CRM - Sodda HEMIS" --confirm 2>$null
Write-Host "OK - Repo tayyor!" -ForegroundColor Green

Write-Host ""
Write-Host "=== Fayllar yuklanmoqda (git push) ===" -ForegroundColor Cyan
git add .
git commit -m "EuroAsia CRM v7.0 - Sodda HEMIS + APK Action" 2>$null
git push -u origin main --force

Write-Host ""
Write-Host "=== TAYYOR! ===" -ForegroundColor Green
Write-Host "GitHub Actions APK yasashni boshlaydi. 5-10 daqiqa kuting." -ForegroundColor Yellow
Write-Host "Keyin shu yerga boring: https://github.com/Abbosxon05/euroasia-crm/actions" -ForegroundColor Cyan
