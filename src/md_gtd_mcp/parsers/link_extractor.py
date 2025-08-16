"""LinkExtractor for parsing links from markdown text."""

import re

from ..models import MarkdownLink


class LinkExtractor:
    """Extract links from markdown text."""

    # Regex patterns for different link types
    CONTEXT_PATTERN = re.compile(r"@(\w+)")
    WIKILINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")
    MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

    @classmethod
    def extract_links(cls, text: str) -> list[MarkdownLink]:
        """Extract all links from markdown text.

        Args:
            text: Markdown text content

        Returns:
            List of MarkdownLink objects
        """
        if not text or not text.strip():
            return []

        links = []
        lines = text.split("\n")

        for line_num, line in enumerate(lines, 1):
            links.extend(cls._extract_line_links(line, line_num))

        return links

    @classmethod
    def _extract_line_links(cls, line: str, line_number: int) -> list[MarkdownLink]:
        """Extract all links from a single line.

        Args:
            line: Single line of text
            line_number: Line number in source text

        Returns:
            List of MarkdownLink objects from this line
        """
        links = []

        # Extract context links (@word)
        for match in cls.CONTEXT_PATTERN.finditer(line):
            context_text = match.group(1)
            if context_text:  # Skip empty contexts
                links.append(
                    MarkdownLink(
                        text=context_text,
                        target=f"@{context_text}",
                        is_external=False,  # Context links are internal
                        line_number=line_number,
                    )
                )

        # Extract wikilinks ([[text]] or [[target|display]])
        for match in cls.WIKILINK_PATTERN.finditer(line):
            wikilink_content = match.group(1)
            if not wikilink_content.strip():  # Skip empty wikilinks
                continue

            # Handle wikilink with display text [[target|display]]
            if "|" in wikilink_content:
                target_text, display_text = wikilink_content.split("|", 1)
                link_text = display_text.strip()
                target = target_text.strip()
            else:
                link_text = wikilink_content.strip()
                target = wikilink_content.strip()

            if link_text:  # Only create link if we have display text
                links.append(
                    MarkdownLink(
                        text=link_text,
                        target=target,
                        is_external=False,  # Wikilinks are internal
                        line_number=line_number,
                    )
                )

        # Extract markdown links [text](url)
        for match in cls.MARKDOWN_LINK_PATTERN.finditer(line):
            link_text = match.group(1)
            link_url = match.group(2)
            if link_text and link_url:  # Skip empty links
                # Determine if link is external (http/https/ftp) or internal
                is_external = cls._is_external_url(link_url)
                links.append(
                    MarkdownLink(
                        text=link_text,
                        target=link_url,
                        is_external=is_external,
                        line_number=line_number,
                    )
                )

        return links

    @classmethod
    def _is_external_url(cls, url: str) -> bool:
        """Determine if a URL is external (starts with protocol) or internal.

        Args:
            url: URL to check

        Returns:
            True if URL is external (has protocol), False if internal/relative
        """
        # External URLs start with protocol schemes
        external_patterns = [
            r"^https?://",  # HTTP/HTTPS
            r"^ftp://",  # FTP
            r"^mailto:",  # Email
            r"^tel:",  # Phone
        ]

        url_lower = url.lower()
        for pattern in external_patterns:
            if re.match(pattern, url_lower):
                return True

        # Consider file:// URLs as external too
        if url_lower.startswith("file://"):
            return True

        # Relative paths and local files are internal unless they look like file paths
        # that would be external to the vault (e.g., ./file.md, ../file.md)
        if url.startswith(("./", "../")) or url.endswith(".md"):
            return True

        return False
