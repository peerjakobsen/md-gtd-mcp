"""Test fixtures for GTD vault testing."""

import shutil
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from md_gtd_mcp.models import VaultConfig


@contextmanager
def create_sample_vault() -> Generator[VaultConfig]:
    """Create a temporary vault with sample GTD data.

    Returns:
        VaultConfig: Configuration for the temporary test vault

    Yields:
        VaultConfig pointing to the temporary vault with sample data
    """
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_vault_path = Path(temp_dir) / "sample_vault"

    try:
        # Copy sample vault fixtures to temporary location
        fixtures_path = Path(__file__).parent / "sample_vault"
        shutil.copytree(fixtures_path, temp_vault_path)

        # Create VaultConfig for the temporary vault
        vault_config = VaultConfig(temp_vault_path)

        yield vault_config

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)


def get_sample_vault_path() -> Path:
    """Get path to the sample vault fixtures.

    Returns:
        Path to the sample_vault fixtures directory
    """
    return Path(__file__).parent / "sample_vault"
