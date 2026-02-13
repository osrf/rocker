#!/usr/bin/env python3
"""
Tests for Git and User extensions with non-standard home directories.
Reproduces issue #337 where extensions assume /home directory.
"""

import unittest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock
import pwd

# Ensure we can import rocker modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rocker.git_extension import Git
from rocker.extensions import User


class TestGitExtensionHomeDirectory(unittest.TestCase):
    """Test Git extension handles various home directory scenarios"""
    
    def setUp(self):
        """Create temporary gitconfig for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_gitconfig = os.path.join(self.temp_dir, '.gitconfig')
        with open(self.temp_gitconfig, 'w') as f:
            f.write('[user]\n\tname = Test User\n\temail = test@example.com\n')
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_root_user_home_directory(self):
        """
        Test that Git extension uses /root for root user, not /home/root.
        This reproduces the issue reported in #337.
        """
        cli_args = {
            'user': True,
            'user_override_name': 'root',
            'git_config_path': self.temp_gitconfig
        }
        
        git_ext = Git()
        docker_args = git_ext.get_docker_args(cli_args)
        
        print("\n=== Docker args for root user ===")
        print(docker_args)
        print("=== End args ===\n")
        
        # Assert: Should mount to /root/.gitconfig
        self.assertIn('/root/.gitconfig', docker_args, 
                     "Git extension should use /root/.gitconfig for root user")
        
        # Assert: Should NOT use /home/root/.gitconfig
        self.assertNotIn('/home/root/.gitconfig', docker_args,
                        "Git extension should not use /home/root/.gitconfig for root user")
    
    def test_custom_nonexistent_user(self):
        """
        Test that Git extension handles users that don't exist in host system.
        This can happen when building containers with custom users.
        """
        cli_args = {
            'user': True,
            'user_override_name': 'nonexistent_user_xyz',
            'git_config_path': self.temp_gitconfig
        }
        
        git_ext = Git()
        docker_args = git_ext.get_docker_args(cli_args)
        
        print("\n=== Docker args for nonexistent user ===")
        print(docker_args)
        print("=== End args ===\n")
        
        # Should default to /home/username for non-root users
        self.assertIn('/home/nonexistent_user_xyz/.gitconfig', docker_args,
                     "Git extension should use /home/username for custom non-root users that don't exist")
    
    def test_existing_user_actual_home(self):
        """
        Test that Git extension uses actual home directory for existing users.
        """
        # Get current user info
        current_user = pwd.getpwuid(os.getuid())
        
        cli_args = {
            'user': True,
            'user_override_name': current_user.pw_name,
            'git_config_path': self.temp_gitconfig
        }
        
        git_ext = Git()
        docker_args = git_ext.get_docker_args(cli_args)
        
        print(f"\n=== Docker args for existing user {current_user.pw_name} ===")
        print(docker_args)
        print("=== End args ===\n")
        
        # Should use the actual home directory
        expected_path = os.path.join(current_user.pw_dir, '.gitconfig')
        self.assertIn(expected_path, docker_args,
                     f"Git extension should use actual home {expected_path} for existing users")


class TestUserExtensionHomeDirectory(unittest.TestCase):
    """Test User extension handles various home directory scenarios"""
    
    def test_root_user_directory(self):
        """
        Test that User extension correctly handles root user.
        When user is root, the extension should detect it and not create a new user.
        """
        cli_args = {
            'user_override_name': 'root'
        }
        
        user_ext = User()
        snippet = user_ext.get_snippet(cli_args)
        
        print("\n=== User extension snippet for root ===")
        print(snippet)
        print("=== End snippet ===\n")
        
        # Root user already exists, so snippet should mention this
        self.assertIn('Detected user is root', snippet,
                     "User extension should detect that root already exists")
        
        # Should NOT try to create root user or use /home/root
        self.assertNotIn('/home/root', snippet,
                        "User extension should not use /home/root for root user")
        self.assertNotIn('useradd', snippet,
                        "User extension should not try to create root user")
    def test_custom_nonexistent_user_directory(self):
        """
        Test that User extension handles non-existent users correctly.
        """
        cli_args = {
            'user_override_name': 'nonexistent_user_xyz'
        }
        
        user_ext = User()
        snippet = user_ext.get_snippet(cli_args)
        
        print("\n=== User extension snippet for nonexistent user ===")
        print(snippet)
        print("=== End snippet ===\n")
        
        # Should use /home/username for non-existent non-root users
        self.assertIn('/home/nonexistent_user_xyz', snippet,
                     "User extension should use /home/username for non-existent custom users")


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)
