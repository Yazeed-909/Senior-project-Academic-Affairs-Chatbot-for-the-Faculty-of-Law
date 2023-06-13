import unittest
from unittest.mock import patch
from DatasetPars import DatasetPars


class TestDatasetPars(unittest.TestCase):
    def setUp(self):
        # Create an instance of the DatasetPars class for each test case
        self.dataset_pars = DatasetPars("Model_data\\Dataset.json")

    def test_loading_dataset(self):
        # Test the Loading_Dataset method
        dataset_location = "Model_data\\Dataset.json"

        # Prepare the mock file content as a JSON-formatted string
        mock_file_content = """
        {
            "dataset": [
                {
                    "tag": "greeting",
                    "response": "Hello!",
                    "index": "01",
                    "input": ["Hi", "Hello", "Hey"]
                },
                {
                    "tag": "farewell",
                    "response": "Goodbye!",
                    "index": "02",
                    "input": ["Bye", "Goodbye", "See you"]
                }
            ]
        }
        """

        # Patch the `open` function in the DatasetPars module
        with patch("DatasetPars.open", unittest.mock.mock_open(read_data=mock_file_content)) as mock_open:
            # Call the method under test
            self.dataset_pars.Loading_Dataset(dataset_location)

            # Assert the expected values after loading the dataset
            self.assertEqual(self.dataset_pars.Vocabulary, ["Bye", "Goodbye", "Hello", "Hey", "Hi", "See", "you"])
            self.assertEqual(self.dataset_pars.Tags, ["greeting", "farewell"])
            self.assertEqual(self.dataset_pars.Index, {1: "greeting", 2: "farewell"})
            self.assertEqual(self.dataset_pars.Words_list, [["Hi"], ["Hello"], ["Hey"], ["Bye"], ["Goodbye"], ["See", "you"]])
            self.assertEqual(self.dataset_pars.Words_list_Tags, ["greeting", "greeting", "greeting", "farewell", "farewell", "farewell"])
            self.assertEqual(self.dataset_pars.Response, {"greeting": "Hello!", "farewell": "Goodbye!"})

            # Assert that the `open` function is called with the correct arguments
            mock_open.assert_called_with(dataset_location, encoding="utf-8")




if __name__ == "__main__":
    unittest.main()