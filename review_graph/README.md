**[youtube_links.txt](video-youtube/youtube_links.txt)** là file chứa link của 120 video Youtube review về 48 mẫu điện thoại từ các thương hiệu iPhone, Samsung, OPPO, Xiaomi, Realme, Vivo.  
**[phones_data.json](phones_data.json)** là file tổng hợp các thông số kĩ thuật của 48 mẫu điện thoại trên từ các trang như CellphoneS, Thế Giới Di Động,...  
**[youtube_reviews.json](phones_data.json)** là file tổng hợp các thông tin review từ 120 video, nhóm theo tên của 48 mẫu điện thoại.  
## 📌 Cách nhanh nhất để có dữ liệu trên Neo4j của bạn để chạy được Cỗ máy rì viu
Từ thư mục gốc là phones-virtual-reviewer (khi vừa clone repo về), di chuyển vào thư mục **review_graph** bằng `cd review-graph`  
GIỮ file [youtube_reviews.json](video-youtube/youtube_reviews.json) đã có trong repo này và chạy file [graph_data.py](video-youtube/transcript_graph/graph_data.py) (PHẢI chạy file này từ thư mục **review_graph**) thì sẽ tự động đẩy dữ liệu của chúng tôi lên Neo4j của bạn.  
=> Thế là đã có dữ liệu để chạy hệ thống Cỗ máy rì viu!

## 🧵 Tổng quan pipeline xử lý video review trên Youtube và thông số kĩ thuật tổ chức dữ liệu lên Neo4j
Pipeline này trích xuất và tổ chức dữ liệu review sản phẩm từ video YouTube, sau đó lưu trữ dưới dạng đồ thị trong cơ sở dữ liệu Neo4j, bao gồm kết hợp xử lý audio, gpt-4-turbo để tóm tắt, và chuyển đổi dữ liệu thành cấu trúc đồ thị.  
### Các bước trong pipeline
#### 1. Tải Audio từ YouTube
- Đầu vào: Danh sách URL video YouTube.
- Thao tác: Tải audio từ từng video.
- Đầu ra: File .mp3 lưu trong thư mục [video-youtube/audio/](video-youtube/audio/).
#### 2. Chuyển Giọng Nói Thành Văn Bản
- Công cụ: faster-whisper.
- Thao tác: Chuyển audio thành transcript (văn bản).
- Đầu ra: File transcript thô.
#### 3. Tóm Tắt Review Bằng gpt-4-turbo
- Đầu vào: Transcript + prompt tùy chỉnh.
- Thao tác: Gửi lên gpt-4-turbo để trích xuất thông tin review có cấu trúc.
- Đầu ra: File JSON chứa thông tin review cho từng video trong thư mục [video-youtube/review_data/](video-youtube/review_data/)
#### 4. Gộp & Nhóm Dữ Liệu Review
- Đầu vào: 120 file JSON riêng lẻ trong thư mục [video-youtube/review_data/](video-youtube/review_data/)
- Thao tác: Gộp tất cả thành một file duy nhất.
- Nhóm theo: Tên sản phẩm.
- Đầu ra: [youtube_reviews.json](video-youtube/youtube_reviews.json)
#### 5. Đẩy Dữ Liệu Lên Neo4j
- Đầu vào: [youtube_reviews.json](video-youtube/youtube_reviews.json) + [phones_data.json](phones_data.json).
- Thao tác: Chuyển dữ liệu thành node và relationship.
- Đầu ra: Đồ thị review sản phẩm trong Neo4j.

### Cách tạo 120 file JSON (từ 120 video Youtube) trong [video-youtube/review_data/](video-youtube/review_data/)
Chạy file **[main.py](video-youtube/main.py)** (PHẢI chạy file này từ thư mục **review_graph**)  
**Lưu ý:** muốn tạo 1 file JSON của 1 video thì
- BẮT BUỘC file audio của video đó CHƯA CÓ trong thư mục [video-youtube/audio/](video-youtube/audio) và dĩ nhiên cũng CHƯA CÓ file JSON đó trong thư mục [video-youtube/review_data/](video-youtube/review_data/).
*Chúng tôi có sẵn 120 file JSON được tổng hợp sẵn từ 120 video Youtube rồi nên bạn có thể tiến đến bước gộp luôn, không cần tạo từng file JSON nữa.*  

**Gợi ý:** Nếu muốn test code (mà không muốn chạy 120 video lại từ đầu -> tốn thời gian):
- Hãy dán 1 link video review Youtube bất kì vào cuối file [youtube_links.txt](video-youtube/youtube_links.txt) (link video thêm vào phải chưa có trong file này) và chạy file main.py như đề cập ở trên.  
**Quan trọng:**
- Khi ra 1 file JSON có thể sẽ có 1 số từ bị sai như "OPPO Find X8" mà lại ghi thành "OPPO 5X8" nên phải lọc và sửa lại cho đúng thông tin.
- Phải nhất quán tên sản phẩm như "OPPO Find X8" thì tất cả file liên quan sản phẩm này đều phải ghi đúng tên như vậy, không được ghi "Oppo Find X8" thì mới tổ chức đúng node lên Neo4j được. (Tên sản phẩm phải trùng khớp với trường "canonical_name" trong file [phones_data.json](phones_data.json))
### Gộp 120 file JSON thành 1 file JSON chung nhóm theo tên sản phẩm
Chạy file [merge_transcript.py](video-youtube/transcript_graph/merge_transcript.py) (PHẢI chạy file này từ thư mục **review_graph**) thì sẽ tự động sinh ra file [youtube_reviews.json](video-youtube/youtube_reviews.json) như đã có trong repo này.

### Tổ chức dữ liệu lên Neo4j
Như đã đề cập [Ở ĐÂY](#-cách-nhanh-nhất-để-có-dữ-liệu-trên-neo4j-của-bạn-để-chạy-được-cỗ-máy-rì-viu)    
Mô tả tổng qua tổ chức dữ liệu trên Neo4j:
```mermaid
graph TD
    YTSource["Source: YoutubeReview"]
    MFSource["Source: Manufacturer"]
    
    Product["Product<br/>name, slug, category"]
    
    VideoReview["VideoReview<br/>video_id, product_name<br/>type, price, recommendation"]
    Video["Video<br/>video_id, title, url<br/>author, upload_date"]
    
    Feature["Feature<br/>text"]
    Pro["Pro<br/>text"]
    Con["Con<br/>text"]
    
    GeneralInfo["GeneralInfo<br/>model, link, price, image"]
    HardwareSpec["HardwareSpec<br/>key, value"]
    SoftwareSpec["SoftwareSpec<br/>os"]
    CameraSpec["CameraSpec<br/>type, detail"]
    DisplaySpec["DisplaySpec<br/>technology, size, resolution"]
    DisplayFeature["DisplayFeature<br/>text"]
    
    YTSource -->|INCLUDES| Product
    MFSource -->|INCLUDES| Product
    
    Product -->|MENTIONED_IN| VideoReview
    VideoReview -->|IN_VIDEO| Video
    VideoReview -->|HAS_FEATURE| Feature
    VideoReview -->|HAS_PRO| Pro
    VideoReview -->|HAS_CON| Con
    
    Product -->|HAS_GENERAL_INFO| GeneralInfo
    Product -->|HAS_HARDWARE| HardwareSpec
    Product -->|HAS_SOFTWARE| SoftwareSpec
    Product -->|HAS_CAMERA| CameraSpec
    Product -->|HAS_DISPLAY| DisplaySpec
    Product -->|HAS_DISPLAY_FEATURE| DisplayFeature
```
