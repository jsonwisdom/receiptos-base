use replay_cli::wasm_runner::execute_wasm;

#[test]
fn tv063_fuel_used_is_recorded() {
    let wasm = wat::parse_str(include_str!("fixtures/tv050.wat")).unwrap();
    let result = execute_wasm(&wasm, &[0xa0]).unwrap();
    assert!(result.fuel_used > 0, "fuel_used must be > 0");
}
