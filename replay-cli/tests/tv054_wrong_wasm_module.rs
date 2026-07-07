use replay_cli::wasm_runner::verify_step_code_hash;
use replay_cli::errors::ReplayExit;
use sha2::{Digest, Sha256};

#[test]
fn tv054_wrong_wasm_module_rejection() {
    let correct_wasm = wat::parse_str(include_str!("fixtures/tv050.wat")).unwrap();
    let wrong_wasm = wat::parse_str(include_str!("fixtures/tv054_wrong.wat")).unwrap();

    let expected = Sha256::digest(&correct_wasm);
    let result = verify_step_code_hash(&wrong_wasm, expected.as_slice());

    assert_eq!(result, Err(ReplayExit::HashMismatch));
}
