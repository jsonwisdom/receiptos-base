[CmdletBinding()]
param(
    [string]$OutputRoot = [Environment]::GetFolderPath('Desktop')
)

$ErrorActionPreference = 'Stop'
$Project = 'jsonwisdom/receiptos-base'
$CharterCommit = '88145a21d298cc17607ed44be5459db6be329fd2'
$ScriptVersion = '0.1.0'
$Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$OutDir = Join-Path $OutputRoot "Jason-Deep-Proof-$Stamp"
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

function Test-IsAdministrator {
    try {
        $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = [Security.Principal.WindowsPrincipal]::new($identity)
        return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    }
    catch { return $false }
}

function Invoke-Probe {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][scriptblock]$Action
    )

    $started = [DateTime]::UtcNow
    try {
        $data = @(& $Action)
        $status = if ($data.Count -gt 0 -and $null -ne $data[0]) { 'OBSERVED' } else { 'EMPTY' }
        [pscustomobject]@{
            probe_name   = $Name
            status       = $status
            observed_utc = $started.ToString('o')
            duration_ms  = [math]::Round(([DateTime]::UtcNow - $started).TotalMilliseconds, 2)
            data         = $data
            error        = $null
        }
    }
    catch {
        [pscustomobject]@{
            probe_name   = $Name
            status       = 'UNAVAILABLE'
            observed_utc = $started.ToString('o')
            duration_ms  = [math]::Round(([DateTime]::UtcNow - $started).TotalMilliseconds, 2)
            data         = @()
            error        = $_.Exception.Message
        }
    }
}

function Classify-Capability {
    param(
        [Parameter(Mandatory)][string]$Domain,
        [Parameter(Mandatory)][object]$Observation
    )

    $tier = switch ($Domain) {
        'system'         { 'PLATFORM_IDENTITY' }
        'cpu'            { 'COMPUTE_BASE' }
        'firmware'       { 'TRUST_ROOT' }
        'device_guard'   { 'HARDENING' }
        'memory'         { 'WORKING_CAPACITY' }
        'disks'          { 'PERSISTENCE' }
        'graphics'       { 'ACCELERATION' }
        'security'       { 'DEFENSE' }
        'virtualization' { 'ISOLATION' }
        'power_recovery' { 'RESILIENCE' }
        'updates'        { 'MAINTENANCE_STATE' }
        default          { 'MISC' }
    }

    $hints = [System.Collections.Generic.List[string]]::new()
    if ($Observation.status -ne 'OBSERVED') { $hints.Add('EVIDENCE_INCOMPLETE') }
    if ($Domain -in @('firmware','device_guard','security') -and $Observation.status -ne 'OBSERVED') {
        $hints.Add('TRUST_CLAIM_BLOCKED')
    }
    if ($Domain -eq 'power_recovery' -and $Observation.status -ne 'OBSERVED') {
        $hints.Add('RECOVERY_CLAIM_BLOCKED')
    }
    if ($hints.Count -eq 0) { $hints.Add('NO_DATA_QUALITY_WARNING') }

    [pscustomobject]@{
        domain           = $Domain
        capability_tier  = $tier
        integrity_status = $Observation.status
        risk_hints       = @($hints)
        observation      = $Observation
    }
}

$isAdmin = Test-IsAdministrator

$systemProbe = Invoke-Probe 'system' {
    Get-ComputerInfo -ErrorAction Stop | Select-Object WindowsProductName,WindowsVersion,
        OsBuildNumber,OsArchitecture,CsManufacturer,CsModel,CsProcessors,
        CsTotalPhysicalMemory,BiosFirmwareType
}

$cpuProbe = Invoke-Probe 'cpu' {
    Get-CimInstance Win32_Processor -ErrorAction Stop | Select-Object Name,Manufacturer,
        NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed,AddressWidth,
        VirtualizationFirmwareEnabled,SecondLevelAddressTranslationExtensions
}

$firmwareProbe = Invoke-Probe 'firmware' {
    [pscustomobject]@{
        bios = @(Get-CimInstance Win32_BIOS -ErrorAction Stop | Select-Object Manufacturer,
            SMBIOSBIOSVersion,ReleaseDate)
        secure_boot = try { Confirm-SecureBootUEFI -ErrorAction Stop } catch { "UNAVAILABLE: $($_.Exception.Message)" }
        tpm = try { @(Get-Tpm -ErrorAction Stop | Select-Object TpmPresent,TpmReady,TpmEnabled,
            TpmActivated,ManufacturerIdTxt,ManufacturerVersion) } catch { @([pscustomobject]@{status='UNAVAILABLE';error=$_.Exception.Message}) }
    }
}

$deviceGuardProbe = Invoke-Probe 'device_guard' {
    Get-CimInstance -Namespace root\Microsoft\Windows\DeviceGuard -ClassName Win32_DeviceGuard -ErrorAction Stop |
        Select-Object VirtualizationBasedSecurityStatus,SecurityServicesConfigured,
        SecurityServicesRunning,RequiredSecurityProperties,AvailableSecurityProperties
}

$memoryProbe = Invoke-Probe 'memory' {
    Get-CimInstance Win32_PhysicalMemory -ErrorAction Stop | Select-Object Manufacturer,PartNumber,
        @{N='CapacityGB';E={[math]::Round($_.Capacity/1GB,2)}},Speed,ConfiguredClockSpeed,DeviceLocator
}

$diskProbe = Invoke-Probe 'disks' {
    Get-PhysicalDisk -ErrorAction Stop | Select-Object FriendlyName,MediaType,BusType,
        @{N='SizeGB';E={[math]::Round($_.Size/1GB,2)}},HealthStatus,OperationalStatus
}

$graphicsProbe = Invoke-Probe 'graphics' {
    Get-CimInstance Win32_VideoController -ErrorAction Stop |
        Select-Object Name,VideoProcessor,DriverVersion,
            @{N='AdapterRAMGB';E={if ($_.AdapterRAM) {[math]::Round($_.AdapterRAM/1GB,2)} else {$null}}}
}

$securityProbe = Invoke-Probe 'security' {
    [pscustomobject]@{
        bitlocker = try { @(Get-BitLockerVolume -ErrorAction Stop | Select-Object MountPoint,VolumeType,
            ProtectionStatus,EncryptionPercentage,EncryptionMethod) } catch { @([pscustomobject]@{status='UNAVAILABLE';error=$_.Exception.Message}) }
        defender = try { @(Get-MpComputerStatus -ErrorAction Stop | Select-Object AntivirusEnabled,
            RealTimeProtectionEnabled,BehaviorMonitorEnabled,IoavProtectionEnabled,
            IsTamperProtected,AntivirusSignatureVersion,AntivirusSignatureLastUpdated) } catch { @([pscustomobject]@{status='UNAVAILABLE';error=$_.Exception.Message}) }
        firewall = try { @(Get-NetFirewallProfile -ErrorAction Stop | Select-Object Name,Enabled,
            DefaultInboundAction,DefaultOutboundAction) } catch { @([pscustomobject]@{status='UNAVAILABLE';error=$_.Exception.Message}) }
    }
}

$virtualizationProbe = Invoke-Probe 'virtualization' {
    [pscustomobject]@{
        hypervisor_present = (Get-CimInstance Win32_ComputerSystem -ErrorAction Stop).HypervisorPresent
        enabled_features = @(Get-WindowsOptionalFeature -Online -ErrorAction Stop |
            Where-Object { $_.State -eq 'Enabled' -and $_.FeatureName -match 'Hyper|Virtual|Sandbox|Linux' } |
            Select-Object FeatureName,State)
    }
}

$powerProbe = Invoke-Probe 'power_recovery' {
    [pscustomobject]@{
        battery = @(Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue |
            Select-Object Name,BatteryStatus,EstimatedChargeRemaining,DesignVoltage)
        available_sleep_states = @(powercfg /a 2>&1)
        recovery_environment = @(reagentc /info 2>&1)
    }
}

$updatesProbe = Invoke-Probe 'updates' {
    Get-HotFix -ErrorAction Stop | Sort-Object InstalledOn -Descending |
        Select-Object -First 20 HotFixID,Description,InstalledOn
}

$capabilities = [ordered]@{
    system         = Classify-Capability 'system' $systemProbe
    cpu            = Classify-Capability 'cpu' $cpuProbe
    firmware       = Classify-Capability 'firmware' $firmwareProbe
    device_guard   = Classify-Capability 'device_guard' $deviceGuardProbe
    memory         = Classify-Capability 'memory' $memoryProbe
    disks          = Classify-Capability 'disks' $diskProbe
    graphics       = Classify-Capability 'graphics' $graphicsProbe
    security       = Classify-Capability 'security' $securityProbe
    virtualization = Classify-Capability 'virtualization' $virtualizationProbe
    power_recovery = Classify-Capability 'power_recovery' $powerProbe
    updates        = Classify-Capability 'updates' $updatesProbe
}

$observedCount = @($capabilities.Values | Where-Object integrity_status -eq 'OBSERVED').Count
$incompleteCount = @($capabilities.Values | Where-Object integrity_status -ne 'OBSERVED').Count

$ReportObject = [ordered]@{
    schema = 'JSONWISDOM_MACHINE_CAPABILITY_EVIDENCE_V0_1'
    control = [ordered]@{
        generated_utc        = [DateTime]::UtcNow.ToString('o')
        hostname             = $env:COMPUTERNAME
        scan_type            = 'READ_ONLY_OBSERVATION'
        script_version       = $ScriptVersion
        administrator_shell  = $isAdmin
        authority_created    = $false
        execution_authorized = $false
        automatic_promotion  = $false
        lane_state           = 'HOLD'
        charter_commit       = $CharterCommit
        project              = $Project
    }
    summary = [ordered]@{
        domains_total      = $capabilities.Count
        domains_observed   = $observedCount
        domains_incomplete = $incompleteCount
        capability_claim   = if ($incompleteCount -eq 0) { 'OBSERVATION_COMPLETE' } else { 'OBSERVATION_PARTIAL' }
        readiness_claim    = 'NOT_ESTABLISHED'
    }
    capabilities = $capabilities
    proof_boundary = [ordered]@{
        proves = @(
            'The listed commands were executed on the recorded host.',
            'The resulting observations were serialized into this report.',
            'The sealed hash identifies the exact report bytes.'
        )
        does_not_prove = @(
            'Ownership or hardware-backed identity.',
            'External correctness or independent reproduction.',
            'Production readiness, deployment approval, or operational authority.',
            'Absence of defects, compromise, or omitted machine state.'
        )
    }
}

$JsonPath = Join-Path $OutDir 'Jason-Deep-Proof.json'
$ReportObject | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $JsonPath -Encoding UTF8

$Hash = Get-FileHash -LiteralPath $JsonPath -Algorithm SHA256
$Hash.Hash | Set-Content -LiteralPath (Join-Path $OutDir 'SHA256.txt') -Encoding ASCII

$Receipt = [ordered]@{
    report_path         = $JsonPath
    report_size_bytes   = (Get-Item -LiteralPath $JsonPath).Length
    sha256              = $Hash.Hash
    generated_utc       = [DateTime]::UtcNow.ToString('o')
    project             = $Project
    charter_commit      = $CharterCommit
    lane_state          = 'HOLD'
    authority_created   = $false
    execution_authorized = $false
}
$ReceiptPath = Join-Path $OutDir 'Jason-Deep-Proof.receipt.json'
$Receipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ReceiptPath -Encoding UTF8

Write-Host "`nCAPABILITY-AWARE PROOF CREATED" -ForegroundColor Green
$Receipt | Format-List
Write-Host "observed_domains:   $observedCount"
Write-Host "incomplete_domains: $incompleteCount"
Write-Host 'AUTHORITY_CREATED = FALSE'
Write-Host 'LANE_STATE = HOLD'
