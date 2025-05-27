{
    'name': 'Motorcycle Financing',
    'summary': 'Streamlines the loan application process for dealerships.',
    'category': 'Kawiil/Custom Modules',
    'version': '18.0.0.0.1',
    'website': 'https://github.com/CarlosCondor99/K-awiil-Motors', 
    'author': 'CarlosCondor99',
    'depends': ['base', 'sale', 'mail'],
    'demo': [
        'data/loan_demo.xml',
    ],
    'data': [
        'security/motorcycle_financing_groups.xml',
        'security/ir.model.access.csv',
        'security/rules.xml',

        'views/loan_application_views.xml',
        'views/loan_application_document_views.xml',
        'views/loan_application_reject_wizard_views.xml',
        'views/res_partner_loan_inherit_views.xml',
        'views/sale_order_view_inherit.xml',
        'views/motorcycle_financing_menu.xml',
    ],
    'license': 'OPL-1',
    'application': True,
    'installable': True,
}
