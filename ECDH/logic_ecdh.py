from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

# --- ECDH: Trao đổi khóa ---
def generate_ecdh_keys():
    priv_key = ec.generate_private_key(ec.SECP256R1())
    pub_bytes = priv_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return priv_key, pub_bytes

def calculate_shared_secret(private_key, peer_public_bytes):
    peer_public_key = serialization.load_pem_public_key(peer_public_bytes)
    return private_key.exchange(ec.ECDH(), peer_public_key)

# --- ECDSA: Chữ ký số ---
def generate_signing_keys():
    priv_signing = ec.generate_private_key(ec.SECP256R1())
    pub_verify_bytes = priv_signing.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return priv_signing, pub_verify_bytes

def sign_data(private_signing_key, data_bytes):
    return private_signing_key.sign(data_bytes, ec.ECDSA(hashes.SHA256()))

def verify_signature(public_verify_bytes, signature, data_bytes):
    public_key = serialization.load_pem_public_key(public_verify_bytes)
    try:
        public_key.verify(signature, data_bytes, ec.ECDSA(hashes.SHA256()))
        return True
    except:
        return False

# --- MẬT MÃ: XOR Cipher cho Bytes ---
def xor_cipher(data, key_bytes):
    """
    Dùng cho cả mã hóa và giải mã. 
    'data' có thể là chuỗi (string) hoặc bytes.
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    return bytes([data[i] ^ key_bytes[i % 32] for i in range(len(data))])