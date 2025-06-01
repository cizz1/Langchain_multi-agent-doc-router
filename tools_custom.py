from typing import TypedDict, List, Optional
import os
from pathlib import Path

class FileContent(TypedDict):
    filename: str
    content: str

def file_parser(filename: str) -> FileContent:
    """Original file parser function"""
    import json
    
    ext = filename.split(".")[-1]
    
    if ext == "json":
        with open(filename, "r") as f:
            return {"filename": filename, "content": json.dumps(json.load(f), indent=2)}
    
    # elif ext in ["eml", "txt"]:
    elif ext == "txt":
        with open(filename, "r", encoding="utf-8") as f:
            return {"filename": filename, "content": f.read()}
    
    elif ext == "pdf":
        import fitz  # PyMuPDF
        doc = fitz.open(filename)
        text = "\n".join([page.get_text() for page in doc])
        return {"filename": filename, "content": text}
    
    else:
        return {"filename": filename, "content": "Unsupported file type"}

def get_dummy_files_list() -> List[str]:
    """
    Get all supported files from the dummy_files directory.
    
    Returns:
        List[str]: List of filenames with full paths from dummy_files directory
    """
    dummy_dir = Path("dummy_files")
    supported_extensions = {'.json', '.eml', '.txt', '.pdf', '.csv', '.xml'}
    
    if not dummy_dir.exists():
        print(f"Warning: {dummy_dir} directory does not exist")
        return []
    
    files = []
    for file_path in dummy_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            files.append(str(file_path))
    
    return sorted(files)

def find_file_in_dummy_dir(filename: str) -> Optional[str]:
    """
    Find a specific file in the dummy_files directory.
    
    Args:
        filename: Name of the file to find (can be with or without path)
        
    Returns:
        Full path to the file if found, None otherwise
    """
    dummy_dir = Path("dummy_files")
    
    if not dummy_dir.exists():
        return None
    
    # If filename includes path separators, treat it as a relative path from dummy_files
    if os.sep in filename or '/' in filename:
        full_path = dummy_dir / filename
        if full_path.exists() and full_path.is_file():
            return str(full_path)
    
    # Otherwise, search for the filename in all subdirectories
    for file_path in dummy_dir.rglob(filename):
        if file_path.is_file():
            return str(file_path)
    
    # If not found, try adding common extensions
    if '.' not in filename:
        for ext in ['.json', '.eml', '.txt', '.pdf']:
            for file_path in dummy_dir.rglob(f"{filename}{ext}"):
                if file_path.is_file():
                    return str(file_path)
    
    return None

def get_file_info(filepath: str) -> dict:
    """
    Get basic information about a file.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Dictionary with file information
    """
    try:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}
        
        return {
            "filename": path.name,
            "full_path": str(path),
            "size_bytes": path.stat().st_size,
            "extension": path.suffix,
            "relative_path": str(path.relative_to(Path("dummy_files"))) if "dummy_files" in str(path) else str(path)
        }
    except Exception as e:
        return {"error": f"Error getting file info: {str(e)}"}
    

