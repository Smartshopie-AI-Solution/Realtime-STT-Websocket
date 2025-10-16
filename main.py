from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Optional

from scripts.config import Config
from scripts.process import AudioProcessor
from scripts.exception_handling import ProjectException

import numpy as np
import asyncio
import warnings
import time
import sys

warnings.filterwarnings("ignore")

app = FastAPI(title="Real-time Speech Transcription")
templates = Jinja2Templates(directory="templates")
config = Config()

class WebSocketManager:
    def __init__(self):
        self.processor = AudioProcessor()
        self.audio_queue = asyncio.Queue()
        self.is_processing = False
        self.processing_task: Optional[asyncio.Task] = None
        self.current_websocket: Optional[WebSocket] = None
        self.stopping = False
        self.shutdown_event = asyncio.Event()

    async def start_processing(self, websocket: WebSocket):
        self.processor.complete_text = ""
        self.processor.current_partial = ""
        self.current_websocket = websocket
        self.is_processing = True
        self.shutdown_event.clear()
        self.processing_task = asyncio.create_task(self._process_audio(websocket))

    async def stop_processing(self):
        if not self.is_processing:
            return
            
        self.stopping = True
        self.shutdown_event.set()
        
        # Wait for final processing to complete
        try:
            if self.processing_task:
                await asyncio.wait_for(self.processing_task, timeout=3.0)
        except asyncio.TimeoutError:
            print("Processing task timeout during shutdown")
        except Exception as e:
            print(f"Error during shutdown: {e}")
        finally:
            self.is_processing = False
            self.current_websocket = None
            self.stopping = False
            if self.processing_task:
                if not self.processing_task.done():
                    self.processing_task.cancel()
                    try:
                        await self.processing_task
                    except asyncio.CancelledError:
                        pass
            # Clear any remaining items in the queue
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

    async def _process_audio(self, websocket: WebSocket):
        accumulated_chunks = []
        last_process_time = time.time()

        try:
            while self.is_processing:
                if self.shutdown_event.is_set() and accumulated_chunks:
                    # Process final chunks before shutting down
                    await self._process_chunks(accumulated_chunks, websocket)
                    break

                try:
                    audio_data = await asyncio.wait_for(
                        self.audio_queue.get(), 
                        timeout=0.1
                    )
                    accumulated_chunks.append(
                        np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                    )
                except asyncio.TimeoutError:
                    if self.stopping and accumulated_chunks:
                        await self._process_chunks(accumulated_chunks, websocket)
                        accumulated_chunks = []
                    continue

                current_time = time.time()
                if (current_time - last_process_time >= config.PROCESS_INTERVAL 
                    and accumulated_chunks):
                    await self._process_chunks(accumulated_chunks, websocket)
                    accumulated_chunks = []
                    last_process_time = current_time

        except Exception as e:
            print(f"Error in process_audio: {e}")
        finally:
            # Ensure we process any remaining chunks
            if accumulated_chunks:
                try:
                    await self._process_chunks(accumulated_chunks, websocket)
                except Exception as e:
                    print(f"Error processing final chunks: {e}")

    async def _process_chunks(self, chunks, websocket):
        if not chunks or not websocket or websocket != self.current_websocket:
            return

        try:
            combined_audio = np.concatenate(chunks)
            transcribed_text = self.processor.process_audio_chunk(combined_audio)
            
            if transcribed_text and not self.shutdown_event.is_set():
                # Check if WebSocket is still open before sending
                if websocket.client_state.name == "CONNECTED":
                    try:
                        await websocket.send_json({
                            "transcribed_text": transcribed_text,
                            "processor_type": config.MODEL_TYPE
                        })
                    except Exception as ws_error:
                        print(f"WebSocket send error: {ws_error}")
                        # Mark as stopping to prevent further attempts
                        self.stopping = True
                        self.shutdown_event.set()
        except Exception as e:
            print(f"Error in process_chunks: {e}")
            # Don't raise ProjectException to prevent system exit

ws_manager = WebSocketManager()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/audio-stream")
async def audio_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        await ws_manager.start_processing(websocket)
        
        while True:
            try:
                audio_data = await websocket.receive_bytes()
                if ws_manager.shutdown_event.is_set():
                    break
                await ws_manager.audio_queue.put(audio_data)
            except WebSocketDisconnect:
                print("WebSocket disconnected by client")
                break
            except Exception as e:
                print(f"Error receiving audio: {e}")
                break
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await ws_manager.stop_processing()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)