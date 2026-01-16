"""
Configuration loader for MRS Viewer application.

Loads settings from config.yaml and provides typed access to configuration values.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Any
import yaml


# =============================================================================
# Configuration Dataclasses
# =============================================================================

@dataclass
class ServerConfig:
    """Server settings."""
    port: int = 8050
    host: str = "127.0.0.1"
    debug: bool = True


@dataclass
class DatabaseConfig:
    """Database connection settings."""
    path: str = "../monras_import.sqlite"
    max_points: int = 50000
    
    def get_absolute_path(self, base_dir: Path) -> Path:
        """Resolve database path relative to config file location."""
        return (base_dir / self.path).resolve()


@dataclass
class LayoutConfig:
    """Layout dimensions."""
    sidebar_width: int = 2
    main_area_width: int = 10
    left_chart_width: int = 8
    right_chart_width: int = 4
    scatter_height: int = 420
    boxplot_height: int = 420
    histogram_height: int = 420
    table_height: int = 420


@dataclass
class TableDisplayConfig:
    """Data table settings."""
    page_size: int = 50
    min_column_width: int = 100


@dataclass
class HistogramConfig:
    """Histogram settings."""
    default_bins: int = 25
    min_bins: int = 5
    max_bins: int = 100
    bin_step: int = 5
    all_data_color: str = "steelblue"
    all_data_opacity: float = 0.5
    selected_color: str = "red"
    selected_opacity: float = 0.7


@dataclass
class BoxplotConfig:
    """Boxplot settings."""
    max_categories: int = 10
    summary_color: str = "steelblue"


@dataclass
class ScatterConfig:
    """Scatter plot settings."""
    marker_size_normal: int = 8
    marker_size_selected: int = 10
    marker_size_highlight: int = 14
    marker_size_outlier: int = 12
    opacity_normal: float = 0.7
    opacity_selected: float = 0.9
    opacity_dimmed: float = 0.3
    default_color: str = "steelblue"
    selection_color: str = "red"
    outlier_color: str = "purple"
    reference_fill_color: str = "rgba(144, 238, 144, 0.2)"
    ti90_color: str = "blue"
    ti95_color: str = "orange"
    ti99_color: str = "red"


@dataclass
class TablePrefilter:
    """
    Prefilter configuration for a specific database table.
    
    Only matching rows will be loaded into the application.
    Empty lists mean "load all values" for that column.
    """
    nuklidy: List[str] = field(default_factory=list)
    lokality: List[str] = field(default_factory=list)
    dodavatele: List[str] = field(default_factory=list)
    exclude_mva: bool = False
    min_date: Optional[str] = None
    max_date: Optional[str] = None


@dataclass
class AppConfig:
    """Main application configuration."""
    server: ServerConfig = field(default_factory=ServerConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    layout: LayoutConfig = field(default_factory=LayoutConfig)
    table: TableDisplayConfig = field(default_factory=TableDisplayConfig)
    histogram: HistogramConfig = field(default_factory=HistogramConfig)
    boxplot: BoxplotConfig = field(default_factory=BoxplotConfig)
    scatter: ScatterConfig = field(default_factory=ScatterConfig)
    category_colors: List[str] = field(default_factory=lambda: [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
    ])
    table_prefilters: Dict[str, TablePrefilter] = field(default_factory=dict)
    hidden_tables: List[str] = field(default_factory=list)
    
    # Internal: base directory for resolving relative paths
    _base_dir: Path = field(default_factory=lambda: Path(__file__).parent)


# =============================================================================
# Configuration Loading
# =============================================================================

def _parse_prefilter(data: dict) -> TablePrefilter:
    """Parse a table prefilter from YAML dict."""
    return TablePrefilter(
        nuklidy=data.get("nuklidy", []) or [],
        lokality=data.get("lokality", []) or [],
        dodavatele=data.get("dodavatele", []) or [],
        exclude_mva=data.get("exclude_mva", False),
        min_date=data.get("min_date"),
        max_date=data.get("max_date"),
    )


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config.yaml. If None, looks for config.yaml
                     in the same directory as this module.
    
    Returns:
        AppConfig instance with loaded values.
    """
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        print(f"Warning: Config file not found at {config_path}, using defaults")
        return AppConfig()
    
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    
    # Parse sub-configurations
    server_data = data.get("server", {})
    db_data = data.get("database", {})
    layout_data = data.get("layout", {})
    table_data = data.get("table", {})
    hist_data = data.get("histogram", {})
    box_data = data.get("boxplot", {})
    scatter_data = data.get("scatter", {})
    
    # Parse prefilters
    prefilters_data = data.get("table_prefilters", {})
    prefilters = {
        name: _parse_prefilter(pf_data) 
        for name, pf_data in prefilters_data.items()
    }
    
    return AppConfig(
        server=ServerConfig(
            port=server_data.get("port", 8050),
            host=server_data.get("host", "127.0.0.1"),
            debug=server_data.get("debug", True),
        ),
        database=DatabaseConfig(
            path=db_data.get("path", "../monras_import.sqlite"),
            max_points=db_data.get("max_points", 50000),
        ),
        layout=LayoutConfig(
            sidebar_width=layout_data.get("sidebar_width", 2),
            main_area_width=layout_data.get("main_area_width", 10),
            left_chart_width=layout_data.get("left_chart_width", 8),
            right_chart_width=layout_data.get("right_chart_width", 4),
            scatter_height=layout_data.get("scatter_height", 420),
            boxplot_height=layout_data.get("boxplot_height", 420),
            histogram_height=layout_data.get("histogram_height", 420),
            table_height=layout_data.get("table_height", 420),
        ),
        table=TableDisplayConfig(
            page_size=table_data.get("page_size", 50),
            min_column_width=table_data.get("min_column_width", 100),
        ),
        histogram=HistogramConfig(
            default_bins=hist_data.get("default_bins", 25),
            min_bins=hist_data.get("min_bins", 5),
            max_bins=hist_data.get("max_bins", 100),
            bin_step=hist_data.get("bin_step", 5),
            all_data_color=hist_data.get("all_data_color", "steelblue"),
            all_data_opacity=hist_data.get("all_data_opacity", 0.5),
            selected_color=hist_data.get("selected_color", "red"),
            selected_opacity=hist_data.get("selected_opacity", 0.7),
        ),
        boxplot=BoxplotConfig(
            max_categories=box_data.get("max_categories", 10),
            summary_color=box_data.get("summary_color", "steelblue"),
        ),
        scatter=ScatterConfig(
            marker_size_normal=scatter_data.get("marker_size_normal", 8),
            marker_size_selected=scatter_data.get("marker_size_selected", 10),
            marker_size_highlight=scatter_data.get("marker_size_highlight", 14),
            marker_size_outlier=scatter_data.get("marker_size_outlier", 12),
            opacity_normal=scatter_data.get("opacity_normal", 0.7),
            opacity_selected=scatter_data.get("opacity_selected", 0.9),
            opacity_dimmed=scatter_data.get("opacity_dimmed", 0.3),
            default_color=scatter_data.get("default_color", "steelblue"),
            selection_color=scatter_data.get("selection_color", "red"),
            outlier_color=scatter_data.get("outlier_color", "purple"),
            reference_fill_color=scatter_data.get("reference_fill_color", "rgba(144, 238, 144, 0.2)"),
            ti90_color=scatter_data.get("ti90_color", "blue"),
            ti95_color=scatter_data.get("ti95_color", "orange"),
            ti99_color=scatter_data.get("ti99_color", "red"),
        ),
        category_colors=data.get("category_colors", [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
            "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
        ]),
        table_prefilters=prefilters,
        hidden_tables=data.get("hidden_tables", []) or [],
        _base_dir=config_path.parent,
    )


# =============================================================================
# Helper Functions
# =============================================================================

def get_table_prefilter(table_name: str) -> Optional[TablePrefilter]:
    """Get prefilter for a specific table, or None if no prefilter defined."""
    return config.table_prefilters.get(table_name)


def build_prefilter_conditions(table_name: str) -> tuple[list[str], list[Any]]:
    """
    Build SQL WHERE conditions and parameters from table prefilter.
    
    Returns:
        (conditions, params) - List of SQL conditions and list of parameters.
        Empty lists if no prefilter or prefilter has no active filters.
    
    Example:
        conditions, params = build_prefilter_conditions("aerosoly")
        # conditions = ["nuklid IN (?, ?)", "odber_misto IN (?)"]
        # params = ["Cs 137", "Be 7", "Praha"]
    """
    prefilter = get_table_prefilter(table_name)
    
    if prefilter is None:
        return [], []
    
    conditions = []
    params = []
    
    if prefilter.nuklidy:
        placeholders = ", ".join("?" * len(prefilter.nuklidy))
        conditions.append(f"nuklid IN ({placeholders})")
        params.extend(prefilter.nuklidy)
    
    if prefilter.lokality:
        placeholders = ", ".join("?" * len(prefilter.lokality))
        conditions.append(f"odber_misto IN ({placeholders})")
        params.extend(prefilter.lokality)
    
    if prefilter.dodavatele:
        placeholders = ", ".join("?" * len(prefilter.dodavatele))
        conditions.append(f"dodavatel_dat IN ({placeholders})")
        params.extend(prefilter.dodavatele)
    
    if prefilter.exclude_mva:
        conditions.append("(pod_mva IS NULL OR pod_mva != 1)")
    
    if prefilter.min_date:
        conditions.append("datum >= ?")
        params.append(prefilter.min_date)
    
    if prefilter.max_date:
        conditions.append("datum <= ?")
        params.append(prefilter.max_date)
    
    return conditions, params


def get_visible_tables(all_tables: List[str]) -> List[str]:
    """Filter out hidden tables from the list."""
    hidden = set(config.hidden_tables)
    return [t for t in all_tables if t not in hidden]


def get_db_path() -> Path:
    """Get absolute path to the database."""
    return config.database.get_absolute_path(config._base_dir)


def get_config_path() -> Path:
    """Get the path to the config.yaml file."""
    # Check user directory first
    user_config = Path.home() / ".mrs_viewer" / "config.yaml"
    if user_config.exists():
        return user_config
    
    # Check app directory
    app_config = Path(__file__).parent / "config.yaml"
    if app_config.exists():
        return app_config
    
    # Default location for creating new config
    return app_config


def reload_config() -> AppConfig:
    """
    Reload the configuration from disk.
    
    Updates the global config instance and returns it.
    Use this after modifying config.yaml to apply changes.
    """
    global config
    config = load_config()
    return config


# =============================================================================
# Global Configuration Instance
# =============================================================================
# This is loaded once when the module is imported.
# Import in other modules: from app.config import config

config = load_config()
