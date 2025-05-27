from odoo import models, fields

class LoanApplicationTag(models.Model):
    _name = 'loan.application.tag'
    _description = 'Loan Application Tag'
    _order = 'name asc'
    name = fields.Char(string="Tag Name", required=True)
    color = fields.Integer(string="Color")

    _sql_constraints = [
        ('unique_tag_name', 'UNIQUE(name)', 'El nombre de la etiqueta debe ser único.'),
    ]
