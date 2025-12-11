Repo này gồm 3 module độc lập (mỗi module có requirements.txt riêng):
- [project/](project/) → website DoraReviewer + sinh review
- [review_graph/](review_graph/) → tổ chức dữ liệu Neo4j
- [evaluate/](evaluate/) → đo ROUGE  
**Lưu ý:** Mỗi module trong dự án sẽ có file **requirements.txt** riêng, khi dùng module nào thì cần tải thư viện cần thiết nên phải di chuyển vào module đó bằng lệnh `cd` và chạy:
```bash
pip install -r requirements.txt
```
## 🚀 Cài đặt

### 1. Clone dự án và cài đặt thư viện cần thiết
**Bước 1:** Clone dự án
```bash
git clone https://github.com/lananh15/phones-virtual-reviewer.git
```
**Bước 2:** Cài thư viện cho Django (module project)
```bash
cd project
pip install -r requirements.txt
```
**Bước 3:** Thêm file .env tại thư mục gốc repo có dạng:
```bash
DJANGO_SECRET_KEY='your-django-secret-key'
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
NEO4J_URI = "your-neo4j-uri"
NEO4J_USER = "your-neo4j-user"
NEO4J_PASS = "your-neo4j-pass"
```
### 2. Cấu hình Tailwind
**Bước 1:** Tailwind cần Node.js để build CSS. Tải tại: https://nodejs.org.  
Kiểm tra:
```bash
node -v
npm -v
```
**Bước 2:** Cài Tailwind dependencies
Vào thư mục theme [project/theme/static_src](project/theme/static_src/):
```bash
cd project/theme/static_src
npm install
```
**Bước 3:** Build Tailwind CSS
Di chuyển về thư mục [project](project/) chạy:
```bash
python manage.py tailwind build
```
### 3. Tổ chức dữ liệu lên Neo4j
[XEM HƯỚNG DẪN Ở ĐÂY](review_graph/README.md)  

⚠️ **Lưu ý:** các script trong [review_graph/](review_graph/) phải được chạy từ đúng thư mục [review_graph/](review_graph/) để tránh lỗi đường dẫn.

### 4. Chạy server Django
Di chuyển vào thư mục project trong terminal bằng `cd project` và chạy:
```bash
python manage.py migrate
python manage.py runserver
```
#### Chọn mô hình sinh review
*(Mặc định dự án đang bật Gemini 2.5 Flash)*

Trong file [project/virtual_reviewer/views/review.py](project/virtual_reviewer/views/review.py), bỏ comment 1 dòng tương ứng với mô hình cần dùng:
```python
# Generate review using LLM
# review, answer = self.deepseek_handler.generate_review(prompt)
# review, answer = self.gpt_handler.generate_review(prompt)
review, answer = self.gemini_handler.generate_review(prompt)

# Save data for rouge score calculation
# save_data(question, answer, context)
```  

### 5. Lưu data để đo rouge
Để lưu bài review + context vào file cho bước evaluate, trong file [project/virtual_reviewer/views/review.py](project/virtual_reviewer/views/review.py) bỏ comment dòng:
```python
save_data(question, answer, context)
``` 
Lưu data từ model nào thì bỏ comment dòng filepath tương ứng và comment 2 dòng còn lại (trong file [project/virtual_reviewer/utils/save_data.py](project/virtual_reviewer/utils/save_data.py)):  
```python
# Used to save the review into the specified file
# filepath = os.path.join(output_dir, "deepseek_review.json")
# filepath = os.path.join(output_dir, "gpt_review.json")
filepath = os.path.join(output_dir, "gemini25_review.json")
``` 

## 🏆 Đo rouge
Sau khi lưu đủ 53 bài review cho 53 sản phẩm trong hệ thống trong các file trong thư mục [evaluate/data](evaluate/data):
- [gemini15_review.json](evaluate/data/gemini15_review.json) (Gemini 1.5 Flash - đã ngừng hoạt động)
- [gemini25_review.json](evaluate/data/gemini25_review.json) (Gemini 2.5 Flash)
- [gpt_review.json](evaluate/data/gpt_review.json) (GPT-4 Turbo)
- [deepseek_review.json](evaluate/data/deepseek_review.json) (deepseek-reasoner)  
Di chuyển vào thư mục [evaluate/](evaluate/) và cài thư viện cần thiết cho module này:
```bash
cd evaluate
pip install -r requirements.txt
```
Sau đó, chạy file [metric.py](evaluate/metric.py) sẽ in ra được rouge-score như bên dưới:  
| Model             | ROUGE-1 | ROUGE-2 | ROUGE-L |
|-------------------|---------|---------|---------|
| gemini-2.5-flash  | 0.5458  | 0.4520  | 0.2940  |
| deepseek-reasoner | 0.7001  | 0.4726  | 0.3022  |
| gpt-4-turbo       | 0.7700  | 0.5367  | 0.3498  |
