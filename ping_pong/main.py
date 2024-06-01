from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import requests
import asyncio
import logging
from logging.handlers import RotatingFileHandler
import os

app = FastAPI()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s",
    handlers=[
        RotatingFileHandler("logs/app.log", maxBytes=100000, backupCount=5),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Dictionary to manage the game state
game_state = {"game_running": False, "pong_time_ms": 0, "instance_id": None}

# Configurable through environment variables
OTHER_INSTANCE_URL = f"http://localhost:{8002 if game_state['instance_id'] == 1 else 8001}/ping"

@app.on_event("startup")
def set_instance_id():
    import sys
    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else "8001"
    game_state["instance_id"] = int(port) - 8000  # Instance ID derived from port


@app.post("/ping")
async def ping_handler(background_tasks: BackgroundTasks):
    if game_state["game_running"]:
        background_tasks.add_task(send_pong, game_state["pong_time_ms"])
        logger.info(
            "Ping received, sending pong after %d ms", game_state["pong_time_ms"]
        )
    else:
        logger.info("Ping received but game is not running")
    return JSONResponse(
        content={"message": "pong", "game_state": game_state}, status_code=200
    )


async def send_pong(wait_time_ms):
    try:
        await asyncio.sleep(wait_time_ms / 1000)
        response = requests.post(
            OTHER_INSTANCE_URL + "/ping"
        )  # Send ping to the other instance
        logger.info("Pong sent after %d ms, response: %s", wait_time_ms, response.text)
    except Exception as e:
        logger.error("Error sending pong: %s", str(e))


@app.get("/start/{pong_time}")
async def start_game(pong_time: int):
    if pong_time <= 0:
        logger.error("Invalid pong_time: %d", pong_time)
        raise HTTPException(status_code=400, detail="pong_time must be greater than 0")

    game_state["game_running"] = True
    game_state["pong_time_ms"] = pong_time

    if game_state["instance_id"] == 1:
        try:
            requests.post(
                OTHER_INSTANCE_URL + "/ping"
            )  # Initial ping to start the game
            logger.info(
                "Game started with pong_time_ms: %d", game_state["pong_time_ms"]
            )
        except Exception as e:
            logger.error("Error starting game: %s", str(e))
            raise HTTPException(status_code=500, detail="Failed to start game")

    return JSONResponse(
        content={"message": "Game started", "game_state": game_state}, status_code=200
    )


@app.get("/pause")
async def pause_game():
    game_state["game_running"] = False
    logger.info("Game paused")
    return JSONResponse(
        content={"message": "Game paused", "game_state": game_state}, status_code=200
    )


@app.get("/resume")
async def resume_game():
    game_state["game_running"] = True
    logger.info("Game resumed")
    return JSONResponse(
        content={"message": "Game resumed", "game_state": game_state}, status_code=200
    )


@app.get("/stop")
async def stop_game():
    game_state["game_running"] = False
    logger.info("Game stopped")
    return JSONResponse(
        content={"message": "Game stopped", "game_state": game_state}, status_code=200
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0")
