from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LoanApplication(models.Model):
    _name = 'loan.application'
    _description = 'Loan Application'
    _order = 'date_application desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char(string="Application Number", required=True)

    date_application = fields.Date(string="Application Date", readonly=True, copy=False)
    date_approval = fields.Date(string="Approval Date", readonly=True, copy=False)
    date_rejection = fields.Date(string="Rejection Date", readonly=True, copy=False)
    date_signed = fields.Datetime(string="Signed On", readonly=True, copy=False)

    down_payment = fields.Monetary(string="Downpayment", required=True, currency_field='currency_id')
    interest_rate = fields.Float(string="Interest Rate (%)", required=True, digits=(5, 2))
    loan_term = fields.Integer(string="Loan Term (Months)", required=True, default=36)

    rejection_reason = fields.Text(string="Rejection Reason", copy=False)

    state = fields.Selection(
        string="Status",
        selection=[
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('review', 'Credit Check'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('signed', 'Signed'),
            ('cancel', 'Canceled')
        ],
        default='draft',
        copy=False,
        tracking=True
    )

    notes = fields.Html(string="Notes", copy=False)

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Related Sale Order"
    )

    product_template_id = fields.Many2one(
        'product.product',
        string="Product"
    )

    document_ids = fields.One2many('loan.application.document', 'application_id', string="Documents")
    tag_ids = fields.Many2many('loan.application.tag', string="Tags")

    
    sale_order_total = fields.Monetary(
        string="Sale Order Total",
        related='sale_order_id.amount_total',
        store=True
    )

    currency_id = fields.Many2one(
        related='sale_order_id.currency_id',
        store=True,
        readonly=False
    )

    partner_id = fields.Many2one(
        related='sale_order_id.partner_id',
        store=True,
        readonly=False
    )

    user_id = fields.Many2one(
        related='sale_order_id.user_id',
        store=True,
        readonly=False
    )

    loan_amount = fields.Monetary(
        string="Loan Amount",
        compute="_compute_loan_amount",
        inverse="_inverse_loan_amount",
        store=True
    )

    document_count = fields.Integer(
        string="Document Count",
        compute="_compute_document_counts",
        store=True
    )

    document_count_approved = fields.Integer(
        string="Approved Documents",
        compute="_compute_document_counts",
        store=True
    )

    down_payment = fields.Monetary(
        string="Downpayment",
        required=True
    )

    _sql_constraints = [
        ('check_down_payment_positive', 'CHECK(down_payment >= 0)', 'El anticipo no puede ser negativo.'),
    ]

    @api.depends('sale_order_total', 'down_payment')
    def _compute_loan_amount(self):
        for rec in self:
            if rec.sale_order_total:
                rec.loan_amount = rec.sale_order_total - rec.down_payment
            else:
                rec.loan_amount = 0.0

    def _inverse_loan_amount(self):
        for rec in self:
            if rec.sale_order_total:
                rec.down_payment = rec.sale_order_total - rec.loan_amount

    @api.depends('document_ids.state')
    def _compute_document_counts(self):
        for rec in self:
            rec.document_count = len(rec.document_ids)
            rec.document_count_approved = len(rec.document_ids.filtered(lambda d: d.state == 'approved'))

    @api.constrains('down_payment', 'sale_order_total')
    def _check_down_payment_vs_order_total(self):
        for rec in self:
            if rec.sale_order_total and rec.down_payment > rec.sale_order_total:
                raise ValidationError("El anticipo no puede ser mayor que el total de la orden de venta.")
            
    def action_send_for_approval(self):
        for rec in self:
            if not rec.document_ids:
                raise ValidationError("No se puede enviar una solicitud sin documentos adjuntos.")
            if any(doc.state != 'approved' for doc in rec.document_ids):
                raise ValidationError("Todos los documentos deben estar aprobados antes de enviar la solicitud.")
            rec.state = 'sent'
            rec.date_application = fields.Date.today()

    def action_approve_loan(self):
        for rec in self:
            rec.state = 'approved'
            rec.date_approval = fields.Date.today()

    def action_reject_loan(self, reason=''):
        for rec in self:
            if not reason:
                raise ValidationError("Debe proporcionar una razón para el rechazo.")
            rec.rejection_reason = reason
            rec.state = 'rejected'
            rec.date_rejection = fields.Date.today()

    def name_get(self):
        result = []
        for record in self:
            partner = record.partner_id.name if record.partner_id else "Sin Cliente"
            product = record.product_template_id.name if record.product_template_id else "Sin Producto"
            name = f"{partner} - {product}"
            result.append((record.id, name))
        return result

    @api.model_create_multi
    def create(self, vals_list):
        applications = super().create(vals_list)

        doc_type_model = self.env['loan.application.document.type']
        active_doc_types = doc_type_model.search([('active', '=', True)])

        for application in applications:
            document_vals = []
            for doc_type in active_doc_types:
                document_vals.append({
                    'name': doc_type.name,
                    'type_id': doc_type.id,
                    'application_id': application.id,
                    'state': 'new',
                })
            self.env['loan.application.document'].create(document_vals)

        return applications
