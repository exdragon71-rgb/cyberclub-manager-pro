from fastapi import FastAPI

app = FastAPI(
    title="CyberClub Manager Pro API",
    description="Backend API for CyberClub Manager Pro",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "app": "CyberClub Manager Pro",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }