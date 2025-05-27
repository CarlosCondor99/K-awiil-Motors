from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    loan_application_ids = fields.One2many('loan.application', 'sale_order_id', string="Loan Applications")
    is_financed = fields.Boolean(string="Requires Financing", default=False)
    state = fields.Selection(
        selection_add=[('loan_requested', 'Solicitado Préstamo')]
    )

    def _get_motorcycle_product(self):
        for order in self:
            motorcycle_lines = order.order_line.filtered(lambda l: l.product_id.categ_id.name == 'Motocicleta')
            if len(motorcycle_lines) > 1:
                raise UserError("Solo se permite una motocicleta por solicitud de préstamo.")
            if not motorcycle_lines:
                raise UserError("No se encontró una motocicleta en las líneas de la orden.")
            return motorcycle_lines[0].product_id

    def _prepare_loan_application_context(self):
        self.ensure_one()
        motorcycle = self._get_motorcycle_product()
        return {
            'default_sale_order_id': self.id,
            'default_product_template_id': motorcycle.id,
            'default_name': f"{self.partner_id.name} - {motorcycle.name}",
        }

    def action_apply_loan(self):
        self.ensure_one()
        ctx = self._prepare_loan_application_context()
        self.write({'state': 'loan_requested'})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Loan Application'),
            'res_model': 'loan.application',
            'view_mode': 'form',
            'target': 'current',
            'context': ctx,
        }

    @api.onchange('is_financed')
    def _onchange_is_financed(self):
        for order in self:
            if order.is_financed:
                motorcycles = order.order_line.filtered(lambda l: l.product_id.categ_id.name == 'Motocicleta')
                if len(motorcycles) != 1:
                    raise UserError("Debe existir exactamente una motocicleta para solicitar financiamiento.")
