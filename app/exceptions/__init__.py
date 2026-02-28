"""
Custom exception classes for the ACH to RTP service.
"""


class AchToRtpException(Exception):
    """Base exception for ACH to RTP service."""
    pass


class AchParsingException(AchToRtpException):
    """Raised when ACH file parsing fails."""
    
    def __init__(self, message: str, line_number: int = None, record_type: str = None):
        self.message = message
        self.line_number = line_number
        self.record_type = record_type
        
        if line_number:
            message = f"Line {line_number}: {message}"
        if record_type:
            message = f"[{record_type}] {message}"
        
        super().__init__(message)


class ValidationException(AchToRtpException):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: str = None, value: str = None):
        self.message = message
        self.field = field
        self.value = value
        
        if field:
            message = f"Field '{field}': {message}"
        if value:
            message = f"{message} (value: {value})"
        
        super().__init__(message)


class RtpMessageException(AchToRtpException):
    """Raised when RTP message generation fails."""
    
    def __init__(self, message: str, entry_id: str = None):
        self.message = message
        self.entry_id = entry_id
        
        if entry_id:
            message = f"Entry {entry_id}: {message}"
        
        super().__init__(message)


class PublishingException(AchToRtpException):
    """Raised when message publishing fails."""
    
    def __init__(self, message: str, job_id: str = None, retry_count: int = None):
        self.message = message
        self.job_id = job_id
        self.retry_count = retry_count
        
        if job_id:
            message = f"Job {job_id}: {message}"
        if retry_count is not None:
            message = f"{message} (attempt {retry_count})"
        
        super().__init__(message)


class FileUploadException(AchToRtpException):
    """Raised when file upload fails."""
    
    def __init__(self, message: str, filename: str = None):
        self.message = message
        self.filename = filename
        
        if filename:
            message = f"File '{filename}': {message}"
        
        super().__init__(message)


class DatabaseException(AchToRtpException):
    """Raised when database operations fail."""
    pass


class ConfigurationException(AchToRtpException):
    """Raised when configuration is invalid."""
    pass
