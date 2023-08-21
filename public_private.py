from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_and_store_keys():
    public_key_filename = "public_key.pem"
    private_key_filename = "private_key.pem"
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    with open(private_key_filename, "wb") as private_key_file:
        private_key_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    public_key = private_key.public_key()
    with open(public_key_filename, "wb") as public_key_file:
        public_key_file.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

# if __name__ == "__main__":
#     public_key_filename = "public_key.pem"
#     private_key_filename = "private_key.pem"

#     generate_and_store_keys(public_key_filename, private_key_filename)
#     print("Keys generated and stored successfully.")