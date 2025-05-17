# Script này sẽ tự động tải các thư mục model cần thiết từ Google Drive về đúng vị trí cho project.
# Yêu cầu: pip install gdown
# Chạy: python download_models.py
import gdown
import shutil
import os

# Các link Google Drive folder (phải công khai)
models_url = "https://drive.google.com/drive/folders/1V4peAevvw_JYdvVRcCoPgyZ243axDb6g"
folder1_url = "https://drive.google.com/drive/folders/1hkE-2W11DA216dXn4Fr6bmdwwq9ilmZP"
folder2_url = "https://drive.google.com/drive/folders/1aUVAZsunZWmlKOLa_2iuOUxaHGVYCEAW"

# Tải folder 'models'
print("🔽 Bắt đầu tải folder 'models'...")
gdown.download_folder(models_url, quiet=False, use_cookies=False)

# Tạo thư mục đích nếu chưa có
target_dir = "t5_intent_response_model"
if not os.path.exists(target_dir):
    os.makedirs(target_dir)
    print(f"📁 Đã tạo thư mục '{target_dir}'")

# Tải thêm 2 thư mục cần ghép vào t5_intent_response_model
print("🔽 Tải thư mục phụ 1...")
gdown.download_folder(folder1_url, quiet=False, use_cookies=False)

print("🔽 Tải thư mục phụ 2...")
gdown.download_folder(folder2_url, quiet=False, use_cookies=False)

# Tên thư mục con (nếu tải về đúng tên)
folder1_name = "checkpoint-9000"
folder2_name = "checkpoint-8500"

# Di chuyển vào thư mục t5_intent_response_model
print("📂 Di chuyển thư mục con vào 't5_intent_response_model'...")

shutil.move(folder1_name, os.path.join(target_dir, folder1_name))
shutil.move(folder2_name, os.path.join(target_dir, folder2_name))

print("✅ Hoàn tất. Thư mục 't5_intent_response_model' và thư mục 'models' đã được bổ sung đầy đủ.")
