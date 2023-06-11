import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
from reportexport import reportexport


def inventoryreport(date, rep_label):
    # variabelen tbv export report
    dirname = "reports_inventory"
    filename = f"inventoryreport_{date}"

    dfb = pd.read_csv("bought.csv", index_col="buyid")
    dfs = pd.read_csv("sold.csv", index_col="id")

    dfb["buypr_total"] = dfb["buyamount"] * dfb["buyprice"]
    dfs["sellpr_total"] = dfs["sellamount"] * dfs["sellprice"]

    # Filter tot en met ingevoerde datum
    # dfb filter is van gekochte producten (b=bought)
    # dfs filter is van verkochte producten (s=sold)
    dfbmask = dfb["buydate"] <= date
    dfbfilter = dfb.loc[dfbmask]
    dfsmask = dfs["selldate"] <= date
    dfsfilter = dfs.loc[dfsmask]

    # pandasdataframe kan leeg zijn na filteren
    # zo niet, dan combineren van gekochte en verkochte items
    # om overzicht te krijgen wat er nog in voorraad is.
    # ook inzicht geven in hoeveelheid producten die over datum zijn.

    if dfbfilter.empty:
        # Als pandasdataframe van gekochte producten en verkochte
        # producten leeg is, is er niets gekocht of verkocht t/m
        # ingevoerde datum. Hiervan wordt een melding gemaakt.
        if dfsfilter.empty:
            print(f"No products bought or sold until {date} (day included)")
            exit()
        else:
            # Als pandasdataframe van gekochte producten leeg is
            # maar van verkochte producten niet, wordt deze lijst
            # opgeslagen als inventarislijst en is dat het rapport.
            dfsgroup = dfsfilter.groupby(["buyid", "product", "expirydate"])[
                "sellamount"
            ].sum()
            dfsgroup.to_parquet(
                os.path.join(
                    os.getcwd(), "report_parquet", "report.parquet.gzip"
                ),
                compression="gzip",
            )
            print(tabulate(dfsgroup, headers="keys", tablefmt="psql"))
            print(f"Only products sold, inventory of {rep_label}")
    if dfsfilter.empty:
        # Als pandasdataframe van verkochte producten leeg is maar
        # die van gekochte producten niet, wordt de lijst van
        # gekochte producten opgeslagen als inventarislijst en
        # is dat het rapport.
        dfbgroup = dfbfilter.groupby(["buyid", "product", "expirydate"])[
            "buyamount"
        ].sum()
        dfbgroup.to_parquet(
            os.path.join(os.getcwd(), "report_parquet", "report.parquet.gzip"),
            compression="gzip",
        )
        print(tabulate(dfbgroup, headers="keys", tablefmt="psql"))
        print(f"Only products bought, inventory of {rep_label}")
    # Als beide dataframes na filteren op datum NIET leeg zijn,
    # worden de gegevens gecombineerd tot een inventarisrapport
    else:
        dfbgroup = dfbfilter.groupby(
            ["buyid", "product", "expirydate", "buypr_total"]
        )["buyamount"].sum()
        dfbgroup = dfbgroup.reset_index().rename_axis(None, axis=1)

        dfsgroup = dfsfilter.groupby(["buyid", "product"])[
            ["sellamount", "sellpr_total"]
        ].sum()
        dfsgroup = dfsgroup.reset_index().rename_axis(None, axis=1)

        invbasis = pd.merge(
            dfbgroup, dfsgroup, how="outer", on=["buyid", "product"]
        ).fillna(0)

        # aan gecombineerde tabel kolommen voor stock
        # en stockvalue toevoegen
        # totalen berekenen voor aantallen in stock en waarde
        # voor aantal producten expired en waarde daarvan
        invbasis["in_stock"] = invbasis["buyamount"] - invbasis["sellamount"]
        invbasis["stockvalue"] = invbasis["in_stock"] * (
            invbasis["buypr_total"] / invbasis["buyamount"]
        )
        invbasis = invbasis.loc[invbasis["in_stock"] > 0]
        totalvalue = invbasis["stockvalue"].sum()

        invbasis["expired"] = np.where(
            invbasis["expirydate"] < date, True, False
        )

        expiredproducts = int(
            (invbasis.loc[invbasis["expired"]])["in_stock"].sum()
        )
        expiredproducts_value = (invbasis.loc[invbasis["expired"]])[
            "stockvalue"
        ].sum()

        print(tabulate(invbasis, headers="keys", tablefmt="psql"))
        print(
            f"Inventoryreport of {rep_label}, total stockvalue:"
            f"{totalvalue}\n{expiredproducts} products expired"
            f"  (for a total value of {expiredproducts_value})."
        )

        # inventorisrapport opslaan als parquet-file tbv export
        # naar diverse bestandsformaten.
        invbasis.to_parquet(
            os.path.join(os.getcwd(), "report_parquet", "report.parquet.gzip"),
            compression="gzip",
        )

        # maken van geclusterde staafdiagram
        user_input = input(
            "Do you want to see a grouped barchart of the inventory?"
            "choose y (yes) or ENTER for no:"
        )
        if user_input.lower() == "y":
            invbasis["stockexp"] = (
                invbasis["in_stock"].where(invbasis["expired"]).fillna(0)
            )
            invbasis["stock_ok"] = (
                invbasis["in_stock"].where(~invbasis["expired"]).fillna(0)
            )
            invplot = invbasis.groupby(["product"])[
                ["stockexp", "stock_ok"]
            ].sum()
            invplot2 = invplot.reset_index()
            x = np.arange(len(invplot2["product"]))
            width = 0.35
            ax = plt.bar

            width = 0.35
            fig, ax = plt.subplots()
            fig.set_size_inches(15, 7)
            ax.bar(
                x - width / 2, invplot2["stock_ok"], width, label="not expired"
            )
            ax.bar(x + width / 2, invplot2["stockexp"], width, label="expired")
            ax.set_ylabel("Amount", fontsize=10)
            ax.set_title("Inventory of products", fontsize=12)
            ax.set_xticks(x)
            ax.set_xticklabels(invplot2["product"], rotation=45, ha="right")
            ax.legend()
            plt.savefig(
                os.path.join(
                    os.getcwd(), f"{dirname}", f"inventory_barchart_{date}.png"
                )
            )
            plt.draw()
            plt.waitforbuttonpress(1)
            input()
            plt.close(fig)

    # export report starten
    reportexport(dirname, filename, rep_label)


if __name__ == "__main__":
    inventoryreport("2023-04-30", "today")
