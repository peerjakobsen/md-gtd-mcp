# MCP Resources Conversion Specification

## Overview

Convert existing read-only MCP tools (`list_gtd_files`, `read_gtd_file`, `read_gtd_files`) to MCP resources following protocol best practices for semantic correctness and improved LLM understanding.

## User Stories

### Story 1: Semantic Protocol Compliance
**As a** Claude Desktop user
**I want** GTD file operations to follow MCP protocol semantics
**So that** read-only operations are clearly distinguished from actions

**Workflow:**
1. User requests GTD file listing → accesses `gtd://vault/files` resource
2. User requests specific file → accesses `gtd://vault/file/inbox.md` resource
3. User requests batch content → accesses `gtd://vault/content` resource
4. MCP client understands these are read-only operations through resource annotations

### Story 2: Improved LLM Understanding
**As a** Claude Desktop
**I want** clear resource annotations (readOnlyHint, idempotentHint)
**So that** I can better understand when operations are safe to repeat and won't modify data

**Workflow:**
1. Claude receives resource templates with proper annotations
2. Claude understands read operations are safe and idempotent
3. Claude can optimize caching and repeated access patterns
4. Claude provides better user experience through informed operation choices

### Story 3: URI-Based Data Access
**As a** MCP client developer
**I want** intuitive URI patterns for GTD data access
**So that** I can build applications using REST-like principles

**Workflow:**
1. Developer accesses `gtd://vault/files` for file listings
2. Developer accesses `gtd://vault/file/{path}` for specific files
3. Developer accesses `gtd://vault/content` for bulk content operations
4. URI patterns follow logical hierarchy and conventions

## Spec Scope

1. **Resource Template Implementation** - Create three core resource templates with proper URI patterns and parameter handling
2. **Tool-to-Resource Migration** - Replace existing `list_gtd_files`, `read_gtd_file`, and `read_gtd_files` tools with corresponding resources
3. **Enhanced Annotations** - Add `readOnlyHint: true` and `idempotentHint: true` annotations for optimal LLM understanding
4. **Filtered Resource Variants** - Implement optional file type filtering through URI parameters for improved data access
5. **Test Migration** - Update existing test suite to use resource reading instead of tool calling patterns

## Out of Scope

- Write operations (tools for creating/modifying files remain unchanged)
- Complex query parameters beyond basic file type filtering
- Advanced caching mechanisms (relies on MCP client-side caching)
- Backward compatibility layer (clean replacement approach)
- Performance optimizations beyond basic resource efficiency

## Expected Deliverable

1. **Functional Resource Access** - All three resource templates (`files`, `file`, `content`) successfully provide read-only access to GTD data with proper URI routing
2. **Protocol Compliance** - Resources follow MCP specification with correct annotations and eliminate tool-based read operations
3. **Test Coverage** - Comprehensive test suite validates resource functionality and demonstrates migration from tool-based approach
