use std::collections::BTreeMap;
use crate::errors::ReplayExit;
use sha2::{Digest, Sha256};

#[derive(Debug, Clone)]
pub struct WasmHostState {
    pub evidence: BTreeMap<[u8; 32], Vec<u8>>,
}

pub const INPUT_OFFSET: u32 = 0x0400;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ExecutionResult {
    pub final_state_cbor: Vec<u8>,
    pub guest_exit_code: i32,
    pub fuel_used: u64,
}


pub fn verify_step_code_hash(
    wasm_bytes: &[u8],
    expected_hash: &[u8],
) -> Result<(), ReplayExit> {
    let computed = Sha256::digest(wasm_bytes);
    if computed.as_slice() == expected_hash {
        Ok(())
    } else {
        Err(ReplayExit::HashMismatch)
    }
}

pub fn execute_wasm(
    wasm_bytes: &[u8],
    envelope_cbor: &[u8],
) -> Result<ExecutionResult, ReplayExit> {
    use wasmtime::{Config, Engine, Instance, Module, Store};

    if envelope_cbor.is_empty() {
        return Err(ReplayExit::InvalidEnvelope);
    }

    let mut config = Config::new();
        config.consume_fuel(true);
        let engine = Engine::new(&config)
        .map_err(|_| ReplayExit::WasmExecutionFailed)?;
    let module = Module::new(&engine, wasm_bytes)
        .map_err(|_| ReplayExit::WasmExecutionFailed)?;

    let mut store = Store::new(&engine, ());
    store.set_fuel(1_000_000)
        .map_err(|_| ReplayExit::WasmExecutionFailed)?;
    let instance = Instance::new(&mut store, &module, &[])
        .map_err(|_| ReplayExit::WasmExecutionFailed)?;

    let memory = instance
        .get_memory(&mut store, "memory")
        .ok_or(ReplayExit::WasmExecutionFailed)?;

    let start = INPUT_OFFSET as usize;
    let end = start.checked_add(envelope_cbor.len())
        .ok_or(ReplayExit::WasmExecutionFailed)?;

    if end > memory.data_size(&store) {
        return Err(ReplayExit::WasmExecutionFailed);
    }

    memory.write(&mut store, start, envelope_cbor)
        .map_err(|_| ReplayExit::WasmExecutionFailed)?;

    let execute = instance
        .get_typed_func::<(u32, u32), i32>(&mut store, "execute")
        .map_err(|_| ReplayExit::WasmExecutionFailed)?;

    let code = execute.call(&mut store, (INPUT_OFFSET, envelope_cbor.len() as u32))
        .map_err(|_| ReplayExit::WasmExecutionFailed)?;

    if code != 0 {
        return Err(ReplayExit::WasmExecutionFailed);
    }

    let get_output_ptr = instance
        .get_typed_func::<(), u32>(&mut store, "get_output_ptr")
        .map_err(|_| ReplayExit::WasmExecutionFailed)?;

    let get_output_len = instance
        .get_typed_func::<(), u32>(&mut store, "get_output_len")
        .map_err(|_| ReplayExit::WasmExecutionFailed)?;

    let out_ptr = get_output_ptr.call(&mut store, ())
        .map_err(|_| ReplayExit::WasmExecutionFailed)? as usize;

    let out_len = get_output_len.call(&mut store, ())
        .map_err(|_| ReplayExit::WasmExecutionFailed)? as usize;

    let out_end = out_ptr.checked_add(out_len)
        .ok_or(ReplayExit::WasmExecutionFailed)?;

    if out_len == 0 || out_end > memory.data_size(&store) {
        return Err(ReplayExit::WasmExecutionFailed);
    }

    let mut final_state_cbor = vec![0u8; out_len];
    memory.read(&store, out_ptr, &mut final_state_cbor)
        .map_err(|_| ReplayExit::WasmExecutionFailed)?;

    Ok(ExecutionResult {
        final_state_cbor,
        guest_exit_code: code,
        fuel_used: 1_000_000u64
            .saturating_sub(store.get_fuel().unwrap_or(1_000_000)),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn wasm_runner_rejects_empty_envelope() {
        let result = execute_wasm(&[], &[]);
        assert_eq!(result, Err(ReplayExit::InvalidEnvelope));
    }

    #[test]
    fn wasm_runner_rejects_invalid_wasm_bytes() {
        let result = execute_wasm(&[], &[0xa0]);
        assert_eq!(result, Err(ReplayExit::WasmExecutionFailed));
    }
}

#[cfg(test)]
mod get_required_tests {
    use super::*;
    use wasmtime::{Caller, Config, Engine, Linker, Module, Store};

    const HASH_PTR: u32 = 0x0100;
    const OUT_PTR: u32 = 0x0200;
    const VALID_HASH: [u8; 32] = [0xAA; 32];
    const MISSING_HASH: [u8; 32] = [0xBB; 32];

    #[test]
    fn test_get_required_abi() -> Result<(), Box<dyn std::error::Error>> {
        let mut config = Config::new();
    config.consume_fuel(true);
    let engine = Engine::new(&config)?;
        let mut linker = Linker::<WasmHostState>::new(&engine);

        linker.func_wrap("env", "get_required", |mut caller: Caller<'_, WasmHostState>, hp: u32, hl: u32, op: u32, oc: u32| -> i32 {
            if hl != 32 { return 3; }
            let mem = caller.get_export("memory").and_then(|e| e.into_memory()).unwrap();
            let mut hash = [0u8; 32];
            mem.read(&caller, hp as usize, &mut hash).unwrap();
            let data = match caller.data().evidence.get(&hash) {
                Some(d) => d.clone(),
                None => return 1,
            };
            if data.len() > oc as usize { return 2; }
            mem.write(&mut caller, op as usize, &data).unwrap();
            0
        })?;

        let wat_source = r#"
        (module
          (import "env" "get_required" (func $get_required (param i32 i32 i32 i32) (result i32)))
          (memory (export "memory") 1)
          (func (export "test_get_required") (param i32 i32 i32 i32) (result i32)
            (call $get_required (local.get 0) (local.get 1) (local.get 2) (local.get 3)))
        )
        "#;

        let module = Module::new(&engine, wat::parse_str(wat_source)?)?;

        let mut evidence = BTreeMap::new();
        evidence.insert(VALID_HASH, vec![0xDE, 0xAD, 0xBE, 0xEF]);

        let mut store = Store::new(&engine, WasmHostState { evidence });
        store.set_fuel(1_000_000)?;
        let instance = linker.instantiate(&mut store, &module)?;
        let mem = instance.get_memory(&mut store, "memory").unwrap();
        let test_fn = instance.get_typed_func::<(u32, u32, u32, u32), i32>(&mut store, "test_get_required")?;

        mem.write(&mut store, HASH_PTR as usize, &VALID_HASH)?;
        assert_eq!(test_fn.call(&mut store, (HASH_PTR, 32, OUT_PTR, 64))?, 0);
        let mut out = [0u8; 4];
        mem.read(&store, OUT_PTR as usize, &mut out)?;
        assert_eq!(out, [0xDE, 0xAD, 0xBE, 0xEF]);

        mem.write(&mut store, HASH_PTR as usize, &MISSING_HASH)?;
        assert_eq!(test_fn.call(&mut store, (HASH_PTR, 32, OUT_PTR, 64))?, 1);

        assert_eq!(test_fn.call(&mut store, (HASH_PTR, 16, OUT_PTR, 64))?, 3);

        mem.write(&mut store, HASH_PTR as usize, &VALID_HASH)?;
        assert_eq!(test_fn.call(&mut store, (HASH_PTR, 32, OUT_PTR, 2))?, 2);

        Ok(())
    }
}
