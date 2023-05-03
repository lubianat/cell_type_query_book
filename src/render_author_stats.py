import pandas as pd
import wikidata2df
from tqdm import tqdm
from pathlib import Path
from helper import *
import pandas as pd
import json
from collections import Counter

HERE = Path(__file__).parent.resolve()

base_folder = f"{HERE}/../results/"

query = HERE.joinpath("queries/cells_and_taxa.rq").read_text()

df = wikidata2df.wikidata2df(query)

total_number = len(set(df["qid"]))
print("Total number of cell types on Wikidata: " + str(total_number))

df.fillna("no taxon specified", inplace=True)
df.groupby("taxon_name").count().sort_values(by="qid").to_csv(
    base_folder + "cells_by_taxon.csv"
)

editors_df = pd.read_csv(base_folder + "cells_wikidata_editors.csv")
editors_df = editors_df[["username", "count", "qid"]]
for i, row in tqdm(df.iterrows(), total=df.shape[0]):
    qid = row["qid"]
    if qid not in list(set(editors_df["qid"])):
        editors_df = editors_df.append(get_editor_df_from_qid(qid))

editors_df = editors_df.drop_duplicates()

editors_df.to_csv(base_folder + "cells_wikidata_editors.csv", index=False)

editors_df_reshaped = editors_df.drop_duplicates().pivot(
    index="qid", columns="username", values="count"
)

editors_df_reshaped.sum().sort_values().tail(10)
editors_df_reshaped.count().sort_values().tail(10)

with open(base_folder + "cells_wikidata_authors.json") as f:
    author_dict = json.loads(f.read())


for i, row in tqdm(df.iterrows(), total=df.shape[0]):
    qid = row["qid"]
    if qid not in author_dict:
        author = get_page_author_from_qid(qid)
        author_dict[qid] = author


with open(base_folder + "cells_wikidata_authors.json", "w") as fp:
    json.dump(author_dict, fp)

res = Counter(author_dict.values())
print(res)

authors_df = pd.DataFrame.from_dict(res, orient="index")
authors_df["author"] = authors_df.index
authors_df.columns = ["count", "author"]
authors_df.to_csv("results/cells_wikidata_authors.csv", index=False)
# Autogenerate text for report:

date = ""
edited = editors_df_reshaped["TiagoLubiana"].count()
created = res["TiagoLubiana"]

percentage_edited = 100 * float(edited) / float(total_number)
percentage_edited = "%.1f" % percentage_edited

percentage_created = 100 * float(created) / float(total_number)
percentage_created = "%.1f" % percentage_created

from time import gmtime, strftime

date = strftime("%d of %B of %Y", gmtime())

text = f"""
Wikidata contains {str(total_number)} subclasses of "cell ([Q7868](https://www.wikidata.org/wiki/Q7868))" as of {date}. 
From those, 550 cell classes are specific for humans, and 318 are specific for mice.  
Currently Wikidata has more cell classes than the Cell Ontology, which lists 2577 classes. 
It is worth noticing that classes on the Cell Ontology are added after careful consideration by ontologists and domain experts and should be considered of higher quality than the ones on Wikidata. 

From the {str(total_number)} cell classes on Wikidata, {edited} ({percentage_edited}%) have been edited somehow by User:TiagoLubiana, and {created} ({percentage_created}%) have been created by User:TiagoLubiana. 
Edits included adding multilanguage labels, connecting a dangling Wikipedia page to the cell subclass hierarchy, adding identifiers, images, markers, and other pieces of information. 
Approximatedly 430 hundred terms were added via manual curation based on PanglaoDB entries, while the remaining {created - 430} entries were created either via Wikidata's web interface or via the curation workflow described in this chapter. 
These statistics are demonstration of how the curation system efficiently contributes to the status of cell type information on Wikidata.
"""
print(text)

with open("author_stats.txt", "w") as fp:
    json.dump(text, fp)
