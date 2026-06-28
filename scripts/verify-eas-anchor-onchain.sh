chmod +x scripts/verify-eas-anchor-onchain.sh
git add scripts/verify-eas-anchor-onchain.sh .github/workflows/verify-anchor.yml
git commit -m "Add RPC-backed EAS anchor replay gate"

git tag -a global-forest-eas-rpc-gate-v1 \
  -m "RPC-backed verification for global forest EAS anchor"

git push origin main
git push origin global-forest-eas-rpc-gate-v1
