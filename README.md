## Immotop.exe

    1. Configure your config.json
    2. Launch exe file
    3. Give the path of the exe file
    4. The excel will be saved in the Outputs folder and the log will be saved in the Log folder

## How does the code work

Depending on the config.json, the code starts to create the url to scrape (thanks to translate_to_url.json).

Then, for each url, the code scrapes the overview pages to get the url of each property. If a property is a project ("parent" property) and contains several properties ("child" properties), the url of the parent is kept and the url of the children are extracted from the web page of the parent.

Finaly, the code scrape each property page by scraping the data contained in a tag 'script' (json format). 