# pylint: disable=missing-module-docstring
# pylint: disable=invalid-name
import argparse
import logging
from os.path import dirname, abspath, exists, join
from shutil import copyfile
import sys
from urllib.request import urlopen
from urllib.error import HTTPError
import pandas as pd
from bs4 import BeautifulSoup


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main():
    """Main execution point for the program."""

    default_path = join(*[dirname(abspath(__file__)), "support", "CardList.xlsx"])

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--file', type=str, 
        default=default_path,
        help='spreadsheet containing price charting urls. See CardList.xlsx for an example.'
    )
    parser.add_argument(
        '-p', '--price_charting_url_col',
        type=str,
        default="price_charting_url",
        help="name of the column where the price charting url information is contained."
    )
    args = parser.parse_args()


    filename = args.file
    price_charting_url = args.price_charting_url_col

    logger.info(f"attempting to read data from {filename}")
    logger.info(f"looking for price charting information in column {price_charting_url}")
    
    if not exists(filename):
        logger.error(f"failed to find {filename}")
        sys.exit(1)
    else:
        backup_filename = f"{filename}.backup"
        logger.debug(f"creating backup file {backup_filename}")
        copyfile(filename, backup_filename)

    df = pd.read_excel(filename)

    # column_names = df.columns.values.tolist()
    df.reset_index()

    for index, row in df.iterrows():

        url_name = row[price_charting_url]

        if not url_name:
            continue

        try:
            with urlopen(url_name) as open_url:
                soup = BeautifulSoup(open_url.read(), features="lxml")
        except (AttributeError, TypeError, ValueError, HTTPError) as error:
            continue

        div = soup.find("div", {"id": "full-prices"})
        if not div:
            logger.debug("failed to find the div")
            continue

        price_table_rows = div.find('table').find_all('tr')
        for row in price_table_rows:
            standard_data = row.find_all('td')
            if len(standard_data) != 2:
                logger.debug("something went wrong in finding and converting standard data")
                continue

            td1 = standard_data[0].get_text()
            try:
                td2 = float(standard_data[1].get_text().replace("$", "").replace(",", ""))
            except ValueError:
                td2 = "N/A"

            if td1.lower() == "ungraded":
                df.at[index, "ebay_raw"] = td2
            elif "Grade" in td1:
                grade = td1.replace("Grade", "PSA").replace(" ", "")
                df.at[index, grade] = td2
            else:
                df.at[index, td1] = td2

    logger.debug("processing saved dataframe into spreadsheet")
    # pylint: disable=abstract-class-instantiated
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    # output the data to an excel file.
    # auto scale the size of the column as well for easier viewing.
    logger.debug("creating sheet WishList")
    df.to_excel(writer, sheet_name="WishList", index=False)
    worksheet = writer.sheets["WishList"]
    logger.debug("resizing column width for viewing")
    for idx, col in enumerate(df):
        series = df[col]
        max_len = max((
            series.astype(str).map(len).max(),
            len(str(series.name))
        )) + 1
        worksheet.set_column(idx, idx, max_len)
    writer.close()
    logger.debug(f"saved data to {filename}")

if __name__ == '__main__':
    main()