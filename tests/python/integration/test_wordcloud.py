# -*- coding: utf-8 -*-
import pytest
import logging

from dku_plugin_test_utils import dss_scenario

pytestmark = pytest.mark.usefixtures("plugin", "dss_target")

test_kwargs = {
    "user": "user1",
    "project_key": "TEST_NLPVISUALIZATIONPLUGIN",
    "logger": logging.getLogger("dss-plugin-test.nlp-visualization.test_wordcloud"),
}


def test_wordcloud_monolingual_simple(user_clients):
    test_kwargs["client"] = user_clients[test_kwargs["user"]]
    dss_scenario.run(scenario_id="monolingual_simple", **test_kwargs)


def test_wordcloud_monolingual_subcharts(user_clients):
    test_kwargs["client"] = user_clients[test_kwargs["user"]]
    dss_scenario.run(scenario_id="Copy_of_monolingual_simple", **test_kwargs)


def test_wordcloud_multilingual_simple(user_clients):
    test_kwargs["client"] = user_clients[test_kwargs["user"]]
    dss_scenario.run(scenario_id="multilingual_simple", **test_kwargs)


def test_wordcloud_multilingual_subcharts(user_clients):
    test_kwargs["client"] = user_clients[test_kwargs["user"]]
    dss_scenario.run(scenario_id="multilingual_subcharts", **test_kwargs)


def test_wordcloud_multilingual_subcharts_unsupported_languages(user_clients):
    test_kwargs["client"] = user_clients[test_kwargs["user"]]
    dss_scenario.run(scenario_id="multilingual_subcharts_unsupported_languages", **test_kwargs)


def test_wordcloud_multilingual_subcharts_per_language(user_clients):
    test_kwargs["client"] = user_clients[test_kwargs["user"]]
    dss_scenario.run(scenario_id="subchart_per_language", **test_kwargs)


def test_wordcloud_partitioned_folder_file(user_clients):
    test_kwargs["client"] = user_clients[test_kwargs["user"]]
    dss_scenario.run(scenario_id="partitionned_folder_file", **test_kwargs)


def test_wordcloud_partitioned_folder_sql(user_clients):
    test_kwargs["client"] = user_clients[test_kwargs["user"]]
    dss_scenario.run(scenario_id="partitionned_folder_sql", **test_kwargs)


def test_wordcloud_partitioned_output(user_clients):
    test_kwargs["client"] = user_clients[test_kwargs["user"]]
    dss_scenario.run(scenario_id="partitionned_output", **test_kwargs)


def test_wordcloud_unpartitioned_folder_file(user_clients):
    test_kwargs["client"] = user_clients[test_kwargs["user"]]
    dss_scenario.run(scenario_id="unpartitionned_folder_file", **test_kwargs)


def test_wordcloud_unpartitioned_folder_sql(user_clients):
    test_kwargs["client"] = user_clients[test_kwargs["user"]]
    dss_scenario.run(scenario_id="unpartitionned_folder_sql", **test_kwargs)
