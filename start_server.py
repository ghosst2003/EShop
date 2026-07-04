#!/usr/bin/env python3
"""启动后端服务"""
import os
import sys
import uvicorn

# 确保 backend 目录在 Python 路径中
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
