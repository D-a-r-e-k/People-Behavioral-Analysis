# import argparse
# import os
# import time
# import pandas as pd
# import numpy as np
# from scipy import sparse
# import implicit
# from azureml.core import Run
# from sklearn.externals import joblib
# from config import Config
# from recommendations_filter_service import RecommendationsFilterService
# from memberships_scorer import MembershipsScorer

# LIMIT = 0.99
# MKL_NUM_THREADS=1
# OPENBLAS_NUM_THREADS=1

# def get_explanations(model, user_items_sparse, teams, user, team):
#     explanation = model.explain(user, user_items_sparse, team, None, N=3)
#     return list(map(lambda x: tuple(teams.loc[x[0], ['Id', 'DisplayName']]),explanation[1]))

# def get_top_recommendations(model, memberships, users, teams, threshold, k):
#     recommendations_filter = RecommendationsFilterService(memberships, users)
    
#     all_recommendations = []
#     user_items_sparse = sparse.csr_matrix(memberships)

#     for u in range(users.shape[0]):
#         user = users.iloc[u]
#         u_dep = user.Department
#         u_loc = f"{user.Country}.{user.City}"

#         recommendations = [x for x in model.recommend(u, user_items_sparse, filter_already_liked_items = True, N=k)\
#             if x[1] > threshold and teams.iloc[x[0], teams.columns.get_loc('IsOutdated')] == 0 and\
#                 recommendations_filter.is_loc_eligible(u_loc, x[0]) and recommendations_filter.is_dep_eligible(u_dep, x[0])]
#         all_recommendations.extend(list(map(lambda x: (u, x[0], x[1]), recommendations)))
    
#     all_recommendations.sort(key=lambda x: x[2], reverse=True)
#     print("Biggest/Smallest analysis:")

#     top_recommendation = all_recommendations[0]
#     print(top_recommendation[2])
#     print(all_recommendations[len(all_recommendations) - 1][2])
#     all_recommendations = [(x[0], x[1], np.sqrt(x[2] / top_recommendation[2])) for x in all_recommendations]
#     print(all_recommendations[0][2])
#     print(all_recommendations[len(all_recommendations) - 1][2])

#     all_recommendations = list(map(lambda x: (x[0], x[1], min(LIMIT, x[2]), 
#             get_explanations(model, user_items_sparse, teams, x[0], x[1])), all_recommendations))

#     formated_recs = list(map(lambda x: (users.loc[x[0], 'DisplayName'], users.loc[x[0], 'Id'], users.loc[x[0], 'Mail'],
#          teams.loc[x[1], 'DisplayName'], teams.loc[x[1], 'Description'], teams.loc[x[1], 'Owners'],
#          teams.loc[x[1], 'Id'], 1 if teams.loc[x[1], 'Visibility'] == "Private" else 0, teams.loc[x[1], 'JoinLink'], round(x[2] * 100,2)) + tuple([e for t in x[3] for e in t]), all_recommendations))

#     recs_df = pd.DataFrame(formated_recs, columns=['User', 'User ID', 'User email', 'Team', 'Team desc',
#                                           'Team owners', 'Team ID', 'Team type',  'Team link', 'Score',
#                                           'Team 1 Id', 'Team 1 Name', 'Team 2 Id', 'Team 2 Name', 'Team 3 Id', 'Team 3 Name'])

#     return recs_df

# def store_predictions(directory, user_factors, item_factors, recommendations):
#     os.makedirs(directory, exist_ok=True)

#     recommendations.to_csv(os.path.join(directory, Config.get("files")["predictions"]), encoding='utf-16')
#     np.savetxt(os.path.join(directory, Config.get("files")["item_factors"]), item_factors, delimiter=",", fmt='%1.4f')
#     np.savetxt(os.path.join(directory, Config.get("files")["user_factors"]), user_factors, delimiter=",", fmt='%1.4f')

# def main():
#     parser = argparse.ArgumentParser("deploy")

#     parser.add_argument("--input_path", type=str, help="Users, Teams, Memberships")
#     parser.add_argument("--tenant", type=str, help="Tenant")
#     parser.add_argument("--model_path", type=str, help="Warm recommendations model")
#     parser.add_argument("--threshold", type=float, help="Treshold")
#     parser.add_argument("--k", type=int, help="K")
#     parser.add_argument("--predict_output_path", type=str, help='Predictions path')
#     parser.add_argument("--engagement_importance", type=int, help="Engagement importance")
#     parser.add_argument("--department_importance", type=int, help="Department importance")
#     parser.add_argument("--office_importance", type=int, help="Office importance")
#     parser.add_argument("--manager_importance", type=int, help="Manager importance")
#     parser.add_argument("--location_importance", type=int, help="Location importance")

#     args = parser.parse_args()

#     print("Argument 1: %s" % args.input_path)
#     print("Argument 2: %s" % args.tenant)
#     print("Argument 3: %s" % args.model_path)
#     print("Argument 4: %f" % args.threshold)
#     print("Argument 5: %d" % args.k)
#     print("Argument 6: %s" % args.predict_output_path)
#     print("Argument 7: %d" % args.engagement_importance)
#     print("Argument 8: %d" % args.department_importance)
#     print("Argument 9: %d" % args.office_importance)
#     print("Argument 10: %d" % args.manager_importance)
#     print("Argument 11: %d" % args.location_importance)

#     model_path = f'{args.model_path}/{args.tenant}-w.sav'
#     model = joblib.load(model_path)

#     memberships_path = os.path.join(args.input_path, Config.get("files")["memberships"])
#     users_path = os.path.join(args.input_path, Config.get("files")["users"])
#     teams_path = os.path.join(args.input_path, Config.get("files")["teams"])
#     engagement_path = os.path.join(args.input_path, Config.get("files")["engagement"])

#     memberships = pd.read_csv(memberships_path, header = None)
#     users = pd.read_csv(users_path)
#     teams = pd.read_csv(teams_path)
#     engagement = pd.read_csv(engagement_path, header = None)

#     memberships, users = MembershipsScorer(memberships, users, teams, engagement, args)\
#         .include_content_information()\
#         .include_engagement_information()\
#         .get_memberships_with_users()

#     recommendations = get_top_recommendations(model, memberships, users, teams, args.threshold, args.k)

#     store_predictions(args.predict_output_path, model.user_factors, model.item_factors, recommendations)

#     print('Successfully updated predictions')
    
# if __name__ == "__main__":
#     main()