import pysolr
import json
import pandas as pd
from datetime import datetime


class SolrHandler:
    def __init__(self, lang="DE"):
        self.solr = {"DE": pysolr.Solr('http://localhost:8983/solr/news_de/', always_commit=False, timeout=10),
                     "EN": pysolr.Solr('http://localhost:8983/solr/news_en/', always_commit=False, timeout=10)}
        self.lang = lang

    def status(self, lang="DE"):
        solr = self.solr[lang] if lang else self.solr[self.lang]
        try:
            return True if json.loads(solr.ping())["status"] == "OK" else False
        except Exception as e:
            print("\nSolrHandler.status(): can not reach solr server, error:", e)
            return False

    def update(self, data=None, lang=None):
        print("SolrHandler.update():")

        solr = self.solr[lang] if lang else self.solr[self.lang]

        if isinstance(data, dict):
            data["date_indexed"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            solr.add(data)
            solr.commit()

        elif isinstance(data, pd.DataFrame) and data.shape[0] > 0 and self.status(lang):
            for row in data.to_dict("index").values():
                row["date_indexed"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                solr.add(row)
            solr.commit()
        print("\tchanges committed to solr.")

    def delete(self, data=None, lang=None):
        print("SolrHandler.delete()")
        solr = self.solr[lang] if lang else self.solr[self.lang]

        if isinstance(data, dict) and "id" in data.keys():
            id_ = data["id"]
            if id_:
                solr.delete(id=data["id"])
                solr.commit()

        elif isinstance(data, pd.DataFrame) and data.shape[0] > 0 and self.status(lang):
            for id_ in data.index:
                solr.delete(id=id_)
            solr.commit()

        else:
            solr.delete(id=data)
            solr.commit()

        print("\tchanges committed to solr.")
