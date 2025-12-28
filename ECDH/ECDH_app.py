import socket
import logic_ecdh

def run_app():
    print("\n=== ECDH + ECDSA: BẢO MẬT CHỐNG MITM ===")
    mode = input("Bạn là: (1) Alice | (2) Bob: ")
    
    ecdh_priv, ecdh_pub = logic_ecdh.generate_ecdh_keys()
    sign_priv, verify_pub = logic_ecdh.generate_signing_keys()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if mode == '1':
        sock.bind(('0.0.0.0', 12345))
        sock.listen(1)
        print("[*] Alice đang đợi tại 12345...")
        conn, _ = sock.accept()
        # Alice gửi: Verify_PubKey (ID) -> ECDH_PubKey -> Signature
        conn.sendall(verify_pub); conn.recv(10)
        conn.sendall(ecdh_pub); conn.recv(10)
        conn.sendall(logic_ecdh.sign_data(sign_priv, ecdh_pub))
        target = conn
    else:
        ip = input(">>> Nhập IP Alice (IP LAN): ")
        sock.connect((ip, 12345))
        # Bob nhận thông tin từ Alice
        v_pub = sock.recv(4096); sock.send(b'OK')
        e_pub = sock.recv(4096); sock.send(b'OK')
        sig = sock.recv(4096)
        
        # KIỂM TRA CHỮ KÝ - ĐÂY LÀ CHỖ EVE BỊ LỘ
        if not logic_ecdh.verify_signature(v_pub, sig, e_pub):
            print("\n[X] NGUY HIỂM: CHỮ KÝ SAI! CÓ KẺ ĐANG TRÁO KHÓA.")
            sock.close(); return
        
        print("[V] XÁC THỰC THÀNH CÔNG!")
        secret = logic_ecdh.calculate_shared_secret(ecdh_priv, e_pub)
        print(f"[*] Khóa bí mật: {secret.hex()[:20]}...")
        target = sock

    input("\nNhấn Enter để thoát...")
    target.close()

if __name__ == "__main__":
    run_app()