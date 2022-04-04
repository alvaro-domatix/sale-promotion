from odoo.tests import Form, common


class TestWebsiteSaleCouponRewardLineDiscriminant(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test pricelist",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "3_global",
                            "compute_price": "formula",
                            "base": "list_price",
                        },
                    )
                ],
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Mr. Odoo", "property_product_pricelist": cls.pricelist.id})
        cls.product_a = cls.env["product.product"].create({"name": "Product A", "sale_ok": True, "list_price": 50})
        cls.product_b = cls.env["product.product"].create({"name": "Product B", "sale_ok": True, "list_price": 60})
        coupon_program_form = Form(
            cls.env["sale.coupon.program"],
            view="sale_coupon.sale_coupon_program_view_promo_program_form",
        )
        coupon_program_form.name = "Test Line Discriminant Program"
        coupon_program_form.promo_code_usage = "no_code_needed"
        coupon_program_form.reward_type = "multi_gift"
        coupon_program_form.rule_products_domain = "[('id', '=', %s)]" % cls.product_a.id
        with coupon_program_form.coupon_multi_gift_ids.new() as reward_line:
            reward_line.reward_product_ids.add(cls.product_b)
            reward_line.reward_product_quantity = 2
        cls.coupon_program = coupon_program_form.save()
        sale_form = Form(cls.env["sale.order"])
        sale_form.partner_id = cls.partner
        with sale_form.order_line.new() as line_form:
            line_form.product_id = cls.product_a
            line_form.product_uom_qty = 1
        cls.sale = sale_form.save()

    def test_website_sale_coupon_reward_line_discriminant(self):
        self.sale.recompute_coupon_lines()
        new_line = self.sale.order_line.new()
        new_line.product_id = self.product_b
        new_line.product_uom_qty = 2
        self.sale.recompute_coupon_lines()
        self.assertEqual(2, new_line.product_uom_qty)
        self.assertFalse(new_line.is_reward_line)
