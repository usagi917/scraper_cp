from bs4 import BeautifulSoup, Comment  # type: ignore
import requests # type: ignore
from typing import Dict, Optional
import re
import chardet  # type: ignore
from selenium import webdriver  # type: ignore
from selenium.webdriver.chrome.service import Service  # type: ignore
from selenium.webdriver.chrome.options import Options  # type: ignore
import time
import os

class CompanyScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        
        # Chromeオプションの設定
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_argument('--disable-infobars')
        
        try:
            from webdriver_manager.chrome import ChromeDriverManager # type: ignore
            from selenium.webdriver.chrome.service import Service # type: ignore
            # ChromeDriverの自動インストール
            self.chrome_driver_path = ChromeDriverManager().install()
        except Exception as e:
            print(f"ChromeDriverManager error: {e}")
            # 環境変数からのフォールバック
            self.chrome_driver_path = os.getenv('CHROME_DRIVER_PATH', '/usr/local/bin/chromedriver')

        # スクレイピング済みURLを追跡
        self.scraped_urls = set()
        
        # 関連ページのキーワード
        self.relevant_keywords = [
            '会社概要', '企業情報', 'about', 'company',
            '採用情報', 'recruit', 'careers',
            'お問い合わせ', 'contact',
            '事業内容', 'business'
        ]

    def validate_url(self, url: str) -> bool:
        """URLの妥当性をチェック"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(url))

    def get_dynamic_content(self, url: str) -> str:
        """Seleniumを使用して動的コンテンツを取得"""
        service = Service(self.chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=self.chrome_options)
        
        try:
            driver.get(url)
            # ページの読み込みを待機
            time.sleep(3)  # 必要に応じて調整
            return driver.page_source
        finally:
            driver.quit()

    def scrape(self, url: str) -> Dict[str, Optional[str]]:
        """指定されたURLから企業情報をスクレイピング（関連ページも含む）"""
        if not self.validate_url(url):
            raise ValueError("無効なURLです")

        try:
            base_url = self._get_base_url(url)
            self.scraped_urls = set()  # スクレイピング済みURLをリセット
            all_text = []
            
            # メインページと関連ページをスクレイピング
            main_content = self._scrape_single_page(url)
            all_text.extend(main_content['texts'])
            
            # 関連ページのURLを収集
            related_urls = self._find_related_pages(main_content['soup'], base_url)
            
            # 関連ページをスクレイピング（最大5ページまで）
            for related_url in list(related_urls)[:5]:
                if related_url not in self.scraped_urls:
                    related_content = self._scrape_single_page(related_url)
                    all_text.extend(related_content['texts'])
                    self.scraped_urls.add(related_url)

            # テキストを結合
            raw_text = ' '.join(all_text)

            # 基本情報の抽出（メインページと関連ページの情報を統合）
            company_info = {
                "company_name": self._extract_company_name(main_content['soup']),
                "business_description": self._extract_business_description(main_content['soup']),
                "address": self._extract_address(main_content['soup']),
                "representative": self._extract_representative(main_content['soup']),
                "tel": self._extract_tel(main_content['soup']),
                "business_hours": self._extract_business_hours(main_content['soup']),
                "raw_text": raw_text
            }

            # デバッグ情報の出力
            print(f"Main URL: {url}")
            print(f"Related URLs scraped: {list(self.scraped_urls)}")
            print("Total extracted text length:", len(raw_text))
            print("Extracted company info:", {k: v[:100] if v else None for k, v in company_info.items()})

            return self._clean_company_info(company_info)

        except Exception as e:
            print(f"Scraping error: {str(e)}")
            raise Exception(f"スクレイピングに失敗しました: {str(e)}")

    def _scrape_single_page(self, url: str) -> Dict:
        """単一ページのスクレイピング"""
        html_content = self.get_dynamic_content(url)
        soup = BeautifulSoup(html_content, 'html.parser')

        # 不要な要素を削除
        for element in soup.find_all(['script', 'style', 'meta', 'link', 'iframe', 'noscript']):
            element.decompose()

        # コメントを削除
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # テキストの抽出
        texts = []
        for tag in soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th', 'dd', 'dt']):
            text = tag.get_text(strip=True)
            if text and self._is_meaningful_text(text):
                normalized_text = self._normalize_text(text)
                if normalized_text:
                    texts.append(normalized_text)

        return {'soup': soup, 'texts': texts}

    def _get_base_url(self, url: str) -> str:
        """URLのベース部分を取得"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _find_related_pages(self, soup: BeautifulSoup, base_url: str) -> set:
        """関連ページのURLを収集"""
        related_urls = set()
        
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            link_text = a.get_text(strip=True).lower()
            
            # 関連ページかどうかをチェック
            is_relevant = any(keyword in link_text for keyword in self.relevant_keywords)
            
            if is_relevant and href:
                # 相対URLを絶対URLに変換
                if href.startswith('/'):
                    full_url = base_url + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                    
                # 同じドメインのURLのみを追加
                if base_url in full_url:
                    related_urls.add(full_url)
        
        return related_urls

    def _normalize_text(self, text: str) -> str:
        """テキストの正規化"""
        if not text:
            return ""
        
        # 空白文字の正規化
        text = ' '.join(text.split())
        
        # 全角スペースを半角に変換
        text = text.replace('\u3000', ' ')
        
        # 制御文字の除去（改行とタブは保持）
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        return text.strip()

    def _is_meaningful_text(self, text: str) -> bool:
        """意味のあるテキストかどうかを判定"""
        if not text or len(text.strip()) <= 1:
            return False
        
        # 少なくとも1つの日本語文字またはアルファベットを含むか確認
        has_meaningful_char = any(
            ord(c) > 127 or  # 日本語文字
            c.isalpha() or   # アルファベット
            c.isdigit()      # 数字
            for c in text
        )
        
        return has_meaningful_char

    def _clean_company_info(self, company_info: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
        """抽出した情報のクリーニング"""
        cleaned_info = {}
        for key, value in company_info.items():
            if value and isinstance(value, str):
                # テキストの正規化
                cleaned_value = self._normalize_text(value)
                # 空文字列の場合はNoneに
                cleaned_info[key] = cleaned_value if cleaned_value else None
            else:
                cleaned_info[key] = value
        return cleaned_info

    def _extract_company_name(self, soup: BeautifulSoup) -> Optional[str]:
        """会社名の抽出"""
        # メタデータから探す
        meta_title = soup.find('meta', property='og:site_name')
        if meta_title and meta_title.get('content'):
            return meta_title['content'].strip()

        # titleタグから探す
        if soup.title:
            title = soup.title.string
            if title:
                # 「株式会社」などの文字列を含む部分を抽出
                company_patterns = [
                    r'株式会社[^\s|｜|\-]*[\w\s]*',
                    r'[\w\s]*株式会社',
                    r'(有限会社|合同会社|合資会社)[^\s|｜|\-]*[\w\s]*',
                ]
                for pattern in company_patterns:
                    match = re.search(pattern, title)
                    if match:
                        return match.group().strip()

        # h1タグから探す
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)

        # 会社名を含むと思われる要素を探す
        company_keywords = ['会社名', '社名', '企業名']
        for keyword in company_keywords:
            result = self._find_in_table(soup, [keyword])
            if result:
                return result

        return None

    def _extract_business_description(self, soup: BeautifulSoup) -> Optional[str]:
        """事業内容の抽出"""
        keywords = ['事業内容', '事業概要', '企業概要', '会社概要']
        
        # テーブルから探す
        description = self._find_in_table(soup, keywords)
        if description:
            return description

        # 特定のクラス名を持つ要素から探す
        for keyword in keywords:
            element = soup.find(string=re.compile(keyword))
            if element:
                parent = element.parent
                # 親要素から次の段落やリストを探す
                next_sibling = parent.find_next_sibling(['p', 'div', 'ul'])
                if next_sibling:
                    return next_sibling.text.strip()
        
        return None

    def _extract_address(self, soup: BeautifulSoup) -> Optional[str]:
        """所在地の抽出"""
        keywords = ['所在地', '住所', '本社所在地', '会社所在地']
        
        # テーブルから探す
        address = self._find_in_table(soup, keywords)
        if address:
            return address

        # 特定のパターンの住所を探す（郵便番号から始まるなど）
        postal_pattern = re.compile(r'〒?\d{3}[-−]\d{4}.*?(?=\n|$)')
        for text in soup.stripped_strings:
            match = postal_pattern.search(text)
            if match:
                return match.group()

        return None

    def _extract_representative(self, soup: BeautifulSoup) -> Optional[str]:
        """代表者名の抽出"""
        return self._find_in_table(soup, ['代表者', '代表取締役'])

    def _extract_tel(self, soup: BeautifulSoup) -> Optional[str]:
        """電話番号の抽出"""
        tel = self._find_in_table(soup, ['電話', 'TEL', 'Tel'])
        if not tel:
            # 電話番号のパターンを探す
            pattern = re.compile(r'\d{2,4}[-−]\d{2,4}[-−]\d{4}')
            for text in soup.stripped_strings:
                match = pattern.search(text)
                if match:
                    return match.group()
        return tel

    def _extract_business_hours(self, soup: BeautifulSoup) -> Optional[str]:
        """営業時間の抽出"""
        return self._find_in_table(soup, ['営業時間', '業務時間'])

    def _find_in_table(self, soup: BeautifulSoup, keywords: list[str]) -> Optional[str]:
        """テーブルから特定のキーワードに関連する情報を探す"""
        for keyword in keywords:
            # 大文字小文字を区別せず、部分一致で検索するための正規表現
            pattern = re.compile(keyword, re.IGNORECASE)
            
            # テーブル内を探索
            for table in soup.find_all('table'):
                # th/tdの組み合わせを探す
                for th in table.find_all('th'):
                    if pattern.search(th.get_text(strip=True)):
                        td = th.find_next('td')
                        if td:
                            return td.get_text(strip=True)

            # dt/ddの組み合わせを探す
            for dt in soup.find_all('dt'):
                if pattern.search(dt.get_text(strip=True)):
                    dd = dt.find_next('dd')
                    if dd:
                        return dd.get_text(strip=True)

            # divやpタグ内のテキストを探す
            for element in soup.find_all(['div', 'p', 'span']):
                text = element.get_text(strip=True)
                if pattern.search(text):
                    # キーワードを含む要素の次の要素を探す
                    next_element = element.find_next(['div', 'p', 'span'])
                    if next_element:
                        return next_element.get_text(strip=True)

        return None
