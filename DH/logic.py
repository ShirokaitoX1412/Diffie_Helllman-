import secrets

def check_prime(n, k=5):
    """Kiểm tra số nguyên tố bằng thuật toán Miller-Rabin (nhanh và chính xác)."""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0: return False

    # Tìm d sao cho n-1 = 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = secrets.randbelow(n - 4) + 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def get_primitive_root_suggestions(p, q, limit=50):
    """Tìm danh sách các căn nguyên thủy của Safe Prime p."""
    suggestions = []
    # Đối với Safe Prime p = 2q + 1, g là căn nguyên thủy nếu g^2 != 1 và g^q != 1 (mod p)
    for g_test in range(2, p):
        if verify_primitive_root(g_test, p, q):
            suggestions.append(g_test)
        if len(suggestions) >= limit:
            break
    return suggestions

def verify_primitive_root(g, p, q):
    """Xác nhận g có phải là căn nguyên thủy hợp lệ cho Safe Prime không."""
    if not (1 < g < p): return False
    return pow(g, 2, p) != 1 and pow(g, q, p) != 1

def generate_safe_prime(bits=32):
    """Sinh số p (Safe Prime) và q cực nhanh."""
    print(f"[HỆ THỐNG] Đang tìm Safe Prime {bits}-bit...")
    while True:
        q = secrets.randbits(bits - 1) | (1 << (bits - 2)) | 1
        if check_prime(q):
            p = 2 * q + 1
            if check_prime(p):
                return p, q

def calculate_public_key(g, priv_key, p):
    return pow(g, priv_key, p)

def calculate_shared_secret(peer_pub, my_priv, p):
    return pow(peer_pub, my_priv, p)

def xor_cipher(text, key):
    """Sử dụng shared secret làm khóa để mã hóa/giải mã văn bản."""
    key_str = str(key)
    result = ""
    for i in range(len(text)):
        # XOR từng ký tự của văn bản với ký tự tương ứng của khóa
        result += chr(ord(text[i]) ^ ord(key_str[i % len(key_str)]))
    return result