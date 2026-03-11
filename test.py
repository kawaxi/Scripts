import argparse
import getpass
import os
import subprocess
import sys
from pathlib import Path


SKIP_NAMES = {
    "encrypt.py",
    "decrypt.py",
   
}

SKIP_SUFFIXES = {
    ".enc",
    ".py",
    ".pyc",
    
}


def should_skip(path: Path) -> bool:
    if not path.is_file():
        return True
    if path.name in SKIP_NAMES:
        return True
    return path.suffix in SKIP_SUFFIXES


def run_openssl(args: list[str], password: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["OPENSSL_PASS"] = password
    return subprocess.run(
        ["openssl", *args, "-pass", "env:OPENSSL_PASS"],
        capture_output=True,
        text=True,
        env=env,
    )


def encrypt_file(path: Path, password: str) -> bool:
    output_path = path.with_name(path.name + ".enc")
    result = run_openssl(
        [
            "enc",
            "-aes-256-cbc",
            "-pbkdf2",
            "-salt",
            "-in",
            str(path),
            "-out",
            str(output_path),
        ],
        password,
    )
    if result.returncode != 0:
        print(f"Failed to encrypt {path.name}: {result.stderr.strip()}", file=sys.stderr)
        return False
    path.unlink()
    print(f"Encrypted: {path.name}")
    return True


def decrypt_file(path: Path, password: str) -> bool:
    output_path = path.with_suffix("")
    result = run_openssl(
        [
            "enc",
            "-d",
            "-aes-256-cbc",
            "-pbkdf2",
            "-in",
            str(path),
            "-out",
            str(output_path),
        ],
        password,
    )
    if result.returncode != 0:
        if output_path.exists():
            output_path.unlink()
        print(f"Failed to decrypt {path.name}: {result.stderr.strip()}", file=sys.stderr)
        return False
    path.unlink()
    print(f"Decrypted: {output_path.name}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Encrypt or decrypt top-level files in a folder")
    parser.add_argument("action", choices=["encrypt", "decrypt"], help="Action to perform")
    parser.add_argument(
        "--directory",
        default=".",
        help="Directory containing files to process. Defaults to the current directory.",
    )
    args = parser.parse_args()

    password = getpass.getpass("Enter password: ")
    target_dir = Path(args.directory).resolve()
    if not target_dir.is_dir():
        print(f"Not a directory: {target_dir}", file=sys.stderr)
        return 1

    processed = 0
    for path in sorted(target_dir.iterdir()):
        if args.action == "encrypt":
            if should_skip(path):
                continue
            if encrypt_file(path, password):
                processed += 1
        else:
            if path.is_file() and path.suffix == ".enc":
                if decrypt_file(path, password):
                    processed += 1

    print(f"Completed {args.action}: {processed} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
