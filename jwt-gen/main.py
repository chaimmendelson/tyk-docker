import jwt
import datetime
import os
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


# Get the directory of the current script
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


def generate_rsa_keypair(private_key_name: str = "rsa_private.pem",
                         public_key_name: str = "rsa_public.pem",
                         key_size: int = 2048) -> None:
    """
    Generate an RSA private/public key pair and save to PEM files in script directory.
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )

    private_path = SCRIPT_DIR / private_key_name
    public_path = SCRIPT_DIR / public_key_name

    # Save private key
    with open(private_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    # Save public key
    public_key = private_key.public_key()
    with open(public_path, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    print(f"RSA key pair generated:\n  Private: {private_path}\n  Public: {public_path}")


def generate_rsa_jwt(payload: dict, expiry_minutes: int = 60,
                     private_key_name: str = "rsa_private.pem") -> str:
    """
    Generate a JWT signed with an RSA private key.
    """
    private_path = SCRIPT_DIR / private_key_name
    with open(private_path, "r") as f:
        private_key = f.read()

    now = datetime.datetime.now(datetime.UTC)
    payload.update({
        "iat": now,
        "exp": now + datetime.timedelta(minutes=expiry_minutes),
    })

    token = jwt.encode(payload, private_key, algorithm="RS256")
    return token


def verify_rsa_jwt(token: str, public_key_name: str = "rsa_public.pem") -> dict:
    """
    Verify JWT using RSA public key.
    """
    public_path = SCRIPT_DIR / public_key_name
    with open(public_path, "r") as f:
        public_key = f.read()

    return jwt.decode(token, public_key, algorithms=["RS256"])


if __name__ == "__main__":
    private_key_file = SCRIPT_DIR / "rsa_private.pem"
    public_key_file = SCRIPT_DIR / "rsa_public.pem"

    # Generate keys if not present
    if not private_key_file.exists() or not public_key_file.exists():
        generate_rsa_keypair()

    # Example claims
    claims = {"sub": "dos", "role": "admin"}

    # Generate token
    token = generate_rsa_jwt(claims)
    print("\nGenerated JWT:\n", token)

    # Verify token
    decoded = verify_rsa_jwt(token)
    print("\nDecoded Payload:\n", decoded)
