# -*- coding: utf-8 -*-
from dku_plugin_test_utils import dss_scenario


TEST_PROJECT_KEY = "TEST_NLPVISUALIZATIONPLUGIN"


def test_wordcloud_monolingual_simple(user_dss_clients):
    dss_scenario.run(user_dss_clients, project_key=TEST_PROJECT_KEY, scenario_id="monolingual_simple")


def test_wordcloud_monolingual_subcharts(user_dss_clients):
    dss_scenario.run(user_dss_clients, project_key=TEST_PROJECT_KEY, scenario_id="Copy_of_monolingual_simple")


def test_wordcloud_multilingual_simple(user_dss_clients):
    dss_scenario.run(user_dss_clients, project_key=TEST_PROJECT_KEY, scenario_id="multilingual_simple")


def test_wordcloud_multilingual_subcharts(user_dss_clients):
    dss_scenario.run(user_dss_clients, project_key=TEST_PROJECT_KEY, scenario_id="multilingual_subcharts")


def test_wordcloud_multilingual_subcharts_unsupported_languages(user_dss_clients):
    dss_scenario.run(
        user_dss_clients, project_key=TEST_PROJECT_KEY, scenario_id="multilingual_subcharts_unsupported_languages"
    )


def test_wordcloud_multilingual_subcharts_per_language(user_dss_clients):
    dss_scenario.run(user_dss_clients, project_key=TEST_PROJECT_KEY, scenario_id="subchart_per_language")


def test_wordcloud_edge_cases_multilingual(user_dss_clients):
    dss_scenario.run(user_dss_clients, project_key=TEST_PROJECT_KEY, scenario_id="EDGE_CASES")


def test_wordcloud_partitioned_folder_file(user_dss_clients):
    dss_scenario.run(user_dss_clients, project_key=TEST_PROJECT_KEY, scenario_id="partitionned_folder_file")


def test_wordcloud_partitioned_folder_sql(user_dss_clients):
    dss_scenario.run(user_dss_clients, project_key=TEST_PROJECT_KEY, scenario_id="partitionned_folder_sql")


def test_wordcloud_partitioned_output(user_dss_clients):
    dss_scenario.run(user_dss_clients, project_key=TEST_PROJECT_KEY, scenario_id="partitionned_output")


def test_wordcloud_unpartitioned_folder_file(user_dss_clients):
    dss_scenario.run(user_dss_clients, project_key=TEST_PROJECT_KEY, scenario_id="unpartitionned_folder_file")


def test_wordcloud_unpartitioned_folder_sql(user_dss_clients):
    dss_scenario.run(user_dss_clients, project_key=TEST_PROJECT_KEY, scenario_id="unpartitionned_folder_sql")

    
def test_wordcloud_long_text(user_dss_clients):
    dss_scenario.run(user_dss_clients, project_key=TEST_PROJECT_KEY, scenario_id="TEST_LONGTEXT")

