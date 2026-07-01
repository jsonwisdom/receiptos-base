# Manual Workflow Patch Required

The production code and prompt manifest are patched. The workflow still needs two manual additions before final production render.

## 1. Add DPI step

Place this after the render step and before checksum generation:

```yaml
      - name: Apply 300 DPI metadata
        run: |
          python scripts/apply_dpi.py \
            --dir output/W031 \
            --dpi 300
```

## 2. Add artifact upload step

Place this after Google Drive upload or after checksum generation:

```yaml
      - name: Upload render artifact
        uses: actions/upload-artifact@v4
        with:
          name: W031-renders
          path: |
            gpp-renderer/output/W031/
            gpp-renderer/sidecars/
```

## Required model setting

Set `REPLICATE_MODEL` to the production SDXL model in repository Actions secrets or variables.

## Current patched files

- `gpp-renderer/prompts/w031_reputation_rascals.json` requests 2048 x 2048 and dpi 300.
- `gpp-renderer/production_specs.yaml` records production render specs.
- `gpp-renderer/scripts/apply_dpi.py` applies PNG DPI metadata.
- `gpp-renderer/scripts/render.py` fails closed unless a production model is supplied.
