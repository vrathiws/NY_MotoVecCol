import unittest
from unittest import mock
from unittest.mock import Mock, MagicMock, call, patch
import comparator

class TestComparators(unittest.TestCase):
    def test_abstract_comparator_must_have_implementation(self):
        class MyClass(comparator.Comparator):
            pass

        with self.assertRaises(TypeError):
            MyClass()

    def test_struct_comparator_can_be_created(self):
        try:
            comparator.StructComparator()
        except:
            self.fail("Creating StructComparator raised an exception")

    def test_struct_comparator_compares_object_equality(self):
        object_a = MagicMock()
        object_a.__eq__.return_value = True
        object_b = "test object"

        cmp = comparator.StructComparator()
        self.assertTrue(cmp.equals(object_a, object_b))

        object_a.__eq__.assert_called_once_with(object_b)

    def test_struct_comparator_handles_nested_structures(self):
        object_a = { "a": [1,2,3,{ "b": 4}, 5], "b": {} }
        object_b = { "a": [1,2,3,{ "b": 4}, 5], "b": {} }
        object_c = { "a": [1,2,3,{ "b": 5}, 5], "b": {} }

        cmp = comparator.StructComparator()
        self.assertTrue(cmp.equals(object_a, object_b))
        self.assertFalse(cmp.equals(object_a, object_c))

    def test_struct_comparator_handles_none_input(self):
        cmp = comparator.StructComparator()
        self.assertTrue(cmp.equals(None, None))
        self.assertFalse(cmp.equals(None, {}))

    def test_json_comparator_can_be_created(self):
        try:
            comparator.JsonComparator()
        except:
            self.fail("Creating JsonComparator raised an exception")

    def test_json_comparator_raises_with_none_input(self):
        cmp = comparator.JsonComparator()

        with self.assertRaises(RuntimeError):
            cmp.equals(None, "{}")

        with self.assertRaises(RuntimeError):
            cmp.equals("{}", None)

        with self.assertRaises(RuntimeError):
            cmp.equals(None, None)

    def test_json_comparator_raises_if_not_string(self):
        cmp = comparator.JsonComparator()

        with self.assertRaises(RuntimeError):
            cmp.equals(1, "{}")

        with self.assertRaises(RuntimeError):
            cmp.equals("{}", cmp)

        with self.assertRaises(RuntimeError):
            cmp.equals(b"{}", "")

    def test_json_comparator_raises_if_empty_string(self):
        cmp = comparator.JsonComparator()

        with self.assertRaises(RuntimeError):
            cmp.equals("{}", "")

        with self.assertRaises(RuntimeError):
            cmp.equals("", "{}")

    def test_json_comparator_raises_if_invalid_json(self):
        cmp = comparator.JsonComparator()

        with self.assertRaises(RuntimeError):
            cmp.equals("some text", "{}")

        with self.assertRaises(RuntimeError):
            cmp.equals("{}", "text")

    def test_json_comparator_works_with_valid_json(self):
        cmp = comparator.JsonComparator()

        try:
            self.assertTrue(cmp.equals("{}", "{}"))
            self.assertFalse(cmp.equals('{"a":[1,2,3]}', '{"a":[1,2]}'))
        except:
            self.fail("Error processing JSON")

    def test_json_comparator_passes_parsed_results_to_delegate(self):
        delegate = Mock()
        delegate.equals = Mock(return_value=True)

        cmp = comparator.JsonComparator(delegate=delegate)
        self.assertTrue(cmp.equals('{"a":[1,2,3]}', '{"a":[1,2]}'))

        delegate.equals.assert_called_once_with(
            {"a": [1,2,3]},
            {"a": [1,2]}
        )

    def test_http_comparator_can_be_created(self):
        try:
            comparator.HttpComparator()
        except:
            self.fail("Creating HttpComparator raised an exception")

    def test_http_comparator_raises_if_none_url(self):
        cmp = comparator.HttpComparator()

        with self.assertRaises(RuntimeError):
            cmp.equals(None, "http://foo.bar")

        with self.assertRaises(RuntimeError):
            cmp.equals("http://foo.bar", None)

    def test_http_comparator_raises_if_non_string_url(self):
        cmp = comparator.HttpComparator()

        with self.assertRaises(RuntimeError):
            cmp.equals(123, "http://foo.bar")

        with self.assertRaises(RuntimeError):
            cmp.equals("http://foo.bar", 123)

        with self.assertRaises(RuntimeError):
            cmp.equals(cmp, "http://foo.bar")

        with self.assertRaises(RuntimeError):
            cmp.equals("http://foo.bar", cmp)

    def test_http_comparator_raises_if_invalid_url(self):
        cmp = comparator.HttpComparator()

        with self.assertRaises(RuntimeError):
            cmp.equals("some text", "http://foo.bar")

        with self.assertRaises(RuntimeError):
            cmp.equals("http://foo.bar", "text")

    def test_http_comparator_calls_http_client_to_get_response(self):
        client = Mock()
        response = MagicMock()
        delegate = MagicMock()
        client.get = Mock(return_value=response)

        cmp = comparator.HttpComparator( http_client = client, body_comparator = delegate )
        cmp.equals("http://foo.bar", "http://bar.buz")

        client.get.assert_has_calls([call("http://foo.bar"), call("http://bar.buz")])

    @patch.object(comparator.HttpClient, "get")
    def test_http_comparator_compares_http_client_response_status(self, mock_client):
        response_a = Mock()
        response_a.status = 1
        response_a.headers = {}

        response_b = Mock()
        response_b.status = 2
        response_b.headers = {}

        mock_client.get.side_effect = [response_a, response_b]

        delegate = Mock()

        cmp = comparator.HttpComparator( http_client = mock_client, body_comparator = delegate )
        self.assertFalse(cmp.equals("http://foo.bar", "http://bar.buz"))

        mock_client.get.assert_has_calls([call("http://foo.bar"), call("http://bar.buz")])

        mock_client.get.side_effect = [response_a, response_a]
        self.assertTrue(cmp.equals("http://foo.bar", "http://bar.buz"))

    @patch.object(comparator.HttpClient, "get")
    def test_http_comparator_compares_http_client_response_headers_with_check_headers(self, mock_client):
        response_a = Mock()
        response_a.status = 1
        response_a.headers = { "bar": "buz" }

        response_b = Mock()
        response_b.status = 1
        response_b.headers = { "foo": "bar" }

        delegate = Mock()

        cmp = comparator.HttpComparator( check_headers=True, http_client = mock_client, body_comparator = delegate )

        mock_client.get.side_effect = [response_a, response_b]
        self.assertFalse(cmp.equals("http://foo.bar", "http://bar.buz"))

        mock_client.get.side_effect = [response_a, response_a]
        self.assertTrue(cmp.equals("http://foo.bar", "http://bar.buz"))
    
    @patch.object(comparator.HttpClient, "get")
    def test_http_comparator_ignores_http_client_response_headers_without_check_headers(self, mock_client):
        response_a = Mock()
        response_a.status = 1
        response_a.headers = { "bar": "buz" }

        response_b = Mock()
        response_b.status = 1
        response_b.headers = { "foo": "bar" }

        delegate = Mock()

        cmp = comparator.HttpComparator( check_headers=False, http_client = mock_client, body_comparator = delegate )

        mock_client.get.side_effect = [response_a, response_b]
        self.assertTrue(cmp.equals("http://foo.bar", "http://bar.buz"))

        mock_client.get.side_effect = [response_a, response_a]
        self.assertTrue(cmp.equals("http://foo.bar", "http://bar.buz"))

    @patch.object(comparator.HttpClient, "get")
    def test_http_comparator_raises_when_reponse_body_cannot_be_read(self, mock_client):
        def raise_exception():
            raise RuntimeError()

        response_a = Mock()
        response_a.status = 1
        response_a.read = raise_exception

        response_b = Mock()
        response_b.status = 1
        response_b.read = Mock(return_value=b"")

        delegate = Mock()

        cmp = comparator.HttpComparator( check_headers=False, http_client = mock_client, body_comparator = delegate )

        mock_client.get.side_effect = [response_a, response_b]
        with self.assertRaises(RuntimeError):
            cmp.equals("http://foo.bar", "http://bar.buz")

        mock_client.get.side_effect = [response_b, response_a]
        with self.assertRaises(RuntimeError):
            cmp.equals("http://foo.bar", "http://bar.buz")

        mock_client.get.side_effect = [response_a, response_a]
        with self.assertRaises(RuntimeError):
            cmp.equals("http://foo.bar", "http://bar.buz")

        mock_client.get.side_effect = [response_b, response_b]
        try:
            cmp.equals("http://foo.bar", "http://bar.buz")
        except:
            self.fail("Should not raise an exception")

    @patch.object(comparator.HttpClient, "get")
    def test_http_comparator_passes_response_body_to_delegate_for_comparison(self, mock_client):
        response_a = Mock()
        response_a.status = 1
        response_a.read = Mock(return_value=b"first response")

        response_b = Mock()
        response_b.status = 1
        response_b.read = Mock(return_value=b"second response")

        delegate = Mock()
        delegate.equals = Mock(return_value=True)

        cmp = comparator.HttpComparator( check_headers=False, http_client = mock_client, body_comparator = delegate )

        mock_client.get.side_effect = [response_a, response_b]
        cmp.equals("http://foo.bar", "http://bar.buz")

        delegate.equals.assert_called_once_with("first response", "second response")

    @patch.object(comparator.HttpClient, "get")
    def test_http_comparator_passes_response_headers_to_delegate_for_comparison(self, mock_client):
        response_a = Mock()
        response_a.status = 1
        response_a.headers = { "first response": "header" }

        response_b = Mock()
        response_b.status = 1
        response_b.headers = { "second response": "header" }

        delegate = Mock()
        delegate.equals = Mock(return_value=False)

        cmp = comparator.HttpComparator( check_headers=True, http_client = mock_client, header_comparator = delegate )

        mock_client.get.side_effect = [response_a, response_b]
        cmp.equals("http://foo.bar", "http://bar.buz")

        delegate.equals.assert_called_once_with({ "first response": "header" }, { "second response": "header" })

if __name__ == '__main__':
    unittest.main()