# Spec Requirements Document

> Spec: GTD Phase-Aware Task Recognition and Inbox Capture Tool
> Created: 2025-08-17

## Overview

Implement file-type aware task recognition that respects GTD phases and create an inbox capture tool for frictionless task entry. This feature ensures inbox files recognize all `- [ ]` items without #task tags (pure capture phase) while other GTD files maintain #task requirements for Obsidian Tasks plugin compatibility, creating clear distinction between captured and clarified items.

## User Stories

### GTD Practitioner Using AI Assistant for Capture

As a GTD practitioner using Claude Desktop, I want to quickly capture thoughts and meeting notes in my inbox without worrying about contexts or metadata, so that I can maintain friction-free capture while ensuring proper separation between captured and clarified items.

**Detailed Workflow**: User tells Claude Desktop "Add 'Review Q3 budget numbers' to my inbox" and the system adds it as a simple `- [ ] Review Q3 budget numbers` line without requiring #task tags, contexts, or detailed metadata. During weekly review, they process inbox items and add #task tags, contexts, and move items to appropriate GTD files.

### Power User Managing Multiple GTD File Types

As a power user with established GTD workflows, I want my project and next-actions files to maintain #task tag requirements for Obsidian Tasks plugin compatibility, so that my existing queries and workflows continue working while inbox remains friction-free.

**Detailed Workflow**: User has projects.md with `- [ ] Plan vacation #task @planning` that works with Obsidian Tasks queries, while inbox.md contains `- [ ] Call dentist` (no #task tag) that gets processed during clarification phase by adding the #task tag and appropriate context.

### AI Assistant Integration for GTD Workflows

As an AI assistant (Claude Desktop), I want to understand which GTD file types require #task tags and which don't, so that I can correctly parse tasks from different file types and guide users through proper GTD methodology during inbox processing.

**Detailed Workflow**: When reading inbox files, AI recognizes all `- [ ]` items as tasks. When reading other GTD files, AI only recognizes items with #task tags as tasks. When helping with inbox processing, AI guides user to add #task tags during clarification phase.

## Spec Scope

1. **File-Type Aware Task Recognition** - Modify TaskExtractor to recognize file types and apply different task recognition rules based on GTD phase requirements
2. **Inbox Task Recognition Without Tags** - Enable recognition of all `- [ ]` checkbox items in inbox files without requiring #task tags
3. **Maintain Plugin Compatibility** - Preserve #task tag requirements for non-inbox GTD files to maintain Obsidian Tasks plugin compatibility
4. **Inbox Capture Tool** - Create MCP tool for adding items directly to inbox following GTD quick-capture principles
5. **Integration with MCP Resources** - Ensure new logic works correctly with existing MCP resource templates for file reading

## Out of Scope

- Automatic context assignment during capture (contexts assigned during clarify phase)
- Modification of existing MCP resource architecture
- Changes to non-inbox file task recognition behavior
- Integration with external GTD applications beyond Obsidian

## Expected Deliverable

1. **File-type aware TaskExtractor** - TaskExtractor.extract_tasks() accepts optional file_type parameter and applies appropriate recognition rules
2. **Inbox capture tool** - New MCP tool `capture_inbox_item` for adding items to inbox without metadata requirements
3. **Maintained backward compatibility** - All existing tests pass with enhanced behavior for inbox files
