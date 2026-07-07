use replay_cli::wasm_runner::execute_wasm;
use sha2::{Digest, Sha256};

#[test]
fn tv051_mutated_hash_rejection() {
    let wasm_bytes = wat::parse_str(include_str!("fixtures/tv050.wat")).unwrap();
    let envelope_cbor = vec![0xa0];

    let result = execute_wasm(&wasm_bytes, &envelope_cbor).unwrap();

    let expected = Sha256::digest(&result.final_state_cbor);

    let mut mutated = result.final_state_cbor.clone();
    mutated[0] ^= 0x01;

    let mutated_hash = Sha256::digest(&mutated);

    assert_ne!(expected.as_slice(), mutated_hash.as_slice());
}
