# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api, fields
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.one
    @api.depends('barcode')
    def _calculate_isbn(self):
        isbn = False
        if self.barcode:
            barcode = self.barcode.replace(' ', '').replace('-', '')
            if len(barcode) == 13 and barcode[0:3] == '978':
                # isbn = self.barcode[3:12]
                isbn = barcode[3:12]
                check_digit = self.calculate_control_digit_isbn(isbn)
                if check_digit is None:
                    isbn = False
                else:
                    isbn += check_digit
        self.isbn = isbn

    def calculate_control_digit_isbn(self, str_partial_isbn):
        if not str_partial_isbn:
            return None
        if len(str_partial_isbn) != 9:
            return None
        try:
            int(str_partial_isbn)
        except:
            return None

        val = 0
        for i in range(len(str_partial_isbn)):
            val += int(str_partial_isbn[i]) * (int(i) + 1)
        if val % 11 == 10:
            ret = 'X'
        else:
            ret = str(val % 11)
        return ret

    isbn = fields.Char(
        compute='_calculate_isbn',
        string='ISBN',
        store=True)

    def name_search(
            self, cr, uid, name, args=None, operator='ilike',
            context=None, limit=100):
        res = super(ProductTemplate, self).name_search(
            cr, uid, name, args, operator, context, limit)
        if len(res) < limit:
            product_ids = self.search(
                cr, uid, [('isbn', operator, name)] + (args or []),
                limit=limit, context=context)
            res += self.name_get(cr, uid, product_ids, context=context)
        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def name_search(
            self, cr, uid, name, args=None, operator='ilike',
            context=None, limit=100):
        res = super(ProductProduct, self).name_search(
            cr, uid, name, args, operator, context, limit)
        if len(res) < limit:
            product_ids = self.search(
                cr, uid, [('isbn', operator, name)] + (args or []),
                limit=limit, context=context)
            res += self.name_get(cr, uid, product_ids, context=context)
        return res
