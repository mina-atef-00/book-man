# book-man

Dyslexia-Friendly Study Companion for OpenCode.

## What is this?

book-man is an OpenCode plugin that helps people with dyslexia build and query personal knowledge wikis from academic books. It implements Karpathy's ["Obsidian RAG" Implementation](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

## Features

- **Obsidian RAG Implementation**: PDF → sources/ → wiki/ → Query/Enhance
- **MCPVault Integration**: Safe vault read/write/search via MCP
- **MinerU Integration**: PDF/EPUB to Markdown conversion
- **Dyslexia-Friendly Formatting**: Max 3-4 sentences per paragraph, clear headings
- **Custom Tools**: `/init`, `/process`, `/media` commands

## Installation

### Automatic Installation (Recommended)

Add to your `opencode.json`:

```json
{
  "plugin": ["book-man"]
}
```

Then edit `~/.config/opencode/opencode.json` to add the MCP configuration below.

### Manual Installation

Clone this repository, then copy to your plugin directory:

```bash
git clone https://github.com/mina-atef-00/book-man.git
cp -r book-man ~/.config/opencode/plugins/
```

## Configuration

Add to your `opencode.json`:

```json
{
  "mcp": {
    "obsidian": {
      "type": "local", 
      "command": ["npx", "@bitbonsai/mcpvault@latest", "/path/to/your/vault/"],
      "enabled": true
    }
  }
}
```

Set MinerU token:

```bash
# Option 1: Copy .env.example and add your token
cp .env.example .env
# Then edit .env and add your token from https://mineru.net/user-center/api-token

# Option 2: Set environment variable directly
export MINERU_TOKEN="your-token-from-mineru.net"
```

## Skills

The plugin auto-loads these skills:
- `obsidian-markdown` - Proper Obsidian markdown formatting
- `obsidian` - MCPVault behavior patterns
- `mineru` - PDF extraction workflow

## Usage

### /init [path]

Initialize a book from PDF/EPUB:

```bash
/init "/path/to/book.pdf"
```

### /process [target]

Process content for study:
- `/process chapter 3` - Generate summary, mindmap, quiz
- `/process section 3.2` - Section-level materials

### /media [target]

Generate media prompts:
- `/media chapter 3` - podcast, video, infographic, flashcards, slides

### Query

Simply ask questions naturally:
- "What's this book about?"
- "How should I study chapter 2?"

## Architecture

```
book-man/
├── AGENT.md              # Agent definition
├── .opencode/
│   └── plugins/
│       └── book-man.ts  # Plugin with custom tools
├── package.json
└── README.md
```

## Dependencies

- [MCPVault](https://github.com/bitbonsai/mcpvault) - Obsidian MCP
- [MinerU](https://github.com/opendatalab/mineru) - PDF converter
- [obsidian-markdown skill](https://skills.sh/kepano/obsidian-skills/obsidian-markdown)
- [mineru skill](https://skills.sh/nebutra/mineru-skill/mineru)