osascript -e 'tell application "Terminal" to do script "cd '$(pwd)'/backend && uv run uvicorn app.main:app --reload"'
osascript -e 'tell application "Terminal" to do script "cd '$(pwd)'/frontend && bun dev"'
