import socket
import logic
import secrets

def run_mitm():
    print("\n=== EVE MITM - TRẠM TRUNG CHUYỂN ĐỘC ÁC (HAI CHIỀU) ===")
    
    ALICE_ADDR = ('127.0.0.1', 12345) 
    EVE_LISTEN_PORT = 1111 

    # 1. Khởi tạo server đợi Bob
    eve_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    eve_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    eve_server.bind(('0.0.0.0', EVE_LISTEN_PORT))
    eve_server.listen(1)
    
    print(f"[*] Đang đợi Bob kết nối...")
    conn_bob, addr_bob = eve_server.accept()
    
    # 2. Kết nối tới Alice
    eve_to_alice = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    eve_to_alice.connect(ALICE_ADDR)

    try:
        # --- BƯỚC 1: TRÁO ĐỔI KHÓA (GIỮ NGUYÊN) ---
        params_data = eve_to_alice.recv(4096).decode()
        p, g = map(int, params_data.split(','))
        conn_bob.send(params_data.encode())

        eve_priv = secrets.randbelow(p-2) + 2
        eve_pub = logic.calculate_public_key(g, eve_priv, p)

        bob_pub_real = int(conn_bob.recv(4096).decode())
        eve_to_alice.send(str(eve_pub).encode())

        alice_pub_real = int(eve_to_alice.recv(4096).decode())
        conn_bob.send(str(eve_pub).encode())

        secret_alice = logic.calculate_shared_secret(alice_pub_real, eve_priv, p)
        secret_bob = logic.calculate_shared_secret(bob_pub_real, eve_priv, p)

        print(f"\n[!] MITM THÀNH CÔNG. Khóa Alice-Eve: {secret_alice} | Khóa Bob-Eve: {secret_bob}")

        # --- BƯỚC 2: MẠO DANH HAI CHIỀU ---
        while True:
            print("\n" + "-"*30)
            print("[*] Đang đợi dữ liệu luân chuyển...")
            
            # Giả sử kịch bản: Alice gửi trước, sau đó Bob phản hồi
            # Lượt 1: Alice -> Bob
            data_from_alice = eve_to_alice.recv(4096).decode()
            if not data_from_alice: break
            
            real_msg_alice = logic.xor_cipher(data_from_alice, secret_alice)
            print(f"[CHẶN ALICE]: '{real_msg_alice}'")
            
            # Eve mạo danh Alice gửi cho Bob
            fake_msg_for_bob = input(f"Eve mạo danh Alice gửi cho Bob (Gốc: {real_msg_alice}): ")
            enc_for_bob = logic.xor_cipher(fake_msg_for_bob, secret_bob)
            conn_bob.send(enc_for_bob.encode())

            # Lượt 2: Bob -> Alice
            data_from_bob = conn_bob.recv(4096).decode()
            if not data_from_bob: break
            
            real_msg_bob = logic.xor_cipher(data_from_bob, secret_bob)
            print(f"[CHẶN BOB]: '{real_msg_bob}'")
            
            # Eve mạo danh Bob gửi lại cho Alice
            fake_msg_for_alice = input(f"Eve mạo danh Bob gửi cho Alice (Gốc: {real_msg_bob}): ")
            enc_for_alice = logic.xor_cipher(fake_msg_for_alice, secret_alice)
            eve_to_alice.send(enc_for_alice.encode())

    except Exception as e:
        print(f"\n[!] Kết thúc phiên chat: {e}")
    finally:
        conn_bob.close()
        eve_to_alice.close()
        eve_server.close()

if __name__ == "__main__":
    run_mitm()