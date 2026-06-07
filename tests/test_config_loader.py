import json
import pytest
from config import config_loader
from config.errors import ConfigError


class TestCreateConfigFile:
    def test_success(self, tmp_path, monkeypatch):
        # Arrange
        test_config = tmp_path / "test_config.json"

        monkeypatch.setattr(config_loader, "CONFIG_FILE", test_config)
        # Act
        config_loader.create_config_file()
        with test_config.open("r", encoding="utf-8") as f:
            data = json.load(f)
        # Assert
        assert test_config.exists()
        assert data == config_loader.DEFAULT_CONFIG
    
    def test_failure(self, tmp_path, monkeypatch):
        # Arrange
        bad_config = tmp_path / "test_dir"
        bad_config.mkdir()

        monkeypatch.setattr(config_loader, "CONFIG_FILE", bad_config)
        # Act & Assert
        with pytest.raises(ConfigError) as excinfo:
            config_loader.create_config_file()
        assert excinfo.value.key == "generate_config_failed"
    

class TestLoadConfig:
    def test_success(self, tmp_path, monkeypatch):
        # Arrange
        test_config = tmp_path / "test_config.json"
        source_dir = tmp_path / "test_source"
        source_dir.mkdir()
        
        config_data = config_loader.DEFAULT_CONFIG.copy()
        config_data["source_directory"] = str(source_dir)

        with test_config.open("w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
            
        monkeypatch.setattr(config_loader, "CONFIG_FILE", test_config)
        # Act
        result = config_loader.load_config()
        # Assert
        assert result["source_directory"] == str(source_dir)
        assert result["dry_run"] is True
        assert isinstance(result["rules"], list)
        assert len(result["rules"]) > 0
    
    def test_file_not_found(self, tmp_path, monkeypatch):
        # Arrange
        test_config = tmp_path / "non_existent.json"
        monkeypatch.setattr(config_loader, "CONFIG_FILE", test_config)
        
        # Act & Assert
        with pytest.raises(ConfigError) as excinfo:
            config_loader.load_config()
        assert excinfo.value.key == "no_config_file"

    def test_invalid_json(self, tmp_path, monkeypatch):
        # Arrange
        test_config = tmp_path / "invalid.json"
        test_config.write_text("{ broken json }", encoding="utf-8")
        monkeypatch.setattr(config_loader, "CONFIG_FILE", test_config)
        
        # Act & Assert
        with pytest.raises(ConfigError) as excinfo:
            config_loader.load_config()
        assert excinfo.value.key == "invalid_config"

    def test_validate_error_propagated(self, tmp_path, monkeypatch):
        # Arrange
        test_config = tmp_path / "invalid_content.json"
        invalid_data = {"dry_run": True, "rules": []}
        with test_config.open("w", encoding="utf-8") as f:
            json.dump(invalid_data, f)
            
        monkeypatch.setattr(config_loader, "CONFIG_FILE", test_config)
        # Act & Assert: validate_config で発生するエラーが伝播することを確認
        with pytest.raises(ConfigError) as excinfo:
            config_loader.load_config()
        assert excinfo.value.key == "source_directory_required"