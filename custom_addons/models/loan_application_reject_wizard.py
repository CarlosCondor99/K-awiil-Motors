from odoo import models, fields

class LoanApplicationRejectWizard(models.TransientModel):
    _name = 'loan.application.reject.wizard'
    _description = 'Wizard to Reject Loan Application'

    reason = fields.Text(string="Reason for Rejection", required=True)
    application_id = fields.Many2one('loan.application', required=True)

    def confirm_rejection(self):
        self.application_id.action_reject_loan(reason=self.reason)
