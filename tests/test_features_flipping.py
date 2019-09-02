import pandas as pd
import os

from src.backend.utils.db_utils import insert_new_feature


def test_feature_flipping_insertion(database, app):

    dir_path = os.path.dirname(os.path.realpath(__file__))
    users_features_path = os.path.join(dir_path, "fixtures", "features_1.xlsx")
    users_df = pd.read_excel(users_features_path)

    insert_new_feature(
        datalake_connection=database,
        feature_name="test_feature",
        feature_description="fake_description",
        platforms=["ios", "android"],
        environments=["prod"],
        users_df=users_df,
    )
