from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


def test_connection(uri, label):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        print(f"✅ Connected to {label}")
        return client
    except ConnectionFailure as e:
        print(f"❌ Failed to connect to {label}: {e}")
        return None


# MongoDB URIs
uri_a = "mongodb+srv://tuyennq:zJEctADAbVDDWpp4@cluster0.zcvec.mongodb.net/?retryWrites=true&w=majority"
uri_b = "mongodb+srv://root:6qKJrwhHEIQgHxlP@mg-sai.moyb1tp.mongodb.net/?retryWrites=true&w=majority&appName=MG-SAI"

# Connect to source and target MongoDB servers
src_client = test_connection(uri_a, "Source (A)")
tgt_client = test_connection(uri_b, "Target (B)")

# Database name to move
db_name = "embai"

if src_client and tgt_client:
    src_db = src_client[db_name]
    tgt_db = tgt_client[db_name]

    collections = src_db.list_collection_names()
    print(f"📚 Found collections: {collections}")

    for col_name in collections:
        print(f"🔄 Copying collection: {col_name}")
        src_col = src_db[col_name]
        tgt_col = tgt_db[col_name]

        docs = list(src_col.find({}))
        if docs:
            tgt_col.drop()  # Optional: clear existing target collection
            tgt_col.insert_many(docs)
            print(f"✅ Copied {len(docs)} documents.")
        else:
            print(f"⚠️ No documents in {col_name}")

    print("🎉 All collections copied from embai_dev.")
else:
    print("⛔ Aborting due to connection error.")
