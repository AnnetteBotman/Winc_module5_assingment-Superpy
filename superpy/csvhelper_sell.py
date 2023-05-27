import csv
import pandas as pd
import pathlib
import os.path


# leeg sold.csv aanmaken
def create_soldcsv():
    with open(
        pathlib.Path(__file__).parent / "sold.csv", "w", newline=""
    ) as soldFile:
        writer = csv.writer(soldFile)
        writer.writerow(
            [
                "id",
                "buyid",
                "selldate",
                "product",
                "sellamount",
                "sellprice",
                "expirydate",
            ]
        )


def append_buyid(productsold):
    check_file = os.path.isfile("sold.csv")
    if not check_file:
        create_soldcsv()
    # Gekochte producten krijgen een 'buyid'.
    # Ieder verkocht product krijgt een eigen id en op basis
    # van productnaam en expirydate het buyid van de bijbehorende
    # inkoopbatch.
    # Hiervoor wordt eerst gekeken hoeveel er nog in voorraad is.
    dfb = pd.read_csv("bought.csv", index_col="buyid")
    dfbgroup = dfb.groupby(["buyid", "product", "expirydate"])[
        "buyamount"
    ].sum()

    dfs = pd.read_csv("sold.csv", index_col="id")
    dfsgroup = dfs.groupby(["buyid", "product", "expirydate"])[
        "sellamount"
    ].sum()

    inventory = pd.merge(
        dfbgroup.reset_index(), dfsgroup, how="left", on=["buyid"]
    ).fillna(0)

    inventory["in_stock"] = inventory["buyamount"] - inventory["sellamount"]

    inv_productsold = inventory[
        inventory["product"].str.match(productsold[1])
        & (inventory["expirydate"].str.match(productsold[4]))
        & (inventory["in_stock"] > 0)
    ]

    # Als het product niet in voorraad is, is er iets fout gegaan bij de
    # invoer van gegevens, bijvoorbeeld typefout in productnaam, het
    # aantal items of in de combinatie van product en expirydate.
    # In dat geval komt er een melding.
    # Ook als er te weinig producten in voorraad zijn tov het ingegeven
    # aantal producten, komt er een melding.
    if inv_productsold.empty:
        print(
            "Product not in stock, or this amount not available.\n"
            "Check productname, sellamount"
            " and/or expirydate-input"
        )
    if inv_productsold["in_stock"].sum(axis=0) < productsold[2]:
        available = inv_productsold["in_stock"].sum(axis=0)
        print(
            "Only "
            + str(available)
            + " items available, check input of sold product:"
            " productname, sellamount and/or expirydate.\n"
            "Product NOT added to bought.csv"
        )
    # Er kunnen op meerdere dagen producten zijn ingekocht met
    # dezelfde productnaam en eenzelfde expirydate.
    # Er zijn dan meer inkoopbatches met een ander buyid
    # Eerst wordt het de eerste rij getoond en daar wordt de
    # de hoeveelheid gekochte producten vanaf gehaald. Is er dan
    # nog over, worden die van de volgende batch afgehaald.
    # Is het product dan uitverkocht, wordt hier melding van gemaakt.
    else:
        buyid = (inv_productsold.head(1)).iat[0, 0]
        instock_buyid = (inv_productsold.head(1)).iat[0, 5]
        if instock_buyid >= productsold[2]:
            prodlist = [buyid] + productsold
            append_prodlist(prodlist)
        elif instock_buyid < productsold[2]:
            prodlist = (
                [buyid] + productsold[:2] + [instock_buyid] + productsold[3:]
            )
            append_prodlist(prodlist)
            restamount = productsold[2] - instock_buyid
            if restamount == 0:
                print("Product out of stock.")
            else:
                restprodlist = productsold[:2] + [restamount] + productsold[3:]
                prodlist = restprodlist
                append_buyid(prodlist)
        if instock_buyid == productsold[2]:
            print("Last product sold, product out of stock.")
        else:
            pass


# Met deze functie worden de producten toegevoegd aan de sold.csv
# Eerst wordt gecontroleerd of er een sold.csv bestaat.
# Afhankelijk daarvan wordt een 1e record toegevoegd met id 1
# of gezocht naar hoogste id en die automatisch met 1 verhoogd.
def append_prodlist(prodlist):
    maxb_id = 0
    check_file = os.path.isfile("sold.csv")
    if check_file:
        dfb = pd.read_csv("sold.csv", index_col="id")
        if dfb.empty:
            prodlist = [1] + prodlist
            with open("sold.csv", "a", newline="") as productFile:
                productFilewriter = csv.writer(productFile)
                productFilewriter.writerow(prodlist)
                print("Product " + str(prodlist) + " is added to sold.csv")
        else:
            maxb_id = max(dfb.index)
            maxb_id += 1
            prodlist = [maxb_id] + prodlist
            with open("sold.csv", "a", newline="") as productFile:
                productFilewriter = csv.writer(productFile)
                productFilewriter.writerow(prodlist)
                print("Product " + str(prodlist) + " is added to sold.csv")
    if not check_file:
        create_soldcsv()
        append_prodlist(prodlist)


if __name__ == "__main__":
    create_soldcsv()
