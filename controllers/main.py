# Copyright 2020 Pafnow

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.addons.sale.controllers.variant import VariantController


class CustomVariantController(http.Controller):
    @http.route(['/product_attribute_type/get_combination_info_custom'], type='json', auth="user", methods=['POST'])
    def get_combination_info_custom(self, product_template_id, product_id, combination, add_qty, pricelist_id, **kw):
        res = VariantController().get_combination_info(product_template_id, product_id, combination, add_qty, pricelist_id, **kw)
        if 'custom_values' in kw:
            for cv in kw.get('custom_values'):
                if cv['custom_product_template_attribute_value_id'] in combination:
                    ptav = request.env['product.template.attribute.value'].browse(cv['custom_product_template_attribute_value_id'])
                    try:
                        ptav.product_attribute_value_id.check_custom_value(cv['custom_value'])
                    except ValidationError as ex:
                        res.update({
                            'is_combination_possible': False,
                            'custom_value_error': ex.args[0]
                        })
        return res

