# Copyright 2020 Pafnow

from odoo import http
from odoo.http import request
from odoo.addons.sale.controllers.variant import VariantController


class CustomVariantController(http.Controller):
    @http.route(['/product_attribute_type/get_combination_info_custom'], type='json', auth="user", methods=['POST'])
    def get_combination_info_custom(self, product_template_id, product_id, combination, add_qty, pricelist_id, **kw):
        res = VariantController().get_combination_info(product_template_id, product_id, combination, add_qty, pricelist_id, **kw)
        #raise exceptions.UserError('Business logic error Damien' + str(kw))
        return res

