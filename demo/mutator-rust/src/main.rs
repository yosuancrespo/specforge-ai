use std::env;
use std::fs;

fn main() {
    let args: Vec<String> = env::args().collect();
    let schema = argument_value(&args, "--schema").unwrap_or_else(|| "demo/specs/openapi.yaml".to_string());
    let seed = argument_value(&args, "--seed").unwrap_or_else(|| "cases/basic-orders.json".to_string());
    let seed_exists = fs::metadata(&seed).is_ok();

    let payload = format!(
        r#"{{
  "schema": "{schema}",
  "seed": "{seed}",
  "seed_available": {seed_exists},
  "mutations": [
    {{
      "id": "mut-001",
      "label": "zero-amount",
      "payload": {{
        "customer_id": "mutator-user",
        "items": [{{"sku": "starter-plan", "quantity": 1}}],
        "amount": 0,
        "discount": 0,
        "currency": "USD"
      }}
    }},
    {{
      "id": "mut-002",
      "label": "empty-items",
      "payload": {{
        "customer_id": "mutator-user",
        "items": [],
        "amount": 20,
        "discount": 0,
        "currency": "USD"
      }}
    }},
    {{
      "id": "mut-003",
      "label": "discount-exceeds-amount",
      "payload": {{
        "customer_id": "mutator-user",
        "items": [{{"sku": "starter-plan", "quantity": 1}}],
        "amount": 30,
        "discount": 45,
        "currency": "USD"
      }}
    }}
  ]
}}"#
    );

    println!("{payload}");
}

fn argument_value(args: &[String], flag: &str) -> Option<String> {
    args.windows(2)
        .find(|pair| pair[0] == flag)
        .map(|pair| pair[1].clone())
}

