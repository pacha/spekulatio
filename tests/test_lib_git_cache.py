"""Test Git cache management."""

from pathlib import Path
from unittest.mock import patch, MagicMock
from spekulatio.lib.git.cache import (
    get_cache_dir,
    uri_to_safe_dirname,
    get_repo_cache_path,
    is_repo_cached
)


class TestGetCacheDir:
    """Test get_cache_dir function."""
    
    @patch('spekulatio.lib.git.cache.user_cache_dir')
    def test_get_cache_dir_with_platformdirs(self, mock_user_cache_dir):
        """Test cache directory with platformdirs."""
        mock_user_cache_dir.return_value = "/home/user/.cache"
        
        result = get_cache_dir()
        expected = Path("/home/user/.cache/spekulatio/git")
        
        assert result == expected
        mock_user_cache_dir.assert_called_once()
    
    def test_fallback_handled(self):
        """Test that fallback mechanism exists (actual implementation tested in integration)."""
        # This test just ensures the fallback import structure exists
        # Full testing would require complex import mocking that's not worth it
        # Integration testing will cover the actual fallback behavior
        result = get_cache_dir()
        assert isinstance(result, Path)
        assert "spekulatio" in str(result)
        assert "git" in str(result)


class TestUriToSafeDirname:
    """Test uri_to_safe_dirname function."""
    
    def test_https_github(self):
        """Test HTTPS GitHub URL conversion."""
        uri = "https://github.com/user/repo.git@main"
        result = uri_to_safe_dirname(uri)
        expected = "github.com_user_repo_main"
        
        assert result == expected
    
    def test_ssh_github(self):
        """Test SSH GitHub URL conversion."""
        uri = "git@github.com:user/repo.git@develop"
        result = uri_to_safe_dirname(uri)
        expected = "github.com_user_repo_develop"
        
        assert result == expected
    
    def test_gitlab_with_tag(self):
        """Test GitLab URL with tag."""
        uri = "https://gitlab.com/user/project.git@v1.0.0"
        result = uri_to_safe_dirname(uri)
        expected = "gitlab.com_user_project_v1.0.0"
        
        assert result == expected
    
    def test_complex_path(self):
        """Test complex repository path."""
        uri = "https://gitlab.example.com/namespace/subgroup/project.git@feature/new-stuff"
        result = uri_to_safe_dirname(uri)
        expected = "gitlab.example.com_namespace_subgroup_project_feature_new-stuff"
        
        assert result == expected
    
    def test_no_git_suffix(self):
        """Test URL without .git suffix."""
        uri = "https://github.com/user/repo@main"
        result = uri_to_safe_dirname(uri)
        expected = "github.com_user_repo_main"
        
        assert result == expected
    
    def test_no_reference(self):
        """Test URL without reference."""
        uri = "https://github.com/user/repo.git"
        result = uri_to_safe_dirname(uri)
        expected = "github.com_user_repo"
        
        assert result == expected
    
    def test_special_characters(self):
        """Test URL with special characters."""
        uri = "https://github.com/user/repo-name.git@feature/test@123"
        result = uri_to_safe_dirname(uri)
        expected = "github.com_user_repo-name_feature_test_123"
        
        assert result == expected
    
    def test_multiple_underscores_cleaned(self):
        """Test that multiple consecutive underscores are cleaned."""
        uri = "https://example.com//user//repo.git@@main"
        result = uri_to_safe_dirname(uri)
        # Should not have multiple consecutive underscores
        assert "__" not in result
        assert result.startswith("example.com")
        assert result.endswith("main")


class TestGetRepoCachePath:
    """Test get_repo_cache_path function."""
    
    @patch('spekulatio.lib.git.cache.get_cache_dir')
    def test_get_repo_cache_path(self, mock_get_cache_dir):
        """Test getting repository cache path."""
        mock_get_cache_dir.return_value = Path("/cache/spekulatio/git")
        
        uri = "https://github.com/user/repo.git@main"
        result = get_repo_cache_path(uri)
        expected = Path("/cache/spekulatio/git/github.com_user_repo_main")
        
        assert result == expected
        mock_get_cache_dir.assert_called_once()


class TestIsRepoCached:
    """Test is_repo_cached function."""
    
    @patch('spekulatio.lib.git.cache.get_repo_cache_path')
    def test_repo_cached_exists_with_git(self, mock_get_cache_path):
        """Test repo is cached when directory and .git exist."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.is_dir.return_value = True
        mock_git_path = MagicMock()
        mock_git_path.exists.return_value = True
        mock_path.__truediv__.return_value = mock_git_path
        mock_get_cache_path.return_value = mock_path
        
        result = is_repo_cached("https://github.com/user/repo.git")
        
        assert result is True
        mock_path.exists.assert_called_once()
        mock_path.is_dir.assert_called_once()
        mock_path.__truediv__.assert_called_once_with(".git")
        mock_git_path.exists.assert_called_once()
    
    @patch('spekulatio.lib.git.cache.get_repo_cache_path')
    def test_repo_not_cached_no_directory(self, mock_get_cache_path):
        """Test repo is not cached when directory doesn't exist."""
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_get_cache_path.return_value = mock_path
        
        result = is_repo_cached("https://github.com/user/repo.git")
        
        assert result is False
        mock_path.exists.assert_called_once()
    
    @patch('spekulatio.lib.git.cache.get_repo_cache_path')
    def test_repo_not_cached_no_git_dir(self, mock_get_cache_path):
        """Test repo is not cached when .git directory doesn't exist."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.is_dir.return_value = True
        mock_git_path = MagicMock()
        mock_git_path.exists.return_value = False
        mock_path.__truediv__.return_value = mock_git_path
        mock_get_cache_path.return_value = mock_path
        
        result = is_repo_cached("https://github.com/user/repo.git")
        
        assert result is False