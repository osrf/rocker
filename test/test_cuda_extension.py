import pytest
import os
from unittest.mock import patch, MagicMock

# Correct import path assuming Cuda is defined in nvidia_extension.py
from rocker.nvidia_extension import Cuda
from rocker.os_detector import detect_os 

# --- Fixture for Mocking a Supported OS ---
# This ensures that when detect_os is called, it returns a supported Linux distro
SUPPORTED_OS_MOCK = ('Ubuntu', '22.04', 'jammy')


# ====================================================================
# TEST CASE 1: INSTALLATION PROCEEDS (Driver Absent)
# This simulates a system WITHOUT the NVIDIA driver installed.
# check_preconditions should return True.
# ====================================================================

# Patch order: top-to-bottom = reverse order of arguments (right-to-left)
@patch('rocker.nvidia_extension.detect_os', return_value=SUPPORTED_OS_MOCK)
@patch('os.path.exists', return_value=False) 
def test_cuda_installs_if_driver_absent(mock_exists, mock_detect_os):
    """
    Tests that the Cuda extension is enabled when the host is missing the 
    /dev/nvidia0 file, confirming the installation logic will be included.
    """
    
    # --- Setup ---
    cliargs = {'base_image': 'ubuntu:22.04', 'cuda': True}
    cuda_ext = Cuda()
    
    # 1. Execute the check_preconditions method
    # It should pass (True) because os.path.exists mocked to False
    status, message = cuda_ext.check_preconditions(cliargs)
    
    # --- Assert Preconditions ---
    
    # Verify os.path.exists was called with the specific path
    mock_exists.assert_called_with('/dev/nvidia0')
    
    # Assertion: Status must be True to allow installation
    assert status is True, f"Precondition failed (expected True): {message}"
    assert "installation prerequisites met" in message 
    
    # 2. Execute get_snippet (Tests the core API contract and snippet generation)
    snippet = cuda_ext.get_snippet(cliargs)
    
    # Assertion: Check that the snippet contains expected installation content
    assert "apt-get update" in snippet 
    assert "cuda-toolkit" in snippet 


# ====================================================================
# TEST CASE 2: INSTALLATION IS SKIPPED (Driver Present)
# This simulates a system WITH the NVIDIA driver installed.
# check_preconditions should return False.
# ====================================================================

# Patch order: top-to-bottom = reverse order of arguments (right-to-left)
@patch('rocker.nvidia_extension.detect_os', return_value=SUPPORTED_OS_MOCK)
@patch('os.path.exists', return_value=True) 
def test_cuda_skips_if_driver_present(mock_exists, mock_detect_os):
    """
    Tests that the Cuda extension is disabled (status=False) when the 
    /dev/nvidia0 file is present, confirming the reinstallation skip logic.
    """
    
    # --- Setup ---
    cliargs = {'base_image': 'ubuntu:22.04', 'cuda': True}
    cuda_ext = Cuda()
    
    # 1. Execute the check_preconditions method
    # It should fail (False) because os.path.exists mocked to True
    status, message = cuda_ext.check_preconditions(cliargs)
    
    # --- Assert Preconditions ---
    
    # Verify os.path.exists was called with the specific path
    mock_exists.assert_called_with('/dev/nvidia0')
    
    # Assertion: Status must be False to skip installation
    assert status is False, f"Precondition passed (expected False): {message}"
    
    # Assertion: Check for the expected skip message
    assert "Skipping installation" in message 
    
    # 2. Assert that get_snippet is NOT called (optional, as the core handles skipping)
    # Since we are not mocking get_snippet here, we will test the output.
    # get_snippet should still generate content, but the core won't use it.
    # However, if we were mocking it, we'd assert it was never called. 
    # For simplicity, we just check the status returned by check_preconditions.