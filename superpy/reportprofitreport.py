import pandas as pd
import numpy as np
import os
from tabulate import tabulate
from reportexport import reportexport
import matplotlib.pyplot as plt


# PROFITREPORT


def profitreport(date, rep_label):
    begindate = date[0]
    enddate = date[1]

    # variabelen tbv export report
    dirname = "reports_profit"
    filename = f"profitreport_{begindate}_{enddate}"

    dfb = pd.read_csv("bought.csv", index_col="buyid")
    dfs = pd.read_csv("sold.csv", index_col="id")
    dfb["buypr_total"] = dfb["buyamount"] * dfb["buyprice"]
    dfs["sellpr_total"] = dfs["sellamount"] * dfs["sellprice"]

    # Filter op periode
    dfbmask = (dfb["buydate"] > begindate) & (dfb["buydate"] <= enddate)
    dfbfilter = dfb.loc[dfbmask]
    dfsmask = (dfs["selldate"] > begindate) & (dfs["selldate"] <= enddate)
    dfsfilter = dfs.loc[dfsmask]

    # als er geen producten zijn gekocht of verkocht in gevraagde periode:
    if dfbfilter.empty:
        if dfsfilter.empty:
            print("No products bought or sold, profit is:0")
            exit()
        else:
            profit = (dfsfilter["sellpr_total"].round(2)).sum()
            profitbasis = dfsfilter
            print(tabulate(profitbasis, headers="keys", tablefmt="psql"))
            print(f"Only products sold, profit is: {profit}")
    if dfsfilter.empty:
        profit = 0 - (dfbfilter["buypr_total"].round(2)).sum()
        profitbasis = dfbfilter
        print(tabulate(profitbasis, headers="keys", tablefmt="psql"))
        print(f"Only products sold, profit is negative: {profit}")
    else:
        # Tabel maken per dag met gesommeerde buy/price gegevens.
        # Hiervoor buy- en sell-date kolommen hernoemen om makkelijk
        # te groeperen en mergen op datum.
        dfbfilter1 = dfbfilter.copy().rename(columns={"buydate": "date"})
        dfbgroup = dfbfilter1.groupby(["date"])[
            ["buyamount", "buypr_total"]
        ].sum()
        dfbgroup2 = dfbgroup.reset_index()

        dfsfilter1 = dfsfilter.copy().rename(columns={"selldate": "date"})
        dfsgroup = dfsfilter1.groupby(["date"])[
            ["sellamount", "sellpr_total"]
        ].sum()
        dfsgroup2 = dfsgroup.reset_index()

        # merge op datum->tabel met gekochte en verkochte producten per dag
        # kolom aanmaken profit
        profitbasis = pd.merge(
            dfbgroup2, dfsgroup2, how="outer", on=["date"]
        ).fillna(0)
        profitbasis["profit"] = (
            profitbasis["sellpr_total"] - profitbasis["buypr_total"]
        )

        profit = (profitbasis["profit"].round(2)).sum()
        print(tabulate(profitbasis, headers="keys", tablefmt="psql"))
        print(f"profit of {rep_label} is: {profit}")

        # maken van linechart
        user_input = input(
            "Do you want to see a linechart of the profit?"
            "choose y (yes) or ENTER for no:"
        )
        if user_input.lower() == "y":
            buypr_total = profitbasis["buypr_total"]
            sellpr_total = profitbasis["sellpr_total"]
            profit = profitbasis["profit"]
            x = np.arange(len(profitbasis["date"]))

            fig, ax = plt.subplots()
            fig.set_size_inches(15, 7)
            ax.plot(
                sellpr_total,
                color="green",
                marker="o",
                linewidth=2,
                label="revenue",
            )
            ax.plot(
                buypr_total,
                color="red",
                marker="o",
                linewidth=2,
                label="expenses",
            )
            ax.plot(
                profit, color="black", marker="o", linewidth=2, label="profit"
            )
            ax.set_xticks(x)
            ax.set_xticklabels(profitbasis["date"], rotation=45, ha="right")
            ax.set_title("Profit per day", fontsize=12)
            ax.set_xlabel("Days", fontsize=10)
            ax.set_ylabel("Price", fontsize=10)
            plt.legend()
            plt.savefig(
                os.path.join(
                    os.getcwd(), f"{dirname}", f"profit_linechart_{date}.png"
                )
            )
            plt.draw()
            plt.waitforbuttonpress(1)
            input()
            plt.close(fig)

    # ook in geval van alleen verkochte producten
    profitbasis.to_parquet(
        os.path.join(os.getcwd(), "report_parquet", "report.parquet.gzip"),
        compression="gzip",
    )
    # export report starten
    reportexport(dirname, filename, rep_label)


if __name__ == "__main__":
    profitreport("2023-04-30")
