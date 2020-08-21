# Copyright 2020 Pafnow

from odoo import api, fields, models
from odoo.exceptions import ValidationError, Warning


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    #display_type = fields.Selection(selection_add=[('input', 'User Input')])
    attribute_type = fields.Selection([
        ('list', 'List'),
        ('char', 'Char'),
        ('int', 'Integer'),
        ('float', 'Float'),
    ], default='list', required=True, compute='_compute_attribute_type', inverse='_inverse_attribute_type')

    custom_value_id = fields.Many2one('product.attribute.value', compute='_compute_custom_value_id')
    custom_value_input_min = fields.Char(related='custom_value_id.input_min', readonly=False)
    custom_value_input_max = fields.Char(related='custom_value_id.input_max', readonly=False)

    @api.depends('custom_value_id', 'custom_value_id.input_type')
    def _compute_attribute_type(self):
        for record in self:
            if record.custom_value_id and record.custom_value_id.input_type:
                record.attribute_type = record.custom_value_id.input_type
            else:
                record.attribute_type = 'list'

    @api.onchange('attribute_type')
    def _inverse_attribute_type(self):
        for record in self:
            v_attribute_type = record.attribute_type #Use local variable here because some recomputation might happen below

            if v_attribute_type == 'list':
                if record.custom_value_id:
                    record.custom_value_id.input_type = None
            else:
                #Create custom value record if no record
                if not len(record.value_ids):
                    record.value_ids = [(0, 0, {
                        'name': 'Value',
                        'is_custom': True,
                    })]
                if not record.custom_value_id:
                    raise ValidationError("Please delete all attribute values before changing Attribute Type (no custom value found).")
                record.custom_value_id.input_type = v_attribute_type
                record.display_type = 'radio'
                record.create_variant = 'no_variant'

    @api.depends('value_ids')
    def _compute_custom_value_id(self):
        for record in self:
            if len(record.value_ids) == 1 and record.value_ids[0].name == 'Value' and record.value_ids[0].is_custom:
                record.custom_value_id = record.value_ids[0]
            else:
                record.custom_value_id = None


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    input_type = fields.Selection([
        ('char', 'Char'),
        ('int', 'Integer'),
        ('float', 'Float'),
    ])
    input_min = fields.Char("Min Value")
    input_max = fields.Char("Max Value")

    @api.constrains('input_type', 'input_min')
    def _check_input_min(self):
        """ Ensure input_min is of the same type than input_type """
        for record in self:
            if record.input_min and record.input_type == 'int':
                try:
                    int(record.input_min)
                except ValueError:
                    raise ValidationError("Min Value cannot be converted to an integer")
            if record.input_min and record.input_type == 'float':
                try:
                    float(record.input_min)
                except ValueError:
                    raise ValidationError("Min Value cannot be converted to a float")

    @api.constrains('input_type', 'input_max')
    def _check_input_max(self):
        """ Ensure input_max is of the same type than input_type """
        for record in self:
            if record.input_max and record.input_type == 'int':
                try:
                    int(record.input_max)
                except ValueError:
                    raise ValidationError("Max Value cannot be converted to an integer")
            if record.input_max and record.input_type == 'float':
                try:
                    float(record.input_max)
                except ValueError:
                    raise ValidationError("Max Value cannot be converted to a float")


class ProductAttributeCustomValue(models.Model):
    _inherit = "product.attribute.custom.value"


"""    @api.constrains('custom_value')
    def _check_custom_value(self):
        for record in self:
            raise ValidationError("Hello Damien Constrains")

    @api.onchange('custom_value')
    def _onchange_custom_value(self):
        for record in self:
            record.custom_value = None
            #raise ValidationError("Hello Damien OnChange")
            return {
                'warning': {
                    'title': "Something bad happened",
                    'message': "It was very bad indeed",
                }
            }
            #raise Warning("Hello OnChange2")


   custom_value_char = fields.Char("Custom Value", compute='_compute_custom_value_char')
    custom_value_int = fields.Integer("Custom Value", compute='_compute_custom_value_int', inverse='_compute_custom_value_int')

    def _compute_custom_value_char(self):
        for record in self:
            if not record.custom_product_template_attribute_value_id.product_attribute_value_id.input_type == 'char':
                record.custom_value_char = None
            else:
                record.custom_value_char = record.custom_value

    def _compute_custom_value_int(self):
        for record in self:
            if not record.custom_product_template_attribute_value_id.product_attribute_value_id.input_type == 'int':
                record.custom_value_int = None
            else:
                record.custom_value_int = int(record.custom_value)
"""
