import os
import pint
import pickle
import pytest
from collections import Counter
from wwtp_configuration.units import u
from wwtp_configuration.utils import ContentsType
from wwtp_configuration.tag import Tag
from wwtp_configuration.parse_json import JSONParser
from wwtp_configuration.node import Cogeneration
from wwtp_configuration.connection import Pipe

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# set skip_all_tests = True to focus on single test
skip_all_tests = False

# set default pint registry so that custom units like MGD are understood
pint.set_application_registry(u)


@pytest.mark.skipif(skip_all_tests, reason="Exclude all tests")
@pytest.mark.parametrize(
    "json_path, tag_name, expected_path",
    [
        ("data/node.json", "PumpRuntime", "data/top_level_node_tag.pkl"),
        ("data/node.json", "ElectricityPurchases", "data/top_level_connection_tag.pkl"),
        ("data/node.json", "Digester1Level", "data/lower_level_node_tag.pkl"),
        (
            "data/node.json",
            "CombinedDigesterGasFlow",
            "data/lower_level_connection_tag.pkl",
        ),
        ("data/node.json", "NonexistentTag", None),
    ],
)
def test_get_tag(json_path, tag_name, expected_path):
    parser = JSONParser(json_path)
    result = parser.initialize_network()
    tag = result.get_tag(tag_name, recurse=True)

    expected = None
    if expected_path:
        with open(expected_path, "rb") as pickle_file:
            expected = pickle.load(pickle_file)

    assert tag == expected


@pytest.mark.skipif(skip_all_tests, reason="Exclude all tests")
@pytest.mark.parametrize(
    "json_path, obj_id, recurse, expected",
    [
        ("data/node.json", "Cogenerator", False, None),
        (
            "data/node.json",
            "Cogenerator",
            True,
            Cogeneration(
                "Cogenerator",
                [ContentsType.Biogas, ContentsType.NaturalGas],
                400 * u.kW,
                750 * u.kW,
                600 * u.kW,
                1,
            ),
        ),
        ("data/node.json", "SewerIntake", False, "data/sewer_intake.pkl"),
        ("data/node.json", "InvalidID", True, None),
    ],
)
def test_get_node_or_connection(json_path, obj_id, recurse, expected):
    result = (
        JSONParser(json_path)
        .initialize_network()
        .get_node_or_connection(obj_id, recurse=recurse)
    )

    if isinstance(expected, str) and os.path.isfile(expected):
        with open(expected, "rb") as pickle_file:
            expected = pickle.load(pickle_file)

    assert result == expected


@pytest.mark.skipif(skip_all_tests, reason="Exclude all tests")
@pytest.mark.parametrize(
    "json_path, recurse, connection_path, node_path, tag_path",
    [
        (
            "data/node.json",
            False,
            "data/top_level_connections.pkl",
            "data/top_level_nodes.pkl",
            "data/top_level_tags.pkl",
        ),
        (
            "data/node.json",
            True,
            "data/all_connections.pkl",
            "data/all_nodes.pkl",
            "data/all_tags.pkl",
        ),
    ],
)
def test_get_all(json_path, recurse, connection_path, node_path, tag_path):
    parser = JSONParser(json_path)
    result = parser.initialize_network()

    with open(connection_path, "rb") as pickle_file:
        connections = pickle.load(pickle_file)

    assert result.get_all_connections(recurse=recurse) == connections

    with open(node_path, "rb") as pickle_file:
        nodes = pickle.load(pickle_file)

    assert result.get_all_nodes(recurse=recurse) == nodes

    with open(tag_path, "rb") as pickle_file:
        tags = pickle.load(pickle_file)

    # Counter is used so that order is ignored
    assert Counter(result.get_all_tags(recurse=recurse)) == Counter(tags)


@pytest.mark.skipif(skip_all_tests, reason="Exclude all tests")
@pytest.mark.parametrize(
    "json_path, cogen_id, efficiency_arg, expected",
    [
        ("data/connection.json", "Cogenerator", None, 0.32),
        ("data/connection.json", "Cogenerator", 2000, 0.32),
    ],
)
def test_set_energy_efficiency(json_path, cogen_id, efficiency_arg, expected):
    parser = JSONParser(json_path)
    result = parser.initialize_network()
    cogen = result.get_node(cogen_id)
    assert cogen.energy_efficiency(efficiency_arg) == expected


@pytest.mark.skipif(skip_all_tests, reason="Exclude all tests")
@pytest.mark.parametrize(
    "json_path, desired_type, recurse, expected",
    [
        ("data/node.json", None, False, "TypeError"),
        ("data/node.json", Cogeneration, False, []),
        ("data/node.json", Pipe, False, "data/get_pipe_no_recurse.pkl"),
        ("data/connection.json", Cogeneration, False, "data/get_cogen.pkl"),
        ("data/node.json", Cogeneration, True, "data/get_cogen.pkl"),
        ("data/node.json", Pipe, True, "data/get_pipe_recurse.pkl"),
    ],
)
def test_get_list_of_type(json_path, desired_type, recurse, expected):
    try:
        parser = JSONParser(json_path)
        result = parser.initialize_network().get_list_of_type(desired_type, recurse)

        if isinstance(expected, str) and os.path.isfile(expected):
            with open(expected, "rb") as pickle_file:
                expected = pickle.load(pickle_file)
    except Exception as err:
        result = type(err).__name__

    assert result == expected


@pytest.mark.skipif(skip_all_tests, reason="Exclude all tests")
@pytest.mark.parametrize(
    "json_path, node_id, expected",
    [
        # Case 1: node does not exist
        ("data/node.json", "InvalidNode", []),
        # Case 2: no incoming connections but node exists
        ("data/node.json", "RawSewagePump", []),
        # Case 3: only normal connections
        ("data/node.json", "Cogenerator", "data/connection_to_cogen.pkl"),
        # Case 4: normal connections and entry_point
        ("data/node.json", "Digester", "data/connection_to_digester.pkl"),
    ],
)
def test_get_all_connections_to(json_path, node_id, expected):
    parser = JSONParser(json_path)
    config = parser.initialize_network()
    result = config.get_all_connections_to(config.get_node(node_id, recurse=True))

    if isinstance(expected, str) and os.path.isfile(expected):
        with open(expected, "rb") as pickle_file:
            expected = pickle.load(pickle_file)

    assert result == expected


@pytest.mark.skipif(skip_all_tests, reason="Exclude all tests")
@pytest.mark.parametrize(
    "json_path, node_id, expected",
    [
        # Case 1: node does not exist
        ("data/node.json", "InvalidNode", []),
        # Case 2: no outgoing connections but node exists
        ("data/node.json", "Cogenerator", []),
        # Case 3: only normal connections
        ("data/node.json", "RawSewagePump", "data/connection_from_sewer.pkl"),
        # Case 4: normal connections and exit_point
        ("data/node.json", "Digester", "data/connection_from_digester.pkl"),
    ],
)
def test_get_all_connections_from(json_path, node_id, expected):
    parser = JSONParser(json_path)
    config = parser.initialize_network()
    result = config.get_all_connections_from(config.get_node(node_id, recurse=True))

    if isinstance(expected, str) and os.path.isfile(expected):
        with open(expected, "rb") as pickle_file:
            expected = pickle.load(pickle_file)

    assert result == expected


@pytest.mark.skipif(skip_all_tests, reason="Exclude all tests")
@pytest.mark.parametrize(
    "json_path, tag_path, expected",
    [
        # Case 1: tag does not exist
        ("data/node.json", "NonexistentTag", None),
        # Case 2: tag exists at a top level connection
        (
            "data/node.json",
            "data/top_level_connection_tag.pkl",
            "data/electricty_to_wwtp.pkl",
        ),
        # Case 3: tag exists at a lower level connection
        (
            "data/node.json",
            "data/lower_level_connection_tag.pkl",
            "data/gas_to_cogen.pkl",
        ),
        # Case 4: tag exists at a top level node
        ("data/node.json", "data/top_level_node_tag.pkl", "data/sewage_pump.pkl"),
        # Case 5: tag exists at a lower level node
        ("data/node.json", "data/lower_level_node_tag.pkl", "data/digester.pkl"),
    ],
)
def test_get_parent_from_tag(json_path, tag_path, expected):
    if isinstance(tag_path, str) and os.path.isfile(tag_path):
        with open(tag_path, "rb") as pickle_file:
            tag = pickle.load(pickle_file)
    else:
        tag = Tag(tag_path, None, None, None, None, None)

    parser = JSONParser(json_path)
    config = parser.initialize_network()
    result = config.get_parent_from_tag(tag)

    if isinstance(expected, str) and os.path.isfile(expected):
        with open(expected, "rb") as pickle_file:
            expected = pickle.load(pickle_file)

    assert result == expected


@pytest.mark.skipif(skip_all_tests, reason="Exclude all tests")
@pytest.mark.parametrize(
    "json_path, source_id, dest_id, source_node_type, dest_node_type, "
    "contents_type, tag_type, recurse, expected",
    [
        # Case 1: no objects match search criteria
        (
            "data/node.json", 
            "NonexistentConnection", 
            None, 
            None,
            None,
            None,
            None,
            True,
            []
        ),
        # Case 2: return a single connection by source and destination
        (
            "data/node.json", 
            "NonexistentConnection", 
            None, 
            None,
            None,
            None,
            None,
            True,
            []
        ),
        # Case 3: return multiple connections by source
        # Case 4: return multiple connections by destination
        # Case 5: return connections by exit point
        # Case 6: return connections by entry point
        # Case 7: return a single tag by source unit ID
        # Case 8: return a single tag by destination unit ID
        # Case 9: return multiple tags by source
        # Case 10: return multiple tags by destination
    ],
)
def test_select_objs(
    json_path, 
    source_id,
    dest_id,
    source_node_type,
    dest_node_type,
    contents_type,
    tag_type,
    recurse,
    expected
):
    parser = JSONParser(json_path)
    config = parser.initialize_network() 
    try:
        result = config.select_objs(
            source_id,
            dest_id,
            source_node_type,
            dest_node_type,
            contents_type,
            tag_type,
            recurse,
        )
    except Exception as err:
        result = type(err).__name__

    if isinstance(expected, str) and os.path.isfile(expected):
        with open(expected, "rb") as pickle_file:
            expected = pickle.load(pickle_file)

    assert result == expected