import pytest
from config.validator import validate_config, _validate_single_rule
from config.errors import ConfigError, ExtensionError, DestinationError

@pytest.fixture
def test_config(tmp_path):
    source_dir = tmp_path / "test_source"
    source_dir.mkdir()
    return {
        "source_directory": str(source_dir),
        "dry_run": True,
        "rules": [
            {"extension": ".jpg", "destination": "images/jpg"}
        ]
    }


class TestValidateConfig:
    def test_full_success(self, test_config):
        validate_config(test_config)


class TestConfigStructure:

    def test_source_directory_missing(self, test_config):
        # Arrange
        del test_config["source_directory"]
        # Act & Assert: Public API を通じて構造的欠陥を検出
        with pytest.raises(ConfigError) as excinfo:
            validate_config(test_config)
        assert excinfo.value.key == "source_directory_required"

    def test_source_directory_not_exists(self, test_config):
        """パスの形式は正しいが、実在しないディレクトリの場合"""
        # Arrange
        test_config["source_directory"] = "not_exist_directory"
        # Act & Assert
        with pytest.raises(ConfigError) as excinfo:
            validate_config(test_config)
        assert excinfo.value.key == "source_dir_not_exist"

    def test_source_directory_not_dir(self, tmp_path, test_config):
        """パスの形式は正しいが、ファイルの場合"""
        # Arrange
        dummy_file = tmp_path / "dummy.txt"
        dummy_file.write_text("dummy file")
        test_config["source_directory"] = str(dummy_file)
        # Act & Assert
        with pytest.raises(ConfigError) as excinfo:
            validate_config(test_config)
        assert excinfo.value.key == "source_dir_not_dir"

    @pytest.mark.parametrize("invalid_val", [1, "true", []])
    def test_dry_run_invalid_type(self, test_config, invalid_val):
        """dry_run の型が bool 以外の場合"""
        # Arrange
        test_config["dry_run"] = invalid_val
        # Act & Assert
        with pytest.raises(ConfigError) as excinfo:
            validate_config(test_config)
        assert excinfo.value.key == "dry_run_not_bool"

    def test_rules_missing(self, test_config):
        """rulesキーが欠落している場合"""
        del test_config["rules"]
        with pytest.raises(ConfigError) as excinfo:
            validate_config(test_config)
        assert excinfo.value.key == "rules_not_exist"

    def test_rules_invalid_type(self, test_config):
        """rules がリストではない場合"""
        test_config["rules"] = "not a list"
        with pytest.raises(ConfigError) as excinfo:
            validate_config(test_config)
        assert excinfo.value.key == "rules_not_list"
    

class TestValidateRule:

    @pytest.mark.parametrize("ext, expected_key", [
        (123, "extension_not_str"),
        ("txt", "extension_must_start_with_dot"),
        ("", "extension_must_start_with_dot"),
    ])
    def test_invalid_extensions(self, ext, expected_key):
        rule = {"extension": ext, "destination": "docs"}
        with pytest.raises(ExtensionError) as excinfo:
            _validate_single_rule(rule)
        assert excinfo.value.key == expected_key

    def test_destination_missing(self):
        rule = {"extension": ".txt"}
        with pytest.raises(DestinationError) as excinfo:
            _validate_single_rule(rule)
        assert excinfo.value.key == "destination_required"
    
    def test_destination_invalid_type(self):
        rule = {"extension": ".txt", "destination": 123}
        with pytest.raises(DestinationError) as excinfo:
            _validate_single_rule(rule)
        assert excinfo.value.key == "destination_not_str"
