"""
Environment Setup Module
Import this module FIRST to suppress Google Cloud and gRPC warnings
"""

import os
import warnings
import sys

# Suppress Google Cloud ALTS and gRPC warnings
# These MUST be set before any Google Cloud libraries are imported
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2" 
os.environ["GOOGLE_APPLICATION_CREDENTIALS_DISABLED"] = "true"

# TensorFlow and ABSL logging
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["ABSL_LOGGING_VERBOSITY"] = "1"

# gRPC specific settings
os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "0"
os.environ["GRPC_POLL_STRATEGY"] = "poll"

# Additional environment variables for comprehensive suppression
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["GRPC_TRACE"] = ""
os.environ["GRPC_VERBOSITY"] = "ERROR"

# Python warnings - be very aggressive
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", module="google.*")
warnings.filterwarnings("ignore", module="grpc.*")
warnings.filterwarnings("ignore", module="absl.*")

# Redirect stderr temporarily to suppress ALTS warnings
class SuppressOutput:
    def __init__(self):
        self.original_stderr = sys.stderr
        self.suppressed = False
    
    def __enter__(self):
        if not self.suppressed:
            sys.stderr = open(os.devnull, 'w')
            self.suppressed = True
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.suppressed:
            sys.stderr.close()
            sys.stderr = self.original_stderr
            self.suppressed = False

# Initialize ABSL logging with stderr suppression
try:
    with SuppressOutput():
        import absl.logging
        absl.logging.set_verbosity(absl.logging.ERROR)
        absl.logging.set_stderrthreshold(absl.logging.ERROR)
        
        # Try to initialize ABSL logging to prevent the "before InitializeLog" warning
        try:
            import absl.app
            absl.app.parse_flags_with_usage([])
        except:
            pass
            
        # Force initialize ABSL logging system
        try:
            absl.logging._warn_preinit_stderr = False
        except:
            pass
            
except ImportError:
    pass

print("🔇 Comprehensive warning suppression activated")