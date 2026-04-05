#!/usr/bin/env bash
# Regenerate docs/assets/audio/peon/*.mp3 — macOS "Bad News" TTS + ffmpeg (gruffer pitch/EQ).
# Requires: say, ffmpeg. Run from repo root: ./scripts/regenerate-peon-audio.sh

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/docs/assets/audio/peon"
mkdir -p "$OUT"
TMP="$OUT/.tmp-aiff"
mkdir -p "$TMP"
trap 'rm -rf "$TMP"' EXIT

cd "$TMP"
say -v "Bad News" -r 218 -o line01.aiff "Work work!"
say -v "Bad News" -r 212 -o line02.aiff "Something need doing?"
say -v "Bad News" -r 215 -o line03.aiff "Okie dokie!"
say -v "Bad News" -r 220 -o line04.aiff "Zug zug!"
say -v "Bad News" -r 210 -o line05.aiff "Be happy to!"
say -v "Bad News" -r 214 -o line06.aiff "Why not me?"
say -v "Bad News" -r 216 -o line07.aiff "Ready to work!"
say -v "Bad News" -r 212 -o line08.aiff "More work?"

AF="asetrate=44100*0.74,atempo=1/0.74,highpass=f=110,lowpass=f=3400,acompressor=threshold=0.125:ratio=2.5:attack=5:release=120:makeup=2,alimiter=limit=0.97"
for i in 01 02 03 04 05 06 07 08; do
  ffmpeg -y -i "line${i}.aiff" -af "$AF" -codec:a libmp3lame -qscale:a 4 "$OUT/peon-${i}.mp3" -loglevel error
done
echo "Wrote $OUT/peon-01.mp3 … peon-08.mp3"
