def alice_generate():
    print("--- PHÍA ALICE ---")
    p = int(input("P: "))
    g = int(input("G: "))
    a = int(input("a (bí mật): "))
    A = pow(g, a, p)
    print(f"\n[!] Khóa công khai A gửi lên mạng: {A}")
if __name__ == "__main__": alice_generate()