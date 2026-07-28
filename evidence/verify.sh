#!/usr/bin/env sh
# Verify the Ed25519 signature on decision.json using OpenSSL, then the audit chain.
set -e
cd "$(dirname "$0")"
echo "== Ed25519 signature =="
openssl pkeyutl -verify -pubin -inkey signing-public-key.pem \
  -rawin -in decision.json -sigfile decision.sig
echo "== Audit chain (SHA-256) =="
python3 verify.py
