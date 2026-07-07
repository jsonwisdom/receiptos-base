use replay_cli::wasm_runner::execute_wasm;
use sha2::{Digest, Sha256};

#[test]
fn tv050_success_path() {
    let wasm_bytes = wat::parse_str(include_str!("fixtures/tv050.wat")).unwrap();
    let envelope_cbor = vec![0xa0];

    let result = execute_wasm(&wasm_bytes, &envelope_cbor).unwrap();

    let expected_final_state_cbor = vec![0xa0];
    assert_eq!(result.final_state_cbor, expected_final_state_cbor);

    let computed = Sha256::digest(&result.final_state_cbor);
    let expected = Sha256::digest(&expected_final_state_cbor);

    assert_eq!(computed.as_slice(), expected.as_slice());
}
