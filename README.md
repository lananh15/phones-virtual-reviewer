## 🚀 Cài đặt

### 1. Clone dự án và cài đặt thư viện cần thiết
```bash
git clone https://github.com/lananh15/phones-virtual-reviewer.git
pip install -r requirements.txt
```
Thêm file .env cùng cấp với requirements.txt có dạng:
```bash
DJANGO_SECRET_KEY='your-django-secret-key'
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
NEO4J_URI = "your-neo4j-uri"
NEO4J_USER = "your-neo4j-user"
NEO4J_PASS = "your-neo4j-pass"
```
### 2. Cài Node.js và npm
Tailwind cần Node.js để build CSS. Tải tại: https://nodejs.org.  
Kiểm tra:
```bash
node -v
npm -v
```
### 4. Cài Tailwind dependencies
Vào thư mục theme (theme/static_src):
```bash
cd project/theme/static_src
npm install
```
### 5. Build Tailwind CSS
Di chuyển về thư mục **phones-virtual-reviewer/project** chạy:
```bash
python manage.py tailwind build
```
### 6. Chạy server Django
Di chuyển vào thư mục project trong terminal bằng `cd project` và chạy:
```bash
python manage.py migrate
python manage.py runserver
```
**Lưu ý:** Để hệ thống sinh bài review từ 1 trong 3 mô hình gpt-4-turbo, gemini-1.5-flash, deepseek-reasoner, thì chỉ cần bỏ comment của dòng có handler tương ứng (trong file **project/virtual_reviewer/views/review.py**) và comment 2 dòng handler còn lại.
![Picture 1](https://github.com/user-attachments/assets/2f22c404-790b-4f13-8109-8ff7dc4d5e73)  
#### Lưu data để đo rouge
Nếu muốn lưu dữ liệu bài review, context (thông tin truy xuất sản phẩm theo nsx, reviewers) vào file data để đo rouge thì chỉ cần bỏ comment dòng `save_data(question, answer, context)` trong hình trên. Và muốn lưu data từ model nào thì chỉ cần bỏ comment dòng filepath tương ứng và comment 2 dòng còn lại (trong file **project/virtual_reviewer/utils/save_data.py**) như hình dưới:  
![Picture 2](https://github.com/user-attachments/assets/3a5cb47f-88b3-4dc8-8bc0-bb4cdf3d7fef)  

## 🏆 Đo rouge
Sau khi lưu đủ 48 bài review cho 48 sản phẩm trong hệ thống trong các file (gemini_review.json, gpt_review.json và deepseek.json) trong thư mục **evaluate/data**, di chuyển vào thư mục evaluate trong terminal bằng `cd evaluate` và chạy file **"metric.py"** sẽ in ra được rouge-score như bên dưới:  
![rouge-score](https://github.com/user-attachments/assets/a0430897-be3c-48c5-91d3-269d51becc8f)  