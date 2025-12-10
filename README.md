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
Vào thư mục theme [project/theme/static_src](project/theme/static_src/):
```bash
cd project/theme/static_src
npm install
```
### 5. Build Tailwind CSS
Di chuyển về thư mục [project](project/) chạy:
```bash
python manage.py tailwind build
```
### 6. Tổ chức dữ liệu lên Neo4j
[Xem hướng dẫn ở đây](review_graph/README.md)

### 7. Chạy server Django
Di chuyển vào thư mục project trong terminal bằng `cd project` và chạy:
```bash
python manage.py migrate
python manage.py runserver
```
**Lưu ý:** Để hệ thống sinh bài review từ 1 trong 3 mô hình gpt-4-turbo, gemini-1.5-flash, deepseek-reasoner, thì chỉ cần bỏ comment của dòng có handler tương ứng (trong file [project/virtual_reviewer/views/review.py](project/virtual_reviewer/views/review.py)) và comment 2 dòng handler còn lại.
```python
# Generate review using LLM
# review, answer = self.deepseek_handler.generate_review(prompt)
# review, answer = self.gpt_handler.generate_review(prompt)
review, answer = self.gemini_handler.generate_review(prompt)

# Save data for rouge score calculation
# save_data(question, answer, context)
```  

#### Lưu data để đo rouge
Nếu muốn lưu dữ liệu bài review, context (thông tin truy xuất sản phẩm theo nsx, reviewers) vào file data để đo rouge thì chỉ cần bỏ comment dòng `save_data(question, answer, context)` trong hình trên. Và muốn lưu data từ model nào thì chỉ cần bỏ comment dòng filepath tương ứng và comment 2 dòng còn lại (trong file [project/virtual_reviewer/utils/save_data.py](project/virtual_reviewer/utils/save_data.py)):  
```python
# Used to save the review into the specified file
# filepath = os.path.join(output_dir, "deepseek_review.json")
# filepath = os.path.join(output_dir, "gpt_review.json")
filepath = os.path.join(output_dir, "gemini25_review.json")
``` 

## 🏆 Đo rouge
Sau khi lưu đủ 53 bài review cho 53 sản phẩm trong hệ thống trong các file ([gemini15_review.json](evaluate/data/gemini15_review.json) (Gemini 1.5 Flash - đã ngừng hoạt động), [gemini25_review.json](evaluate/data/gemini25_review.json) (Gemini 2.5 Flash), [gpt_review.json](evaluate/data/gpt_review.json) (GPT-4 Turbo) và [deepseek_review.json](evaluate/data/deepseek_review.json) (deepseek-reasoner)) trong thư mục [evaluate/data](evaluate/data), di chuyển vào thư mục evaluate trong terminal bằng `cd evaluate` và chạy file [metric.py](evaluate/metric.py) sẽ in ra được rouge-score như bên dưới:  
| Model             | ROUGE-1 | ROUGE-2 | ROUGE-L |
|-------------------|---------|---------|---------|
| gemini-2.5-flash  | 0.5458  | 0.4520  | 0.2940  |
| deepseek-reasoner | 0.7001  | 0.4726  | 0.3022  |
| gpt-4-turbo       | 0.7700  | 0.5367  | 0.3498  |