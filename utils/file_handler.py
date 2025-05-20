import os
import uuid
import shutil
from typing import Optional, Tuple
from werkzeug.utils import secure_filename

class FileHandler:
    """Utility class for handling file operations in the application"""
    
    def __init__(self, base_dir: str):
        """
        Initialize the FileHandler
        
        Args:
            base_dir: Base directory for storing files
        """
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
    
    def save_uploaded_file(self, file, subfolder: Optional[str] = None) -> Tuple[bool, str]:
        """
        Save an uploaded file to the specified subfolder
        
        Args:
            file: The file object from request.files
            subfolder: Optional subfolder within base_dir
            
        Returns:
            Tuple of (success, file_path or error_message)
        """
        try:
            if not file:
                return False, "No file provided"
                
            # Create a secure filename with a UUID to avoid collisions
            original_filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4()}_{original_filename}"
            
            # Determine the target directory
            target_dir = self.base_dir
            if subfolder:
                target_dir = os.path.join(self.base_dir, subfolder)
                os.makedirs(target_dir, exist_ok=True)
                
            # Save the file
            file_path = os.path.join(target_dir, filename)
            file.save(file_path)
            
            return True, file_path
            
        except Exception as e:
            return False, f"Error saving file: {str(e)}"
    
    def delete_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Delete a file
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"
                
            os.remove(file_path)
            return True, f"File deleted: {file_path}"
            
        except Exception as e:
            return False, f"Error deleting file: {str(e)}"
    
    def clean_old_files(self, max_age_hours: int = 24, subfolder: Optional[str] = None) -> Tuple[int, str]:
        """
        Clean files older than the specified age
        
        Args:
            max_age_hours: Maximum age of files in hours
            subfolder: Optional subfolder to clean
            
        Returns:
            Tuple of (number_of_files_deleted, message)
        """
        import time
        
        try:
            target_dir = self.base_dir
            if subfolder:
                target_dir = os.path.join(self.base_dir, subfolder)
                
            if not os.path.exists(target_dir):
                return 0, f"Directory not found: {target_dir}"
                
            now = time.time()
            max_age_seconds = max_age_hours * 3600
            deleted_count = 0
            
            for filename in os.listdir(target_dir):
                file_path = os.path.join(target_dir, filename)
                
                # Skip directories
                if os.path.isdir(file_path):
                    continue
                    
                # Check file age
                file_age = now - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    os.remove(file_path)
                    deleted_count += 1
                    
            return deleted_count, f"Deleted {deleted_count} old files from {target_dir}"
            
        except Exception as e:
            return 0, f"Error cleaning old files: {str(e)}" 