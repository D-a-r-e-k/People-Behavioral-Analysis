# import argparse
# import os
# import time
# import pandas as pd
# import numpy as np
# from scipy import sparse
# import implicit
# from azureml.core import Run
# from sklearn.externals import joblib
# from azureml.core import Workspace, Datastore
# from blob_service import BlobService
# import pip
# from feedback_service import FeedbackService
# from config import Config

# LIMIT = 0.99
# MKL_NUM_THREADS=1
# OPENBLAS_NUM_THREADS=1

# def store_predictions(blob_service_ref, source_path, destination_path):
#     blob_service_ref.store_blob(os.path.join(source_path, Config.get("files")["predictions"]), os.path.join(destination_path, Config.get("files")["predictions"]))
#     blob_service_ref.store_blob(os.path.join(source_path, Config.get("files")["user_factors"]), os.path.join(destination_path, Config.get("files")["user_factors"]))
#     blob_service_ref.store_blob(os.path.join(source_path, Config.get("files")["item_factors"]), os.path.join(destination_path, Config.get("files")["item_factors"]))

# def main():

#     parser = argparse.ArgumentParser("post_process")

#     parser.add_argument("--tenant", type=str, help="Tenant")
#     parser.add_argument("--predict_output_path", type=str, help="Warm recommendations")
#     parser.add_argument("--top_k", type=int, help="Top K recommendations for return")
#     parser.add_argument("--processed_output_container", type=str, help="Processed output container")
#     parser.add_argument("--processed_output_account", type=str, help="Processed output storage account")
#     parser.add_argument("--processed_output_key", type=str, help="Processed output storage account key")
#     parser.add_argument("--final_output_path", type=str, help="Warm recommendations")
#     parser.add_argument("--tenant_id", type=str, help="Tenant id")

#     args = parser.parse_args()

#     print("Argument 1: %s" % args.tenant)
#     print("Argument 2: %s" % args.predict_output_path)
#     print("Argument 3: %d" % args.top_k)
#     print("Argument 4: %s" % args.processed_output_container)
#     print("Argument 5: %s" % args.processed_output_account)
#     print("Argument 6: %s" % args.processed_output_key)
#     print("Argument 7: %s" % args.final_output_path)
#     print("Argument 8: %s" % args.tenant_id)

#     predictions = pd.read_csv(os.path.join(args.predict_output_path, Config.get("files")["predictions"]), encoding='utf-16')
#     print(len(predictions))
#     predictions = predictions[:args.top_k]

#     blob_service_ref = BlobService(args.processed_output_account, args.processed_output_key, args.processed_output_container)
#     feedback_service_ref = FeedbackService(args.processed_output_account, args.processed_output_key, args.tenant_id)

#     predicate = list(map(lambda x: not feedback_service_ref.is_recommendation_negative(x[0], x[1]) and\
#                                    not feedback_service_ref.is_recommendation_in_blacklist(x[0], x[1]), predictions[['User ID', 'Team ID']].values))
#     predictions = predictions[predicate]
#     print(f"After feedback & blacklist: {len(predictions)}")

#     predictions.iloc[:,1:].to_csv(os.path.join(args.predict_output_path, Config.get("files")["predictions"]), encoding='utf-16')

#     store_predictions(blob_service_ref, args.predict_output_path, args.tenant)
#     store_predictions(blob_service_ref, args.predict_output_path, os.path.join(args.tenant, time.strftime("%Y-%m-%d")))

#     # in order to hook cold recommendations pipeline
#     changelog_file_path = os.path.join(args.predict_output_path, Config.get("files")["changelog"])
#     with open(changelog_file_path, "w") as f:
#         f.write(f"{time.strftime('%Y-%m-%d')} - warm recommendations calculated.")
    
#     blob_service_ref.store_blob(changelog_file_path, Config.get("files")["changelog"])

#     print('Done.')

# if __name__ == "__main__":
#     main()