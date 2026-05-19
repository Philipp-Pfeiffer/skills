---
name: minimax-cli
description: MiniMax AI CLI (mmx) for text, image, video, music, speech, and vision generation. Use when Philipp asks to generate images, videos, music, or TTS directly via the command line. Also use for quota checks, auth management, or any MiniMax platform operations that should bypass OpenClaw's TTS streaming limitations. Installed at /home/p-pfeiffer/.mmx/ — API key already configured.
---

# minimax-cli Skill

Wrapper for the `mmx` CLI tool. Provides direct access to MiniMax's API without OpenClaw's routing layer.

## Prerequisites
- CLI installed: `npm install -g mmx-cli`
- Auth configured: Key stored at `~/.mmx/config.json`
- Usage tracked under Philipp's MiniMax Token Plan

## Core Commands

### Text / Chat
```bash
mmx text chat --message "Hello" --model MiniMax-M2.7-highspeed --stream
mmx text chat --system "You are a helpful assistant" --message "Write a Python script"
mmx text chat --messages-file - --output json  # pipe JSON messages
```

### Image Generation
```bash
mmx image "A futuristic city at sunset" --aspect-ratio 16:9
mmx image generate --prompt "Logo design" --n 3 --out-dir ./out/
```

### Video Generation
```bash
mmx video generate --prompt "Ocean waves at sunset" --async
mmx video generate --prompt "A robot painting" --download robot.mp4
mmx video task get --task-id <id>
mmx video download --file-id <id> --out video.mp4
```

### Music Generation
```bash
mmx music generate --prompt "Upbeat pop" --lyrics "[verse] La da dee"
mmx music generate --prompt "Indie folk" --lyrics-optimizer --out song.mp3
mmx music generate --prompt "Cinematic orchestral" --instrumental --out bgm.mp3
mmx music cover --audio-file original.mp3 --prompt "Jazz piano" --out cover.mp3
```

### Speech / TTS
```bash
mmx speech synthesize --text "Hello!" --out hello.mp3
mmx speech synthesize --text "Stream test" --stream | mpv -
mmx speech synthesize --text "Breaking news" --voice English_magnetic_voiced_man --speed 1.2 --out news.mp3
mmx speech voices  # list all available voices
```

### Vision
```bash
mmx vision photo.jpg
mmx vision describe --image https://example.com/img.jpg --prompt "What do you see?"
```

### Search
```bash
mmx search "MiniMax AI latest news"
mmx search query --q "query" --output json
```

## Utility Commands
```bash
mmx auth status         # check auth state
mmx auth login         # re-authenticate
mmx quota              # show current quota usage
mmx config show        # show config
mmx config set --key region --value cn  # switch region (global/cn)
mmx update            # update CLI
```

## Workflows

### Image → Send to Philipp
1. Generate: `mmx image "prompt" --aspect-ratio 1:1`
2. Output lands in current dir or `--out-dir`
3. Send via message tool: `message(action=send, filePath="path", channel="whatsapp")`
4. Reply with NO_REPLY after message send

### TTS → Play Audio
```bash
mmx speech synthesize --text "Text to speak" --stream | mpv -
```
Note: Streaming TTS bypasses OpenClaw's buffering issue.

### Video → Async Workflow
1. Start: `mmx video generate --prompt "..." --async`
2. Poll status: `mmx video task get --task-id <id>`
3. Download when ready: `mmx video download --file-id <id> --out video.mp4`

## Output Paths
Default output directory: `~/.mmx/output/` for images/videos/songs when `--out` not specified.

## Quota Notes
- Text: Philipp's main pool (shared with OpenClaw)
- speech-hd: here probably token plan quota (seperate from quota for turbo)
- image-01: limited per 5h
- music-2.6: limited per 5h
- Video: usage-based

Current quota check: `mmx quota`

## Troubleshooting
- "No API key found" → run `mmx auth login --api-key <key>`
- Slow generation → try `--model MiniMax-M2.7-highspeed`
- Region issues → `mmx config set --key region --value cn` for CN API
