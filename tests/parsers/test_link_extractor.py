"""Tests for LinkExtractor class."""

from md_gtd_mcp.parsers.link_extractor import LinkExtractor


class TestLinkExtractor:
    """Test LinkExtractor parsing of links from markdown text."""

    def test_simple_context_link(self) -> None:
        """Test extracting simple context link."""
        text = "Call dentist @calls"
        links = LinkExtractor.extract_links(text)

        assert len(links) == 1
        link = links[0]

        assert link.text == "calls"
        assert link.target == "@calls"
        assert link.is_external is False  # Context links are internal
        assert link.line_number == 1

    def test_multiple_contexts_same_line(self) -> None:
        """Test extracting multiple context links from same line."""
        text = "Buy groceries @errands and call dentist @calls"
        links = LinkExtractor.extract_links(text)

        assert len(links) == 2

        assert links[0].text == "errands"
        assert links[0].target == "@errands"
        assert links[0].is_external is False

        assert links[1].text == "calls"
        assert links[1].target == "@calls"
        assert links[1].is_external is False

    def test_context_links_multiline(self) -> None:
        """Test extracting context links across multiple lines."""
        text = """Meeting prep @office
Call client @calls
Email updates @computer"""

        links = LinkExtractor.extract_links(text)

        assert len(links) == 3
        assert links[0].text == "office"
        assert links[0].line_number == 1
        assert links[1].text == "calls"
        assert links[1].line_number == 2
        assert links[2].text == "computer"
        assert links[2].line_number == 3

        for link in links:
            assert link.is_external is False

    def test_simple_wikilink(self) -> None:
        """Test extracting simple wikilink."""
        text = "Review budget [[Home Renovation]]"
        links = LinkExtractor.extract_links(text)

        assert len(links) == 1
        link = links[0]

        assert link.text == "Home Renovation"
        assert link.target == "Home Renovation"
        assert link.is_external is False
        assert link.line_number == 1

    def test_wikilink_with_display_text(self) -> None:
        """Test extracting wikilink with custom display text."""
        text = "See project notes [[Project Alpha|Alpha Notes]]"
        links = LinkExtractor.extract_links(text)

        assert len(links) == 1
        link = links[0]

        assert link.text == "Alpha Notes"
        assert link.target == "Project Alpha"
        assert link.is_external is False
        assert link.line_number == 1

    def test_wikilink_with_sections(self) -> None:
        """Test extracting wikilink with section reference."""
        text = "Check status [[Project Alpha#Status Updates]]"
        links = LinkExtractor.extract_links(text)

        assert len(links) == 1
        link = links[0]

        assert link.text == "Project Alpha#Status Updates"
        assert link.target == "Project Alpha#Status Updates"
        assert link.is_external is False
        assert link.line_number == 1

    def test_multiple_wikilinks_same_line(self) -> None:
        """Test extracting multiple wikilinks from same line."""
        text = "Update [[Project A]] and review [[Project B]]"
        links = LinkExtractor.extract_links(text)

        assert len(links) == 2

        assert links[0].text == "Project A"
        assert links[0].target == "Project A"
        assert links[0].is_external is False

        assert links[1].text == "Project B"
        assert links[1].target == "Project B"
        assert links[1].is_external is False

    def test_markdown_link_simple(self) -> None:
        """Test extracting simple markdown link."""
        text = "Check out [Google](https://google.com)"
        links = LinkExtractor.extract_links(text)

        assert len(links) == 1
        link = links[0]

        assert link.text == "Google"
        assert link.target == "https://google.com"
        assert link.is_external is True
        assert link.line_number == 1

    def test_multiple_markdown_links(self) -> None:
        """Test extracting multiple markdown links."""
        text = "Visit [Google](https://google.com) and [GitHub](https://github.com)"
        links = LinkExtractor.extract_links(text)

        assert len(links) == 2

        assert links[0].text == "Google"
        assert links[0].target == "https://google.com"
        assert links[0].is_external is True

        assert links[1].text == "GitHub"
        assert links[1].target == "https://github.com"
        assert links[1].is_external is True

    def test_mixed_link_types_same_text(self) -> None:
        """Test extracting mixed link types from same text."""
        text = """Project update for [[Home Renovation]]
- Call contractor @calls
- Check prices at [Home Depot](https://homedepot.com)
- Review plans with [[Architect|John Smith]]"""

        links = LinkExtractor.extract_links(text)

        assert len(links) == 4

        # Wikilink
        assert links[0].text == "Home Renovation"
        assert links[0].target == "Home Renovation"
        assert links[0].is_external is False
        assert links[0].line_number == 1

        # Context
        assert links[1].text == "calls"
        assert links[1].target == "@calls"
        assert links[1].is_external is False
        assert links[1].line_number == 2

        # Markdown link
        assert links[2].text == "Home Depot"
        assert links[2].target == "https://homedepot.com"
        assert links[2].is_external is True
        assert links[2].line_number == 3

        # Wikilink with display text
        assert links[3].text == "John Smith"
        assert links[3].target == "Architect"
        assert links[3].is_external is False
        assert links[3].line_number == 4

    def test_links_in_task_format(self) -> None:
        """Test extracting links from Obsidian Tasks format."""
        text = """- [ ] Review budget [[Home Renovation]] @office #task
- [x] Call dentist @calls ✅2024-01-10 #task
- [ ] Check [project docs](https://docs.example.com) @computer #task"""

        links = LinkExtractor.extract_links(text)

        assert len(links) == 5

        # Links are extracted in order: @office, [[Home Renovation]], @calls,
        # @computer, [project docs]
        assert links[0].text == "office"
        assert links[0].target == "@office"
        assert links[0].is_external is False

        assert links[1].text == "Home Renovation"
        assert links[1].target == "Home Renovation"
        assert links[1].is_external is False

        assert links[2].text == "calls"
        assert links[2].target == "@calls"
        assert links[2].is_external is False

        assert links[3].text == "computer"
        assert links[3].target == "@computer"
        assert links[3].is_external is False

        assert links[4].text == "project docs"
        assert links[4].target == "https://docs.example.com"
        assert links[4].is_external is True

    def test_edge_cases_empty_links(self) -> None:
        """Test handling of edge cases with empty or malformed links."""
        text = """Malformed links test:
- Empty wikilink [[]]
- Empty context @
- Empty markdown [](https://example.com)
- Valid link [[Project Alpha]]"""

        links = LinkExtractor.extract_links(text)

        # Only the valid link should be extracted
        assert len(links) == 1
        assert links[0].text == "Project Alpha"
        assert links[0].is_external is False

    def test_links_with_special_characters(self) -> None:
        """Test extracting links containing special characters."""
        text = """Links with special chars:
- Context with numbers @calls_2024
- Wikilink with spaces [[My Project - Phase 1]]
- Markdown with query params [Search](https://google.com?q=test&src=web)"""

        links = LinkExtractor.extract_links(text)

        assert len(links) == 3

        assert links[0].text == "calls_2024"
        assert links[0].is_external is False

        assert links[1].text == "My Project - Phase 1"
        assert links[1].is_external is False

        assert links[2].text == "Search"
        assert links[2].target == "https://google.com?q=test&src=web"
        assert links[2].is_external is True

    def test_no_links_in_text(self) -> None:
        """Test handling text with no links."""
        text = """Regular markdown text with no links.

This is just plain text with some formatting:
- Regular list item
- Another item with text
- No links here"""

        links = LinkExtractor.extract_links(text)
        assert links == []

    def test_empty_text(self) -> None:
        """Test handling empty or whitespace-only text."""
        assert LinkExtractor.extract_links("") == []
        assert LinkExtractor.extract_links("   \n\n   ") == []

    def test_context_validation(self) -> None:
        """Test context link validation (must be single word)."""
        text = """Valid and invalid contexts:
- Valid: @calls @office @errands
- Invalid: @multi word @with-dashes
- Edge case: @123numbers"""

        links = LinkExtractor.extract_links(text)

        # Should extract all valid contexts (regex \w+ allows alphanumeric + underscore)
        context_links = [link for link in links if link.target.startswith("@")]
        context_texts = [link.text for link in context_links]

        # Valid single-word contexts
        assert "calls" in context_texts
        assert "office" in context_texts
        assert "errands" in context_texts
        assert "123numbers" in context_texts  # Numbers are valid in \w+

    def test_line_number_tracking_accuracy(self) -> None:
        """Test accurate line number tracking across complex text."""
        text = """Line 1: Regular text
Line 2: Has [[wikilink]]

Line 4: Empty line above, context @office
Line 5: Multiple links [[Project A]] and [website](https://example.com)

Line 7: Another [[wikilink2]]"""

        links = LinkExtractor.extract_links(text)

        # Create a mapping for easier verification
        line_map = {}
        for link in links:
            line_map[link.text] = link.line_number

        assert line_map["wikilink"] == 2
        assert line_map["office"] == 4
        assert line_map["Project A"] == 5
        assert line_map["website"] == 5
        assert line_map["wikilink2"] == 7

    def test_urls_vs_wikilinks_detection(self) -> None:
        """Test that URLs and wikilinks are properly distinguished."""
        text = """Different link formats:
- Wikilink: [[Project Alpha]]
- Wikilink with display: [[Project Beta|Beta Project]]
- Context: @office
- Markdown: [Example](https://example.com)
- Local markdown: [Local](./local.md)"""

        links = LinkExtractor.extract_links(text)

        # URLs should be external, wikilinks and contexts should be internal
        external_links = [link for link in links if link.is_external]
        internal_links = [link for link in links if not link.is_external]

        # Should have 2 external (https and ./local.md)
        assert len(external_links) == 2
        external_targets = [link.target for link in external_links]
        assert "https://example.com" in external_targets
        assert "./local.md" in external_targets

        # Should have 3 internal (2 wikilinks + 1 context)
        assert len(internal_links) == 3
