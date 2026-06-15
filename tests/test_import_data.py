from pathlib import Path


def test_project_structure_exists():
    assert Path("app").is_dir()
    assert Path("app/import_data.py").is_file()
    assert Path("app/analysis.py").is_file()
    assert Path("app/main.py").is_file()
