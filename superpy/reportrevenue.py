import pandas as pd
import os
from tabulate import tabulate
from reportexport import reportexport
import matplotlib.pyplot as plt


# REVENUEREPORT
def revenuereport(date, rep_label):
    begindate = date[0]
    enddate = date[1]

    # variabelen tbv export report
    dirname = "reports_revenue"
    filename = f"revenuereport_{begindate}_{enddate}"

    dfs = pd.read_csv("sold.csv", index_col="id")
    dfs["revenue"] = dfs["sellamount"] * dfs["sellprice"]

    # Filter t/m beginddatum
    dfsmask = dfs["selldate"] <= begindate
    dfsfilter1 = dfs.loc[dfsmask]

    # Filter t/m einddatum
    dfsmask = dfs["selldate"] <= enddate
    dfsfilter2 = dfs.loc[dfsmask]
    rev_enddate = dfsfilter2["revenue"].sum()

    # Revenuereport van gevraagde dag/periode
    # is het verschil tussen eind- en begindatum
    revenuereport = dfsfilter2[~dfsfilter2.isin(dfsfilter1)].dropna()
    revenue = revenuereport["revenue"].sum()

    # Datafame kan leeg zijn, keuze geven om revenue
    # tot aan keuzedatum (enddate) weer te geven.
    if revenuereport.empty:
        print(f"No products sold on/from {rep_label}, revenue = 0")
        if not dfsfilter2.empty:
            user_input = input(
                f"Do you want a revenuereport until {enddate}, without"
                " startdate? (choose y(yes) or ENTER (no):"
            )
            if user_input.lower() == "y":
                print(tabulate(dfsfilter2, headers="keys", tablefmt="psql"))
                print(
                    f"Revenue until {enddate} (day included) is: {rev_enddate}"
                )
                revenuereport = dfsfilter2
            else:
                exit()

    else:
        print(tabulate(revenuereport, headers="keys", tablefmt="psql"))
        print(f"revenue of {rep_label} is: {revenue}")

    revenuereport.to_parquet(
        os.path.join(os.getcwd(), "report_parquet", "report.parquet.gzip"),
        compression="gzip",
    )
    #  for a line chart of revenue per day
    user_input = input(
        "Do you want to see a linechart of the revenue per day?"
        "choose y (yes) or ENTER for no:"
    )
    if user_input.lower() == "y":
        plotrevreport = revenuereport.groupby(["selldate"])[["revenue"]].sum()
        plotrevreport.reset_index(inplace=True)
        fig = plt.figure()
        fig.set_size_inches(15, 7)
        plt.plot(
            plotrevreport["selldate"],
            plotrevreport["revenue"],
            color="red",
            marker="o",
        )
        fig.autofmt_xdate()
        plt.title("Revenue per day", fontsize=12)
        plt.xlabel("Days", fontsize=10)
        plt.ylabel("Revenue", fontsize=10)
        plt.grid(True)
        plt.savefig(
            os.path.join(
                os.getcwd(),
                f"{dirname}",
                f"revenue_linechart_{date}.png",
            )
        )
        plt.draw()
        plt.waitforbuttonpress(1)
        input()
        plt.close(fig)

    reportexport(dirname, filename, rep_label)


if __name__ == "__main__":
    revenuereport("2023-04-30")
