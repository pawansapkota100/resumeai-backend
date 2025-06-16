import tempfile
import os
from contextlib import contextmanager

@contextmanager
def with_temp_file(uploaded_file, suffix=".pdf"):
    """
    Context manager to save an uploaded file temporarily and automatically delete it.
    
    Usage:
        with with_temp_file(uploaded_file) as file_path:
            # use file_path here
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)
        temp_file.flush()
        temp_file.close()
        yield temp_file.name
    finally:
        os.remove(temp_file.name)
