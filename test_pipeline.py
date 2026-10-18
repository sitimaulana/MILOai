import asyncio
import traceback
from app.services.pipeline import MILOPipeline
from app.db.database import AsyncSessionLocal

async def main():
    try:
        from app.core.asr import whisper_asr
        whisper_asr.load()
        p = MILOPipeline(AsyncSessionLocal())
        with open('test.ogg', 'rb') as f:
            audio_bytes = f.read()
        res = await p.process_voice('test1', audio_bytes, 'test.ogg', '', 'B1', True)
        print("Success:", res)
    except Exception as e:
        traceback.print_exc()

asyncio.run(main())
