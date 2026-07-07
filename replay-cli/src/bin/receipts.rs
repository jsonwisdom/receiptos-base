use replay_cli::signing::verify_packet;
use std::{env, path::Path};

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() != 3 || args[1] != "verify" {
        eprintln!("usage: receipts verify <packet-or-corpus-dir>");
        std::process::exit(2);
    }

    let root = Path::new(&args[2]);

    if !root.exists() {
        eprintln!("verify failed: path does not exist: {}", root.display());
        std::process::exit(3);
    }

    let sig = root.join("signatures.json");
    let shas = root.join("shas.json");

    if sig.exists() && shas.exists() {
        if verify_packet(root) {
            println!(r#"{{"status":"valid","path":"{}"}}"#, root.display());
            std::process::exit(0);
        } else {
            eprintln!(r#"{{"status":"invalid","path":"{}","reason":"SIGNATURE_OR_HASH_INVALID"}}"#, root.display());
            std::process::exit(3);
        }
    }

    // v0.1 corpus may not yet have signed packet at root.
    // Fail closed until signed packet layout exists.
    eprintln!(r#"{{"status":"invalid","path":"{}","reason":"NO_SIGNED_PACKET_FOUND"}}"#, root.display());
    std::process::exit(3);
}
