import csv
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

def parse_date(date_str: str) -> str:
    """Parse date string to SQL date format"""
    try:
        # Try parsing DD/MM/YYYY format
        dt = datetime.strptime(date_str.strip(), '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        # Try other common formats
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y']:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
    raise ValueError(f"Cannot parse date: {date_str}")

def parse_amount(amount_str: str) -> float:
    """Parse amount string to float, handling currency symbols and formatting"""
    if not amount_str or amount_str.strip() == '':
        return 0.0
    
    # Remove currency symbols (L, $, etc.), commas, and extra spaces
    cleaned = re.sub(r'[L$,\s]', '', amount_str.strip())
    
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def escape_sql_string(s: str) -> str:
    """Escape single quotes for SQL"""
    if s is None:
        return ''
    return s.replace("'", "''")

def parse_journal_number(numero_partida: str) -> Optional[int]:
    """Remove MY- prefix and convert to integer"""
    if not numero_partida or numero_partida.strip() == '':
        return None
    
    # Remove MY- prefix (case insensitive)
    cleaned = re.sub(r'^MY-', '', numero_partida.strip(), flags=re.IGNORECASE)
    
    try:
        return int(cleaned)
    except ValueError:
        return None

def generate_insert_statements(csv_file: str, output_file: str = 'journals_insert.sql'):
    """Generate SQL INSERT statements from CSV"""
    
    # Group entries by journal number
    journals_data: Dict[Optional[int], List[Dict]] = defaultdict(list)
    single_entries: List[Dict] = []  # For entries without journal number
    
    # Read CSV and process entries
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            journal_number = parse_journal_number(row.get('Número de Partida', ''))
            account_code = row.get('Número de Cuenta', '').strip()
            account_name = row.get('Nombre de Cuenta', '').strip()
            description = row.get('Descripción', '').strip()
            debe = parse_amount(row.get('Debe', ''))
            haber = parse_amount(row.get('Haber', ''))
            date_str = row.get('Fecha', '').strip()
            estado_cuenta = row.get('Estado de cuenta', '').strip()
            proposito = row.get('Propósito Asignado', '').strip()
            
            # Skip rows with no amount
            if debe == 0.0 and haber == 0.0:
                continue
            
            entry_data = {
                'journal_number': journal_number,
                'account_code': account_code,
                'account_name': account_name,
                'description': description,
                'debe': debe,
                'haber': haber,
                'date': parse_date(date_str),
                'estado_cuenta': estado_cuenta,
                'proposito': proposito
            }
            
            if journal_number is None:
                single_entries.append(entry_data)
            else:
                journals_data[journal_number].append(entry_data)
    
    # Generate SQL statements
    sql_statements = []
    sql_statements.append("-- Insert journals and journal entries\n")
    sql_statements.append("BEGIN;\n\n")
    
    # Process grouped journals (with journal number)
    for journal_number, entries in sorted(journals_data.items()):
        if not entries:
            continue
        
        # Use first entry for journal-level data
        first_entry = entries[0]
        date_sql = first_entry['date']
        statement = first_entry['estado_cuenta']
        
        # Build metadata
        metadata = {
            'estado_cuenta': first_entry['estado_cuenta'],
            'original_journal_number': f"MY-{journal_number:05d}"
        }
        if first_entry['proposito']:
            metadata['proposito'] = first_entry['proposito']
        
        metadata_json = json.dumps(metadata, ensure_ascii=False)
        metadata_escaped = escape_sql_string(metadata_json)
        
        # Combine descriptions from all entries
        descriptions = [e['description'] for e in entries if e['description']]
        combined_description = ' | '.join(set(descriptions)) if descriptions else ''
        description_escaped = escape_sql_string(combined_description)
        
        # Insert journal with explicit journal_number
        sql_statements.append(f"-- Journal MY-{journal_number:05d}\n")
        sql_statements.append(f"""INSERT INTO journals (journal_number, description, date, metadata, statement)
VALUES ({journal_number}, '{description_escaped}', '{date_sql}', '{metadata_escaped}'::jsonb, '{statement}');
""")
        
        # Insert journal entries
        for entry in entries:
            account_code_escaped = escape_sql_string(entry['account_code'])
            entry_description_escaped = escape_sql_string(entry['description'])
            
            # Determine amount and side
            if entry['debe'] > 0:
                amount = entry['debe']
                side = 'debe'
            else:
                amount = entry['haber']
                side = 'haber'
            
            # Build entry metadata
            entry_metadata = {
                'proposito': entry['proposito']
            } if entry['proposito'] else None
            entry_metadata_json = json.dumps(entry_metadata, ensure_ascii=False)
            entry_metadata_escaped = escape_sql_string(entry_metadata_json)
            
            sql_statements.append(f"""INSERT INTO journal_entries (journal_id, account_id, amount, side, description, metadata)
VALUES (
    (SELECT id FROM journals WHERE journal_number = {journal_number}),
    (SELECT id FROM accounts WHERE code = '{account_code_escaped}'),
    {amount:.2f},
    '{side}',
    '{entry_description_escaped}',
    {f"'{entry_metadata_escaped}'" if entry_metadata else 'NULL'}
);
""")
        
        sql_statements.append("\n")
    
    # Process single entries (without journal number)
    if single_entries:
        sql_statements.append("-- Single entries without journal number\n\n")
        
        for entry in single_entries:
            date_sql = entry['date']
            description_escaped = escape_sql_string(entry['description'])
            account_code_escaped = escape_sql_string(entry['account_code'])
            
            # Build metadata
            metadata = {
                'estado_cuenta': entry['estado_cuenta'],
                'single_entry': True
            }
            if entry['proposito']:
                metadata['proposito'] = entry['proposito']
            
            metadata_json = json.dumps(metadata, ensure_ascii=False)
            metadata_escaped = escape_sql_string(metadata_json)
            
            # Insert journal (journal_number will be auto-generated)
            sql_statements.append(f"""INSERT INTO journals (description, date, metadata)
VALUES ('{description_escaped}', '{date_sql}', '{metadata_escaped}'::jsonb)
RETURNING id;
""")
            
            # Determine amount and side
            if entry['debe'] > 0:
                amount = entry['debe']
                side = 'debe'
            else:
                amount = entry['haber']
                side = 'haber'
            
            reference_escaped = escape_sql_string(entry['proposito']) if entry['proposito'] else ''
            
            # Note: This will need manual adjustment or a different approach
            # since we can't directly reference the RETURNING id in plain SQL
            sql_statements.append(f"""-- INSERT INTO journal_entries (journal_id, account_id, amount, side, description, reference)
-- VALUES (
--     <last_journal_id>,
--     (SELECT id FROM accounts WHERE code = '{account_code_escaped}'),
--     {amount:.2f},
--     '{side}',
--     '{description_escaped}',
--     '{reference_escaped}'
-- );
""")
            sql_statements.append("\n")
    
    sql_statements.append("COMMIT;\n")
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(sql_statements)
    
    total_journals = len(journals_data) + len(single_entries)
    total_entries = sum(len(entries) for entries in journals_data.values()) + len(single_entries)
    
    print(f"Generated {total_journals} journals with {total_entries} total entries")
    print(f"Output written to: {output_file}")
    print("\nNote: Single entries without journal numbers are commented out")
    print("      and require manual handling or use of a procedural approach (PL/pgSQL)")
    
    return sql_statements

if __name__ == "__main__":
    # Usage example
    csv_file = "journals.csv"  # Change this to your CSV file path
    output_file = "journals_insert.sql"
    
    try:
        generate_insert_statements(csv_file, output_file)
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()