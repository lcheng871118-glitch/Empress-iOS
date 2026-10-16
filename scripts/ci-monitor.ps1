param(
  [string]$Repo = "lcheng871118-glitch/Empress-iOS",
  [string]$LogDir = ""
)
if (-not $LogDir) { $LogDir = Split-Path -Parent $MyInvocation.MyCommand.Definition }
$ErrorActionPreference = "Stop"

function Get-Token {
  $tok = [IO.File]::ReadAllText((Join-Path $LogDir ".token.tmp")).Trim()
  return $tok
}

$targetSha = (git -C $LogDir rev-parse origin/main).Trim()
"TARGET_COMMIT: $targetSha"

$tok = Get-Token
$bodyFile = Join-Path $LogDir ".dispatch-body.json"
[IO.File]::WriteAllText($bodyFile, '{"ref":"main"}', (New-Object Text.UTF8Encoding($false)))
$dispatchHttp = curl.exe -s -m 20 -X POST -H "Authorization: Bearer $tok" -H "Accept: application/vnd.github+json" -H "Content-Type: application/json" -d "@$bodyFile" -w "|%{http_code}" "https://api.github.com/repos/$Repo/actions/workflows/build-ios.yml/dispatches"
"DISPATCH: $dispatchHttp"
if (-not $dispatchHttp.Contains("|204")) { "DISPATCH_FAILED, aborting"; exit 3 }
"DISPATCH_SENT, monitoring..."

$deadline = (Get-Date).AddMinutes(30)
while ((Get-Date) -lt $deadline) {
  Start-Sleep -Seconds 25
  try {
    $json = curl.exe -s -m 15 -H "Authorization: Bearer $tok" "https://api.github.com/repos/$Repo/actions/runs?per_page=3"
    $d = $json | ConvertFrom-Json
    $run = $d.workflow_runs | Where-Object { $_.head_sha -eq $targetSha } | Select-Object -First 1
    if ($null -eq $run) { "WAIT_RUN_CREATED ..."; continue }
    "RUN $($run.id) status=$($run.status)"
    if ($run.status -eq "completed") {
      if ($run.conclusion -eq "success") {
        "RESULT: SUCCESS run=$($run.id)"
        exit 0
      } else {
        "RESULT: FAILURE reason=$($run.conclusion)"
        $jobs = curl.exe -s -m 15 -H "Authorization: Bearer $tok" "https://api.github.com/repos/$Repo/actions/runs/$($run.id)/jobs" | ConvertFrom-Json
        $job = $jobs.jobs | Where-Object { $_.conclusion -eq "failure" } | Select-Object -First 1
        if ($null -eq $job) { $job = $jobs.jobs[0] }
        curl.exe -sL -m 60 -H "Authorization: Bearer $tok" "https://api.github.com/repos/$Repo/actions/jobs/$($job.id)/logs" -o "$LogDir\ci-last-log.txt"
        "LOG_SAVED: ci-last-log.txt"
        exit 1
      }
    }
  } catch {
    "POLL_ERROR: $_"
    Start-Sleep -Seconds 10
  }
}
"RESULT: TIMEOUT"
exit 2