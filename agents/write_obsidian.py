from pathlib import Path

def write_markdown_file(content, out_dir, filename):
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)  # если директория не существует — создать
    file_path = out_path / filename
    file_path.write_text(content, encoding='utf-8')
    print(f"✅ Markdown saved to: {file_path}")
