import pytest
import json
from pathlib import Path
from config.errors import MoveError
from services import move_action


@pytest.fixture
def temp_setup(tmp_path):
    """テスト用のディレクトリとファイル構造を準備するフィクスチャ"""
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    src_dir.mkdir()
    
    # テストファイルの作成
    test_file = src_dir / "test.txt"
    test_file.write_text("hello")
    
    return {
        "src_dir": src_dir,
        "dst_dir": dst_dir,
        "test_file": test_file,
        "history_file": tmp_path / "history.json"
    }


class TestGetDestination:
    def test_success(self):
        # Arrange
        item = Path("test_file.txt")
        rule = {"extension": ".txt", "destination": "docs"}
        # Act & Assert
        assert move_action.get_destination(item, [rule]) == "docs"

    def test_no_match(self):
        # Arrange
        item = Path("test.jpg")
        rules = [{"extension": ".txt", "destination": "docs"}]
        # Act & Assert
        assert move_action.get_destination(item, rules) == "jpg"


class TestExecuteMoves:
    def test_success(self, temp_setup):
        # Arrange
        src = temp_setup["test_file"]
        dst = temp_setup["dst_dir"] / "test.txt"
        
        planned_moves = [{"src": src, "dst": dst}]
        # Act
        move_action.execute_moves(planned_moves)
        # Assert
        assert not src.exists()
        assert dst.exists()
        assert dst.read_text() == "hello"

    def test_failure_invalid_src(self, temp_setup):
        # Arrange
        src = temp_setup["src_dir"] / "non_existent.txt"
        dst = temp_setup["dst_dir"] / "test.txt"

        planned_moves = [{"src": src, "dst": dst}]
        # Act & Assert
        with pytest.raises(MoveError) as excinfo:
            move_action.execute_moves(planned_moves)
        assert excinfo.value.key == "move_failed"


class TestSaveLatestChange:
    def test_success(self, temp_setup, monkeypatch):
        # Arrange
        monkeypatch.setattr(move_action, "LATEST_CHANGE_FILE", temp_setup["history_file"])
        planned_moves = [{"src": Path("a.txt"), "dst": Path("dir/a.txt")}]
        # Act
        move_action.save_latest_change(planned_moves)
        # Assert
        assert temp_setup["history_file"].exists()
        with open(temp_setup["history_file"], "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data[0]["src"] == "a.txt"

    def test_failure(self, temp_setup, monkeypatch):
        # Arrange:
        monkeypatch.setattr(move_action, "LATEST_CHANGE_FILE", temp_setup["src_dir"])
        
        planned_moves = [{"src": Path("a.txt"), "dst": Path("dir/a.txt")}]
        
        # Act & Assert
        with pytest.raises(MoveError) as excinfo:
            move_action.save_latest_change(planned_moves)
        assert excinfo.value.key == "save_history_failed"
    

class TestClearHistory:
    def test_success(self, temp_setup, monkeypatch):
        # Arrange
        history_file = temp_setup["history_file"]
        history_file.write_text("[]")
        monkeypatch.setattr(move_action, "LATEST_CHANGE_FILE", history_file)
        # Act
        move_action.clear_undo_history()
        # Assert
        assert not history_file.exists()

    def test_failure(self, temp_setup, monkeypatch):
        # Arrange
        # unlink() はファイル用のため、ディレクトリに対して実行するさせる
        bad_path = temp_setup["src_dir"]
        monkeypatch.setattr(move_action, "LATEST_CHANGE_FILE", bad_path)

        # Act & Assert
        with pytest.raises(MoveError) as excinfo:
            move_action.clear_undo_history()
        assert excinfo.value.key == "delete_history_failed"


class TestBuildMovePlan:
    def test_success(self, temp_setup):
        # Arrange
        config = {
            "source_directory": str(temp_setup["src_dir"]),
            "rules": [{"extension": ".txt", "destination": "text_files"}]
        }
        # Act
        plan = move_action.build_move_plan(config)
        # Assert
        assert len(plan) == 1
        assert plan[0]["src"] == temp_setup["test_file"]
        assert plan[0]["dst"] == (temp_setup["src_dir"]/ "text_files" / "test.txt")


class TestBuildUndoPlan:
    def test_success(self, temp_setup, monkeypatch):
        # Arrange
        history_file = temp_setup["history_file"]
        data = [{"src": "source/a.txt", "dst": "dest/a.txt"}]
        history_file.write_text(json.dumps(data), encoding="utf-8")
        monkeypatch.setattr(move_action, "LATEST_CHANGE_FILE", history_file)
        # Act
        undo_plan = move_action.build_undo_plan()
        # Assert
        assert len(undo_plan) == 1
        assert undo_plan[0]["src"] == Path("dest/a.txt")
        assert undo_plan[0]["dst"] == Path("source/a.txt")

    def test_no_history(self, tmp_path, monkeypatch):
        # 履歴ファイルがない場合
        monkeypatch.setattr(move_action, "LATEST_CHANGE_FILE", tmp_path / "none.json")
        assert move_action.build_undo_plan() == []

    def test_failure(self, temp_setup, monkeypatch):
        # Arrange: 壊れたJSONファイルを書き込む
        history_file = temp_setup["history_file"]
        history_file.write_text("invalid json content", encoding="utf-8")
        monkeypatch.setattr(move_action, "LATEST_CHANGE_FILE", history_file)

        # Act & Assert
        with pytest.raises(MoveError) as excinfo:
            move_action.build_undo_plan()
        assert excinfo.value.key == "read_history_failed"
