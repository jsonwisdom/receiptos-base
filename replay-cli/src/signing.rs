use ed25519_dalek::{Signature, Signer, SigningKey, Verifier, VerifyingKey};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::{fs, path::Path};

const ZERO_HASH: &str = "0000000000000000000000000000000000000000000000000000000000000000";
const ZERO_SIG: &str = "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000";

fn normalize_json_for_packet(path: &Path, bytes: &[u8]) -> Vec<u8> {
    let name = path.file_name().unwrap().to_string_lossy();
    if name != "signatures.json" && name != "shas.json" { return bytes.to_vec(); }
    let mut v: Value = serde_json::from_slice(bytes).unwrap();
    if let Some(o) = v.as_object_mut() {
        if o.contains_key("signature") { o.insert("signature".into(), json!(ZERO_SIG)); }
        if o.contains_key("packet_sha256") { o.insert("packet_sha256".into(), json!(ZERO_HASH)); }
    }
    serde_json::to_vec(&v).unwrap()
}

pub fn packet_sha256(dir: &Path) -> String {
    let mut files = fs::read_dir(dir).unwrap()
        .map(|e| e.unwrap().path())
        .filter(|p| p.is_file())
        .collect::<Vec<_>>();
    files.sort();
    let mut h = Sha256::new();
    for p in files {
        let name = p.file_name().unwrap().to_string_lossy();
        let b = fs::read(&p).unwrap();
        h.update(name.as_bytes());
        h.update([0u8]);
        h.update(normalize_json_for_packet(&p, &b));
        h.update([0u8]);
    }
    hex::encode(h.finalize())
}

pub fn sign_packet(dir: &Path, secret: [u8;32]) {
    let key = SigningKey::from_bytes(&secret);
    let public_key = hex::encode(key.verifying_key().to_bytes());
    fs::write(dir.join("signatures.json"), serde_json::to_vec(&json!({
        "signature_version":"GRP-004-SIG-v0.1","algorithm":"ed25519",
        "public_key_id":"grp004-runner-v0.1","public_key":public_key,
        "packet_sha256":ZERO_HASH,"signature":ZERO_SIG
    })).unwrap()).unwrap();
    fs::write(dir.join("shas.json"), serde_json::to_vec(&json!({"packet_sha256":ZERO_HASH})).unwrap()).unwrap();

    let root = packet_sha256(dir);
    let sig = key.sign(&hex::decode(&root).unwrap());
    fs::write(dir.join("signatures.json"), serde_json::to_vec(&json!({
        "signature_version":"GRP-004-SIG-v0.1","algorithm":"ed25519",
        "public_key_id":"grp004-runner-v0.1","public_key":hex::encode(key.verifying_key().to_bytes()),
        "packet_sha256":root,"signature":hex::encode(sig.to_bytes())
    })).unwrap()).unwrap();
    fs::write(dir.join("shas.json"), serde_json::to_vec(&json!({"packet_sha256":root})).unwrap()).unwrap();
}

pub fn verify_packet(dir: &Path) -> bool {
    let sigs: Value = serde_json::from_slice(&fs::read(dir.join("signatures.json")).unwrap()).unwrap();
    let root = packet_sha256(dir);
    if sigs["packet_sha256"] != root { return false; }
    let pk = hex::decode(sigs["public_key"].as_str().unwrap()).unwrap();
    let sig = hex::decode(sigs["signature"].as_str().unwrap()).unwrap();
    let vk = VerifyingKey::from_bytes(pk.as_slice().try_into().unwrap()).unwrap();
    let sig = Signature::from_slice(&sig).unwrap();
    vk.verify(&hex::decode(root).unwrap(), &sig).is_ok()
}
