from ..src.services.simulation.lin_reg_graph import (
    ToolState,
    analysis_node,
    build_lin_reg_graph,
    validation_node,
)

# Kovakoodattuna tai voidaan käyttää sitä dataskriptiä...?
TEST_DATA_DICT = {
    "sales": {
        0: 172,
        1: 162,
        2: 84,
        3: 176,
        4: 141,
        5: 90,
        6: 172,
        7: 191,
        8: 144,
        9: 157,
        10: 186,
        11: 169,
        12: 173,
        13: 122,
        14: 71,
        15: 157,
        16: 107,
        17: 199,
        18: 90,
        19: 127,
        20: 91,
        21: 158,
        22: 118,
        23: 128,
        24: 84,
        25: 120,
        26: 177,
        27: 124,
        28: 133,
        29: 120,
    },
    "price": {
        0: 13.4,
        1: 12.25,
        2: 10.07,
        3: 14.71,
        4: 12.82,
        5: 11.93,
        6: 10.08,
        7: 11.15,
        8: 11.21,
        9: 13.42,
        10: 13.05,
        11: 14.17,
        12: 10.87,
        13: 11.96,
        14: 10.91,
        15: 13.78,
        16: 12.13,
        17: 11.04,
        18: 12.84,
        19: 10.16,
        20: 14.21,
        21: 12.25,
        22: 11.98,
        23: 14.63,
        24: 13.64,
        25: 11.63,
        26: 12.85,
        27: 12.6,
        28: 14.81,
        29: 14.22,
    },
    "customers": {
        0: 84,
        1: 57,
        2: 86,
        3: 92,
        4: 63,
        5: 65,
        6: 64,
        7: 99,
        8: 99,
        9: 99,
        10: 84,
        11: 80,
        12: 68,
        13: 54,
        14: 84,
        15: 40,
        16: 64,
        17: 46,
        18: 48,
        19: 63,
        20: 40,
        21: 83,
        22: 47,
        23: 63,
        24: 50,
        25: 90,
        26: 56,
        27: 47,
        28: 74,
        29: 74,
    },
    "sunny": {
        0: False,
        1: False,
        2: False,
        3: True,
        4: False,
        5: True,
        6: False,
        7: True,
        8: False,
        9: False,
        10: True,
        11: True,
        12: True,
        13: False,
        14: True,
        15: False,
        16: False,
        17: True,
        18: True,
        19: False,
        20: False,
        21: True,
        22: True,
        23: True,
        24: False,
        25: False,
        26: False,
        27: False,
        28: False,
        29: False,
    },
}

CORRECT_OUTPUT = {
    "price": 1.40,
    "sunny": 10.75,
    "customers": 0.44,
    "intercept": 86.0,
    "r-square": 0.08,
}


# def test_lin_graph_outputs_correct_values():
#     graph = build_lin_reg_graph()
#     graph_ran = graph.invoke({"df":TEST_DATA_DICT, 'y_value':'sales'})

#     results = graph_ran["results"]

#     price = round(results["coefficients"]["price"],2)
#     sunny = round(results["coefficients"]["sunny"],2)
#     customers = round(results["coefficients"]["customers"],2)
#     intercept = round(results["intercept"],2)
#     r_square = round(results["r2_score"],2)


#     assert price == CORRECT_OUTPUT["price"]
#     assert sunny == CORRECT_OUTPUT["sunny"]
#     assert customers == CORRECT_OUTPUT["customers"]
#     assert intercept == CORRECT_OUTPUT["intercept"]
#     assert r_square == CORRECT_OUTPUT["r-square"]


def test_validation_node_empty_dataframe():
    state: ToolState = {"df": {}}
    updated_state = validation_node(state)
    assert "errors" in updated_state
    assert updated_state["errors"] == ["No data provided."]


def test_validation_node_none_dataframe():
    state: ToolState = {"df": None}
    updated_state = validation_node(state)
    assert "errors" in updated_state
    assert updated_state["errors"] == ["No data provided."]


# def test_validation_node_missing_columns_in_data():
#     incomplete_data = {k: v for k, v in TEST_DATA_DICT.items() if k not in ("sunny")}
#     state: ToolState = {"df": incomplete_data}
#     updated_state = validation_node(state)
#     assert "errors" in updated_state


def test_analysis_node_skips_when_errors():
    state: ToolState = {"df": TEST_DATA_DICT, "errors": ["Some error happened"]}
    updated_state = analysis_node(state)
    assert "results" not in updated_state
    assert updated_state["errors"] == ["Some error happened"]
