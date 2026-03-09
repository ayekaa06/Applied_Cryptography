# SIS2 — SHA-256, HMAC, PBKDF2, HKDF Implementation

## Overview
This project is a console-based cryptographic toolkit that implements core primitives **from scratch** in Python for educational purposes. The implementation does **not** use `hashlib`, `hmac`, `pbkdf2_hmac`, or external cryptographic libraries for the core algorithms.

Implemented components:
- SHA-256
- HMAC-SHA256
- PBKDF2-HMAC-SHA256
- HKDF-SHA256
- Password manager
- File integrity checker

> **Educational use only.** This project was built to demonstrate understanding of cryptographic algorithms and should not be used as a production security library.

---

## Project Structure

```text
SIS2/
├── app/
│   ├── main.py                # console interface
│   ├── password_manager.py    # password storage and verification
│   └── file_integrity.py      # manifest creation and integrity checking
├── crypto_core/
│   ├── sha256.py              # SHA-256 implementation
│   ├── hmac.py                # HMAC-SHA256 implementation
│   ├── pbkdf2.py              # PBKDF2-HMAC-SHA256 implementation
│   └── hkdf.py                # HKDF-SHA256 implementation
├── utils/
│   ├── bit_ops.py             # bitwise helper functions
│   ├── hex.py                 # hex conversion helpers
│   └── random.py              # random byte generation helpers
├── tests/
│   └── test_vectors.py        # algorithm test vectors
├── data/
│   └── passwords.json         # stored password entries
├── demo_files/
│   ├── file1.txt
│   └── manifest.sha256manifest.json
├── stdlib_replacements.py
└── README.md
```

---

## Implemented Features

### 1. Hash Tool
Computes the SHA-256 hash of a text message.

Features:
- text hashing
- SHA-256 output in hexadecimal
- optional educational mode showing internal round states

### 2. HMAC Tool
Generates and verifies HMAC tags using **HMAC-SHA256**.

Features:
- accepts key as text or hex
- computes authentication tag for a message
- verifies a user-provided tag against the computed value

### 3. Password Manager
Stores user passwords securely using **PBKDF2-HMAC-SHA256**.

Features:
- generates a random 16-byte salt for each password
- uses **120000 iterations** by default
- stores records in JSON format
- verifies passwords by recomputing the derived key

Each stored entry contains:
- username
- salt
- derived password hash
- iteration count

### 4. Key Derivation Tool
Supports two key derivation modes:

#### PBKDF2 Mode
Input:
- password
- salt
- iteration count
- desired key length

Output:
- derived key in hex

#### HKDF Mode
Input:
- input key material (IKM)
- salt
- info/context
- desired output length

Output:
- PRK and OKM in hex

### 5. File Integrity Tool
Checks whether files were modified after manifest creation.

Features:
- computes SHA-256 for files
- creates a manifest file with `file → hash` pairs
- verifies files against a saved manifest
- detects:
  - `OK`
  - `TAMPERED`
  - `MISSING`


## How to Run

Open a terminal in the project root folder (`SIS2`) and run:

```bash
python app/main.py
```

If imports fail, run from the root folder with:

```bash
PYTHONPATH=. python app/main.py
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH='.'
python app/main.py
```

---

## How to Run Tests

### Test vectors
Run the main validation tests:

```bash
PYTHONPATH=. python tests/test_vectors.py
```

### Comprehensive testing
If you add a separate comprehensive test file, run:

```bash
PYTHONPATH=. python tests/comprehensive_tests.py
```

---

## Test Coverage
The project is intended to be validated with the following categories of tests:

### Algorithm test vectors
- SHA-256 known vectors
- HMAC-SHA256 RFC-style vectors
- PBKDF2 output validation
- HKDF output validation

### Functional tests
- different inputs produce different hashes
- avalanche effect demonstration
- HMAC valid/invalid tag verification
- password storage and verification
- same password with different salts produces different hashes
- file integrity verification for clean and modified files

### Performance checks
- SHA-256 hashing speed
- HMAC computation time
- PBKDF2 runtime for high iteration counts
- file hashing speed for different file sizes

---

## Example Usage

### SHA-256
Input:
```text
abc
```
Output:
```text
ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
```

### HMAC-SHA256
Example message:
```text
Hi There
```

### PBKDF2
Example parameters:
- password: `password`
- salt: `salt`
- iterations: `1`
- length: `20`

### HKDF
Example parameters:
- ikm: `hello`
- salt: custom hex value
- info: optional context string
- length: `16`

---

## Security Notes
- This implementation is for **learning and demonstration**.
- Real systems should use well-tested and audited cryptographic libraries.
- Password storage should normally use dedicated password hashing functions such as Argon2, scrypt, or bcrypt in production.
- Custom cryptographic implementations are risky outside an educational environment.

---

## Known Limitations
- Console-based interface only
- Hash Tool currently focuses on text input
- HMAC Tool currently focuses on text input
- No GUI/web frontend
- Not hardened for production use

---

## Author
Prepared as part of the SIS2 assignment on manual implementation of SHA-256, HMAC, PBKDF2, and HKDF.
    