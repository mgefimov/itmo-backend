import unittest
from ...main import DiscountItem


class TestItemMethods(unittest.TestCase):
    def test_is_valid(self):
        item = DiscountItem(username='test user', price=100.0, item_name='test name')
        self.assertTrue(item.is_valid())

        item2 = DiscountItem(username='test user', price=0.0, item_name='test name')
        self.assertTrue(item2.is_valid())

        not_valid_item = DiscountItem(username='test user', price=-55.0, item_name='test name')
        self.assertFalse(not_valid_item.is_valid())

    def test_apply_discount(self):
        item = DiscountItem(username='test user', price=100.0, item_name='test name')
        item.apply_discount()
        self.assertAlmostEqual(item.price, 80.0)

        item2 = DiscountItem(username='test user', price=0.0, item_name='test name')
        item2.apply_discount()
        self.assertAlmostEqual(item2.price, 0)

        item3 = DiscountItem(username='test user', price=55.2, item_name='test name')
        item3.apply_discount()
        self.assertAlmostEqual(item3.price, 44.16)


if __name__ == '__main__':
    unittest.main()
