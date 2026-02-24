import os
from pathlib import Path

def inject_katex(html_content):
    """HTMLにKaTeXの自動レンダリングスクリプトを注入する"""
    
    # すでにKaTeXが導入されている場合は何もしない
    if 'katex.min.js' in html_content:
        return html_content

    # KaTeXのCDNリンクと実行用スクリプト
    # インライン ($...$) も有効にする設定にしています
    katex_assets = """
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" 
            onload="renderMathInElement(document.body, {
                delimiters: [
                    {left: '$$', right: '$$', display: true},
                    {left: '$', right: '$', display: false}
                ],
                throwOnError: false
            });"></script>
    """

    # </head> の直前、もしくはファイルの先頭に挿入
    if '</head>' in html_content:
        return html_content.replace('</head>', f'{katex_assets}</head>')
    else:
        return katex_assets + html_content
    