param(
    [Parameter(Mandatory)][string]$RequestId,
    [Parameter(Mandatory)][string]$Amount,
    [Parameter(Mandatory)][string]$Status,
    [Parameter(Mandatory)][string]$ReceiptDigest
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($env:DISCORD_WEBHOOK_URL)) {
    throw "DISCORD_WEBHOOK_URL is not loaded."
}

$payload = @{
    username = "JSONWisdom ReceiptOS"
    content = @"
⚙️ RECEIPTOS EVENT

Identity: jaywisdom.eth
Request: $RequestId
Amount: $Amount
Status: $Status
Receipt: $ReceiptDigest
Authority created: FALSE
"@
    allowed_mentions = @{
        parse = @()
    }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
    -Method Post `
    -Uri "$($env:DISCORD_WEBHOOK_URL)?wait=true" `
    -ContentType "application/json" `
    -Body $payload | Out-Null

Write-Host "PASS: Receipt notification delivered."
