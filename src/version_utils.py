
import subprocess
from typing import Optional

def get_git_revision_hash() -> Optional[str]:
    """
    Retrieve the current git commit hash.
    
    Returns:
        Full git hash string, or None if git is not available or not in a repo.
    """
    try:
        # We use HEAD to get the current commit
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], 
                                     stderr=subprocess.DEVNULL).decode('ascii').strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None

def get_git_short_hash() -> Optional[str]:
    """
    Retrieve the short (7-char) git commit hash.
    
    Returns:
        Short git hash string, or None if git is not available.
    """
    try:
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], 
                                     stderr=subprocess.DEVNULL).decode('ascii').strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None
