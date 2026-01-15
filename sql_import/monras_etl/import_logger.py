"""
Modul pro sběr a logování problémů během importu.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
from datetime import datetime


@dataclass
class ImportProblem:
    """Jeden problém nalezený během importu."""
    file: str
    sheet: str
    column: str
    row: Optional[int]  # None pokud se týká celého sloupce
    value: str
    problem_type: str
    message: str


@dataclass
class ImportLogger:
    """Sbírá problémy během importu a zapisuje je do souboru."""
    problems: List[ImportProblem] = field(default_factory=list)
    
    def add(self, 
            file: str, 
            sheet: str, 
            column: str, 
            row: Optional[int], 
            value: str, 
            problem_type: str, 
            message: str) -> None:
        """Přidá problém do seznamu."""
        self.problems.append(ImportProblem(
            file=file,
            sheet=sheet,
            column=column,
            row=row,
            value=str(value)[:100],  # Omezíme délku hodnoty
            problem_type=problem_type,
            message=message
        ))
    
    def add_value_overflow(self, file: str, sheet: str, column: str, row: int, value) -> None:
        """Hodnota je příliš velká pro SQLite INTEGER."""
        self.add(file, sheet, column, row, str(value), 
                 "VALUE_OVERFLOW", 
                 f"Hodnota příliš velká pro SQLite INTEGER (max 2^63-1)")
    
    def add_parse_error(self, file: str, sheet: str, column: str, row: int, value, expected_type: str) -> None:
        """Hodnotu nelze parsovat na očekávaný typ."""
        self.add(file, sheet, column, row, str(value),
                 "PARSE_ERROR",
                 f"Nelze převést na {expected_type}")
    
    def add_datetime_error(self, file: str, sheet: str, column: str, row: int, value) -> None:
        """Neplatný datetime formát."""
        self.add(file, sheet, column, row, str(value),
                 "DATETIME_ERROR",
                 "Neplatný formát data/času")
    
    def add_header_not_found(self, file: str, message: str) -> None:
        """Hlavička nebyla nalezena."""
        self.add(file, "", "", None, "",
                 "HEADER_NOT_FOUND",
                 message)
    
    def add_general_error(self, file: str, sheet: str, message: str) -> None:
        """Obecná chyba při zpracování."""
        self.add(file, sheet, "", None, "",
                 "GENERAL_ERROR",
                 message)
    
    def has_problems(self) -> bool:
        """Vrací True pokud byly nalezeny nějaké problémy."""
        return len(self.problems) > 0
    
    def count(self) -> int:
        """Vrací počet problémů."""
        return len(self.problems)
    
    def write_report(self, output_path: Path) -> None:
        """Zapíše report problémů do textového souboru."""
        if not self.problems:
            return
        
        output_path = Path(output_path)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write(f"REPORT PROBLÉMŮ Z IMPORTU XLSX -> SQLite\n")
            f.write(f"Vygenerováno: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Celkem problémů: {len(self.problems)}\n")
            f.write("=" * 80 + "\n\n")
            
            # Seskupit podle souboru
            by_file = {}
            for p in self.problems:
                if p.file not in by_file:
                    by_file[p.file] = []
                by_file[p.file].append(p)
            
            for file, problems in sorted(by_file.items()):
                f.write("-" * 80 + "\n")
                f.write(f"SOUBOR: {file}\n")
                f.write(f"Počet problémů: {len(problems)}\n")
                f.write("-" * 80 + "\n\n")
                
                # Seskupit podle typu problému
                by_type = {}
                for p in problems:
                    if p.problem_type not in by_type:
                        by_type[p.problem_type] = []
                    by_type[p.problem_type].append(p)
                
                for ptype, type_problems in sorted(by_type.items()):
                    f.write(f"  [{ptype}] ({len(type_problems)}x)\n")
                    
                    for p in type_problems[:20]:  # Max 20 příkladů na typ
                        if p.row is not None:
                            f.write(f"    - Řádek {p.row}, sloupec '{p.column}': {p.message}\n")
                            if p.value:
                                f.write(f"      Hodnota: {p.value}\n")
                        elif p.column:
                            f.write(f"    - Sloupec '{p.column}': {p.message}\n")
                        else:
                            f.write(f"    - {p.message}\n")
                    
                    if len(type_problems) > 20:
                        f.write(f"    ... a dalších {len(type_problems) - 20} podobných problémů\n")
                    
                    f.write("\n")
                
                f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("KONEC REPORTU\n")
            f.write("=" * 80 + "\n")
    
    def print_summary(self) -> None:
        """Vypíše souhrn problémů na stdout."""
        if not self.problems:
            return
        
        # Počet podle typu
        by_type = {}
        for p in self.problems:
            by_type[p.problem_type] = by_type.get(p.problem_type, 0) + 1
        
        print(f"\n⚠️  Nalezeno {len(self.problems)} problémů:")
        for ptype, count in sorted(by_type.items()):
            print(f"   - {ptype}: {count}x")
