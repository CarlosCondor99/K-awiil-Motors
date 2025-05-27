from odoo import models, fields, api

class LoanApplicationDocument(models.Model):
    _name = 'loan.application.document'
    _description = 'Loan Application Document'
    sequence = fields.Integer(string="Sequence")
    _order = 'sequence asc'

    name = fields.Char(string="Document Name", required=True)
    application_id = fields.Many2one('loan.application', string="Application", required=True)
    attachment = fields.Binary(string="Attachment")
    type_id = fields.Many2one('loan.application.document.type', string="Type")
    state = fields.Selection([
        ('new', 'New'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='new', required=True)

    _sql_constraints = [
        ('attachment_not_null', 'CHECK(attachment IS NOT NULL)', 'El documento adjunto no puede estar vacío.'),
    ]

    @api.onchange('attachment')
    def _onchange_attachment(self):
        if self.attachment:
            self.state = 'new'

    def action_approve_document(self):
        for rec in self:
            rec.state = 'approved'

    def action_reject_document(self):
        for rec in self:
            rec.state = 'rejected'