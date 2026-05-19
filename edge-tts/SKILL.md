# edge-tts

## Beschreibung
Text-to-Speech via Microsoft Edge (kostenlos, kein API-Key nötig).

## Voraussetzungen
- Python mit `edge_tts`: `/home/linuxbrew/.linuxbrew/bin/python3`
- `pip install edge-tts` (linuxbrew)

## Verfügbare deutsche Stimmen
| Voice | Gender | Type |
|---|---|---|
| `de-DE-KatjaNeural` | Female | Neural |
| `de-DE-AmalaNeural` | Female | Neural |
| `de-DE-KillianNeural` | Male | Neural |
| `de-DE-ConradNeural` | Male | Neural |
| `de-DE-FlorianMultilingualNeural` | Male | Multilingual |
| `de-DE-SeraphinaMultilingualNeural` | Female | Multilingual |

## Benchmark (assistomat)
| Voice | Zeit | Bytes |
|---|---|---|
| de-DE-KatjaNeural (♀) | ~0.8s | ~35KB |
| de-DE-KillianNeural (♂) | ~1.0s | ~32KB |
| de-DE-ConradNeural (♂) | ~1.3s | ~32KB |
| de-DE-FlorianMultilingualNeural (♂) | ~2.7s | ~29KB |

## Nutzung
```bash
/home/linuxbrew/.linuxbrew/bin/python3 scripts/edge_tts.py "Text" -v de-DE-KatjaNeural -o output.mp3

# Speed/Pitch/Volume
edge_tts.py "Text" -v de-DE-KatjaNeural -r +10% -p -5Hz -o output.mp3
```

## Hinweis
Nutzungsbedingungen von Microsoft beachten — für private/Entwicklungszwecke.
