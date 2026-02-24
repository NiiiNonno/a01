import os
import zipfile
import base64
import re
import shutil
from pathlib import Path
from urllib.parse import unquote

# extract hypertext file from zip file exported by notion, embed image file with base64, reduce width restriction and set padding instead.

# --- 設定 ---
TARGET_EXTENSIONS = {'.html', '.png', '.jpg', '.jpeg', '.gif', '.svg'}
CSS_OLD_PATTERN = r'@media only screen \{\s+body \{\s+margin: 2em auto;\s+max-width: 900px;'
CSS_NEW_TEXT = '''
            @media only screen {
                body {
                    padding: 25px; /* AUTO REPLACED */
'''

def extract_zip_recursive(zip_path, extract_to):
    """ZIPファイルを再帰的に展開する"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    
    # 展開されたファイルの中にさらにZIPがあれば展開
    for root, dirs, files in os.walk(extract_to):
        for file in files:
            if file.lower().endswith('.zip'):
                full_path = os.path.join(root, file)
                nested_extract_to = os.path.join(root, file.replace('.zip', '_extracted'))
                extract_zip_recursive(full_path, nested_extract_to)
                os.remove(full_path) # 中のZIPは削除

def process_html(html_path, folder_path):
    """HTML内の画像をBase64化し、CSSを置換する"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. CSSの置換
    content = re.sub(CSS_OLD_PATTERN, CSS_NEW_TEXT, content, flags=re.MULTILINE)

    # 2. 画像のBase64埋め込み & <a>タグ削除
    # パターン: <a ...><img ... src="image.png"></a>
    def embed_base64(match):
        img_tag = match.group(0)
        # src属性を抽出
        src_match = re.search(r'src=["\'](.*?)["\']', img_tag)
        if not src_match:
            return img_tag
        
        # URLエンコードされた文字列をデコードする (例: image%201.png -> image 1.png)
        img_filename = unquote(src_match.group(1))
        img_path = Path(folder_path) / img_filename
        
        if img_path.exists():
            ext = img_path.suffix.lower().replace('.', '')
            with open(img_path, "rb") as i:
                b64_str = base64.b64encode(i.read()).decode('utf-8')
            
            # imgタグのみを再構築 (<a>を消すためにimg部分だけ返す)
            # 既存のstyleなどは保持する設計
            new_img = re.sub(r'src=["\'](.*?)["\']', f'src="data:image/{ext};base64,{b64_str}"', img_tag)
            # 外側の<a>を取り除くための正規表現置換
            new_img = re.sub(r'^<a[^>]*>(.*)</a>$', r'\1', new_img, flags=re.DOTALL)
            return new_img
        return img_tag

    # <a><img src="..."></a> のパターンにマッチさせる
    content = re.sub(r'<a\s+[^>]*>(<img\s+[^>]*src=["\'][^>]*["\'][^>]*>)</a>', embed_base64, content)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main(*args):
    current_dir = args[0] if 1 <= len(args) and args[0] else Path('.')
    temp_dir = current_dir / "temp_work"
    if not temp_dir.exists(): temp_dir.mkdir()

    zip_files = list(current_dir.glob('*.zip'))
    
    for zip_file in zip_files:
        print(f"Processing: {zip_file}")
        work_path = temp_dir / zip_file.stem
        extract_zip_recursive(zip_file, work_path)

        # ファイルチェックと処理
        for root, dirs, files in os.walk(work_path):
            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix.lower()

                if ext not in TARGET_EXTENSIONS:
                    print(f"⚠️ 警告: 予期しないファイルがあります: {file_path}")
                    continue
                
                if ext == '.html':
                    process_html(file_path, root)
                    # 最終的なHTMLをカレントディレクトリへ移動
                    final_name = file #f"{zip_file.stem}_{file}"
                    shutil.move(str(file_path), str(current_dir / final_name))

        # 元のZIPを削除（必要に応じてコメントアウトしてください）
        os.remove(zip_file)

    # 作業用ディレクトリの削除
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    print("完了しました。")

if __name__ == "__main__":
    main()