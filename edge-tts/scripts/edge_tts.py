#!/usr/bin/env python3
"""edge-tts wrapper for CLI usage."""
import argparse
import asyncio
import sys
import time
import os

# Use linuxbrew python
import edge_tts

def main():
    p = argparse.ArgumentParser(description="Microsoft Edge TTS")
    p.add_argument("text", help="Text to synthesize")
    p.add_argument("--voice", "-v", default="de-DE-KatjaNeural",
                   help="Voice ID (default: de-DE-KatjaNeural)")
    p.add_argument("--rate", "-r", default="+0%",
                   help="Speech rate adjustment (e.g. +10%, -20%)")
    p.add_argument("--pitch", "-p", default="+0Hz",
                   help="Pitch adjustment (e.g. +5Hz, -10Hz)")
    p.add_argument("--volume", default="+0%",
                   help="Volume adjustment (e.g. +10%, -20%)")
    p.add_argument("--output", "-o", help="Output file (MP3)")
    p.add_argument("--json", action="store_true", help="JSON timing output")
    args = p.parse_args()

    async def run():
        start = time.time()
        communicate = edge_tts.Communicate(
            args.text,
            args.voice,
            rate=args.rate,
            pitch=args.pitch,
            volume=args.volume
        )
        if args.output:
            await communicate.save(args.output)
            elapsed = time.time() - start
            size = os.path.getsize(args.output)
            if args.json:
                print(f'{{"elapsed": {elapsed:.3f}, "bytes": {size}}}')
            else:
                print(f"Saved: {args.output} ({size} bytes, {elapsed:.2f}s)")
        else:
            audio = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio += chunk["data"]
            sys.stdout.buffer.write(audio)
            if args.json:
                sys.stderr.write(f'{{"elapsed": {time.time()-start:.3f}, "bytes": {len(audio)}}}')

    asyncio.run(run())

if __name__ == "__main__":
    main()
