import os
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app):
    allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "*")
    if allowed_origins_str == "*":
        allowed_origins = ["*"]
    else:
        allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]
        
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
