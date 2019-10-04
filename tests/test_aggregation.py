from icinga_notificator.functions import aggregation
import test_objects


# class like icingaNotification, but limited to content
# class icingaNotification:
#    def __init__(self, toObj):
#        self.obj= toObj

# basic tests to check if we can aggregate objects
def test_aggregateBy_BadArgs1():
    # args: NoneType(bad)
    assert aggregation.aggregateBy(None, None) == 1


def test_aggregateBy_BadArgs2():
    # args: empty list(bad); none(bad)
    assert aggregation.aggregateBy(list(), None) == 1


def test_aggregateBy_BadArgs3():
    # args: empty list(bad), string(ok)
    assert aggregation.aggregateBy(list(), "HOST") == 1


def test_aggregateBy_BadArgs4():
    # args: list(ok), int(bad)
    assert aggregation.aggregateBy([{"host": "data", "service": "data"}], 123) == 1


def test_aggregateBy_BadArgs5():
    # args: list(ok), str(ok); should fail, bad input
    assert aggregation.aggregateBy(["some", "thing"], "host") == 1


def test_aggregateBy_AggregationBasic1():
    # basic check if everything works as it should (first usage)
    e = dict()

    by = "a"
    c = test_objects.icingaNotifGen().getObj("list")
    e = {"1": c}

    assert aggregation.aggregateBy(c, by) == e


def test_aggregateBy_AggregationBasic2():
    # basic check if everything works as it should (second usage)
    e = dict()

    by = "a"
    c = test_objects.icingaNotifGen().getObj("class")
    e = {"1": c}

    assert aggregation.aggregateBy(c, by) == e


def test_aggregateBy_AggregationBasic3():
    e = dict()

    by = "c"
    c = test_objects.icingaNotifGen(15).getObj("list")
    e = {"Host(UP)": c}

    assert aggregation.aggregateBy(c, by) == e


def test_aggregateBy_AggregationBasic4():
    e = dict()

    by = "d"
    c = test_objects.icingaNotifGen(5).getObj("list")
    e = {"one": c, "two": c}

    print(aggregation.aggregateBy(c, by))
    assert aggregation.aggregateBy(c, by) == e


def test_aggregateBy_AggregationBasic5():
    e = dict()

    by = "d"
    c = test_objects.icingaNotifGen(5).getObj("class")
    e = {"one": c, "two": c}

    print(aggregation.aggregateBy(c, by))
    assert aggregation.aggregateBy(c, by) == e
