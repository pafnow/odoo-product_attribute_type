# Copyright 2020 Pafnow

from odoo import api, fields, models
from odoo.exceptions import ValidationError, Warning


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    attribute_type = fields.Selection([
        ('list', 'List'),
        ('char', 'Char'),
        ('int', 'Integer'),
        ('float', 'Float'),
    ], default='list', required=True, compute='_compute_attribute_type', inverse='_inverse_attribute_type')

    custom_value_id = fields.Many2one('product.attribute.value', compute='_compute_custom_value_id')
    custom_value_required = fields.Boolean(related='custom_value_id.custom_required', readonly=False)
    custom_value_min = fields.Char(related='custom_value_id.custom_min', readonly=False)
    custom_value_max = fields.Char(related='custom_value_id.custom_max', readonly=False)

    @api.depends('custom_value_id', 'custom_value_id.custom_type')
    def _compute_attribute_type(self):
        for record in self:
            if record.custom_value_id and record.custom_value_id.custom_type:
                record.attribute_type = record.custom_value_id.custom_type
            else:
                record.attribute_type = 'list'

    @api.onchange('attribute_type')
    def _inverse_attribute_type(self):
        for record in self:
            v_attribute_type = record.attribute_type #Use local variable here because some recomputation might happen below

            if v_attribute_type == 'list':
                if record.custom_value_id:
                    record.custom_value_id.custom_type = None
            else:
                #Create custom value record if no record
                if not len(record.value_ids):
                    record.value_ids = [(0, 0, {
                        'name': 'Value',
                        'is_custom': True,
                    })]
                if not record.custom_value_id:
                    raise ValidationError("Please delete all attribute values before changing Attribute Type (no custom value found).")
                record.custom_value_id.custom_type = v_attribute_type
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

    custom_type = fields.Selection([
        ('char', 'Char'),
        ('int', 'Integer'),
        ('float', 'Float'),
    ])
    custom_required = fields.Boolean("Required")
    custom_min = fields.Char("Min Value")
    custom_max = fields.Char("Max Value")

    @api.constrains('custom_type', 'custom_min')
    def _check_custom_min(self):
        """ Ensure custom_min is of the same type than custom_type """
        for record in self:
            if record.custom_min and record.custom_type == 'int':
                try:
                    int(record.custom_min)
                except ValueError:
                    raise ValidationError("Min Value cannot be converted to an integer")
            if record.custom_min and record.custom_type == 'float':
                try:
                    float(record.custom_min)
                except ValueError:
                    raise ValidationError("Min Value cannot be converted to a float")

    @api.constrains('custom_type', 'custom_max')
    def _check_custom_max(self):
        """ Ensure custom_max is of the same type than custom_type """
        for record in self:
            if record.custom_max and record.custom_type == 'int':
                try:
                    int(record.custom_max)
                except ValueError:
                    raise ValidationError("Max Value cannot be converted to an integer")
            if record.custom_max and record.custom_type == 'float':
                try:
                    float(record.custom_max)
                except ValueError:
                    raise ValidationError("Max Value cannot be converted to a float")

    def check_custom_value(self, custom_value):
        """
        This function test if custom_value follows the conditions for this attribute value
        """
        self.ensure_one()
        if not custom_value:
            if self.custom_required:
                raise ValidationError("Custom Value is required, please fill its value")
        elif self.custom_type == 'int':
            #Type
            try:
                int(custom_value)
            except ValueError:
                raise ValidationError("Custom Value [%s] cannot be converted to an integer" % custom_value)
            #Min
            if self.custom_min and int(self.custom_min) > int(custom_value):
                raise ValidationError("Custom Value [%s] is smaller than the minimum allowed [%s]" % (custom_value, self.custom_min))
            #Max
            if self.custom_max and int(self.custom_max) < int(custom_value):
                raise ValidationError("Custom Value [%s] is bigger than the maximum allowed [%s]" % (custom_value, self.custom_max))
        elif self.custom_type == 'float':
            #Type
            try:
                float(custom_value)
            except ValueError:
                raise ValidationError("Custom Value [%s] cannot be converted to a float" % custom_value)
            #Min
            if self.custom_min and float(self.custom_min) > float(custom_value):
                raise ValidationError("Custom Value [%s] is smaller than the minimum allowed [%s]" % (custom_value, self.custom_min))
            #Max
            if self.custom_max and float(self.custom_max) < float(custom_value):
                raise ValidationError("Custom Value [%s] is bigger than the maximum allowed [%s]" % (custom_value, self.custom_max))
