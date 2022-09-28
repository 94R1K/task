from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

# Скрипт проверки настройки service аккаунта GoogleAPI
# Настроить аккаунт как описано в статье:
# https://habr.com/ru/post/483302/
# 
# указать путь к файлу с ключами:
CREDENTIALS_FILE = 'secret/credentials.json'
#
# Если ОК, в консоли будет выведен текст таблицы из двух столбцов,
# а в папке, где лежит файл CREDENTIALS_FILE появится новый
# файл token.json с access-токеном
# 
# Запускайте скрипт из папки, относительно которой
# указан путь к CREDENTIALS_FILE
# 


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'

TOKEN_FILENAME = 'token.json'


def main():
  token_path = os.path.join(os.path.dirname(CREDENTIALS_FILE), TOKEN_FILENAME)

  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if not os.path.exists(token_path):
    # создаю файл, если его нет
    with open(token_path, 'w'): pass
  creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                           SCOPES)

  # If there are no (valid) credentials available, let the user log in.
  if not creds:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())

  # Save the credentials for the next run
  print('creds ok', creds)
  with open(token_path, 'w') as token:
    token.write(creds.to_json())

  try:
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
      print('No data found.')
      return

    print('Name, Major:')
    for row in values:
      # Print columns A and E, which correspond to indices 0 and 4.
      print('%s, %s' % (row[0], row[4]))
  except HttpError as err:
    print(err)


if __name__ == '__main__':
  main()
