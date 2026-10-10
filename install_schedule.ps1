# Script de Agendamento no Windows Task Scheduler para LigaPokemon Scraper
$TaskName = "LigaPokemonScraper"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c cd /d `"$ScriptDir`" && python scraper.py >> data\scheduler.log 2>&1"

# Horário agendado: 20:00 (8:00 PM)
$Trigger = New-ScheduledTaskTrigger -Daily -At 8:00PM

# Configurações: StartWhenAvailable garante que se o PC estava desligado às 20:00,
# a tarefa roda na primeira inicialização após esse horário.
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   AGENDADOR DIÁRIO - SCRAPER LIGAPOKEMON" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Criando/Atualizando tarefa agendada: $TaskName"
Write-Host "Horário agendado: Diariamente às 20:00 (8:00 PM)"
Write-Host "Opção ativada: Executar na 1ª inicialização se o PC estava desligado às 20:00"

try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -User $env:USERNAME -Force
    Write-Host "`n[SUCESSO] Tarefa agendada '$TaskName' atualizada com sucesso!" -ForegroundColor Green
    Write-Host "Log de execução será salvo em: $ScriptDir\data\scheduler.log"
} catch {
    Write-Host "`n[ERRO] Falha ao criar a tarefa: $_" -ForegroundColor Red
}
