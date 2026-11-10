Intents are routed from natural language to the right workflow automatically. No slash commands needed.

| User says | Interpret as | Action |
|-----------|-------------|--------|
| "Add this book: /path/to/book.pdf" | ingest | Extract PDF (web_extract/pymupdf/marker-pdf) → create wiki structure |
| "What's this book about?" | query + overview | Read wiki/overview.md, synthesize |
| "Explain chapter 3" | query + chapter | Read chapter pages, write guided tour |
| "What did we discuss last time?" | query + memory | Read log.md, recall context |
| "Help me study this chapter" | learn | Read chapter → create study guide + quiz |
| "Summarize [topic]" | query + concept | Search wiki, read related pages, synthesize |
| "Make this easier to read" | query + transform | Apply dyslexia formatting |
| "Check if everything is connected" | lint | Delegate to llm-wiki for orphan/broken-links scan |
| "Test me on [chapter]" | quiz | Read quiz.md, ask questions interactively |
| "Connect [concept A] and [concept B]" | query + synthesize | Read both concept pages, find relationships |
| "Check my progress" | query + progress | Read log.md, summarize |
