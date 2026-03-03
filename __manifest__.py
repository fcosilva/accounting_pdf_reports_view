{
    'name': 'Accounting PDF Reports View Extension',
    'version': '17.0.2.0.0',
    'summary': 'Adds on-screen view output for accounting PDF report wizards',
    'author': 'OpenLab',
    'license': 'LGPL-3',
    'depends': [
        'accounting_pdf_reports',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/accounting_report_views.xml',
    ],
    'installable': True,
    'application': False,
}
