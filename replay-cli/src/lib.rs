pub mod errors;
pub mod wasm_runner;

#[cfg(test)]
mod tests {
    #[test]
    fn replay_cli_crate_boots() {
        assert_eq!(2 + 2, 4);
    }
}

pub mod signing;
