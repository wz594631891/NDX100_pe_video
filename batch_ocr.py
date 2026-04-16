"""
批量OCR识别脚本 - 使用AI视觉能力识别图片中的数据
"""
import sqlite3
import os
import base64
from pathlib import Path

# 数据库路径
DB_PATH = "cropped_frames.db"
IMAGES_DIR = "cropped_frames"

def get_unprocessed_files():
    """获取所有未处理的图片文件"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT filename FROM ocr_results')
    processed = set(row[0] for row in cursor.fetchall())
    conn.close()
    
    all_files = sorted([f for f in os.listdir(IMAGES_DIR) if f.endswith('.jpg')])
    unprocessed = [f for f in all_files if f not in processed]
    return unprocessed

def image_to_base64(image_path):
    """将图片转换为base64编码"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def insert_result(filename, raw_text, date=None, pe_ttm=None, std_plus=None, avg=None, std_minus=None, close_price=None):
    """插入识别结果到数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO ocr_results (filename, raw_text, date, pe_ttm, std_plus, avg, std_minus, close_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (filename, raw_text, date, pe_ttm, std_plus, avg, std_minus, close_price))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"  [WARNING] {filename} 已存在，跳过")
        return False
    finally:
        conn.close()

def main():
    unprocessed = get_unprocessed_files()
    print(f"未处理图片数量: {len(unprocessed)}")
    print()
    
    # 生成待识别的图片列表，供外部AI处理
    results = []
    for filename in unprocessed:
        image_path = os.path.join(IMAGES_DIR, filename)
        base64_image = image_to_base64(image_path)
        results.append({
            'filename': filename,
            'base64': base64_image
        })
    
    return results

if __name__ == "__main__":
    files = main()
    print(f"请处理 {len(files)} 张图片")
