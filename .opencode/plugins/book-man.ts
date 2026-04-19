import type { Plugin, tool } from "@opencode-ai/plugin"

export const BookManPlugin: Plugin = async (ctx) => {
  return {
    tool: {
      "book-init": tool({
        description: "Initialize a new book from PDF/EPUB file",
        args: {
          path: tool.schema.string(),
        },
        async execute(args, context) {
          return `Initializing book from: ${args.path}`
        },
      }),

      "book-process": tool({
        description: "Process chapter/section for study",
        args: {
          target: tool.schema.string(),
        },
        async execute(args, context) {
          return `Processing: ${args.target}`
        },
      }),

      "book-media": tool({
        description: "Generate media prompts for chapter or section",
        args: {
          target: tool.schema.string(),
        },
        async execute(args, context) {
          return `Generating media for: ${args.target}`
        },
      }),
    },

    "installation.updated": async (input, output) => {
      output.mcp = {
        obsidian: {
          type: "local",
          command: ["npx", "@bitbonsai/mcpvault@latest"],
          args: [],
          enabled: true,
        },
      }

      output.skills = ["obsidian-markdown", "obsidian", "mineru"]
    },
  }
}

export default BookManPlugin