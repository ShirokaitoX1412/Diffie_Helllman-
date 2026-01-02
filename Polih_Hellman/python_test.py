def pohlig_hellman():
    print("--- HACKER: POHLIG-HELLMAN ---")
    p, g, A = int(input("P: ")), int(input("G: ")), int(input("A: "))
    n = p - 1
    
    # Phân tích thừa số nguyên tố của P-1
    factors, d, temp = {}, 2, n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1: factors[temp] = factors.get(temp, 0) + 1
    
    rem, mods = [], []
    for q, e in factors.items():
        qe, g_s, a_s = q**e, pow(g, n // q**e, p), pow(A, n // q**e, p)
        for x in range(qe):
            if pow(g_s, x, p) == a_s:
                rem.append(x); mods.append(qe)
                break

    # Ráp bằng CRT (Sử dụng nghịch đảo modulo)
    prod, result = 1, 0
    for m in mods: prod *= m
    for r, m in zip(rem, mods):
        pm = prod // m
        # pow(pm, -1, m) tìm nghịch đảo modulo pm mod m
        result += r * pow(pm, -1, m) * pm
    
    print(f"\n[!] SỐ BÍ MẬT HACK ĐƯỢC: a = {result % prod}")

if __name__ == "__main__":
    pohlig_hellman()