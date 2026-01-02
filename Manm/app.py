import socket
import logic

def get_valid_private_key(p):
    while True:
        try:
            val = input(f">>> Nhập khóa bí mật của bạn (1 <= x < {p}): ")
            priv = int(val)
            if 1 <= priv < p: return priv
            print(f"[!] Khóa phải từ 1 đến {p-1}")
        except ValueError:
            print("[!] Vui lòng nhập số nguyên.")

def run_dh():
    print("\n=== MÔ PHỎNG TRAO ĐỔI KHÓA DIFFIE-HELLMAN ===")
    mode = input("Bạn là: (1) Alice (Server) | (2) Bob (Client): ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if mode == '1':
        p, q = logic.generate_safe_prime(32)
        suggestions = logic.get_primitive_root_suggestions(p, q)
        print(f"[HỆ THỐNG] p = {p}. Căn nguyên thủy gợi ý: {suggestions[:5]}")
        while True:
            g = int(input(">>> Nhập G: "))
            if logic.verify_primitive_root(g, p, q): break
        
        my_priv = get_valid_private_key(p)
        sock.bind(('0.0.0.0', 12345))
        sock.listen(1)
        print("[*] Đang đợi kết nối...")
        conn, addr = sock.accept()
        conn.send(f"{p},{g}".encode())
        
        # Trao đổi Key
        my_pub = logic.calculate_public_key(g, my_priv, p)
        peer_pub = int(conn.recv(1024).decode())
        conn.send(str(my_pub).encode())
        target_conn = conn
    else:
        ip = input(">>> Nhập IP Alice (hoặc IP Kali nếu MITM): ")
        sock.connect((ip, 12345))
        data = sock.recv(1024).decode().split(',')
        p, g = int(data[0]), int(data[1])
        print(f"[HỆ THỐNG] p = {p}, g = {g}")
        
        my_priv = get_valid_private_key(p)
        my_pub = logic.calculate_public_key(g, my_priv, p)
        sock.send(str(my_pub).encode())
        peer_pub = int(sock.recv(1024).decode())
        target_conn = sock

    shared_secret = logic.calculate_shared_secret(peer_pub, my_priv, p)
    print(f"\n[V] THÀNH CÔNG! KHÓA CHUNG: {shared_secret}")

    # --- CHẾ ĐỘ CHAT ---
    print("\n--- CHAT (Gõ 'exit' để thoát) ---")
    import threading
    
    def receive_msgs():
        while True:
            try:
                data = target_conn.recv(4096).decode()
                if not data: break
                decrypted = logic.xor_cipher(data, shared_secret)
                print(f"\n[ĐỐI PHƯƠNG]: {decrypted}\n>>> Bạn: ", end="")
            except: break

    threading.Thread(target=receive_msgs, daemon=True).start()

    while True:
        msg = input(">>> Bạn: ")
        if msg.lower() == 'exit': break
        encrypted = logic.xor_cipher(msg, shared_secret)
        target_conn.send(encrypted.encode())

    sock.close()

if __name__ == "__main__":
    run_dh()