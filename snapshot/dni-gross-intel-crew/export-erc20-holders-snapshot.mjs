#!/usr/bin/env node

/**
 * DNI Gross-Intel Crew holder snapshot exporter
 *
 * Purpose:
 *   Reconstruct ERC-20 holder balances for the Zora/Base coin at a fixed Base block,
 *   then output the deterministic eligible holder list and Merkle root.
 *
 * Usage:
 *   npm install ethers
 *   BASE_RPC_URL="https://mainnet.base.org" node snapshot/dni-gross-intel-crew/export-erc20-holders-snapshot.mjs
 *
 * Outputs:
 *   snapshot/dni-gross-intel-crew/snapshot.json
 *   snapshot/dni-gross-intel-crew/eligible-holders.json
 *   snapshot/dni-gross-intel-crew/merkle-root.txt
 *   snapshot/dni-gross-intel-crew/snapshot-spec-v1.1.md
 */

import fs from "fs";
import path from "path";
import { ethers } from "ethers";

const RPC_URL = process.env.BASE_RPC_URL || "https://mainnet.base.org";
const COLLECTION = "0xe423ae19FfFcEe95919DDE96a31e828bC060E36F";
const SNAPSHOT_BLOCK = 48046843;
const SNAPSHOT_BLOCK_HASH = "0x8f3c626fc7cd9b805b8e2ac82643aae3652a99f28ac5aec2f5bbccac0cc73282";
const GENESIS_UID = "0xe4735bff8c92672ce266364e67966cf35b29b7daeb2a693b7b14d24e338686f0";
const OUT_DIR = path.join("snapshot", "dni-gross-intel-crew");
const ZERO = "0x0000000000000000000000000000000000000000";
const TRANSFER_TOPIC = ethers.id("Transfer(address,address,uint256)");

function normalizeAddress(addr) {
  return ethers.getAddress(addr).toLowerCase();
}

function topicToAddress(topic) {
  return normalizeAddress("0x" + topic.slice(26));
}

function leafHash(address) {
  return ethers.solidityPackedKeccak256(["address"], [address]);
}

function hashPair(a, b) {
  const [x, y] = a.toLowerCase() <= b.toLowerCase() ? [a, b] : [b, a];
  return ethers.keccak256(ethers.concat([x, y]));
}

function merkleRoot(addresses) {
  if (addresses.length === 0) return ethers.ZeroHash;
  let layer = addresses.map(leafHash).sort((a, b) => a.localeCompare(b));
  while (layer.length > 1) {
    const next = [];
    for (let i = 0; i < layer.length; i += 2) {
      if (i + 1 === layer.length) next.push(layer[i]);
      else next.push(hashPair(layer[i], layer[i + 1]));
    }
    layer = next.sort((a, b) => a.localeCompare(b));
  }
  return layer[0];
}

async function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const provider = new ethers.JsonRpcProvider(RPC_URL, { name: "base", chainId: 8453 });

  const block = await provider.getBlock(SNAPSHOT_BLOCK);
  if (!block) throw new Error(`Snapshot block not found: ${SNAPSHOT_BLOCK}`);
  if (block.hash.toLowerCase() !== SNAPSHOT_BLOCK_HASH.toLowerCase()) {
    throw new Error(`Block hash mismatch. Expected ${SNAPSHOT_BLOCK_HASH}, got ${block.hash}`);
  }

  const latest = await provider.getBlockNumber();
  if (latest < SNAPSHOT_BLOCK) throw new Error(`RPC latest block ${latest} is behind snapshot block ${SNAPSHOT_BLOCK}`);

  const balances = new Map();
  const chunk = Number(process.env.LOG_CHUNK || 50000);

  const START_BLOCK = Number(process.env.START_BLOCK || 47990000);
  const DELAY_MS = Number(process.env.LOG_DELAY_MS || 750);

  for (let fromBlock = START_BLOCK; fromBlock <= SNAPSHOT_BLOCK; fromBlock += chunk) {
    const toBlock = Math.min(fromBlock + chunk - 1, SNAPSHOT_BLOCK);
    console.error(`Fetching Transfer logs ${fromBlock}-${toBlock}`);
    const logs = await provider.getLogs({
      address: COLLECTION,
      topics: [TRANSFER_TOPIC],
      fromBlock,
      toBlock
    });

    await new Promise(r => setTimeout(r, DELAY_MS));

    for (const log of logs) {
      const from = topicToAddress(log.topics[1]);
      const to = topicToAddress(log.topics[2]);
      const value = BigInt(log.data);
      if (from !== ZERO) balances.set(from, (balances.get(from) || 0n) - value);
      if (to !== ZERO) balances.set(to, (balances.get(to) || 0n) + value);
    }
  }

  const eligibleHolders = [...balances.entries()]
    .filter(([addr, bal]) => addr !== ZERO && bal > 0n)
    .map(([addr]) => addr)
    .sort((a, b) => a.localeCompare(b));

  const root = merkleRoot(eligibleHolders);

  const snapshot = {
    artifactId: "DNI-GROSS-INTEL-CREW-SNAPSHOT-48037949",
    network: "Base Mainnet",
    chainId: 8453,
    rpcEndpoint: RPC_URL,
    collectionAddress: COLLECTION,
    snapshotBlock: SNAPSHOT_BLOCK,
    snapshotBlockHash: SNAPSHOT_BLOCK_HASH,
    genesisUid: GENESIS_UID,
    eligibilityRule: "ERC-20 balance greater than zero at snapshot block, reconstructed from Transfer events up to and including snapshotBlock.",
    holderCount: eligibleHolders.length,
    merkleRoot: root,
    generatedAt: new Date().toISOString(),
    note: "This snapshot is independent from the EAS genesis provenance attestation."
  };

  fs.writeFileSync(path.join(OUT_DIR, "snapshot.json"), JSON.stringify(snapshot, null, 2) + "\n");
  fs.writeFileSync(path.join(OUT_DIR, "eligible-holders.json"), JSON.stringify(eligibleHolders, null, 2) + "\n");
  fs.writeFileSync(path.join(OUT_DIR, "merkle-root.txt"), root + "\n");
  fs.writeFileSync(path.join(OUT_DIR, "snapshot-spec-v1.1.md"), `# Merkle Snapshot Specification v1.1\n\nNetwork: Base Mainnet\n\nCollection: \`${COLLECTION}\`\n\nSnapshot block: \`${SNAPSHOT_BLOCK}\`\n\nSnapshot block hash: \`${SNAPSHOT_BLOCK_HASH}\`\n\nEligibility rule: ERC-20 balance greater than zero at snapshot block, reconstructed from Transfer events up to and including the snapshot block.\n\nAddress normalization: lowercase hex.\n\nAddress sorting: lexicographical ascending.\n\nLeaf hash: \`keccak256(abi.encodePacked(address))\`.\n\nPair hashing: sort each pair lexicographically, concatenate 32-byte hashes, then \`keccak256\`.\n\nGenesis UID: \`${GENESIS_UID}\`\n\nBoundary: EAS provenance and Merkle eligibility are separate records. This root only records claim eligibility for Foil Chase #4.\n`);

  console.log(JSON.stringify({ eligibleHolders, merkleRoot: root }, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
