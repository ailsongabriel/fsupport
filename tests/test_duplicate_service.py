import unittest

from services.duplicate_service import DuplicateService


class DuplicateServiceTest(unittest.TestCase):

  def test_windows_protected_path_is_detected(self):
    service = DuplicateService()
    service.os_type = "Windows"

    self.assertTrue(service._is_protected_path("C:\\Windows\\System32\\kernel32.dll"))
    self.assertTrue(service._is_protected_path("C:\\Program Files\\App\\app.exe"))
    self.assertFalse(service._is_protected_path("C:\\Users\\Public\\Downloads\\file.zip"))

  def test_linux_protected_path_is_detected(self):
    service = DuplicateService()
    service.os_type = "Linux"

    self.assertTrue(service._is_protected_path("/usr/bin/python"))
    self.assertTrue(service._is_protected_path("/etc/hosts"))
    self.assertFalse(service._is_protected_path("/home/user/Downloads/file.zip"))


if __name__ == "__main__":
  unittest.main()
