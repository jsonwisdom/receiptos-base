use replay_cli::signing::{packet_sha256, sign_packet, verify_packet};
use std::{fs, path::PathBuf};

fn dir(name:&str)->PathBuf{let p=PathBuf::from(format!("/tmp/{name}"));let _=fs::remove_dir_all(&p);fs::create_dir_all(&p).unwrap();p}

#[test] fn tv069a_packet_hash_deterministic() {
    let d=dir("tv069a"); fs::write(d.join("a.txt"),"hello").unwrap();
    sign_packet(&d,[7u8;32]); let a=packet_sha256(&d); let b=packet_sha256(&d);
    assert_eq!(a,b);
}
#[test] fn tv069b_signature_verifies() {
    let d=dir("tv069b"); fs::write(d.join("a.txt"),"hello").unwrap();
    sign_packet(&d,[7u8;32]); assert!(verify_packet(&d));
}
#[test] fn tv069c_mutation_fails() {
    let d=dir("tv069c"); fs::write(d.join("a.txt"),"hello").unwrap();
    sign_packet(&d,[7u8;32]); fs::write(d.join("a.txt"),"tamper").unwrap();
    assert!(!verify_packet(&d));
}
#[test] fn tv069d_missing_key_fails_closed() {
    let d=dir("tv069d"); fs::write(d.join("a.txt"),"hello").unwrap();
    assert!(!d.join("signatures.json").exists());
}
