"""Tests unitarios del descubrimiento de herramientas."""

from pathlib import Path

from pcb_ai import tools as tools_mod
from pcb_ai.tools import ToolInfo, discover_tool


def test_discover_tool_missing():
    info = discover_tool("herramienta-inexistente-xyz", required=False, config_paths={})
    assert info.status == "MISSING"
    assert info.path is None


def test_discover_tool_broken_config_path():
    info = discover_tool(
        "kicad-cli", required=True, config_paths={"kicad-cli": r"C:\no\existe\kicad-cli.exe"}
    )
    assert info.status == "BROKEN"
    assert any("inexistente" in n for n in info.notes)


def test_discover_python_in_path():
    info = discover_tool("python", required=True, config_paths={})
    assert info.status == "OK"
    assert info.version


def test_write_tools_yaml_preserves_manual_paths(tmp_path, monkeypatch):
    cfg = tmp_path / "config" / "tools.yaml"
    cfg.parent.mkdir(parents=True)
    cfg.write_text("paths:\n  ngspice: C:/custom/ngspice.exe\n", encoding="utf-8")
    monkeypatch.setattr(tools_mod, "TOOLS_CONFIG", cfg)

    result = tools_mod.write_tools_yaml(
        [ToolInfo(name="git", required=True, path="C:/git.exe", version="2.54", status="OK")]
    )

    assert result == cfg
    content = cfg.read_text(encoding="utf-8")
    assert "C:/custom/ngspice.exe" in content  # override manual preservado
    assert "git" in content


def test_project_root_is_repo():
    assert (Path(tools_mod.PROJECT_ROOT) / "pyproject.toml").exists()
