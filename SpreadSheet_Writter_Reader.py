from oauth2client import file, client, tools
from httplib2 import Http
from googleapiclient.discovery import build
from read_write import WriteAds, ReadAds
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# My base code for a log generator read and write application using google drive
# Reads ads from a Googledrive Spreadsheet and saves it locally to a txt file
def read_and_write():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    store = file.Storage('../JSON/credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('../JSON/client_secret1.json', scope)
        creds = tools.run_flow(flow, store)

    service = build('sheets', 'v4', http=creds.authorize(Http()))

    spreadsheet_id = 'ENTER_SPREADSHEET_ID_HERE'
    # This is the first sheet of the spreadsheet and where I will be keeping all of the ads
    range_ = 'MASTER LOG'
    # If there are ads already saved I want to get them first
    # Note JsLint will say there is an error with service. There isn't.
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                 range=range_).execute()
    values = result.get('values', [])
    ad_dic = {}

    i = 0
    for row in values:
        # Skip The first 3 Lines as they are the Key for the rest of the SpreadSheet
        if i > 3:
            if len(row) < 7:
                # If we have less than 7 columns of information, skip it
                pass
            elif len(row) == 7:
                ad_dic[row[1]] = {'Date': row[0], 'Address': row[2], 'Platform Retrieved': row[3],
                                  'Phone': row[4], 'Email': row[5], 'Location': row[6]}

        i += 1
    WriteAds(ad_dic, '../Files,Databases/Master Log')


# This method is used to write to a SpreadSheet in Googledrive
# Within this method I utilize 2 different ways of accesing and updating spreadsheet data
# The first is to update on a row by row basis the other is row,column
def write_to():
    # initializing connection to Spreadsheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # credentials
    store = file.Storage('../JSON/credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('../JSON/client_secret1.json', scope)
        creds = tools.run_flow(flow, store)
    # credentials for the row,column functionality
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    # You can get the spreadsheet Id from your Googledrive
    spreadsheet_id = 'ENTER_SPREADSHEET_ID_HERE'
    # Credentials for the gspread Fuctions for the row update functionality
    credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    gc = gspread.authorize(credentials)
    # Get the Spread Sheet Names
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')
    # Storage variable for all the Sheet names
    sheet_names = []
    # This reads in all of the names of each sheet of this spreadsheet and adds it to
    # sheet_names which will be used later to save ads
    for i in range(1, len(sheets)):
        title_ = sheets[i]['properties']['title']
        sheet_id_ = sheets[i]['properties']['sheetId']
        # If there are Sheets that you don't want to save ads to Ignore them
        if title_ != 'IGNORE_SHEET1' and title_ != 'IGNORE_SHEET2' and title_ != 'IGNORE_SHEET3':
            sheet_names.append((title_, sheet_id_))
    # Read the scrapped adds
    new_ads = ReadAds('Recorded Ads')
    # Sanity Check
    print("Done reading.")
    # Variable that keeps all the ads in order to be submitted
    body = {
        'values': []
    }
    # This variable is used to split up the ads evenly into a preset number of sheets
    i = 0
    # This is where we Read all the Already Existing Ads scrapped off Kijiji
    # This Also Varies Depending on how you structure your spreadsheet
    range_ = 'NAME_OF_SHEET_WITH_ADs'

    # The Fields in the spread sheet are as follows
    # The Date the ad was posted, Ad Id, Address(hyperlinked), Platform in this case Kijiji,
    # Phone number if any, ...
    for key in new_ads:
        # if we could not find a phone number set it to N/A
        # don't want to have empty fields, might want to implement a phone look up later
        if new_ads[key]['phone'] == '':
            new_ads[key]['phone'] = "N/A"
        # Here I'm splitting up the generated ads b/w the length of sheet_names
        # Sheet_names are all the differing sheets you want to split up your ads to
        # In this project I was splitting up all the generated ads between a preset number
        # The -2 comes from the extra sheets that were also present but not important
        if i % len(sheet_names) - 2 == 0:
            # remember gc are your Gspread credentials
            wks = gc.open('SPREADSHEET_NAME').worksheet(sheet_names[0][0])
            # Adding new rows to your spredsheet can be done using this command
            wks.append_row([new_ads[key]['Date'], key,
                            '=HYPERLINK(\"' + new_ads[key]['Url'] + "\",\"" + new_ads[key]['Address'] + "\")",
                            'kijiji.ca',
                            new_ads[key]['phone'], 'N/A', new_ads[key]['Location'],
                            new_ads[key]['Property Type'], 'Kijiji Scrapper', sheet_names[0][0]],
                           value_input_option='USER_ENTERED')
            body['values'].append(
                [new_ads[key]['Date'], key,
                 '=HYPERLINK(\"' + new_ads[key]['Url'] + "\",\"" + new_ads[key]['Address'] + "\")",
                 'kijiji.ca',
                 new_ads[key]['phone'], 'N/A', new_ads[key]['Location'],
                 new_ads[key]['Property Type'], 'Kijiji Scrapper', sheet_names[0][0]])
        elif i % len(sheet_names) - 2 == 1:
            wks = gc.open('SPREADSHEET_NAME').worksheet(sheet_names[1][0])
            wks.append_row([new_ads[key]['Date'], key,
                            '=HYPERLINK(\"' + new_ads[key]['Url'] + "\",\"" + new_ads[key]['Address'] + "\")",
                            'kijiji.ca',
                            new_ads[key]['phone'], 'N/A', new_ads[key]['Location'],
                            new_ads[key]['Property Type'], 'Kijiji Scrapper', sheet_names[1][0], 'Open', '', '', '',
                            ''], value_input_option='USER_ENTERED')
            body['values'].append(
                [new_ads[key]['Date'], key,
                 '=HYPERLINK(\"' + new_ads[key]['Url'] + "\",\"" + new_ads[key]['Address'] + "\")",
                 'kijiji.ca',
                 new_ads[key]['phone'], 'N/A', new_ads[key]['Location'],
                 new_ads[key]['Property Type'], 'Kijiji Scrapper', sheet_names[1][0], 'Open', '', '', '',
                 ''])
        elif i % len(sheet_names) - 2 == 2:
            wks = gc.open('SPREADSHEET_NAME').worksheet(sheet_names[2][0])
            wks.append_row([new_ads[key]['Date'], key,
                            '=HYPERLINK(\"' + new_ads[key]['Url'] + "\",\"" + new_ads[key]['Address'] + "\")",
                            'kijiji.ca',
                            new_ads[key]['phone'], 'N/A', new_ads[key]['Location'],
                            new_ads[key]['Property Type'], 'Kijiji Scrapper', sheet_names[2][0], 'Open', '', '', '',
                            ''], value_input_option='USER_ENTERED')
            body['values'].append(
                [new_ads[key]['Date'], key,
                 '=HYPERLINK(\"' + new_ads[key]['Url'] + "\",\"" + new_ads[key]['Address'] + "\")",
                 'kijiji.ca',
                 new_ads[key]['phone'], 'N/A', new_ads[key]['Location'],
                 new_ads[key]['Property Type'], 'Kijiji Scrapper', sheet_names[2][0], 'Open', '', '', '',
                 ''])
        elif i % len(sheet_names) - 2 == 3:
            wks = gc.open('SPREADSHEET_NAME').worksheet(sheet_names[3][0])
            wks.append_row([new_ads[key]['Date'], key,
                            '=HYPERLINK(\"' + new_ads[key]['Url'] + "\",\"" + new_ads[key]['Address'] + "\")",
                            'kijiji.ca',
                            new_ads[key]['phone'], 'N/A', new_ads[key]['Location'],
                            new_ads[key]['Property Type'], 'Kijiji Scrapper', sheet_names[3][0], 'Open', '', '', '',
                            ''], value_input_option='USER_ENTERED')
            body['values'].append(
                [new_ads[key]['Date'], key,
                 '=HYPERLINK(\"' + new_ads[key]['Url'] + "\",\"" + new_ads[key]['Address'] + "\")",
                 'kijiji.ca',
                 new_ads[key]['phone'], 'N/A', new_ads[key]['Location'],
                 new_ads[key]['Property Type'], 'Kijiji Scrapper', sheet_names[4][0], 'Open', '', '', '',
                 ''])
        elif i % len(sheet_names) - 2 == 4:
            # Alternattive way of utilizing credentials
            result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                         range=sheet_names[4][0]).execute()
            values = result.get('values', [])
            place_holder = sheet_names[4][0]
            wks = gc.open('SPREADSHEET_NAME').worksheet(place_holder)
            # If you already have data that doesn't match and want to add your data to the next free row
            # k is a counter till the next available row
            k = len(values)

            values = [new_ads[key]['Date'], key,
                      '=HYPERLINK(\"' + new_ads[key]['Url'] + "\",\"" + new_ads[key]['Address'] + "\")",
                      'kijiji.ca',
                      new_ads[key]['phone'], 'N/A', new_ads[key]['Location'],
                      new_ads[key]['Property Type'], 'Kijiji Scrapper', place_holder, 'Open', '', '', '',
                      '']
            # You are also able to update individual cells
            for j in range(1, 11):
                wks.update_cell(k, j, values[j])
            body['values'].append(values)
        i += 1
    # After I have spread the ads among the sheets of my choosing
    # I finish by adding all of the ads to the the list of all the ads in MASTER LOG
    service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_,
                                           valueInputOption='USER_ENTERED',
                                           body=body, insertDataOption='INSERT_ROWS').execute()