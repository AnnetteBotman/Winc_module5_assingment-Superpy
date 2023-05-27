import csv
import pandas as pd
import os.path
import pathlib


# leeg bought.csv bestand aanmaken.
def create_boughtcsv():
    with open(
        pathlib.Path(__file__).parent / "bought.csv", "w", newline=""
    ) as productFile:
        writer = csv.writer(productFile)
        writer.writerow(
            [
                "buyid",
                "buydate",
                "product",
                "buyamount",
                "buyprice",
                "expirydate",
            ]
        )


def append_boughtcsv(product):
    product
    maxb_id = 0
    check_file = os.path.isfile("bought.csv")
    if check_file:
        dfb = pd.read_csv("bought.csv", index_col="buyid")
        # als csv leeg is, wordt 1e record toegevoegd met buyid 1001
        # vanaf dan wordt het buyid van ieder nieuw record automatisch
        # met 1 opgehoogd.
        # als er al gegevens in het csv bestand staan, wordt gezocht naar
        # hoogste buyid en vanaf daar opgehoogd.
        if dfb.empty:
            prodlist = [1001] + product
            with open("bought.csv", "a", newline="") as productFile:
                productFilewriter = csv.writer(productFile)
                productFilewriter.writerow(prodlist)
                print("Product " + str(product) + " is added to bought.csv")
        else:
            maxb_id = max(dfb.index)
            maxb_id += 1
            prodlist = [maxb_id] + product
            with open("bought.csv", "a", newline="") as productFile:
                productFilewriter = csv.writer(productFile)
                productFilewriter.writerow(prodlist)
                print("Product " + str(product) + " is added to bought.csv")
    # als er nog geen csv bestand is aangemaakt, wordt dat eerst gedaan
    # voordat gegevens kunnen worden toegevoegd.
    else:
        create_boughtcsv()
        append_boughtcsv(product)


if __name__ == "__main__":
    print(create_boughtcsv())
