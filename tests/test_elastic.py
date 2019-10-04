from icinga_notificator.utils import elastic
import pytest
import mock


def test_queryEs_BadArgs1():
    assert elastic.queryEs(None, None, None, None, None) == 1


def test_queryEs_BadArgs2():
    assert elastic.queryEs(None, "icinga", "why not", 123, 122) == 2


@mock.patch("elasticsearch.Elasticsearch")
def test_queryEs_OKArgs1(mock_es):
    mock_es.search.return_value = 123
    assert elastic.queryEs(mock_es, "icinga", "why not", 123, 122) == 123


def test_markAsHandled_BadArgs1():
    assert elastic.markAsHandled(None, None, None, None, None) == 1


def test_markAsHandled_BadArgs2():
    assert elastic.markAsHandled(None, "icinga", "why not", 123, 122) == 2


@mock.patch("elasticsearch.Elasticsearch")
def test_markAsHandled_OKArgs1(mock_es):
    mock_es.update_by_query.return_value = 123
    assert elastic.markAsHandled(mock_es, "icinga", "why not", 123, 122) == 0
