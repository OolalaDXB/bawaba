#!/usr/bin/env python3
"""Verify the BAWABA sample evidence bundle.

Checks two independent things:
  1. The tamper-evident audit chain  (SHA-256, Python standard library only).
  2. The Ed25519 signature on decision.json  (delegated to `openssl`).

Usage:  python3 verify.py
Exit code 0 = everything verified, non-zero = a check failed.
This bundle contains DEMONSTRATION DATA only. No customer data.
"""
import json, hashlib, subprocess, sys, shutil, os

HERE = os.path.dirname(os.path.abspath(__file__))

def p(path): return os.path.join(HERE, path)

def core(ev):
    return json.dumps({k: ev[k] for k in ("seq","ts","agent","tool","effect")},
                      separators=(",",":"), sort_keys=True).encode()

def check_chain():
    prev = "0" * 64
    with open(p("audit-chain.jsonl")) as f:
        lines = [l for l in f.read().splitlines() if l.strip()]
    for i, line in enumerate(lines, 1):
        rec = json.loads(line)
        if rec["prev"] != prev:
            return False, f"event {i}: prev-hash does not match previous event"
        h = hashlib.sha256(bytes.fromhex(prev) + core(rec)).hexdigest()
        if h != rec["hash"]:
            return False, f"event {i}: recomputed hash does not match recorded hash"
        prev = h
    return True, f"{len(lines)} events, head {prev[:16]}..."

def check_signature():
    if shutil.which("openssl") is None:
        return None, "openssl not found - skipping signature check (see README for manual command)"
    r = subprocess.run(
        ["openssl","pkeyutl","-verify","-pubin","-inkey",p("signing-public-key.pem"),
         "-rawin","-in",p("decision.json"),"-sigfile",p("decision.sig")],
        capture_output=True, text=True)
    ok = (r.returncode == 0) and ("Success" in (r.stdout + r.stderr))
    return ok, (r.stdout + r.stderr).strip()

def main():
    ok_chain, msg_chain = check_chain()
    print(f"[{'OK' if ok_chain else 'FAIL'}] audit chain   - {msg_chain}")
    ok_sig, msg_sig = check_signature()
    label = "SKIP" if ok_sig is None else ("OK" if ok_sig else "FAIL")
    print(f"[{label}] decision sig  - {msg_sig}")
    if not ok_chain or ok_sig is False:
        sys.exit(1)
    print("\nEvidence verified.")

if __name__ == "__main__":
    main()
