"""Test Git URI parsing and validation."""

import pytest
from spekulatio.lib.git.uri import is_git_uri, parse_git_uri, GitUriInfo


class TestIsGitUri:
    """Test is_git_uri function."""
    
    def test_https_github_with_git(self):
        """Test HTTPS GitHub URL with .git suffix."""
        assert is_git_uri("https://github.com/user/repo.git")
        assert is_git_uri("https://github.com/user/repo.git@main")
        assert is_git_uri("https://github.com/user/repo.git@v1.0.0")
    
    def test_https_github_without_git(self):
        """Test HTTPS GitHub URL without .git suffix."""
        assert is_git_uri("https://github.com/user/repo")
        assert is_git_uri("https://github.com/user/repo@main")
    
    def test_https_gitlab(self):
        """Test HTTPS GitLab URLs."""
        assert is_git_uri("https://gitlab.com/user/repo.git")
        assert is_git_uri("https://gitlab.com/user/repo")
        assert is_git_uri("https://gitlab.com/user/repo@develop")
    
    def test_ssh_github(self):
        """Test SSH GitHub URLs."""
        assert is_git_uri("git@github.com:user/repo.git")
        assert is_git_uri("git@github.com:user/repo.git@main")
    
    def test_ssh_gitlab(self):
        """Test SSH GitLab URLs."""
        assert is_git_uri("git@gitlab.com:user/repo.git")
        assert is_git_uri("git@gitlab.com:user/repo.git@develop")
    
    def test_non_git_uris(self):
        """Test non-Git URIs return False."""
        assert not is_git_uri("local/path")
        assert not is_git_uri("/absolute/path")
        assert not is_git_uri("https://example.com")
        assert not is_git_uri("ftp://example.com/file")
        assert not is_git_uri("")
        assert not is_git_uri(None)
        assert not is_git_uri(123)


class TestParseGitUri:
    """Test parse_git_uri function."""
    
    def test_https_without_ref(self):
        """Test HTTPS URL without reference."""
        uri = "https://github.com/user/repo.git"
        result = parse_git_uri(uri)
        
        assert result.repo_url == "https://github.com/user/repo.git"
        assert result.ref_type == "branch"
        assert result.ref_value is None
    
    def test_https_with_branch(self):
        """Test HTTPS URL with branch reference."""
        uri = "https://github.com/user/repo.git@main"
        result = parse_git_uri(uri)
        
        assert result.repo_url == "https://github.com/user/repo.git"
        assert result.ref_type == "branch"
        assert result.ref_value == "main"
    
    def test_https_with_tag_v_prefix(self):
        """Test HTTPS URL with tag reference (v prefix)."""
        uri = "https://github.com/user/repo.git@v1.2.3"
        result = parse_git_uri(uri)
        
        assert result.repo_url == "https://github.com/user/repo.git"
        assert result.ref_type == "tag"
        assert result.ref_value == "v1.2.3"
    
    def test_https_with_tag_semantic_version(self):
        """Test HTTPS URL with semantic version tag."""
        uri = "https://github.com/user/repo.git@1.0.0"
        result = parse_git_uri(uri)
        
        assert result.repo_url == "https://github.com/user/repo.git"
        assert result.ref_type == "tag"
        assert result.ref_value == "1.0.0"
    
    def test_ssh_with_branch(self):
        """Test SSH URL with branch reference."""
        uri = "git@github.com:user/repo.git@develop"
        result = parse_git_uri(uri)
        
        assert result.repo_url == "git@github.com:user/repo.git"
        assert result.ref_type == "branch"
        assert result.ref_value == "develop"
    
    def test_ssh_without_ref(self):
        """Test SSH URL without reference."""
        uri = "git@github.com:user/repo.git"
        result = parse_git_uri(uri)
        
        assert result.repo_url == "git@github.com:user/repo.git"
        assert result.ref_type == "branch"
        assert result.ref_value is None
    
    def test_invalid_uri_raises_error(self):
        """Test that invalid URIs raise ValueError."""
        with pytest.raises(ValueError, match="Invalid Git URI"):
            parse_git_uri("not-a-git-uri")
    
    def test_gitlab_without_git_suffix(self):
        """Test GitLab URL without .git suffix."""
        uri = "https://gitlab.com/user/project@main"
        result = parse_git_uri(uri)
        
        assert result.repo_url == "https://gitlab.com/user/project"
        assert result.ref_type == "branch"
        assert result.ref_value == "main"


class TestGitUriInfo:
    """Test GitUriInfo dataclass."""
    
    def test_creation(self):
        """Test GitUriInfo creation."""
        info = GitUriInfo(
            repo_url="https://github.com/user/repo.git",
            ref_type="branch",
            ref_value="main"
        )
        
        assert info.repo_url == "https://github.com/user/repo.git"
        assert info.ref_type == "branch"
        assert info.ref_value == "main"
    
    def test_creation_without_ref(self):
        """Test GitUriInfo creation without reference."""
        info = GitUriInfo(
            repo_url="https://github.com/user/repo.git",
            ref_type="branch",
            ref_value=None
        )
        
        assert info.repo_url == "https://github.com/user/repo.git"
        assert info.ref_type == "branch"
        assert info.ref_value is None