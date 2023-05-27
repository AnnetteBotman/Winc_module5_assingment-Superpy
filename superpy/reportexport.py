import pandas as pd
import os


# Deze functie wordt vanuit alle functies die een rapport genereren
# aangeroepen. Er kan gekozen worden uit 3 exportformaten.
# Voor ieder type rapport is een directory aangemaakt, hierin
# worden de exportbestanden opgeslagen, in de bestandsnaam wordt
# de ingevoerde datums verwerkt.
def reportexport(dirname, filename, rep_label):
    report = pd.read_parquet(
        os.path.join(os.getcwd(), "report_parquet", "report.parquet.gzip")
    )
    user_input = input(
        "Do you want to export this report (choose c(csv),e(excel),h(html),"
        " ENTER(no export):"
    )
    if user_input.lower() == "c":
        report.to_csv(
            os.path.join(os.getcwd(), f"{dirname}", f"{filename}.csv")
        )

        print(f"report of {rep_label} is saved as: {filename}.csv")

    elif user_input.lower() == "e":
        report.to_excel(
            os.path.join(os.getcwd(), f"{dirname}", f"{filename}.xlsx")
        )
        print(f"report of {rep_label} is saved as: {filename}.xlsx")

    elif user_input.lower() == "h":
        report.to_html(
            os.path.join(os.getcwd(), f"{dirname}", f"{filename}.html")
        )
        print(f"report of {rep_label} is saved as: {filename}.htm")
    else:
        print("Report is not exported")


if __name__ == "__main__":
    reportexport(os.path.join(os.getcwd(), "reports_inventory", "test.xlsx"))
