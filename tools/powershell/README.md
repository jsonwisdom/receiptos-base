# Constitutional Inventory of Jason’s Laptop

**Subtitle:** A sovereignty-preserving, capability-aware, read-only machine evidence engine

## Status

```text
PROJECT                 = jsonwisdom/receiptos-base
ENGINE                  = Invoke-JasonDeepProof.ps1
CLASSIFICATION          = LOCAL MACHINE EVIDENCE TOOL
SCAN_TYPE               = READ_ONLY_OBSERVATION
AUTHORITY_CREATED       = FALSE
EXECUTION_AUTHORIZED    = FALSE
AUTOMATIC_PROMOTION     = FALSE
LANE_STATE              = HOLD
```

This tool inventories a Windows machine from platform identity outward, classifies observed capabilities, serializes the observations into JSON, and seals the report with SHA-256.

It is designed around one controlling rule:

> A machine may produce evidence about what happened. Only an authorized human or governance process decides what that evidence permits next.

## Constitutional lineage

The engine records the repository and the Physical Sovereignty Charter commit:

```text
repository      = jsonwisdom/receiptos-base
charter_commit  = 88145a21d298cc17607ed44be5459db6be329fd2
```

The charter separates computation from physical authority. This inventory therefore reports observations and evidence quality without claiming ownership, truth, readiness, permission, or command authority.

## Core-outward model

The engine observes the machine through capability domains:

| Domain | Capability tier | Purpose |
|---|---|---|
| System | `PLATFORM_IDENTITY` | Windows, manufacturer, model, architecture, and firmware type |
| CPU | `COMPUTE_BASE` | Processor identity, cores, threads, and virtualization support |
| Firmware | `TRUST_ROOT` | BIOS, Secure Boot, and TPM observations |
| Device Guard | `HARDENING` | Virtualization-based security and configured security services |
| Memory | `WORKING_CAPACITY` | Installed memory modules, capacities, and configured speeds |
| Disks | `PERSISTENCE` | Physical storage media, size, bus, and reported health |
| Graphics | `ACCELERATION` | Display adapters, processors, memory, and drivers |
| Security | `DEFENSE` | BitLocker, Microsoft Defender, and firewall observations |
| Virtualization | `ISOLATION` | Hypervisor presence and enabled virtualization features |
| Power and recovery | `RESILIENCE` | Battery, sleep states, and Windows recovery environment |
| Updates | `MAINTENANCE_STATE` | Recently installed Windows hotfixes |

Each domain receives an observation envelope containing:

```text
probe_name
status
observed_utc
duration_ms
data
error
capability_tier
integrity_status
risk_hints
```

A missing or unavailable observation is reported as incomplete. It is not silently promoted into a capability claim.

## Run

Open **Administrator PowerShell**, switch to the repository branch containing the tool, and run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\powershell\Invoke-JasonDeepProof.ps1
```

An alternate output root may be supplied:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\powershell\Invoke-JasonDeepProof.ps1 `
  -OutputRoot "C:\Evidence"
```

## Outputs

The script creates a timestamped folder:

```text
Jason-Deep-Proof-YYYYMMDD-HHMMSS\
├── Jason-Deep-Proof.json
├── Jason-Deep-Proof.receipt.json
└── SHA256.txt
```

### `Jason-Deep-Proof.json`

Contains the control block, summary, classified capability observations, and proof boundary.

### `Jason-Deep-Proof.receipt.json`

Records the report path, byte size, SHA-256 digest, project, charter commit, and final control state.

### `SHA256.txt`

Contains the SHA-256 digest of the exact JSON report bytes.

## Proof boundary

### What a completed run supports

- The listed commands were executed on the recorded hostname.
- The script captured the observations it received.
- The observations were serialized into the report.
- The SHA-256 digest identifies the exact report bytes.

### What a completed run does not establish

- Ownership of the computer.
- Hardware-backed personal identity.
- Independent correctness of the operating system or probe results.
- Absence of compromise, defects, omissions, or misleading firmware responses.
- Production readiness or deployment approval.
- Legal, military, institutional, or operational authority.
- Truth merely because data was hashed or published.

## Evidence doctrine

```text
HASH        = BYTE IDENTITY
REPLAY      = REPRODUCIBILITY EVIDENCE
RECEIPT     = BOUNDED EVENT RECORD
TRUTH CLAIM = REQUIRES EVIDENTIARY SUPPORT
AUTHORITY   = REQUIRES VALID GOVERNANCE
MODEL       = NOT THE COMMANDER
```

The report may change what is known. It may not independently change what is authorized.

## Privacy and publication

The current probes avoid passwords, authentication tokens, product keys, external IP addresses, and disk serial numbers. Machine inventory may still reveal sensitive details such as hostnames, hardware models, security configuration, recovery state, and installed updates.

Review every report before publishing it.

```text
LOCAL_REPORT_CREATED   ≠ PUBLICATION_APPROVED
PUBLICATION            ≠ CANON
CANON                   ≠ AUTHORITY
```

## Replay procedure

A reviewer should:

1. Freeze the repository commit and script blob.
2. Record the execution environment.
3. Run the approved command.
4. preserve standard output, standard error, and exit status when available.
5. Verify the generated report against `SHA256.txt`.
6. Inspect incomplete domains and risk hints.
7. State exactly what the run proves and does not prove.
8. End in human or governance review.

## Licensing and governance

The repository is licensed under the Apache License 2.0. The license grants legal permissions concerning use, modification, and distribution; it does not create truth, sovereignty, operational permission, or execution authority.

Constitutional restrictions and evidence boundaries are implemented through documentation, receipt fields, review rules, and runtime behavior. They are governance declarations, not additions to or modifications of the Apache License.

## Final state

```text
EVIDENCE_CREATED       = POSSIBLE
AUTHORITY_CREATED      = FALSE
EXECUTION_AUTHORIZED   = FALSE
AUTOMATIC_PROMOTION    = FALSE
HUMAN_REVIEW_REQUIRED  = TRUE
LANE_STATE             = HOLD
```

> Private observation enters. Public evidence may exit. Sovereignty stays with the authorized human and governance boundary.
