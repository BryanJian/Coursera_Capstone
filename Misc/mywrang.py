# %%
import pandas as pd
import numpy as np

# %%
# Population Data
popsheet = pd.read_excel(
    "t1-9.xls", sheet_name="T7(Total)"
)  # Read Planning Area population

# Dropping empty rows
popdf = popsheet.dropna(how="all", thresh=2)
popdf = popdf.dropna(how="all", thresh=2, axis=1)

# Making header
popdf.columns = popdf.iloc[0]
popdf = popdf[1:]

# Removing redundant headers, columns and rows
popdf = popdf[popdf["Planning Area"] != "Planning Area"]
popdf.dropna(inplace=True)
popdf = popdf[["Planning Area", "Total"]]
popdf = popdf[~popdf["Planning Area"].str.contains("Total")]

# Convert Planning Area Names to all-caps
popdf["Planning Area"] = popdf["Planning Area"].str.upper()
popdf = popdf.rename(columns={"Total": "Population"})

popdf.replace({"-": np.nan}, inplace=True)
popdf = popdf.reset_index(drop=True)

popdf.to_csv("SG_planningarea_pop.csv", index=False)

# %% Income Data
incsheet = pd.read_excel("t143-147.xls", sheet_name="T145")  # Read Planning Area income

# Dropping empty columns and rows
incdf = incsheet.dropna(how="all", thresh=3)
incdf = incdf.dropna(axis=1)

# Making Header
incdf.columns = incdf.iloc[0]
incdf = incdf[1:]

incdf = incdf[~incdf["Planning Area"].str.contains("Total")]
incdf = incdf[~incdf["Planning Area"].str.contains("Others")]
incdf = incdf.drop(columns="Total")

incdf["Planning Area"] = incdf["Planning Area"].str.upper()

incdf = incdf.reset_index(drop=True)

incdf.to_csv("SG_planningarea_inc.csv", index=False)

