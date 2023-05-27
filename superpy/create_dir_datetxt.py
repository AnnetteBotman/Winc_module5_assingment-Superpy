import os
from datetime import datetime
import contextlib
import pathlib


# Met deze functie wordt txt-bestand aangemaakt.
# Dit bestand wordt aangepast met de commando's
#
def create_datetxtfile():
    check_file = os.path.isfile("dateset.txt")
    if not check_file:
        with open(pathlib.Path(__file__).parent / "dateset.txt", "w") as t:
            with contextlib.redirect_stdout(t):
                t = datetime.today().strftime("%Y-%m-%d")
                print(t)
    else:
        pass


def create_reportdir():
    current_dir = pathlib.Path(__file__).parent
    if not os.path.exists(current_dir / "reports_revenue"):
        os.mkdir(current_dir / "reports_revenue")
        if not os.path.exists(current_dir / "reports_inventory"):
            os.mkdir(current_dir / "reports_inventory")
            if not os.path.exists(current_dir / "reports_profit"):
                os.mkdir(current_dir / "reports_profit")
                if not os.path.exists(current_dir / "report_parquet"):
                    os.mkdir(current_dir / "report_parquet")
    else:
        pass


if __name__ == "__main__":
    create_reportdir()
