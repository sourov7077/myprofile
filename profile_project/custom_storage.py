# profile_project/custom_storage.py

import os
from django.core.files.storage import FileSystemStorage
from django.core.files import File

class TermuxFileStorage(FileSystemStorage):
    """
    Custom storage for Termux to avoid file locking issues
    """
    
    def _save(self, name, content):
        """
        Save content to file without using file locking
        """
        full_path = self.path(name)
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Write file directly without Django's file handling
        if hasattr(content, 'temporary_file_path'):
            # Temporary uploaded file
            import shutil
            shutil.copy(content.temporary_file_path(), full_path)
        else:
            # In-memory uploaded file
            mode = 'wb' if isinstance(content, File) else 'wb'
            with open(full_path, mode) as destination:
                for chunk in content.chunks():
                    destination.write(chunk)
        
        return name
    
    def delete(self, name):
        """
        Delete file without locking
        """
        if self.exists(name):
            try:
                os.remove(self.path(name))
            except:
                pass

class NoLockFileSystemStorage(TermuxFileStorage):
    """
    Simple storage that completely bypasses Django's file locking
    """
    pass"""
Custom file storage for Termux Android
"""
import os
import shutil
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile

class TermuxFileStorage(FileSystemStorage):
    """
    Custom storage that completely bypasses Django's file locking mechanisms
    which cause OSError: [Errno 38] Function not implemented in Termux
    """
    
    def _save(self, name, content):
        """
        Save file without using any file locking functions
        """
        full_path = self.path(name)
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            os.makedirs(directory, mode=0o755, exist_ok=True)
        
        # Determine if content is already saved to a temporary file
        if hasattr(content, 'temporary_file_path'):
            # File is already on disk (temporary upload)
            temp_path = content.temporary_file_path()
            
            # Copy file using shutil to avoid locking
            try:
                shutil.copy2(temp_path, full_path)
            except Exception as e:
                # Fallback: simple file copy
                with open(temp_path, 'rb') as src, open(full_path, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
        else:
            # File is in memory
            if hasattr(content, 'read'):
                # File-like object
                with open(full_path, 'wb') as destination:
                    if hasattr(content, 'chunks'):
                        # Django's UploadedFile
                        for chunk in content.chunks():
                            destination.write(chunk)
                    else:
                        # Regular file-like object
                        destination.write(content.read())
            else:
                # Raw content (bytes/string)
                with open(full_path, 'wb') as destination:
                    if isinstance(content, str):
                        destination.write(content.encode())
                    else:
                        destination.write(content)
        
        # Set proper permissions (Termux compatible)
        try:
            os.chmod(full_path, 0o644)
        except:
            pass
        
        return name
    
    def delete(self, name):
        """
        Delete file without locking
        """
        if self.exists(name):
            try:
                os.remove(self.path(name))
            except:
                pass
    
    def exists(self, name):
        """
        Check if file exists
        """
        return os.path.exists(self.path(name))
    
    def size(self, name):
        """
        Get file size
        """
        try:
            return os.path.getsize(self.path(name))
        except:
            return 0
    
    def url(self, name):
        """
        Get file URL
        """
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        return super().url(name)