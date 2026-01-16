"""
Suspicious records basket callbacks.

Handles adding, removing, and exporting suspicious records
that users identify during data analysis.
"""
import base64
import io
from datetime import datetime
from typing import Optional

import pandas as pd
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback_context, html, no_update, dcc

from .. import ids
from .status_log import add_log_entry


def register_suspicious_callbacks(app):
    """Register callbacks for suspicious records basket functionality."""
    
    @app.callback(
        [
            Output(ids.STORE_SUSPICIOUS, "data"),
            Output(ids.TOAST_CONTAINER, "children", allow_duplicate=True),
            Output(ids.STORE_STATUS_LOG, "data", allow_duplicate=True),
        ],
        Input(ids.BTN_ADD_TO_SUSPICIOUS, "n_clicks"),
        [
            State(ids.AGGRID_TABLE, "selectedRows"),
            State(ids.DROPDOWN_DATASET, "value"),
            State(ids.STORE_SUSPICIOUS, "data"),
            State(ids.STORE_STATUS_LOG, "data"),
        ],
        prevent_initial_call=True,
    )
    def add_to_suspicious(n_clicks, selected_rows, dataset, store_data, log_data):
        """Add selected rows from main table to suspicious basket."""
        if not n_clicks or not selected_rows or not dataset:
            return no_update, no_update, no_update
        
        # Get current records
        current_records = store_data.get("records", []) if store_data else []
        existing_keys = {r["row_key"] for r in current_records}
        
        # Add new records (skip duplicates)
        added_count = 0
        for row in selected_rows:
            row_key = row.get("row_key")
            if row_key and row_key not in existing_keys:
                # Add dataset info and timestamp
                record = {
                    "row_key": row_key,
                    "dataset": dataset,
                    "nuklid": row.get("nuklid", ""),
                    "datum": row.get("datum", ""),
                    "hodnota": row.get("hodnota", ""),
                    "nejistota": row.get("nejistota", ""),
                    "jednotka": row.get("jednotka", ""),
                    "odber_misto": row.get("odber_misto", ""),
                    "dodavatel_dat": row.get("dodavatel_dat", ""),
                    "id_zppr_vzorek": row.get("id_zppr_vzorek", ""),
                    "pod_mva": row.get("pod_mva", ""),
                    "added_at": datetime.now().isoformat(),
                }
                current_records.append(record)
                existing_keys.add(row_key)
                added_count += 1
        
        # Check limit (soft limit 1000)
        if len(current_records) > 1000:
            toast = dbc.Toast(
                f"Přidáno {added_count} záznamů. Zásobník obsahuje více než 1000 záznamů!",
                header="⚠️ Varování",
                icon="warning",
                duration=4000,
                is_open=True,
                style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 1000},
            )
            new_log = add_log_entry(log_data, f"Zásobník: přidáno {added_count}, celkem > 1000!", "warning")
        elif added_count > 0:
            toast = dbc.Toast(
                f"Přidáno {added_count} záznamů do zásobníku.",
                header="✓ Přidáno",
                icon="success",
                duration=3000,
                is_open=True,
                style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 1000},
            )
            new_log = add_log_entry(log_data, f"Zásobník: přidáno {added_count} záznamů", "success")
        else:
            toast = dbc.Toast(
                "Vybrané záznamy již jsou v zásobníku.",
                header="ℹ️ Info",
                icon="info",
                duration=3000,
                is_open=True,
                style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 1000},
            )
            new_log = add_log_entry(log_data, "Zásobník: záznamy již existují", "info")
        
        return {"records": current_records}, toast, new_log
    
    @app.callback(
        [
            Output(ids.STORE_SUSPICIOUS, "data", allow_duplicate=True),
            Output(ids.TOAST_CONTAINER, "children", allow_duplicate=True),
            Output(ids.STORE_STATUS_LOG, "data", allow_duplicate=True),
        ],
        Input(ids.BTN_CLEAR_SUSPICIOUS, "n_clicks"),
        [
            State(ids.AGGRID_SUSPICIOUS, "selectedRows"),
            State(ids.STORE_SUSPICIOUS, "data"),
            State(ids.STORE_STATUS_LOG, "data"),
        ],
        prevent_initial_call=True,
    )
    def remove_from_suspicious(n_clicks, selected_rows, store_data, log_data):
        """Remove selected rows from suspicious basket."""
        if not n_clicks:
            return no_update, no_update, no_update
        
        current_records = store_data.get("records", []) if store_data else []
        
        if not selected_rows:
            # If no rows selected, show info
            toast = dbc.Toast(
                "Nejsou vybrány žádné záznamy k odebrání.",
                header="ℹ️ Info",
                icon="info",
                duration=3000,
                is_open=True,
                style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 1000},
            )
            return no_update, toast, no_update
        
        # Get keys to remove
        keys_to_remove = {row.get("row_key") for row in selected_rows if row.get("row_key")}
        
        # Filter out removed records
        new_records = [r for r in current_records if r["row_key"] not in keys_to_remove]
        removed_count = len(current_records) - len(new_records)
        
        toast = dbc.Toast(
            f"Odebráno {removed_count} záznamů ze zásobníku.",
            header="✓ Odebráno",
            icon="success",
            duration=3000,
            is_open=True,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 1000},
        )
        
        new_log = add_log_entry(log_data, f"Zásobník: odebráno {removed_count} záznamů", "info")
        
        return {"records": new_records}, toast, new_log
    
    @app.callback(
        Output(ids.AGGRID_SUSPICIOUS, "rowData"),
        Input(ids.STORE_SUSPICIOUS, "data"),
    )
    def update_suspicious_table(store_data):
        """Update the suspicious table when store changes."""
        if not store_data:
            return []
        return store_data.get("records", [])
    
    @app.callback(
        Output(ids.SUSPICIOUS_COUNT_BADGE, "children"),
        Input(ids.STORE_SUSPICIOUS, "data"),
    )
    def update_suspicious_count(store_data):
        """Update the badge showing count of suspicious records."""
        if not store_data:
            return "0"
        count = len(store_data.get("records", []))
        return str(count)
    
    @app.callback(
        [
            Output(ids.DOWNLOAD_SUSPICIOUS, "data"),
            Output(ids.TOAST_CONTAINER, "children", allow_duplicate=True),
            Output(ids.STORE_STATUS_LOG, "data", allow_duplicate=True),
        ],
        Input(ids.BTN_EXPORT_SUSPICIOUS, "n_clicks"),
        [
            State(ids.STORE_SUSPICIOUS, "data"),
            State(ids.STORE_STATUS_LOG, "data"),
        ],
        prevent_initial_call=True,
    )
    def export_suspicious_to_excel(n_clicks, store_data, log_data):
        """Export suspicious records to Excel file."""
        if not n_clicks:
            return no_update, no_update, no_update
        
        records = store_data.get("records", []) if store_data else []
        
        if not records:
            toast = dbc.Toast(
                "Zásobník je prázdný - není co exportovat.",
                header="ℹ️ Info",
                icon="info",
                duration=3000,
                is_open=True,
                style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 1000},
            )
            return no_update, toast, no_update
        
        # Create DataFrame
        df = pd.DataFrame(records)
        
        # Select and reorder columns for export
        export_columns = [
            "dataset", "nuklid", "datum", "hodnota", "nejistota", "jednotka",
            "odber_misto", "dodavatel_dat", "id_zppr_vzorek", "pod_mva", "added_at"
        ]
        # Keep only existing columns
        export_columns = [c for c in export_columns if c in df.columns]
        df = df[export_columns]
        
        # Rename columns for export
        column_names = {
            "dataset": "Dataset",
            "nuklid": "Nuklid",
            "datum": "Datum",
            "hodnota": "Hodnota",
            "nejistota": "Nejistota",
            "jednotka": "Jednotka",
            "odber_misto": "Odběrové místo",
            "dodavatel_dat": "Dodavatel",
            "id_zppr_vzorek": "ID Vzorek",
            "pod_mva": "Pod MVA",
            "added_at": "Přidáno",
        }
        df = df.rename(columns=column_names)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"podezrele_zaznamy_{timestamp}.xlsx"
        
        # Create Excel file in memory with formatting
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Podezřelé záznamy", index=False)
            
            # Get workbook and worksheet for formatting
            workbook = writer.book
            worksheet = writer.sheets["Podezřelé záznamy"]
            
            # Header format
            header_format = workbook.add_format({
                "bold": True,
                "bg_color": "#FFC107",
                "border": 1,
            })
            
            # Apply header format
            for col_num, column in enumerate(df.columns):
                worksheet.write(0, col_num, column, header_format)
                # Auto-adjust column width
                max_len = max(
                    df[column].astype(str).map(len).max() if len(df) > 0 else 0,
                    len(column)
                )
                worksheet.set_column(col_num, col_num, min(max_len + 2, 50))
            
            # Freeze header row
            worksheet.freeze_panes(1, 0)
        
        output.seek(0)
        
        # Encode as base64 for download
        content_base64 = base64.b64encode(output.getvalue()).decode("utf-8")
        
        toast = dbc.Toast(
            f"Exportováno {len(records)} záznamů do {filename}",
            header="✓ Export dokončen",
            icon="success",
            duration=4000,
            is_open=True,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 1000},
        )
        
        new_log = add_log_entry(log_data, f"Export: {len(records)} záznamů → {filename}", "success")
        
        return dcc.send_bytes(output.getvalue(), filename), toast, new_log
