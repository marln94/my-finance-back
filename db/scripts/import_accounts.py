import csv
import json
from typing import Dict, Optional

def parse_account_type(code: str) -> str:
    """Determine account type based on code prefix"""
    if code.startswith('1-'):
        return 'activo'
    elif code.startswith('2-'):
        return 'pasivo'
    elif code.startswith('3-'):
        return 'patrimonio'
    elif code.startswith('4-'):
        return 'ingresos'
    elif code.startswith('5-'):
        return 'egresos'
    else:
        return 'activo'  # default

def parse_normal_side(tipo_saldo: str) -> str:
    """Convert 'Tipo de Saldo' to normal_side"""
    if tipo_saldo.lower() == 'deudor':
        return 'debe'
    elif tipo_saldo.lower() == 'acreedor':
        return 'haber'
    else:
        return 'debe'  # default

def escape_sql_string(s: str) -> str:
    """Escape single quotes for SQL"""
    return s.replace("'", "''")

def generate_insert_statements(csv_file: str, output_file: str = 'accounts_insert.sql'):
    """Generate SQL INSERT statements from CSV"""
    
    # Store accounts by code for parent lookup
    accounts_by_code: Dict[str, Dict] = {}
    
    # Read CSV and process accounts
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            code = row['Código'].strip()
            name = row['Nombre'].strip()
            tipo_saldo = row['Tipo de Saldo'].strip()
            
            # Determine parent code (the immediate parent in hierarchy)
            parent_code = row.get('Código Cuenta 2', '').strip() or None
            
            # Build extra_data with hierarchy information
            extra_data = {}
            if row.get('Identificador Bancario', '').strip():
                extra_data['identificador_bancario'] = row['Identificador Bancario'].strip()
            
            # Store hierarchy information
            if row.get('Código Cuenta 2'):
                extra_data['cuenta_2'] = {
                    'codigo': row['Código Cuenta 2'].strip(),
                    'nombre': row['Cuenta 2'].strip()
                }
            if row.get('Código Cuenta 3'):
                extra_data['cuenta_3'] = {
                    'codigo': row['Código Cuenta 3'].strip(),
                    'nombre': row['Cuenta 3'].strip()
                }
            if row.get('Código Cuenta 4'):
                extra_data['cuenta_4'] = {
                    'codigo': row['Código Cuenta 4'].strip(),
                    'nombre': row['Cuenta 4'].strip()
                }
            
            accounts_by_code[code] = {
                'code': code,
                'name': name,
                'type': parse_account_type(code),
                'normal_side': parse_normal_side(tipo_saldo),
                'parent_code': parent_code,
                'extra_data': extra_data
            }
            
            # Create parent accounts from hierarchy if they don't exist
            # Process Cuenta 4 (top level)
            if row.get('Código Cuenta 4', '').strip() and row.get('Cuenta 4', '').strip():
                parent_code_4 = row['Código Cuenta 4'].strip()
                parent_name_4 = row['Cuenta 4'].strip()
                if parent_code_4 not in accounts_by_code:
                    accounts_by_code[parent_code_4] = {
                        'code': parent_code_4,
                        'name': parent_name_4,
                        'type': parse_account_type(parent_code_4),
                        'normal_side': 'debe',  # Default for parent accounts
                        'parent_code': None,
                        'extra_data': {}
                    }
            
            # Process Cuenta 3
            if row.get('Código Cuenta 3', '').strip() and row.get('Cuenta 3', '').strip():
                parent_code_3 = row['Código Cuenta 3'].strip()
                parent_name_3 = row['Cuenta 3'].strip()
                if parent_code_3 not in accounts_by_code:
                    # Link to Cuenta 4 if exists
                    parent_of_3 = row.get('Código Cuenta 4', '').strip() or None
                    accounts_by_code[parent_code_3] = {
                        'code': parent_code_3,
                        'name': parent_name_3,
                        'type': parse_account_type(parent_code_3),
                        'normal_side': 'debe',
                        'parent_code': parent_of_3,
                        'extra_data': {}
                    }
            
            # Process Cuenta 2
            if row.get('Código Cuenta 2', '').strip() and row.get('Cuenta 2', '').strip():
                parent_code_2 = row['Código Cuenta 2'].strip()
                parent_name_2 = row['Cuenta 2'].strip()
                if parent_code_2 not in accounts_by_code:
                    # Link to Cuenta 3 if exists
                    parent_of_2 = row.get('Código Cuenta 3', '').strip() or None
                    accounts_by_code[parent_code_2] = {
                        'code': parent_code_2,
                        'name': parent_name_2,
                        'type': parse_account_type(parent_code_2),
                        'normal_side': 'debe',
                        'parent_code': parent_of_2,
                        'extra_data': {}
                    }
    
    # Generate SQL statements
    sql_statements = []
    sql_statements.append("-- Insert accounts in hierarchical order\n")
    sql_statements.append("BEGIN;\n")
    
    # Sort accounts by code to ensure parents are inserted before children
    sorted_accounts = sorted(accounts_by_code.values(), key=lambda x: x['code'])
    
    for account in sorted_accounts:
        name_escaped = escape_sql_string(account['name'])
        code_escaped = escape_sql_string(account['code'])
        extra_data_json = json.dumps(account['extra_data'], ensure_ascii=False)
        extra_data_escaped = escape_sql_string(extra_data_json)
        
        # Handle parent_id reference
        if account['parent_code']:
            parent_code_escaped = escape_sql_string(account['parent_code'])
            parent_clause = f"(SELECT id FROM accounts WHERE code = '{parent_code_escaped}')"
        else:
            parent_clause = "NULL"
        
        sql = f"""INSERT INTO accounts (name, type, code, normal_side, extra_data, parent_id)
VALUES ('{name_escaped}', '{account['type']}', '{code_escaped}', '{account['normal_side']}', '{extra_data_escaped}'::jsonb, {parent_clause});
"""
        sql_statements.append(sql)
    
    sql_statements.append("\nCOMMIT;")
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(sql_statements)
    
    print(f"Generated {len(sorted_accounts)} INSERT statements")
    print(f"Output written to: {output_file}")
    
    return sql_statements

if __name__ == "__main__":
    # Usage example
    csv_file = "accounts.csv"  # Change this to your CSV file path
    output_file = "accounts_insert.sql"
    
    try:
        generate_insert_statements(csv_file, output_file)
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found")
    except Exception as e:
        print(f"Error: {e}")