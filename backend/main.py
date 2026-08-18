from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/")
async def check():
    return {"Hello":"World"}

