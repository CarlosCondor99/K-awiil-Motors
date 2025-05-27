from odoo import models, fields

class LoanApplicationDocumentType(models.Model):
    _name = 'loan.application.document.type'
    _description = 'Loan Application Document Type'
    _order = 'name asc'
    name = fields.Char(string="Document Type", required=True)
    active = fields.Boolean(default=True)
    document_number = fields.Integer(string="Required Document Number", required=True)

    _sql_constraints = [
        ('unique_type_name', 'UNIQUE(name)', 'El nombre del tipo de documento debe ser único.'),
    ]