import socket
import logic

def run_dh():
    print("\n=== MÔ PHỎNG TRAO ĐỔI KHÓA DIFFIE-HELLMAN ===")
    mode = input("Bạn là: (1) Người đợi - Alice (Server) | (2) Người kết nối - Bob (Client): ")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if mode == '1':
        # --- CHẾ ĐỘ ALICE (SERVER) ---
        port = 12345
        p, q = logic.generate_safe_prime(32)
        print(f"[HỆ THỐNG] Đã tìm thấy Safe Prime p = {p}")
        
        suggestions = logic.get_primitive_root_suggestions(p, q)
        print(f"[HỆ THỐNG] Các căn nguyên thủy gợi ý: {suggestions[:10]}")

        while True:
            try:
                g = int(input("\n>>> Nhập số G bạn chọn: "))
                if logic.verify_primitive_root(g, p, q):
                    break
                print(f"[X] LỖI: {g} không phải căn nguyên thủy!")
            except ValueError:
                print("[!] Vui lòng nhập số nguyên.")

        my_priv = get_valid_private_key(p)
        
        sock.bind(('0.0.0.0', port))
        sock.listen(1)
        print(f"\n[SERVER] Alice đang đợi kết nối tại port {port}...")
        conn, addr = sock.accept()
        print(f"[KẾT NỐI] Đã nhận kết nối từ {addr[0]}:{addr[1]}")

        # Bước 1: Gửi p, g
        conn.send(f"{p},{g}".encode())
        
        # Bước 2: Nhận Public Key của Bob và gửi Public Key của mình
        my_pub = logic.calculate_public_key(g, my_priv, p)
        peer_pub_data = conn.recv(1024).decode()
        if not peer_pub_data: return
        peer_pub = int(peer_pub_data)
        conn.send(str(my_pub).encode())
        
        target_conn = conn

    else:
        # --- CHẾ ĐỘ BOB (CLIENT) ---
        ip = input(">>> Nhập IP đối phương (Alice): ")
        port = 12345
        
        try:
            sock.connect((ip, port))
            print(f"[*] Đã kết nối tới {ip}:{port}")
        except Exception as e:
            print(f"[X] Lỗi kết nối: {e}")
            return
        
        # Bước 1: Nhận p, g
        data = sock.recv(1024).decode().split(',')
        p, g = int(data[0]), int(data[1])
        print(f"\n[HỆ THỐNG] Đã nhận tham số: p = {p}, g = {g}")

        my_priv = get_valid_private_key(p)
        my_pub = logic.calculate_public_key(g, my_priv, p)
        
        # Bước 2: Gửi Public Key của mình và nhận Public Key của Alice
        sock.send(str(my_pub).encode())
        peer_pub_data = sock.recv(1024).decode()
        if not peer_pub_data: return
        peer_pub = int(peer_pub_data)
        
        target_conn = sock

    # --- TÍNH KHÓA CHUNG ---
    shared_secret = logic.calculate_shared_secret(peer_pub, my_priv, p)
    print("\n" + "="*45)
    print(f"[*] THÀNH CÔNG! KHÓA BÍ MẬT CHUNG: {shared_secret}")
    print("="*45)

    # --- CHỨC NĂNG TRAO ĐỔI TIN NHẮN THỰC TẾ ---
    print("\n--- BẮT ĐẦU TRAO ĐỔI TIN NHẮN BẢO MẬT ---")
    if mode == '1':
        # Alice gửi tin nhắn đầu tiên
        message = input("[ALICE] Nhập tin nhắn muốn gửi cho Bob: ")
        encrypted = logic.xor_cipher(message, shared_secret)
        target_conn.send(encrypted.encode())
        print(f"[>] Đã gửi tin nhắn (dưới dạng mã hóa): {encrypted.encode().hex()}")
    else:
        # Bob nhận tin nhắn và giải mã
        print("[BOB] Đang đợi tin nhắn từ Alice...")
        encrypted_received = target_conn.recv(4096).decode()
        decrypted = logic.xor_cipher(encrypted_received, shared_secret)
        print(f"[<] Đã nhận tin nhắn mã hóa: {encrypted_received.encode().hex()}")
        print(f"[!] Nội dung giải mã được: {decrypted}")

    target_conn.close()
    sock.close()
    input("\nNhấn Enter để thoát...")

def get_valid_private_key(p):
    while True:
        try:
            val = input(f">>> Nhập khóa bí mật của bạn (1 <= x < {p}): ")
            priv = int(val)
            if 1 <= priv < p: return priv
            print(f"[!] Khóa phải từ 1 đến {p-1}")
        except ValueError:
            print("[!] Vui lòng nhập số nguyên.")

if __name__ == "__main__":
    run_dh()