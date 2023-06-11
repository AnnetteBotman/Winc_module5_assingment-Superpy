import csv
import pandas as pd
import pathlib
import os.path
from validate import validate_date


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

# def checkexpdate(productsold):


def append_buyid(productsold):
    check_file = os.path.isfile("sold.csv")
    if not check_file:
        create_soldcsv()
    # Gekochte producten krijgen een 'buyid'.
    # Ieder verkocht product krijgt een eigen id en op basis
    # van productnaam en expirydate het buyid van de bijbehorende
    # inkoopbatch.
    # Hiervoor wordt eerst gekeken hoeveel er nog in voorraad is.

    # Lijst genereren met gekochte producten, aantal sommeren
    # op product en expirydate
    dfb = pd.read_csv("bought.csv", index_col="buyid")
    dfbgroup = dfb.groupby(["buyid", "product", "expirydate"])[
        "buyamount"
    ].sum()

    # Lijst genereren met verkochte producten, aantal sommeren
    # op product en expirydate
    dfs = pd.read_csv("sold.csv", index_col="id")
    dfsgroup = dfs.groupby(["buyid", "product", "expirydate"])[
        "sellamount"
    ].sum()

    # deze gegevens mergen op buyid
    inventory = pd.merge(
        dfbgroup.reset_index(), dfsgroup, how="left", on=["buyid"]
    ).fillna(0)

    # kolom toevoegen om aantal producten nog in voorraad uit te rekenen
    inventory["in_stock"] = inventory["buyamount"] - inventory["sellamount"]

    # ingevoerde product opzoeken in lijst om expirydate erbij te zoeken
    inv_productsold = inventory[
        inventory["product"].str.match(productsold[1])
    ]
    if inv_productsold.empty:
        print(
            "Product not in stock, or this amount not available.\n"
            "Check productname, sellamount"
        )
        exit()
    if len(inv_productsold) == 1 & (inv_productsold["in_stock"].sum(axis=0)
                                    < productsold[2]):
        available = inv_productsold["in_stock"].sum(axis=0)
        if available == 0:
            print("Product sold out")
        else:
            print(
                "Only "
                + str(available)
                + " items available, check input of sold product:"
                " productname or sellamount.\n"
                "Product NOT added to bought.csv"
            )
            exit()
    if len(inv_productsold) == 1 & (inv_productsold["in_stock"].sum(axis=0)
                                    >= productsold[2]):
        if inv_productsold.iat[0, 2] < productsold[0]:
            print("Product expired, product NOT added to sold.csv")
        else:
            buyid = inv_productsold.iat[0, 0]
            expdate = inv_productsold.iat[0, 2]
            prodlist = [buyid] + productsold + [expdate]
            append_prodlist(prodlist)
    if len(inv_productsold) > 1:
        print(inv_productsold)
        expdate = input("More expirydates available for this product, type "
                        "expirydate of your product:")
        validate_date(expdate)
        productsold = productsold + [expdate]
        appendbuyid_morexpdate(productsold)
# Er kunnen op meerdere dagen producten zijn ingekocht met
# dezelfde productnaam en eenzelfde expirydate of dezelfde productnaam
# en meerdere expirydates.
# Met behulp van bovenstaande functie wordt gecheckt of er bij een
# ingevoerd product meerdere expirydatums horen en laat die zien.
# De gebruiker moet de juiste expirydate invoeren.

# Hierna wordt een 2e functie gestart die eventueel nog een keer
# gestart kan worden als er producten worden verkocht die verdeeld moeten
# worden over meerdere inkoopbatches.
# Eerst wordt het de eerste batch getoond en daar wordt de
# de hoeveelheid gekochte producten vanaf gehaald. Is er dan
# nog over, worden die van de volgende batch afgehaald.
# Is het product dan uitverkocht, wordt hier melding van gemaakt.


def appendbuyid_morexpdate(productsold):
    # Begin van de functie is hetzelfde als de hierbovenstaande functie
    dfb = pd.read_csv("bought.csv", index_col="buyid")
    dfbgroup = dfb.groupby(["buyid", "product", "expirydate"])[
        "buyamount"
    ].sum()

    # Lijst met verkochte producten, aantal sommeren op product en expirydate
    dfs = pd.read_csv("sold.csv", index_col="id")
    dfsgroup = dfs.groupby(["buyid", "product", "expirydate"])[
        "sellamount"
    ].sum()

    # deze gegevens mergen op buyid
    inventory = pd.merge(
        dfbgroup.reset_index(), dfsgroup, how="left", on=["buyid"]
    ).fillna(0)

    # kolom toevoegen om aantal producten nog in voorraad uit te rekenen
    inventory["in_stock"] = inventory["buyamount"] - inventory["sellamount"]
    inv_productsold = inventory[
            inventory["product"].str.match(productsold[1])
            & (inventory["expirydate"].str.match(productsold[4]))
            & (inventory["in_stock"] > 0)]
    # Als er te weinig producten in voorraad zijn tov het ingegeven
    # aantal producten, komt er een melding.
    if inv_productsold["in_stock"].sum(axis=0) < productsold[2]:
        available = inv_productsold["in_stock"].sum(axis=0)
        print(
            "Only "
            + str(available)
            + " items available, check input of sold product:"
            " productname, sellamount and/or expirydate.\n"
            "Product NOT added to bought.csv"
        )
# Als er genoeg items in voorraad zijn, wordt buyid van 1e batch
# toegevoegd aan het verkochte product en aan bought.csv toegevoegd
    else:
        buyid = (inv_productsold.head(1)).iat[0, 0]
        instock_buyid = (inv_productsold.head(1)).iat[0, 5]
        if instock_buyid >= productsold[2]:
            prodlist = [buyid] + productsold
            append_prodlist(prodlist)
# Als er producten van een 2e inkoopbatch afgehaald moeten worden,
# wordt dat in het volgende stukje van de functie gedaan en wordt
# de functie herstart om met nieuwe voorraadgegevens te werken en
# de juiste inkoopbatch te gebruiken.
        elif instock_buyid < productsold[2]:
            prodlist = ([buyid] + productsold[:2] + [instock_buyid]
                        + productsold[3:])
            append_prodlist(prodlist)
            restamount = productsold[2] - instock_buyid
            if restamount == 0:
                print("Product out of stock.")
            else:
                restprodlist = productsold[:2] + [restamount] + productsold[3:]
                productsold = restprodlist
                appendbuyid_morexpdate(productsold)
    # Er komt een melding als het product is uitverkocht.
        if instock_buyid == productsold[2]:
            print("Last product sold, product out of stock.")
        else:
            pass


# # Met deze functie worden de producten toegevoegd aan de sold.csv
# # Eerst wordt gecontroleerd of er een sold.csv bestaat.
# # Afhankelijk daarvan wordt een 1e record toegevoegd met id 1
# # of gezocht naar hoogste id en die automatisch met 1 verhoogd.
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
