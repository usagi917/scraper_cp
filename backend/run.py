import uvicorn # type: ignore

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # すべてのインターフェースでリッスン
        port=8000,
        reload=True      # 開発時の自動リロード
    ) 