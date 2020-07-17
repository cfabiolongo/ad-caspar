import pymongo


class ManageLKB(object):
    def __init__(self, host):

        self.host = host
        self.client = pymongo.MongoClient(self.host)
        self.reason_keys = []
        self.confidence = 0.0


    def set_confidence(self, confidence):
        if self.confidence == 0.0:
            self.confidence = confidence


    def get_confidence(self):
        return self.confidence


    def reset_confidence(self):
        self.confidence = 0.0



    def add_reason_keys(self, keys):
        if len(self.reason_keys) == 0:
            self.reason_keys.extend(keys)


    def reset_last_keys(self):
        self.reason_keys = []


    def get_last_keys(self):
        return self.reason_keys


    def insert_clause_db(self, cls):

        db = self.client["ad-caspar"]
        clauses = db["clauses"]

        features = self.extract_features(cls)
        print("\nfeatures:", features)

        try:

            clause = {
                "value": cls,
                "features": features
                }
            sentence_id = clauses.insert_one(clause).inserted_id
            print("sentence_id: " + str(sentence_id))

        except pymongo.errors.DuplicateKeyError:
             print("\nClause already present in Lower KB!")



    def extract_features(self, sent):
        chunks = sent.split(" ")
        def_chinks = []
        for chu in chunks:
            chinks = chu.split("(")
            for chi in chinks:
                if ')' not in chi and chi not in def_chinks and chi != '' and chi != "==>":
                    def_chinks.append(chi)
        return def_chinks



    def show_LKB(self):

        db = self.client["ad-caspar"]
        clauses = db["clauses"]

        myclauses = clauses.find()
        for cls in myclauses:
            print("\n")
            print(cls['value'])
            print(cls['features'])
        return myclauses.count()


    def clear_lkb(self):

        db = self.client["ad-caspar"]
        clauses = db["clauses"]
        x = clauses.delete_many({})
        return x.deleted_count


    def extract_features(self, sent):
        chunks = sent.split(" ")
        def_chinks = []
        for chu in chunks:
            chinks = chu.split("(")
            for chi in chinks:
                if ')' not in chi and chi not in def_chinks and chi != '' and chi != "==>":
                    def_chinks.append(chi)
        return def_chinks



    def aggregate_clauses(self, cls, aggregated_clauses, min_confidence):

        db = self.client["ad-caspar"]
        features = self.extract_features(cls)
        feat_num = len(features)

        aggr = db.clauses.aggregate([
            {"$project": {
                "value": 1, "_id": 1,
                "intersection": {"$size": {"$setIntersection": ["$features", features]}}
            }},
            {"$group":
                 {"_id": "$intersection",
                  "group1": {"$push": "$value"}, "group2": {"$push": "$_id"}}},
            {"$sort": {"_id": -1}},
            {"$limit": 2}
        ])

        for a in aggr:
            occurrencies = a['_id']
            confidence = int(occurrencies) / int(feat_num)
            clauses = a['group1']
            self.set_confidence(confidence)
            self.add_reason_keys(a['group2'])
            for c in clauses:
                if c not in aggregated_clauses and confidence > min_confidence:
                    aggregated_clauses.append(c)
                    print("\naggregated: ", c)
                    print("confidence: ", confidence)
                    self.aggregate_clauses(c, aggregated_clauses, min_confidence)

        return aggregated_clauses

    """
    def get_fol_from_db(self, id): 

        db = self.client["ad-caspar"]
        terms = db["clauses"]
        fol = []

        query = {'sentence_id': ObjectId(str(id))}
        mydoc = terms.find(query)
        for t in mydoc:
            clause = []
            term.append(t['value'])
            term.append(t['features'])
            fol.append(term)
        return fol
    """












