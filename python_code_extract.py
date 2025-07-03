import os
import pathlib

# تنظیم مسیر جاری
current_dir = pathlib.Path.cwd()
output_file = current_dir / "python_files_content2.txt"

# باز کردن فایل خروجی برای نوشتن
with open(output_file, "w", encoding="utf-8") as outfile:
    # پیمایش تمام فایل‌های .py در مسیر جاری و زیرپوشه‌ها
    for py_file in current_dir.glob("**/*.py"):
        # محاسبه مسیر نسبی
        relative_path = py_file.relative_to(current_dir)
        
        # نوشتن هدر فایل
        outfile.write(f"\n{'=' * 50}\n")
        outfile.write(f"File: {relative_path}\n")
        outfile.write(f"{'=' * 50}\n\n")
        
        # خواندن و نوشتن محتوای فایل
        try:
            with open(py_file, "r", encoding="utf-8") as infile:
                outfile.write(infile.read())
                outfile.write("\n\n")  # فاصله بین فایل‌ها
        except Exception as e:
            outfile.write(f"Error reading file: {e}\n\n")

print(f"تمامی فایل‌های .py در فایل {output_file} ذخیره شدند.")