from odoo import _, fields, models
from odoo.tools.misc import get_lang


class AccountingReport(models.TransientModel):
    _inherit = 'accounting.report'

    def _get_form_data(self):
        fields_to_read = [
            'account_report_id',
            'company_id',
            'date_from',
            'date_to',
            'date_from_cmp',
            'date_to_cmp',
            'journal_ids',
            'target_move',
            'filter_cmp',
            'debit_credit',
            'enable_filter',
            'label_filter',
        ]
        return self.read(fields_to_read)[0]

    def _build_report_data(self):
        form_data = self._get_form_data()
        base_data = {'form': form_data}
        used_context = self._build_contexts(base_data)
        form_data['used_context'] = dict(used_context, lang=get_lang(self.env).code)
        if form_data.get('enable_filter'):
            form_data['comparison_context'] = self._build_comparison_context({'form': form_data})
        return form_data

    def action_view_report(self):
        self.ensure_one()
        report_action = self.with_context(
            active_model=self._name,
            active_id=self.id,
            active_ids=[self.id],
        ).check_report()
        form_data = (report_action.get('data') or {}).get('form') or self._build_report_data()
        report_context = dict(self.env.context, **(report_action.get('context') or {}))
        report_service = self.env['report.accounting_pdf_reports.report_financial']
        report_lines = report_service.with_context(report_context).get_account_lines(form_data)

        line_commands = [(5, 0, 0)]
        for sequence, line in enumerate(report_lines, start=1):
            if not line.get('level'):
                continue
            line_commands.append((0, 0, {
                'sequence': sequence,
                'name': line.get('name'),
                'level': int(line.get('level', 0)),
                'line_type': line.get('type'),
                'account_type': line.get('account_type'),
                'debit': line.get('debit', 0.0),
                'credit': line.get('credit', 0.0),
                'balance': line.get('balance', 0.0),
                'balance_cmp': line.get('balance_cmp', 0.0),
            }))
        preview = self.env['accounting.report.preview'].create({
            'name': self.account_report_id.display_name or _('Report Preview'),
            'report_wizard_id': self.id,
            'line_ids': line_commands,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Vista previa'),
            'res_model': 'accounting.report.preview',
            'view_mode': 'form',
            'view_id': self.env.ref('accounting_pdf_reports_view.view_accounting_report_preview_form').id,
            'res_id': preview.id,
            'target': 'current',
        }


class AccountingReportPreview(models.TransientModel):
    _name = 'accounting.report.preview'
    _description = 'Accounting Report Preview'

    name = fields.Char(readonly=True)
    report_wizard_id = fields.Many2one('accounting.report', required=True, readonly=True, ondelete='cascade')
    account_report_id = fields.Many2one(related='report_wizard_id.account_report_id', readonly=True)
    company_id = fields.Many2one(related='report_wizard_id.company_id', readonly=True)
    date_from = fields.Date(related='report_wizard_id.date_from', readonly=True)
    date_to = fields.Date(related='report_wizard_id.date_to', readonly=True)
    target_move = fields.Selection(related='report_wizard_id.target_move', readonly=True)
    label_filter = fields.Char(related='report_wizard_id.label_filter', readonly=True)
    debit_credit = fields.Boolean(related='report_wizard_id.debit_credit', readonly=True)
    enable_filter = fields.Boolean(related='report_wizard_id.enable_filter', readonly=True)
    line_ids = fields.One2many('accounting.report.preview.line', 'preview_id', string='Lines', readonly=True)

    def action_export_pdf(self):
        self.ensure_one()
        return self.report_wizard_id.with_context(
            active_model=self.report_wizard_id._name,
            active_id=self.report_wizard_id.id,
            active_ids=[self.report_wizard_id.id],
        ).check_report()


class AccountingReportPreviewLine(models.TransientModel):
    _name = 'accounting.report.preview.line'
    _description = 'Accounting Report Preview Line'
    _order = 'sequence, id'

    preview_id = fields.Many2one('accounting.report.preview', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, readonly=True)
    level = fields.Integer(readonly=True)
    line_type = fields.Char(readonly=True)
    account_type = fields.Char(readonly=True)
    currency_id = fields.Many2one(
        related='preview_id.report_wizard_id.company_id.currency_id',
        readonly=True,
        store=False,
    )
    debit = fields.Monetary(currency_field='currency_id', readonly=True)
    credit = fields.Monetary(currency_field='currency_id', readonly=True)
    balance = fields.Monetary(currency_field='currency_id', readonly=True)
    balance_cmp = fields.Monetary(currency_field='currency_id', readonly=True)
