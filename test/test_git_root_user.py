#!/usr/bin/env python3
"""
Integration tests for Git and User extensions with non-standard home directories.
Reproduces issue #337 where extensions assume /home directory.

These tests verify the actual behavior with users that have non-standard home
directories, matching the reproduction case from cottsay's Containerfile.
"""

import unittest
import os
import sys
import tempfile

# Ensure we can import rocker modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rocker.git_extension import Git
from rocker.extensions import User


class TestNonStandardHomeDirectory(unittest.TestCase):
    """
    Test Git and User extensions with non-standard home directories.
    This reproduces the scenario from issue #337.
    """
    
    def test_git_extension_nonstandard_home_directory(self):
        """
        Test Git extension with a user that has a non-standard home directory.
        
        This reproduces the scenario from cottsay's Containerfile where:
        - User 'buildfarm' has home at /var/lib/buildfarm (not /home/buildfarm)
        - Git extension should use the correct home directory
        
        Reference: https://gist.githubusercontent.com/cottsay/4360265b49b7e830c2b3de22b8978994/raw/Containerfile
        """
        # Create a temporary gitconfig
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gitconfig', delete=False) as f:
            f.write('[user]\n\tname = Test User\n\temail = test@example.com\n')
            temp_gitconfig = f.name
        
        try:
            # Test case 1: User that doesn't exist in host system (like 'buildfarm')
            # Should fall back to /home/buildfarm
            cli_args = {
                'user': True,
                'user_override_name': 'buildfarm',  # Non-existent user
                'git_config_path': temp_gitconfig
            }
            
            git_ext = Git()
            docker_args = git_ext.get_docker_args(cli_args)
            
            print("\n=== Docker args for buildfarm user ===")
            print(docker_args)
            print("=== End args ===\n")
            
            # Should use /home/buildfarm/.gitconfig as fallback
            # (The container will have the user with /var/lib/buildfarm as home,
            # but that's configured inside the container, not on the host)
            self.assertIn('buildfarm/.gitconfig', docker_args,
                         "Git extension should handle non-existent users")
            
            # Test case 2: Root user
            cli_args_root = {
                'user': True,
                'user_override_name': 'root',
                'git_config_path': temp_gitconfig
            }
            
            docker_args_root = git_ext.get_docker_args(cli_args_root)
            
            print("\n=== Docker args for root user ===")
            print(docker_args_root)
            print("=== End args ===\n")
            
            # Should use /root/.gitconfig, NOT /home/root/.gitconfig
            self.assertIn('/root/.gitconfig', docker_args_root,
                         "Git extension should use /root for root user")
            self.assertNotIn('/home/root/.gitconfig', docker_args_root,
                            "Git extension should not use /home/root for root user")
            
        finally:
            if os.path.exists(temp_gitconfig):
                os.unlink(temp_gitconfig)
    
    def test_user_extension_nonstandard_home_directory(self):
        """
        Test User extension with non-standard home directories.
        
        Verifies that the User extension correctly handles:
        1. Root user (home at /root)
        2. Non-existent users (fallback to /home/username)
        """
        # Test root user
        cli_args_root = {
            'user_override_name': 'root'
        }
        
        user_ext_root = User()
        snippet_root = user_ext_root.get_snippet(cli_args_root)
        
        print("\n=== User extension snippet for root ===")
        print(snippet_root)
        print("=== End snippet ===\n")
        
        # Root should be detected as existing
        self.assertIn('Detected user is root', snippet_root,
                     "User extension should detect root already exists")
        self.assertNotIn('/home/root', snippet_root,
                        "User extension should not use /home/root")
        
        # Test non-existent user (like buildfarm)
        cli_args_buildfarm = {
            'user_override_name': 'buildfarm'
        }
        
        user_ext_buildfarm = User()
        snippet_buildfarm = user_ext_buildfarm.get_snippet(cli_args_buildfarm)
        
        print("\n=== User extension snippet for buildfarm ===")
        print(snippet_buildfarm)
        print("=== End snippet ===\n")
        
        # Should create user with /home/buildfarm
        # Note: The container can override this later, but the initial
        # Dockerfile should use /home as the default for non-root users
        self.assertIn('/home/buildfarm', snippet_buildfarm,
                     "User extension should use /home for non-existent users")


class TestRootUserHandling(unittest.TestCase):
    """
    Specific tests for root user handling, which is the primary case
    mentioned in issue #337.
    """
    
    def test_root_user_git_config_path(self):
        """
        Test that root user gets /root/.gitconfig, not /home/root/.gitconfig.
        This is the core issue from #337.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gitconfig', delete=False) as f:
            f.write('[user]\n\tname = Root User\n')
            temp_gitconfig = f.name
        
        try:
            cli_args = {
                'user': True,
                'user_override_name': 'root',
                'git_config_path': temp_gitconfig
            }
            
            git_ext = Git()
            docker_args = git_ext.get_docker_args(cli_args)
            
            print("\n=== CRITICAL TEST: Root user git config path ===")
            print(docker_args)
            print("=== End ===\n")
            
            # CRITICAL: Must use /root/.gitconfig
            self.assertIn(':/root/.gitconfig:ro', docker_args,
                         "FAIL: Git extension must mount to /root/.gitconfig for root user")
            
            # CRITICAL: Must NOT use /home/root/.gitconfig
            self.assertNotIn('/home/root', docker_args,
                            "FAIL: Git extension must not use /home/root for root user")
            
        finally:
            if os.path.exists(temp_gitconfig):
                os.unlink(temp_gitconfig)


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)
