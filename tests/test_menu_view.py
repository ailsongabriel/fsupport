import unittest
from unittest.mock import patch

from views.menu_view import MenuView


class MenuViewTest(unittest.TestCase):

  def test_get_option_returns_none_for_invalid_input(self):
    view = MenuView()
    with patch("builtins.input", return_value="abc"):
      self.assertIsNone(view.get_option())

  def test_get_option_returns_integer_for_valid_input(self):
    view = MenuView()
    with patch("builtins.input", return_value="4"):
      self.assertEqual(view.get_option(), 4)


if __name__ == "__main__":
  unittest.main()
