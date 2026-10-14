#!/usr/bin/env bash
set -e

echo "🚀 Initialisiere lokales Git-Repository..."
git init
git branch -M main
git add .
git commit -m "Initial Setup: Autonomous AI Evolution Loop"

if command -v gh &> /dev/null; then
    echo "📦 Erstelle öffentliches GitHub-Repository 'ki-rpg-projekt' und lade alle Dateien hoch..."
    gh repo create ki-rpg-projekt --public --source=. --remote=origin --push
    echo ""
    echo "✅ Fertig! Dein Repository ist online."
    echo "🔑 Jetzt nur noch deinen Gemini API-Key hinterlegen mit:"
    echo "   gh secret set GEMINI_API_KEY"
else
    echo "⚠️ GitHub CLI (gh) nicht installiert."
    echo "Erstelle ein leeres Repository auf github.com und führe dann aus:"
    echo "   git remote add origin https://github.com/DEIN_USERNAME/ki-rpg-projekt.git"
    echo "   git push -u origin main"
fi
