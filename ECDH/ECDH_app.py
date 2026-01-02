import socket
import threading
import logic_ecdh
from cryptography.hazmat.primitives import hashes

def run_app():
    print("\n=== ECDH + ECDSA: BẢO MẬT CHỐNG MITM (BẢN CHUẨN) ===")
    mode = input("Bạn là: (1) Alice (Server) | (2) Bob (Client): ")
    
    # 1. Tạo cặp khóa Trao đổi (ECDH) và cặp khóa Định danh (ECDSA)
    ecdh_priv, ecdh_pub = logic_ecdh.generate_ecdh_keys()
    sign_priv, verify_pub = logic_ecdh.generate_signing_keys()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if mode == '1':
        sock.bind(('0.0.0.0', 12345))
        sock.listen(1)
        print("[*] Alice đang đợi kết nối tại cổng 12345...")
        conn, addr = sock.accept()
        print(f"[+] Kết nối từ: {addr}")
        
        # --- QUY TRÌNH BẮT TAY (HANDSHAKE) ---
        # Gửi khóa Verify (Định danh) 
        conn.sendall(verify_pub)
        peer_verify_pub = conn.recv(4096)
        
        # Gửi khóa ECDH Public và Chữ ký
        signature = logic_ecdh.sign_data(sign_priv, ecdh_pub)
        conn.sendall(ecdh_pub)
        conn.recv(1024) # Chờ ACK để tránh gộp gói tin
        conn.sendall(signature)
        
        # Nhận khóa ECDH và Chữ ký từ đối phương
        peer_ecdh_pub = conn.recv(4096)
        conn.sendall(b'ACK')
        peer_sig = conn.recv(4096)
        
        target_conn = conn
    else:
        ip = input(">>> Nhập IP của đối phương: ")
        sock.connect((ip, 12345))
        
        # --- QUY TRÌNH BẮT TAY (HANDSHAKE) ---
        # Nhận khóa Verify (Định danh) và gửi lại của mình
        peer_verify_pub = sock.recv(4096)
        sock.sendall(verify_pub)
        
        # Nhận khóa ECDH và Chữ ký từ đối phương
        peer_ecdh_pub = sock.recv(4096)
        sock.sendall(b'ACK')
        peer_sig = sock.recv(4096)
        
        # Gửi khóa ECDH của mình và Chữ ký
        signature = logic_ecdh.sign_data(sign_priv, ecdh_pub)
        sock.sendall(ecdh_pub)
        sock.recv(1024) # Chờ ACK
        sock.sendall(signature)
        
        target_conn = sock

    # --- KIỂM TRA CHỮ KÝ (CHỐNG MITM) ---
    if logic_ecdh.verify_signature(peer_verify_pub, peer_sig, peer_ecdh_pub):
        print("\n" + "v"*30)
        print("[V] XÁC THỰC THÀNH CÔNG: Chữ ký đúng chính chủ!")
        
        # Tính Shared Secret và băm về 32 bytes dùng SHA-256
        raw_secret = logic_ecdh.calculate_shared_secret(ecdh_priv, peer_ecdh_pub)
        digest = hashes.Hash(hashes.SHA256())
        digest.update(raw_secret)
        shared_secret = digest.finalize()
        
        print(f"[*] Khóa chung (SHA-256): {shared_secret.hex()}")
        print("v"*30 + "\n")
    else:
        print("\n" + "!"*30)
        print("[X] CẢNH BÁO: CHỮ KÝ SAI! CÓ KẺ ĐANG ĐỨNG GIỮA (MITM).")
        print("!"*30 + "\n")
        sock.close()
        return

    # --- PHẦN CHAT MÃ HÓA ---
    def receive_msgs():
        while True:
            try:
                data = target_conn.recv(4096)
                if not data: break
                # Dùng hàm xor_cipher chuẩn từ logic_ecdh
                decrypted_bytes = logic_ecdh.xor_cipher(data, shared_secret)
                print(f"\n[ĐỐI PHƯƠNG]: {decrypted_bytes.decode('utf-8')}\n>>> Bạn: ", end="")
            except:
                break

    threading.Thread(target=receive_msgs, daemon=True).start()

    while True:
        try:
            msg = input(">>> Bạn: ")
            if msg.lower() == 'exit': break
            if not msg: continue
            
            # Mã hóa tin nhắn
            encrypted_data = logic_ecdh.xor_cipher(msg, shared_secret)
            target_conn.sendall(encrypted_data)
        except KeyboardInterrupt:
            break

    print("[*] Đang đóng kết nối...")
    sock.close()

if __name__ == "__main__":
    run_app()