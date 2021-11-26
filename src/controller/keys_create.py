from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import jwt

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
# DER-encoded and PKCS8EncodedKeySpec
# consistent with Pulsar (not necessary, since Pulsar not need private key)
private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8, # PKCS8EncodedKeySpec
    encryption_algorithm=serialization.NoEncryption()
)

# DER-encoded and X509EncodedKeySpec, consistent with Pulsar
public_bytes = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PublicFormat.SubjectPublicKeyInfo # X509EncodedKeySpec
)

with open('/private_key/private.key', 'wb') as f:
    f.write(private_bytes)

with open('/public_key/public.key', 'wb') as f:
    f.write(public_bytes)

with open('/token/super_user', 'wt') as f:
    f.write(jwt.encode({'sub': 'super-user'}, private_key, algorithm='RS256', headers={'typ': None}))