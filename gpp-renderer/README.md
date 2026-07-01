# GPP Renderer

Automated renderer for **Garbage Pail Politics** production assets.

This package renders card prompts through Replicate, writes PNG outputs and JSON sidecars, computes SHA256 checksums, and uploads the organized bundle to Google Drive.

## Canon separation

- **Canon Layer:** immutable card IDs, wave numbers, roster, and release identity.
- **Editorial Layer:** prompt JSON and sidecar metadata; versioned through Git.
- **Production Layer:** renderer scripts, models, layout tuning, and output assets; evolvable.
- **Variant Layer:** alternate images remain non-canonical unless promoted by explicit errata.

This folder is isolated under `gpp-renderer/` and does not mutate existing receipt/protocol canon.

## Folder output

Local output:

```text
output/w031/
  GPP-W031-0001-Signal_Sally.png
  GPP-W031-0002-Credibility_Carl.png
  GPP-W031-0003-Status_Stanley.png
  GPP-W031-0004-Gossip_Greta.png
  GPP-W031-0005-Trust_Tessa.png
sidecars/w031_sidecar_manifest.json
sidecars/w031_checksums.json
```

Google Drive target:

```text
GPP_Cards/
  First_Printing/
    W031_Reputation_Rascals/
```

## Required secrets

GitHub Actions repository secrets:

```text
REPLICATE_API_TOKEN
GDRIVE_ROOT_FOLDER_ID
GDRIVE_SERVICE_ACCOUNT_JSON
```

Optional:

```text
REPLICATE_MODEL
```

Default model is configured by `scripts/render.py`.

## Manual run

```bash
cd gpp-renderer
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export REPLICATE_API_TOKEN="..."
python scripts/render.py --prompt prompts/w031_reputation_rascals.json --out output/w031
python scripts/checksum_manifest.py --wave W031 --output-dir output/w031 --manifest sidecars/w031_sidecar_manifest.json
python scripts/upload_gdrive.py --wave W031 --folder-name W031_Reputation_Rascals --local-dir output/w031 --sidecars sidecars
```

## GitFlow

```text
main                          frozen production/canon
render/w031-reputation-rascals active renderer branch
release/gpp-renderer-v0.1      review-ready renderer package
```

## Prompt style boundary

Prompts should describe original parody trading cards using generic descriptors such as:

```text
retro gross-out satirical trading card, sticker-card border, original goblin character, systems satire
```

Avoid asking a model to imitate any living artist or proprietary franchise style directly.
