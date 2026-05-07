param(
    [string]$Message
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

$branch = (git branch --show-current).Trim()
if (-not $branch) {
    $branch = "main"
    git checkout -B $branch
}

Write-Host ""
Write-Host "Repository: $repoRoot"
Write-Host "Branch:     $branch"
Write-Host ""

git status --short

if (-not $Message) {
    $Message = Read-Host "Commit message"
}

if (-not $Message) {
    $Message = "Update fv_runner"
}

git add -A

git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m $Message
} else {
    Write-Host "No local changes to commit."
}

git push -u origin $branch

Write-Host ""
Write-Host "Push complete."
