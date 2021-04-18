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

popdf.replace({"-": 0}, inplace=True)
popdf = popdf.reset_index(drop=True)
