import pytest
import os
from unittest.mock import patch, MagicMock
from rocker.nvidia_extension import Cuda
from rocker.os_detector import detect_os 


SUPPORTED_OS_MOCK = ('Ubuntu', '22.04', 'jammy')



@patch('rocker.nvidia_extension.detect_os', return_value=SUPPORTED_OS_MOCK)
@patch('os.path.exists', return_value=False) 
def test_cuda_installs_if_driver_absent(mock_exists, mock_detect_os):
    """
    Tests that the Cuda extension is enabled when the host is missing the 
    /dev/nvidia0 file, confirming the installation logic will be included.
    """
    

    cliargs = {'base_image': 'ubuntu:22.04', 'cuda': True}
    cuda_ext = Cuda()
    
   
    status, message = cuda_ext.check_preconditions(cliargs)
    

    

    mock_exists.assert_called_with('/dev/nvidia0')
    
    
    assert status is True, f"Precondition failed (expected True): {message}"
    assert "installation prerequisites met" in message 
    
   
    snippet = cuda_ext.get_snippet(cliargs)
    
   
    assert "apt-get update" in snippet 
    assert "cuda-toolkit" in snippet 



@patch('rocker.nvidia_extension.detect_os', return_value=SUPPORTED_OS_MOCK)
@patch('os.path.exists', return_value=True) 
def test_cuda_skips_if_driver_present(mock_exists, mock_detect_os):
    """
    Tests that the Cuda extension is disabled (status=False) when the 
    /dev/nvidia0 file is present, confirming the reinstallation skip logic.
    """
    
   
    cliargs = {'base_image': 'ubuntu:22.04', 'cuda': True}
    cuda_ext = Cuda()
    
   
    status, message = cuda_ext.check_preconditions(cliargs)
    

    
    
    mock_exists.assert_called_with('/dev/nvidia0')
    

    assert status is False, f"Precondition passed (expected False): {message}"
    

    assert "Skipping installation" in message 
    
