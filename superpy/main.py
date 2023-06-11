# Imports
import argparse
import pathlib
from datetime import timedelta
from datetime import datetime as dt
from create_dir_datetxt import create_datetxtfile, create_reportdir
from csvhelper_sell import append_buyid
from csvhelper_buy import append_boughtcsv
from validate import validate_date
from reportinventory import inventoryreport
from reportrevenue import revenuereport
from reportprofitreport import profitreport
import calendar
import re


# Do not change these lines.
__winc_id__ = "a2bc36ea784242e4989deb157d527ba0"
__human_name__ = "superpy"

# Your code below this line.


def main():
    # textfile creeëren ivm met de functie time waarbij de tijd op
    # bijvoorbeeld vandaag kan worden gezet, of aantal dagen vooruit/achteruit
    # of op willekeurige datum

    # en directories creeëren voor het opslaan van diverse rapportages
    # en grafieken
    create_datetxtfile()
    create_reportdir()
    with open(pathlib.Path(__file__).parent / "dateset.txt") as f:
        dateset = f.read().rstrip()

    parser = argparse.ArgumentParser(
        description="Keep control over your stock"
    )
    subparser = parser.add_subparsers(dest="command")

    # subparsers maken voor de functies time, buy, sell en report
    time = subparser.add_parser("time", help="time help")
    buy = subparser.add_parser("buy", help="buy help")
    sell = subparser.add_parser("sell", help="sold help")
    report = subparser.add_parser("report", help="report help")

    # met de functie tijd kan de buydate of selldate worden ingesteld
    # op een bepaalde datum, deze wordt opgeslagen in dateset.txt filet.
    # Bij de invoer van producten hoeft geen datum te worden ingevoerd,
    # als default wordt de datum uit dateset.txt gebruikt.
    # wel kan eenmalig een andere datum worden ingevoerd.

    time.add_argument(
        "--advance",
        type=int,
        help="move modified date date forward by number of days",
    )
    time.add_argument(
        "--setback",
        type=int,
        help="move modified date backward by number of days",
    )
    time.add_argument(
        "--setdate",
        type=str,
        help="modify date to a desired date",
    )
    time.add_argument(
        "--reset",
        action="store_true",
        help="reset modified date to today's date",
    )
    time.add_argument(
        "--check",
        action="store_true",
        help="shows the modified date",
    )

    # buydate is een positional argument. Voordat producten worden ingevoerd
    # moet met de functie time de juiste datum worden ingesteld.
    # Vervolgens hoeft bij de invoer van producten dan geen datum te worden
    # ingevoerd, als default wordt de datum uit dateset.txt gebruikt.
    # wel kan eenmalig een andere datum worden ingevoerd.
    buy.add_argument(
        "buydate",
        type=str,
        help="The date when product was bought",
        nargs="?",
        default=dateset,
    )
    buy.add_argument("product", type=str, help="The product you bought")
    buy.add_argument("amount", type=int, help="Amount of products bought")
    buy.add_argument("buyprice", type=float, help="Price of product")
    buy.add_argument(
        "expirydate", type=str, help="Expirydate in YYYY-MM-DD format"
    )

    # selldate is een positional argument. Voordat producten worden ingevoerd
    # moet met de functie time de juiste datum worden ingesteld
    # Vervolgens hoeft bij de invoer van producten dan geen datum te worden
    # ingevoerd, als default wordt de datum uit dateset.txt gebruikt.
    # wel kan eenmalig een andere datum worden ingevoerd.
    sell.add_argument(
        "selldate",
        type=str,
        help="The date when product was sold",
        nargs="?",
        default=dateset,
    )
    sell.add_argument("product", type=str, help="The product you sold")
    sell.add_argument("amount", type=int, help="Amount of products sold")
    sell.add_argument("sellprice", type=float, help="Price of product sold")

    report.add_argument(
        "report",
        choices=["inventory", "revenue", "profit"],
        help="Make a choice of a report, inventory, revenue or profit",
    )
    report.add_argument("--now", action="store_true", help="report of today")
    report.add_argument(
        "--yesterday", action="store_true", help="report of yesterday"
    )
    report.add_argument("--date", type=str, help="date in YYYY-MM-DD")
    report.add_argument("--date2", type=str, help="date in YYYY-MM-DD")

    args = parser.parse_args()

    if args.command == "time":
        if args.check:
            with open(
                pathlib.Path(__file__).parent / "dateset.txt", "r"
            ) as check:
                print("Date is currently set to: " + check.read())
        else:
            with open(
                pathlib.Path(__file__).parent / "dateset.txt", "r+"
            ) as t:
                datechange = t.read().rstrip()
                if args.advance:
                    datechange = (
                        dt.strptime(datechange, "%Y-%m-%d").date()
                        + timedelta(days=args.advance)
                    ).strftime("%Y-%m-%d")
                    t.seek(0)
                    t.write(datechange)
                elif args.setback:
                    datechange = (
                        dt.strptime(datechange, "%Y-%m-%d").date()
                        - timedelta(days=args.setback)
                    ).strftime("%Y-%m-%d")
                    t.seek(0)
                    t.write(datechange)
                elif args.setdate:
                    validate_date(args.setdate)
                    datechange = dt.strptime(
                        args.setdate, "%Y-%m-%d"
                    ).strftime("%Y-%m-%d")
                    t.seek(0)
                    t.write(datechange)
                elif args.reset:
                    datechange = dt.today().strftime("%Y-%m-%d")
                    t.seek(0)
                    t.write(datechange)
                else:
                    pass
            with open(
                pathlib.Path(__file__).parent / "dateset.txt", "r"
            ) as check:
                print("Modified date is: " + check.read())

    elif args.command == "buy":
        product = [
            args.buydate,
            args.product,
            args.amount,
            args.buyprice,
            args.expirydate,
        ]

        validate_date(args.buydate)
        validate_date(args.expirydate)
        if dt.strptime(args.expirydate, "%Y-%m-%d") < dt.strptime(
            args.buydate, "%Y-%m-%d"
        ):
            print(
                "Alert:product has expired or one of the inputdates"
                " is not correct, product is NOT added to bought.csv"
            )
        else:
            append_boughtcsv(product)

    elif args.command == "sell":
        productsold = [
            args.selldate,
            args.product,
            args.amount,
            args.sellprice,
        ]
        validate_date(args.selldate)
        append_buyid(productsold)

    elif args.command == "report":
        if args.date and args.date2:
            date = [args.date, args.date2]
            validate_date(date[0])
            validate_date(date[1])
            begindate = (
                dt.strptime(args.date, "%Y-%m-%d").date().strftime("%Y-%m-%d")
            )
            enddate = (
                dt.strptime(args.date2, "%Y-%m-%d").date().strftime("%Y-%m-%d")
            )
            rep_label = f"{args.date} till {args.date2}"
            if begindate > enddate:
                print(
                    "Enddate is before begindate,"
                    " correct entered dates please."
                )
                exit()
            if args.report == "inventory":
                user_input = input(
                    f"Inventoryreport will be generated for {enddate},"
                    "choose y (yes) or ENTER for no:"
                )
                if user_input.lower() == "y":
                    rep_label = enddate
                    inventoryreport(enddate, rep_label)
                    exit()
        if args.now:
            begindate = ((dt.now().date()) - timedelta(days=1)).strftime(
                "%Y-%m-%d"
            )
            enddate = (dt.now().date()).strftime("%Y-%m-%d")
            rep_label = "today"
        if args.yesterday:
            begindate = ((dt.now().date()) - timedelta(days=2)).strftime(
                "%Y-%m-%d"
            )
            enddate = ((dt.now().date()) - timedelta(days=1)).strftime(
                "%Y-%m-%d"
            )
            rep_label = "yesterday"
        if args.date and not args.date2:
            date = args.date
            date_regex = re.compile(r"^\d{4}-\d{2}-\d{2}$")
            if date_regex.match(date):
                begindate = (
                    dt.strptime(args.date, "%Y-%m-%d").date()
                    - timedelta(days=1)
                ).strftime("%Y-%m-%d")
                enddate = (
                    dt.strptime(args.date, "%Y-%m-%d")
                    .date()
                    .strftime("%Y-%m-%d")
                )
                rep_label = enddate
            else:
                date_regex = re.compile(r"^\d{4}-\d{2}$")
                if date_regex.match(date):
                    datesplit = date.split("-")
                    rep_label = dt.strptime(args.date, "%Y-%m").strftime(
                        "%B %Y"
                    )
                    endmonth = calendar.monthrange(
                        int(datesplit[0]), int(datesplit[1])
                    )
                    begindate = f"{date}-01"
                    enddate = f"{date}-{endmonth[1]}"
                    if args.report == "inventory":
                        rep_label = enddate
                        user_input = input(
                            f"Inventoryreport will be generated for {enddate},"
                            "choose y (yes) or ENTER for no:"
                        )
                        if user_input.lower() == "y":
                            inventoryreport(enddate, rep_label)
                            exit()
                else:
                    print(
                        "Invalid date string, date must be"
                        " of the format YYYY-MM-DD / "
                        "monthdate of the format YYYY-MM"
                    )
                    exit()

        if args.report == "inventory":
            inventoryreport(enddate, rep_label)
            exit()

        date = (begindate, enddate)
        if args.report == "revenue":
            revenuereport(date, rep_label)
            exit()
        if args.report == "profit":
            profitreport(date, rep_label)
            exit()


if __name__ == "__main__":
    main()
