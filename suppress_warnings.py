"""
Environment Setup Module
Import this module FIRST to suppress Google Cloud and gRPC warnings
"""

import os
import warnings

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

# Python warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.*")
warnings.filterwarnings("ignore", category=UserWarning, module="grpc.*")

# Initialize ABSL logging if available
try:
    import absl.logging
    absl.logging.set_verbosity(absl.logging.ERROR)
    absl.logging.set_stderrthreshold(absl.logging.ERROR)
    # Try to initialize ABSL logging to prevent the "before InitializeLog" warning
    try:
        # This will initialize ABSL logging system
        import absl.app
        absl.app.parse_flags_with_usage([])
    except:
        pass
except ImportError:
    pass

print("🔇 Environment configured - Google Cloud warnings suppressed")