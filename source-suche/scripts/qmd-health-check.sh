#!/bin/bash
# QMD Health-Check für Source-Suche
# Verifiziert, dass die sources-Collection existiert und indexiert ist.

set -e

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"

echo "=== QMD Source Health-Check ==="

# 1. Collection existiert?
if ! qmd collection list 2>/dev/null | grep -q "sources"; then
    echo "❌ Collection 'sources' fehlt. Erstelle..."
    qmd collection add sources "$HOME/.openclaw/workspace/sources" --pattern "**/*.md"
    echo "✅ Collection 'sources' erstellt."
else
    echo "✅ Collection 'sources' vorhanden."
fi

# 2. Dateien gezählt?
FILE_COUNT=$(find "$HOME/.openclaw/workspace/sources" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "📄 Markdown files in sources/: $FILE_COUNT"

INDEXED_COUNT=$(qmd ls sources 2>/dev/null | wc -l | tr -d ' ')
echo "📄 Indexed entries in QMD: $INDEXED_COUNT"

if [ "$FILE_COUNT" -eq 0 ] && [ "$INDEXED_COUNT" -eq 0 ]; then
    echo "⚠️  Keine Dateien im Archiv und nichts indexiert. Force-update..."
    qmd update --collection sources --force
    qmd embed --collection sources
    FILE_COUNT=$(find "$HOME/.openclaw/workspace/sources" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    INDEXED_COUNT=$(qmd ls sources 2>/dev/null | wc -l | tr -d ' ')
    echo "📄 Nach Reindex: $FILE_COUNT files, $INDEXED_COUNT indexed"
fi

# 3. Test-Suche
TEST_RESULT=$(qmd search "test" --collection sources 2>/dev/null | head -5 || echo "")
if [ -z "$TEST_RESULT" ]; then
    echo "⚠️  Test-Suche lieferte keine Ergebnisse. Archiv ist möglicherweise leer."
else
    echo "✅ Test-Suche funktioniert."
fi

echo "=== Health-Check complete ==="
