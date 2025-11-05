import uvicorn
import os

if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.getenv("PORT", 8000))

    uvicorn.run(
        "services.fapi:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
