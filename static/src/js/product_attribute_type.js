/* Copyright 2020 Pafnow */

odoo.define('product_attribute_type', function (require) {
    "use strict";

    var core = require('web.core');
    var ajax = require('web.ajax');
    var _t = core._t;
    var ProductConfiguratorFormRenderer = require('sale_product_configurator.ProductConfiguratorFormRenderer');

    ProductConfiguratorFormRenderer.include({
        _getCombinationInfo: function(ev) {
            /*
            * Below code is duplicated from sale/static/src/js/variant_mixin.js
            * and modified to call get_combination_info with custom value
            */
            var self = this;

            /*if ($(ev.target).hasClass('variant_custom_value')) {
                return Promise.resolve();
            }*/

            var $parent = $(ev.target).closest('.js_product');
            var qty = $parent.find('input[name="add_qty"]').val();
            var combination = this.getSelectedVariantValues($parent);
            var customvalues = this.getCustomVariantValues($parent);
            var parentCombination = $parent.find('ul[data-attribute_exclusions]').data('attribute_exclusions').parent_combination;
            var productTemplateId = parseInt($parent.find('.product_template_id').val());

            self._checkExclusions($parent, combination);

            return ajax.jsonRpc(this._getUri('/product_attribute_type/get_combination_info_custom'), 'call', {
                'product_template_id': productTemplateId,
                'product_id': this._getProductId($parent),
                'combination': combination,
                'custom_values': customvalues,
                'add_qty': parseInt(qty),
                'pricelist_id': this.pricelistId || false,
                'parent_combination': parentCombination,
            }).then(function (combinationData) {
                self._onChangeCombination(ev, $parent, combinationData);
            });
        },
        _onChangeCombination: function (ev, $parent, combination) {
            if (combination.custom_value_error) {
                $parent.find('.css_not_available_msg').html(combination.custom_value_error);
            } else {
                $parent.find('.css_not_available_msg').html('This combination does not exist.')
            }
            this._super.apply(this, arguments);
        }
    });
});
