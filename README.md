## Kijiji Webscrapper
This Project was given to me by a friend as a means to improve my coding and ended up becoming a stepping stone. This is a short demo on webscrapping, multithreading, and some google APIs using kijiji as the website of choice. Keep in mind you shouldn't blast a website with requests as you are likely to get a time out if not a full ban.

## Tech/framework used

<b>Built with</b>
- [Python](https://www.python.org/)

## Features
- Upload/download to/from Google Spreadsheets
- Formating Spreadsheet information
- Read and Write to local storage
- Webscrapping

## API Reference

- [multiprocessing](https://docs.python.org/3.5/library/multiprocessing.html)
- [Bs4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [oauth2client](https://oauth2client.readthedocs.io/en/latest/#supported-python-versions)
- [httplib2](https://kite.com/python/docs/httplib2)
- [GoogleAPIs](https://developers.google.com/api-client-library/python/start/get_started)
- [gspread](https://gspread.readthedocs.io/en/latest/)

## Tests
Make sure all files are in thesame directory and Run Kijiji_Webscrapper. SpreadSheet_Writter_Reader will need to have a couple things changed. First you need to set up an excell spreadsheet and find it's spreadsheet id, next you need to download your client secret and credentials and link to the corresponding file directories. For more information about [credentials](https://developers.google.com/sheets/api/guides/authorizing). Finally make sure you go through the documentation for gspread and also the comments in SpreadSheet_Writter_Reader.
