from fastapi import FastAPI, HTTPException # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from pydantic import BaseModel, HttpUrl # type: ignore
from typing import Optional, Dict
from .scraper import CompanyScraper
from .llm_processor import LLMProcessor
import traceback  # 追加

app = FastAPI(
    title="Company Scraper API",
    description="企業Webサイトから情報を抽出するAPI",
    version="1.0.0"
)

# CORS設定を修正
origins = [
    "http://localhost:3000",  # Next.jsの開発サーバー
    "http://127.0.0.1:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# リクエストモデル
class ScrapeRequest(BaseModel):
    url: str

# レスポンスモデル
class ScrapeResponse(BaseModel):
    message: str = "Success"
    company_name: Optional[str] = None
    business_description: Optional[str] = None
    address: Optional[str] = None
    representative: Optional[str] = None
    tel: Optional[str] = None
    business_hours: Optional[str] = None
    access: Optional[str] = None
    raw_text: Optional[str] = None
    llm_analysis: Optional[dict] = None

@app.post("/api/scrape")
async def scrape_company(request: ScrapeRequest):
    try:
        # スクレイパーのインスタンス化
        scraper = CompanyScraper()
        
        # スクレイピングの実行
        scraped_data = scraper.scrape(request.url)
        
        # LLMプロセッサーのインスタンス化
        llm_processor = LLMProcessor()
        
        try:
            # LLMでの分析
            result = await llm_processor.process_company_info(scraped_data)
            
            # エラーチェック
            if "error" in result:
                return result

            # レスポンスの構築
            return {
                "message": "Success",
                "basic_info": result["basic_info"],
                "analysis": result["analysis"]
            }

        except Exception as llm_error:
            print(f"LLM Error: {str(llm_error)}")
            print(f"LLM Error Traceback: {traceback.format_exc()}")
            return {
                "message": "Error",
                "error": f"LLM処理中にエラーが発生しました: {str(llm_error)}",
                "basic_info": {
                    "company_name": "取得できませんでした",
                    "business_description": "取得できませんでした",
                    "address": "取得できませんでした",
                    "representative": "取得できませんでした",
                    "tel": "取得できませんでした",
                    "business_hours": "取得できませんでした",
                    "raw_text": scraped_data.get("raw_text", "")
                },
                "analysis": {
                    "summary": "分析できませんでした",
                    "investor_analysis": "分析できませんでした",
                    "job_seeker_info": "分析できませんでした"
                }
            }

    except ValueError as e:
        error_detail = str(e)
        print(f"Validation Error: {error_detail}")
        print(f"Validation Error Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=error_detail)
    except Exception as e:
        error_detail = str(e)
        print(f"Server Error: {error_detail}")
        print(f"Error Traceback: {traceback.format_exc()}")
        return {
            "message": "Error",
            "error": f"処理に失敗しました: {error_detail}",
            "basic_info": {
                "company_name": "取得できませんでした",
                "business_description": "取得できませんでした",
                "address": "取得できませんでした",
                "representative": "取得できませんでした",
                "tel": "取得できませんでした",
                "business_hours": "取得できませんでした",
                "raw_text": ""
            },
            "analysis": {
                "summary": "分析できませんでした",
                "investor_analysis": "分析できませんでした",
                "job_seeker_info": "分析できませんでした"
            }
        }

@app.get("/api/health")
async def health_check():
    """
    ヘルスチェックエンドポイント
    """
    return {"status": "healthy"}
