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
Vào thư mục theme (theme/):
```bash
cd project/theme
npm install
```
### 5. Build Tailwind CSS
Di chuyển về thư mục **phones-virtual-reviewer/project** chạy:
```bash
python manage.py tailwind start
```
### 6. Chạy server Django
```bash
python manage.py migrate
python manage.py runserver
```