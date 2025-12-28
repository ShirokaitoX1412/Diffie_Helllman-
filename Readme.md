# 🛡️ Mô phỏng Trao đổi khóa Diffie-Hellman & Tấn công MITM

Dự án này cung cấp một cái nhìn thực tế về giao thức trao đổi khóa mật mã **Diffie-Hellman (DH)** và lỗ hổng bảo mật nghiêm trọng của nó trước tấn công **Man-in-the-Middle (MITM)** khi không có lớp xác thực.

---

## 📂 Cấu trúc mã nguồn

| File | Chức năng |
| :--- | :--- |
| `logic.py` | Chứa các hàm toán học: Miller-Rabin (kiểm tra số nguyên tố), Lũy thừa Modulo, XOR Cipher. |
| `app_dh.py` | Ứng dụng dành cho **Alice** và **Bob** để trao đổi khóa và chat mã hóa. |
| `mitm.py` | Ứng dụng dành cho **Eve** để thực hiện hành vi đánh chặn và mạo danh. |

---

## 🔄 1. Luồng hoạt động: Trao đổi khóa an toàn (Alice ↔️ Bob)

Đây là kịch bản lý tưởng khi không có kẻ tấn công. Alice và Bob thiết lập một kênh truyền bí mật trên môi trường công khai.

### Các bước thực hiện:
1. **Khởi tạo**: Alice sinh số nguyên tố an toàn $p$ và căn nguyên thủy $g$. Cô ấy gửi chúng cho Bob.
2. **Công khai khóa**: 
   - Alice chọn số bí mật $a \rightarrow$ gửi $A = g^a \pmod p$.
   - Bob chọn số bí mật $b \rightarrow$ gửi $B = g^b \pmod p$.
3. **Thiết lập bí mật**:
   - Cả hai tính toán ra cùng một số $K$ (Shared Secret).
4. **Mã hóa**: Tin nhắn được mã hóa bằng thuật toán XOR dựa trên khóa $K$.



---

## 😈 2. Luồng hoạt động: Tấn công MITM (Alice ↔️ Eve ↔️ Bob)

Kịch bản này mô phỏng việc **Eve** đứng giữa, đánh lừa cả hai bên để chiếm quyền kiểm soát toàn bộ cuộc hội thoại.

### Giai đoạn 1: Đánh tráo khóa (Key Replacement)
Eve không bẻ khóa mã hóa, cô ấy **thay thế** nó:
* Eve tạo ra **hai kết nối riêng biệt**: Một với Alice và một với Bob.
* Cô ấy gửi khóa công khai của mình ($E$) cho cả hai.
* Kết quả: Alice nghĩ mình đang chat với Bob (dùng khóa $K_{A-E}$), Bob nghĩ mình đang chat với Alice (dùng khóa $K_{B-E}$).



### Giai đoạn 2: Nghe lén và Mạo danh (Interception & Impersonation)
Khi có dữ liệu luân chuyển qua Eve:
1. **Chặn (Intercept)**: Eve nhận tin nhắn mã hóa từ Alice, giải mã bằng $K_{A-E}$ và đọc nội dung rõ.
2. **Sửa đổi (Modify)**: Eve có thể sửa nội dung tin nhắn (ví dụ: thay đổi số tiền, thay đổi địa chỉ).
3. **Gửi tiếp (Forward)**: Eve mã hóa lại tin nhắn đã sửa bằng $K_{B-E}$ và gửi cho Bob.

> **Hệ quả**: Bob nhận được tin nhắn, giải mã thành công và hoàn toàn tin tưởng đó là tin nhắn từ Alice.

---

## 🛠 Hướng dẫn vận hành

### Bước 1: Chuẩn bị môi trường
Đảm bảo bạn đã cài đặt Python 3 và để các file cùng một thư mục.

### Bước 2: Chạy chế độ an toàn
1. Mở Terminal 1: `python app_dh.py` -> Chọn **1** (Alice).
2. Mở Terminal 2: `python app_dh.py` -> Chọn **2** (Bob) và nhập IP `127.0.0.1`.

### Bước 3: Chạy chế độ tấn công MITM
1. Mở Terminal 1: Chạy **Alice** (Port 12345).
2. Mở Terminal 2: Chạy **Eve** (`python mitm.py`). Eve sẽ kết nối tới Alice và đợi Bob ở Port 1111.
3. Mở Terminal 3: Chạy **Bob**, nhưng kết nối tới IP của Eve và Port **1111**.

## 🔬 Giải thuật kiểm tra số nguyên tố Miller-Rabin

Trong hệ thống Diffie-Hellman, việc sinh số nguyên tố lớn $p$ là tối quan trọng. Chúng ta sử dụng thuật toán **Miller-Rabin**, một thuật toán kiểm tra số nguyên tố xác suất (probabilistic primality test) mạnh mẽ và hiệu quả hơn nhiều so với phương pháp chia thử truyền thống.

### 1. Nguyên lý toán học
Thuật toán dựa trên hai tính chất của số nguyên tố:
1.  **Định lý nhỏ Fermat**: Nếu $p$ là số nguyên tố, thì $a^{p-1} \equiv 1 \pmod p$ với mọi $a$ không chia hết cho $p$.
2.  **Căn bậc hai của đơn vị**: Trong trường số nguyên tố, nếu $x^2 \equiv 1 \pmod p$, thì $x \equiv 1$ hoặc $x \equiv p-1 \pmod p$.



### 2. Các bước xử lý trong file `logic.py`

Hàm `check_prime(n, k=5)` thực hiện các bước sau:

#### Bước 1: Phân tích $n-1$
Vì $n$ là số lẻ, $n-1$ phải là số chẵn. Ta phân tích $n-1$ dưới dạng:
$$n - 1 = 2^r \cdot d$$
*(Trong đó $d$ là một số lẻ và $r \ge 1$)*

#### Bước 2: Thử nghiệm với các "nhân chứng" (Witness)
Ta chọn ngẫu nhiên một số $a$ (nhân chứng) trong khoảng $[2, n-2]$ bằng thư viện `secrets`. Sau đó tính:
$$x = a^d \pmod n$$

* Nếu $x = 1$ hoặc $x = n-1$: Số $n$ vượt qua bài kiểm tra lần này (có khả năng cao là số nguyên tố).
* Nếu không, ta bình phương $x$ liên tiếp $r-1$ lần: $x = x^2 \pmod n$.
    * Nếu tại bất kỳ bước nào $x$ trở thành $n-1$: Số $n$ vượt qua bài kiểm tra.
    * Nếu sau tất cả các lần bình phương mà $x$ vẫn không bao giờ là $n-1$: Số $n$ chắc chắn là **hợp số** (Composite).



### 3. Tại sao chọn Miller-Rabin?

| Tiêu chí | Phương pháp Chia thử | Miller-Rabin |
| :--- | :--- | :--- |
| **Độ phức tạp** | Rất cao ($O(\sqrt{n})$) | Rất thấp ($O(k \log^3 n)$) |
| **Khả năng xử lý** | Chỉ số nhỏ | Số cực lớn (hàng nghìn bit) |
| **Độ chính xác** | 100% | Xác suất sai số $\le (1/4)^k$ |

### 4. Vai trò của tham số `k`
Tham số `k` xác định số lần lặp lại thử nghiệm với các giá trị $a$ khác nhau.
- Với $k=5$ (như trong code), xác suất một hợp số bị nhận nhầm là số nguyên tố là $\approx 0.09\%$.
- Trong các hệ thống thực tế (như SSL/TLS), $k$ thường được chọn từ $40$ đến $64$ để đảm bảo an toàn tuyệt đối.
## 🕵️ Chi tiết kỹ thuật tấn công Man-in-the-Middle (MITM)

Tấn công MITM trong hệ thống Diffie-Hellman là một dạng tấn công **Active Attack** (tấn công chủ động). Kẻ tấn công không chỉ nghe lén mà còn trực tiếp can thiệp và sửa đổi luồng dữ liệu trao đổi khóa.

### 1. Cơ chế "Đánh tráo thực thể" (Entity Impersonation)

Trong file `mitm.py`, Eve không cố gắng bẻ gãy thuật toán mã hóa. Thay vào đó, cô ấy lợi dụng việc thiếu xác thực danh tính để thiết lập hai kênh truyền riêng biệt:

1.  **Kênh Alice - Eve**: Alice nghĩ mình đang trao đổi khóa với Bob, nhưng thực tế là với Eve.
2.  **Kênh Bob - Eve**: Bob nghĩ mình đang trao đổi khóa với Alice, nhưng thực tế là với Eve.



### 2. Quy trình 3 bước của Eve

#### Bước 1: Đánh chặn tham số (Sniffing)
Eve lắng nghe cổng kết nối. Khi Alice gửi các tham số công khai $(p, g)$, Eve chặn lại và chuyển tiếp y hệt cho Bob. Điều này khiến Bob tin rằng mình đang nhận dữ liệu trực tiếp từ Alice.

#### Bước 2: Tráo đổi Khóa công khai (Key Replacement)
Đây là bước quan trọng nhất trong mã nguồn `mitm.py`:
* Alice gửi Public Key $A = g^a \pmod p$. Eve giữ lại $A$ và gửi cho Alice khóa giả $E = g^e \pmod p$.
* Bob gửi Public Key $B = g^b \pmod p$. Eve giữ lại $B$ và gửi cho Bob cũng khóa giả $E = g^e \pmod p$.

#### Bước 3: Thiết lập hai khóa bí mật (Dual Secrets)
Sau bước 2, hai khóa bí mật chung (Shared Secrets) được hình thành mà Alice và Bob không hề nghi ngờ:
* Alice tính: $K_{Alice-Eve} = E^a \pmod p$.
* Bob tính: $K_{Bob-Eve} = E^b \pmod p$.
* **Eve tính cả hai**: $K_{Alice-Eve} = A^e \pmod p$ và $K_{Bob-Eve} = B^e \pmod p$.



### 3. Khả năng kiểm soát tin nhắn (Read & Modify)

Khi khóa đã bị tráo, mọi tin nhắn đi qua Eve đều bị lộ:

| Luồng dữ liệu | Hành động của Eve | Kết quả |
| :--- | :--- | :--- |
| **Alice → Bob** | Giải mã bằng $K_{Alice-Eve} \rightarrow$ Sửa nội dung $\rightarrow$ Mã hóa bằng $K_{Bob-Eve}$ | Bob nhận tin nhắn "giả" nhưng giải mã vẫn thành công. |
| **Bob → Alice** | Giải mã bằng $K_{Bob-Eve} \rightarrow$ Sửa nội dung $\rightarrow$ Mã hóa bằng $K_{Alice-Eve}$ | Alice nhận tin nhắn "giả" nhưng giải mã vẫn thành công. |




