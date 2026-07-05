use replay_cli::wasm_runner::execute_wasm;
use replay_cli::signing::sign_packet;
use sha2::{Digest, Sha256};
use std::{env, fs, path::PathBuf};

fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{:02x}", b)).collect()
}

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() != 5 || args[1] != "generate-fixture" || args[2] != "tv050" || args[3] != "--output" {
        eprintln!("usage: replay-cli generate-fixture tv050 --output <dir>");
        std::process::exit(41);
    }

    let out = PathBuf::from(&args[4]);
    fs::create_dir_all(&out).unwrap();

    let wat = fs::read_to_string("replay-cli/tests/fixtures/tv050.wat").unwrap();
    let wasm = wat::parse_str(&wat).unwrap();
    let envelope = vec![0xa0];

    let result = execute_wasm(&wasm, &envelope).unwrap();

    fs::write(out.join("step_runner.wat"), wat).unwrap();
    fs::write(out.join("envelope.cbor"), &envelope).unwrap();
    fs::write(out.join("final_state.cbor"), &result.final_state_cbor).unwrap();

    fs::write(out.join("step_runner.wasm.sha256"), hex(&Sha256::digest(&wasm))).unwrap();
    fs::write(out.join("final_state.sha256"), hex(&Sha256::digest(&result.final_state_cbor))).unwrap();

    sign_packet(&out, [7u8; 32]);

    println!("TV-061 fixture generated: {}", out.display());
}
