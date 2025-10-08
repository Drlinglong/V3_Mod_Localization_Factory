import pytest
from unittest.mock import MagicMock
from scripts.utils.response_parser import parse_json_response

# 使用 parametrize 装饰器来覆盖多个测试场景
@pytest.mark.parametrize(
    "name, response_text, expected_count, expected_output",
    [
        # 场景1: 完美的JSON
        ("perfect_json", '["translation1", "translation2"]', 2, ["translation1", "translation2"]),

        # 场景2: 带Markdown代码块
        ("markdown_wrapped", '```json\n["item1", "item2"]\n```', 2, ["item1", "item2"]),

        # 场景3: 另一种Markdown形式
        ("markdown_simple", '```\n["itemA", "itemB"]\n```', 2, ["itemA", "itemB"]),

        # 场景4: “套壳”响应
        ("nested_response", '{"response": "[\\"nested1\\", \\"nested2\\"]"}', 2, ["nested1", "nested2"]),

        # 场景5: 格式错误的JSON
        ("malformed_json", '["missing_quote, "item2"]', 2, ["", ""]),

        # 场景6: JSON类型错误 (对象而非列表)
        ("wrong_type_json", '{"key": "value"}', 1, []),

        # 场景7: 数量不匹配 (少于预期)
        ("count_mismatch_less", '["only_one"]', 2, ["only_one", ""]),

        # 场景8: 数量不匹配 (多于预期)
        ("count_mismatch_more", '["one", "two", "three"]', 2, ["one", "two"]),

        # 场景9: 空列表
        ("empty_list", '[]', 0, []),

        # 场景10: 空字符串输入
        ("empty_string", '', 2, ["", ""]),

        # 场景11: 嵌套的错误JSON
        ("nested_malformed", '{"response": "[\\"invalid"}', 1, [""]),

        # 场景12: 包含数字和布尔值的JSON
        ("mixed_types", '[1, true, "text"]', 3, ["1", "True", "text"]),
    ],
)
def test_parse_json_response(mocker, name, response_text, expected_count, expected_output):
    """
    统一测试 parse_json_response 函数的多种场景。
    """
    # 模拟 i18n.t 函数，使其返回一个简单的格式化字符串
    mocker.patch("scripts.utils.i18n.t", side_effect=lambda key, **kwargs: f"i18n:{key} {kwargs}")

    # 模拟 _save_debug_file 函数，防止其在测试中创建文件
    mock_save_debug = mocker.patch("scripts.utils.response_parser._save_debug_file")

    # 执行被测试的函数
    result = parse_json_response(response_text, expected_count)

    # 断言结果是否符合预期
    assert result == expected_output, f"Test case '{name}' failed"

    # 验证在解析失败时是否调用了调试文件保存函数
    if name in ["malformed_json", "wrong_type_json", "nested_malformed", "empty_string"]:
        assert mock_save_debug.called, f"Expected _save_debug_file to be called for '{name}'"
    else:
        assert not mock_save_debug.called, f"Expected _save_debug_file not to be called for '{name}'"
