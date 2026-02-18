#!/usr/bin/env python3
import os
import re
import subprocess

def extract_book_info(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    title = re.search(r'\\def\\entitle\{([^}]+)\}', content).group(1)
    level = re.search(r'\\def\\level\{([^}]+)\}', content).group(1)
    category = re.search(r'^%(\w+)', content, re.MULTILINE).group(1)
    
    # Clean LaTeX formatting
    title = title.replace('~', ' ').replace('\\&', '&')
    level = level.replace('ky\\=u', 'k').replace('\\=u', '').replace(' dan', 'd').replace(' k', 'k')
    
    return {
        'filename': os.path.basename(filepath).replace('.tex', ''),
        'title': title,
        'level': level,
        'category': category
    }

def level_sort_key(book):
    level = book['level']
    if 'k' in level:
        return 100 - int(re.search(r'(\d+)', level).group(1))
    elif 'd' in level:
        return 100 + int(re.search(r'(\d+)', level).group(1))
    return 999

def generate_index():
    books = {'tesuji': [], 'tsumego': [], 'endgame': []}
    
    for filename in os.listdir('books'):
        if filename.endswith('.tex') and filename != 'header.tex':
            book_info = extract_book_info(os.path.join('books', filename))
            books[book_info['category']].append(book_info)
    
    for category in books:
        books[category].sort(key=level_sort_key)
    
    with open('index.html', 'r', encoding='utf-8') as f:
        original = f.read()
    
    total_books = sum(len(books[cat]) for cat in books)
    html_parts = original.split('<p>Tesuji:</p>')[0].rstrip() + '\n'
    
    for category in ['tesuji', 'tsumego', 'endgame']:
        html_parts += f'    <p>{category.title()}:</p>\n    <ul>\n'
        
        processed = set()
        for book in books[category]:
            if book['filename'] in processed:
                continue
            
            base_title = re.sub(r', Part \d+$', '', book['title'])
            parts = [b for b in books[category] if b['title'].startswith(base_title)]
            parts.sort(key=lambda x: x['filename'])
            
            if book['filename'] != parts[0]['filename']:
                continue
            
            for p in parts:
                processed.add(p['filename'])
            
            if len(parts) > 1:
                html_parts += f'      <li>\n        ({parts[0]["level"]}) {base_title}:\n        '
                links = []
                for p in parts:
                    part_num = re.search(r'Part (\d+)', p['title'])
                    num = part_num.group(1) if part_num else '?'
                    links.append(f'<a href="pdfs/{p["filename"]}.pdf">{num}</a>')
                html_parts += ',\n        '.join(links) + '\n      </li>\n'
            else:
                html_parts += f'      <li>({book["level"]}) <a href="pdfs/{book["filename"]}.pdf">{book["title"]}</a></li>\n'
        
        html_parts += '    </ul>\n'
    
    # Get commit date and problem count
    commit_date = subprocess.run(['git', 'log', '-1', '--format=%cd', '--date=format:%B %Y'], 
                                capture_output=True, text=True).stdout.strip()
    
    with open('problem-count.log', 'r') as f:
        problem_count = f"{int(f.read().strip()):,}".replace(',', "'")
    
    html_parts += f'    <p>Last updated <a href="https://github.com/101books/101books.github.io/commits/main/">{commit_date}</a></p>\n  </body>\n</html>\n'
    html_parts = re.sub(r'selection of \d+ go/weiqi/baduk booklets, featuring a total of [\d\']+ problems', 
                       f'selection of {total_books} go/weiqi/baduk booklets, featuring a total of {problem_count} problems', 
                       html_parts)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_parts)
    
    print(f"Generated index.html with {total_books} books")

if __name__ == '__main__':
    generate_index()
