```markdown
# Company Information Scraper

## 概要
企業のWebサイトから情報を自動的に収集し、AIを活用して分析するWebアプリケーションです。

## 主な機能
- 企業WebサイトのURLからの情報自動収集
- Google Gemini AIを使用した企業情報の分析
- 以下の情報を抽出・分析：
  - 基本情報（会社名、事業内容、所在地、代表者名、電話番号、営業時間）
  - AI分析（企業の特徴要約、投資家向け分析、就職活動者向け情報）

## 技術スタック

### バックエンド
- Python 3.11.5
- FastAPI
- BeautifulSoup4
- Selenium
- Google Generative AI (Gemini)

### フロントエンド
- Next.js
- TypeScript

## セットアップ

### 必要条件
- Python 3.11.5
- Node.js
- Chrome（Seleniumのスクレイピングに使用）

### バックエンド設定

1. **環境構築**

    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate # Windowsの場合: venv\Scripts\activate
    pip install -r requirements.txt
    ```

2. **環境変数の設定**

    `backend/.env` ファイルを作成し、以下を追加します：

    ```env
    GOOGLE_API_KEY=your_google_api_key
    ```

3. **サーバー起動**

    ```bash
    python run.py
    ```

### フロントエンド設定

1. **依存関係のインストール**

    ```bash
    cd frontend
    npm install
    ```

2. **開発サーバー起動**

    ```bash
    npm run dev
    ```

## 使用方法

1. フロントエンドの開発サーバーを起動します。
2. バックエンドサーバーを同時に起動してください。
3. アプリケーションのインターフェースから企業WebサイトのURLを入力し、「送信」をクリックします。
4. AIが情報を分析し、結果を画面に表示します。

### APIリクエストの例

バックエンドに直接リクエストを送信する場合：

```json
{
  "url": "https://example.com"
}
```

**レスポンス例：**

```json
{
  "company_name": "Example Corp",
  "business_description": "A global leader in innovative solutions.",
  "location": "123 Example Street, City, Country",
  "ceo_name": "John Doe",
  "phone_number": "+1234567890",
  "business_hours": "9:00 AM - 5:00 PM",
  "ai_analysis": {
    "summary": "The company specializes in cutting-edge technology and has a strong global presence.",
    "investor_info": "High potential for investment due to consistent growth.",
    "job_seeker_info": "A great workplace for innovation-driven individuals."
  }
}
```

## ライセンス
このプロジェクトはMITライセンスのもとで提供されています。詳細は[LICENSE](LICENSE)ファイルをご確認ください。


