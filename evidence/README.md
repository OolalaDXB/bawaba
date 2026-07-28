# BAWABA — sample evidence bundle

This is a **demonstration** evidence pack produced by BAWABA. It shows the shape
of the artifacts BAWABA emits and lets you verify them yourself, independently,
with tools you already have (OpenSSL and Python). Everything here is simulated:
**no customer data, no production keys.**

## What's inside

| File | What it is |
|------|------------|
| `decision.json` | A sample jurisdiction-routing decision (which agent, which policy, where the data may be processed). |
| `decision.sig` | Ed25519 signature over the exact bytes of `decision.json`. |
| `signing-public-key.pem` | The public key that verifies the signature. |
| `audit-chain.jsonl` | A tamper-evident audit log: each event carries the SHA-256 of the previous event, so any edit breaks the chain. |
| `verify.py` | Verifies the audit chain (Python standard library) and the signature (via OpenSSL). |
| `verify.sh` | Same, driven from OpenSSL first. |

## Verify it yourself

One command:

```sh
python3 verify.py
```

Expected output:

```
[OK] audit chain   - 5 events, head 4fe4a8506eb68135...
[OK] decision sig  - Signature Verified Successfully

Evidence verified.
```

### Verify the signature by hand (OpenSSL)

```sh
openssl pkeyutl -verify -pubin -inkey signing-public-key.pem \
  -rawin -in decision.json -sigfile decision.sig
```

### See tamper-evidence in action

Change a single character in `decision.json` or any line of `audit-chain.jsonl`,
then re-run `python3 verify.py`: the corresponding check fails. That is the whole
point — the evidence does not rely on trusting the store, only the maths.

## Notes

- The audit-chain hash for each event is `SHA-256( prev_hash_bytes || canonical_event )`,
  where `canonical_event` is the compact, key-sorted JSON of `{seq, ts, agent, tool, effect}`.
- The genesis `prev` is 64 zeros.
- In production, decisions are signed inside the client perimeter and the chain is
  verified server-side; the console shows what is happening but does not sit inside
  the cryptographic trust boundary.

Questions: contact@bawaba.systems
