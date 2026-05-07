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

git fetch origin
git pull --rebase origin $branch

Write-Host ""
Write-Host "Pull complete."
