use replay_cli::wasm_runner::execute_wasm;
use replay_cli::errors::ReplayExit;

#[test]
fn tv064_infinite_loop_fails_closed() {
    let wasm = wat::parse_str(include_str!("fixtures/tv064_infinite_loop.wat")).unwrap();
    let result = execute_wasm(&wasm, &[0xa0]);
    assert_eq!(result, Err(ReplayExit::WasmExecutionFailed));
}
