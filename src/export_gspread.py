import configparser
import csv
from pathlib import Path
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from my_logging import get_my_logger
logger = get_my_logger(__name__)


root_csv_dir = Path('../csv')
concat_csv_dir = root_csv_dir / 'concat'

def connect_gspread(json_path, spreadsheet_key):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
    gc = gspread.authorize(credentials)
    workbook = gc.open_by_key(spreadsheet_key)
    return workbook

def update_sheet(workbook, worksheet_name, csv_path):
    if not worksheet_name in [worksheet.title for worksheet in workbook.worksheets()]:
        workbook.add_worksheet(title=worksheet_name, rows=50, cols=50)
    ws = workbook.worksheet(worksheet_name)
    ws.clear()
    workbook.values_update(
        worksheet_name,
        params={'valueInputOption': 'USER_ENTERED'},
        body={'values': list(csv.reader(open(csv_path, encoding='utf-8')))}
    )
    

def main():
    config_ini = configparser.ConfigParser()
    config_ini.read('config.ini', encoding='utf-8')
    spreadsheet_key = config_ini.get('SPREAD_SHEET', 'Key')
    workbook = connect_gspread(json_path="client_secret.json", spreadsheet_key=spreadsheet_key)

    ## asset
    assets = [dict(config_ini.items(section)) for section in config_ini.sections() if "asset_" in section]
    for asset in assets:
        csv_path = concat_csv_dir / f"{asset['id']}.csv"
        if not csv_path.exists():
            continue
        update_sheet(workbook, asset['sheet_name'], csv_path)
        logger.info(f"{asset['sheet_name']}: {csv_path}")
    
    ## history
    csv_path = root_csv_dir / "all_history_with_profit_and_loss.csv"
    sheet_name = config_ini.get('SPREAD_SHEET', 'Worksheet_name')
    update_sheet(workbook, sheet_name, csv_path)
    logger.info(f"{sheet_name}: {csv_path}")


if __name__ == "__main__":
    main()