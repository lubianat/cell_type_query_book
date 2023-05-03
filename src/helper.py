import requests
import pandas as pd


def get_editor_df_from_qid(qid):
    results = requests.get(
        f"https://xtools.wmflabs.org/api/page/top_editors/wikidata.org/{qid}?limit=1000"
    )
    result = results.json()
    df_nested_list = pd.json_normalize(result, record_path=["top_editors"])
    df_for_qid = df_nested_list[["username", "count"]]
    df_for_qid["qid"] = qid
    return df_for_qid


def get_page_author_from_qid(qid):
    results = requests.get(
        f"https://xtools.wmflabs.org/api/page/articleinfo/wikidata.org/{qid}"
    )
    result = results.json()
    return result["author"]
