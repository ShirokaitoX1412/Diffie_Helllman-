import socket
import logic_ecdh

def run_mitm():
    print("\n=== EVE MITM: ĐANG THỰC HIỆN TRÁO KHÓA ===")
    EVE_PORT = 2222
    ALICE_ADDR = ('127.0.0.1', 12345)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', EVE_PORT))
    server.listen(1)
    
    print(f"[*] Eve đợi Bob tại cổng {EVE_PORT}...")
    conn_bob, _ = server.accept()
    
    # Kết nối tới Alice
    eve_to_alice = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    eve_to_alice.connect(ALICE_ADDR)

    # Eve tự tạo khóa giả để tráo
    _, eve_ecdh_pub = logic_ecdh.generate_ecdh_keys()

    try:
        # --- LUỒNG NHẬN TỪ ALICE ---
        v_pub = eve_to_alice.recv(4096); eve_to_alice.send(b'OK')
        e_pub_real = eve_to_alice.recv(4096); eve_to_alice.send(b'OK')
        sig_real = eve_to_alice.recv(4096)

        # --- LUỒNG GỬI CHO BOB (TRÁO ĐỔI) ---
        conn_bob.sendall(v_pub); conn_bob.recv(10)      # Gửi khóa Verify thật của Alice
        conn_bob.sendall(eve_ecdh_pub); conn_bob.recv(10) # GỬI KHÓA ECDH GIẢ CỦA EVE
        conn_bob.sendall(sig_real)                      # Gửi chữ ký thật của Alice

        print("[!] Đã tráo khóa xong. Đang xem Bob có bị lừa không...")
        
        # Đợi xem Bob phản ứng thế nào (Bob sẽ verify và thấy sai)
        data = conn_bob.recv(1024)
        if not data:
            print("\n[X] KẾT QUẢ: Bob phát hiện chữ ký sai và ngắt kết nối!")
        
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        conn_bob.close()
        eve_to_alice.close()
        server.close()

if __name__ == "__main__":
    run_mitm()