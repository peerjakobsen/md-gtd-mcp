# MCP Resources Conversion (Lite)

Convert read-only MCP tools to resources for protocol compliance and better LLM understanding. Replace `list_gtd_files`, `read_gtd_file`, `read_gtd_files` tools with URI-based resource templates: `gtd://vault/files`, `gtd://vault/file/{path}`, `gtd://vault/content`. Add proper annotations (readOnlyHint, idempotentHint) and support optional file type filtering. Maintains semantic separation between read operations (resources) and write operations (tools) following MCP best practices.
