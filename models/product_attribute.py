# Copyright 2020 Pafnow

from odoo import api, fields, models


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    display_type = fields.Selection(selection_add=[('input', 'User Input')])

    default_value_id = fields.Many2one('product.attribute.value', compute='_compute_default_value_id')
    default_value_input_type = fields.Selection(related='default_value_id.input_type', readonly=False)
    default_value_input_min = fields.Float(related='default_value_id.input_min', readonly=False)
    default_value_input_max = fields.Float(related='default_value_id.input_max', readonly=False)

    @api.depends('display_type')
    def _compute_default_value_id(self):
        for record in self:
            if record.display_type != 'input':
                self.default_value_id = None
            else:
                if not len(self.value_ids):
                    self.value_ids = [(0, 0, {
                        'name': 'Value',
                        'is_custom': True,
                    })]
                #//TODO: Handle case with multiple value_ids. Should delete all but the first/default one?
                #//TODO: Try to fetch the value marked as default, instead of first record [0]
                self.default_value_id = self.value_ids[0]


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    input_type = fields.Selection([
        ('char', 'Char'),
        ('int', 'Integer'),
        ('float', 'Float'),
    ])
    input_min = fields.Float("Min Value", digits=(12, 6))
    input_max = fields.Float("Max Value", digits=(12, 6))
