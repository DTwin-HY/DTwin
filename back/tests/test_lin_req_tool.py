import pandas as pd
from unittest.mock import MagicMock, patch

from ..src.services.simulation import lin_reg_tool as tool_module
from ..tests.test_lin_reg_graph import TEST_DATA_DICT


def test_lin_reg_tool_success():
    mock_csv_fetch = MagicMock(return_value=TEST_DATA_DICT)
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {"results": {"r-square":0.08}}
    mock_build_graph = MagicMock(return_value=mock_graph)

    with patch.object(tool_module, "csv_fetch", mock_csv_fetch), \
         patch.object(tool_module, "build_lin_reg_graph", mock_build_graph):

        result = tool_module.lin_reg_tool.invoke({"data_location": "fake_path.csv", 'y_value':'sales'})

        mock_csv_fetch.assert_called_once_with("fake_path.csv")
        mock_build_graph.assert_called_once()
        mock_graph.invoke.assert_called_once_with({"df": TEST_DATA_DICT, 'y_value':'sales'})

        assert result["r-square"] == 0.08

def test_lin_reg_tool_error_on_csv_fail():
    with patch.object(tool_module, "csv_fetch", side_effect=FileNotFoundError):
        result = tool_module.lin_reg_tool.invoke({"data_location": "bad_path.csv",'y_value':'sales'})
        assert result == "Failed to load data."
        
def test_csv_fetch(tmp_path):
    file_path = tmp_path / "test_data.csv"
    pd.DataFrame.from_dict(TEST_DATA_DICT).to_csv(file_path, index=False)

    result = tool_module.csv_fetch(str(file_path))

    assert isinstance(result, dict)
