from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import get_lang


class AccountReportGeneralLedger(models.TransientModel):
    _inherit = 'account.report.general.ledger'

    def _prepare_preview_data(self):
        self.ensure_one()
        data = {
            'ids': [self.id],
            'model': self._name,
            'form': self.read([
                'date_from',
                'date_to',
                'journal_ids',
                'target_move',
                'company_id',
            ])[0],
        }
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)
        return self._get_report_data(data)

    def action_view_report(self):
        self.ensure_one()
        report_action = self.with_context(
            active_model=self._name,
            active_id=self.id,
            active_ids=[self.id],
        ).check_report()
        data = report_action.get('data') or {}
        form_data = data.get('form') or {}
        records = self.env[data.get('model', self._name)].browse(data.get('ids') or [self.id])
        report_context = dict(self.env.context, **(report_action.get('context') or {}))
        report_values = self.env['report.accounting_pdf_reports.report_general_ledger'].with_context(
            report_context
        )._get_report_values(
            records.ids, data=data
        )

        line_commands = [(5, 0, 0)]
        sequence = 1
        for account in report_values.get('Accounts', []):
            line_commands.append((0, 0, {
                'sequence': sequence,
                'line_type': 'section',
                'name': f"[{account.get('code')}] {account.get('name')}",
                'debit': account.get('debit', 0.0),
                'credit': account.get('credit', 0.0),
                'balance': account.get('balance', 0.0),
                'code': account.get('code'),
            }))
            sequence += 1
            for move_line in account.get('move_lines', []):
                line_commands.append((0, 0, {
                    'sequence': sequence,
                    'line_type': 'line',
                    'name': move_line.get('lname') or move_line.get('lref') or '',
                    'date': move_line.get('ldate') or False,
                    'code': account.get('code'),
                    'journal_name': move_line.get('lcode') or '',
                    'move_name': move_line.get('move_name') or '',
                    'partner_name': move_line.get('partner_name') or '',
                    'debit': move_line.get('debit', 0.0),
                    'credit': move_line.get('credit', 0.0),
                    'balance': move_line.get('balance', 0.0),
                }))
                sequence += 1

        preview = self.env['account.audit.report.preview'].create({
            'name': _('General Ledger Preview'),
            'report_type': 'general_ledger',
            'wizard_ref': f'{self._name},{self.id}',
            'company_id': self.company_id.id,
            'date_from': form_data.get('date_from') or self.date_from,
            'date_to': form_data.get('date_to') or self.date_to,
            'target_move': form_data.get('target_move') or self.target_move,
            'line_ids': line_commands,
        })
        return preview._open_action()


class AccountBalanceReport(models.TransientModel):
    _inherit = 'account.balance.report'

    def _prepare_preview_data(self):
        self.ensure_one()
        data = {
            'ids': [self.id],
            'model': self._name,
            'form': self.read([
                'date_from',
                'date_to',
                'journal_ids',
                'target_move',
                'company_id',
            ])[0],
        }
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)
        return self._get_report_data(data)

    def action_view_report(self):
        self.ensure_one()
        report_action = self.with_context(
            active_model=self._name,
            active_id=self.id,
            active_ids=[self.id],
        ).check_report()
        data = report_action.get('data') or {}
        form_data = data.get('form') or {}
        records = self.env[data.get('model', self._name)].browse(data.get('ids') or [self.id])
        report_context = dict(self.env.context, **(report_action.get('context') or {}))
        report_values = self.env['report.accounting_pdf_reports.report_trialbalance'].with_context(
            report_context
        )._get_report_values(
            records.ids, data=data
        )

        line_commands = [(5, 0, 0)]
        for sequence, account in enumerate(report_values.get('Accounts', []), start=1):
            line_commands.append((0, 0, {
                'sequence': sequence,
                'line_type': 'line',
                'name': account.get('name') or '',
                'code': account.get('code') or '',
                'debit': account.get('debit', 0.0),
                'credit': account.get('credit', 0.0),
                'balance': account.get('balance', 0.0),
            }))

        preview = self.env['account.audit.report.preview'].create({
            'name': _('Trial Balance Preview'),
            'report_type': 'trial_balance',
            'wizard_ref': f'{self._name},{self.id}',
            'company_id': self.company_id.id,
            'date_from': form_data.get('date_from') or self.date_from,
            'date_to': form_data.get('date_to') or self.date_to,
            'target_move': form_data.get('target_move') or self.target_move,
            'line_ids': line_commands,
        })
        return preview._open_action()


class AccountPrintJournal(models.TransientModel):
    _inherit = 'account.print.journal'

    def _prepare_preview_data(self):
        self.ensure_one()
        data = {
            'ids': [self.id],
            'model': self._name,
            'form': self.read([
                'date_from',
                'date_to',
                'journal_ids',
                'target_move',
                'company_id',
            ])[0],
        }
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)
        return self._get_report_data(data)

    def action_view_report(self):
        self.ensure_one()
        report_action = self.with_context(
            active_model=self._name,
            active_id=self.id,
            active_ids=[self.id],
        ).check_report()
        data = report_action.get('data') or {}
        form_data = data.get('form') or {}
        report_context = dict(self.env.context, **(report_action.get('context') or {}))
        report_values = self.env['report.accounting_pdf_reports.report_journal'].with_context(
            report_context
        )._get_report_values([], data=data)

        line_commands = [(5, 0, 0)]
        sequence = 1
        lines_by_journal = report_values.get('lines', {})
        for journal in report_values.get('docs', self.env['account.journal']):
            line_commands.append((0, 0, {
                'sequence': sequence,
                'line_type': 'section',
                'name': f"[{journal.code}] {journal.name}",
                'journal_name': journal.code,
            }))
            sequence += 1
            for move_line in lines_by_journal.get(journal.id, self.env['account.move.line']):
                line_commands.append((0, 0, {
                    'sequence': sequence,
                    'line_type': 'line',
                    'date': move_line.date,
                    'code': move_line.account_id.code,
                    'name': move_line.name or move_line.ref or '',
                    'journal_name': journal.code,
                    'move_name': move_line.move_id.name,
                    'partner_name': move_line.partner_id.name or '',
                    'debit': move_line.debit,
                    'credit': move_line.credit,
                    'balance': move_line.debit - move_line.credit,
                }))
                sequence += 1

        preview = self.env['account.audit.report.preview'].create({
            'name': _('Journals Audit Preview'),
            'report_type': 'journals_audit',
            'wizard_ref': f'{self._name},{self.id}',
            'company_id': self.company_id.id,
            'date_from': form_data.get('date_from') or self.date_from,
            'date_to': form_data.get('date_to') or self.date_to,
            'target_move': form_data.get('target_move') or self.target_move,
            'line_ids': line_commands,
        })
        return preview._open_action()


class AccountTaxReport(models.TransientModel):
    _inherit = 'account.tax.report.wizard'

    def action_view_report(self):
        self.ensure_one()
        report_action = self.with_context(
            active_model=self._name,
            active_id=self.id,
            active_ids=[self.id],
        ).check_report()
        data = report_action.get('data') or {}
        form_data = data.get('form') or {}
        report_context = dict(self.env.context, **(report_action.get('context') or {}))
        report_values = self.env['report.accounting_pdf_reports.report_tax'].with_context(
            report_context
        )._get_report_values([], data=data)

        line_commands = [(5, 0, 0)]
        sequence = 1
        group_labels = {
            'sale': _('Sales Taxes'),
            'purchase': _('Purchase Taxes'),
        }

        for group_code in ('sale', 'purchase'):
            tax_lines = report_values.get('lines', {}).get(group_code, [])
            if not tax_lines:
                continue
            line_commands.append((0, 0, {
                'sequence': sequence,
                'line_type': 'section',
                'name': group_labels.get(group_code, group_code.title()),
            }))
            sequence += 1
            for tax_line in tax_lines:
                line_commands.append((0, 0, {
                    'sequence': sequence,
                    'line_type': 'tax',
                    'name': tax_line.get('name') or '',
                    'net': tax_line.get('net', 0.0),
                    'tax': tax_line.get('tax', 0.0),
                }))
                sequence += 1

        preview = self.env['account.audit.report.preview'].create({
            'name': _('Tax Report Preview'),
            'report_type': 'tax_report',
            'wizard_ref': f'{self._name},{self.id}',
            'company_id': self.company_id.id,
            'date_from': form_data.get('date_from') or self.date_from,
            'date_to': form_data.get('date_to') or self.date_to,
            'target_move': form_data.get('target_move') or self.target_move,
            'line_ids': line_commands,
        })
        return preview._open_action()


class AccountAuditReportPreview(models.TransientModel):
    _name = 'account.audit.report.preview'
    _description = 'Audit Report Preview'

    name = fields.Char(readonly=True)
    report_type = fields.Selection([
        ('general_ledger', 'General Ledger'),
        ('trial_balance', 'Trial Balance'),
        ('journals_audit', 'Journals Audit'),
        ('tax_report', 'Tax Report'),
    ], required=True, readonly=True)
    wizard_ref = fields.Reference(selection='_selection_wizard_ref', required=True, readonly=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True)
    date_from = fields.Date(readonly=True)
    date_to = fields.Date(readonly=True)
    target_move = fields.Selection([
        ('posted', 'All Posted Entries'),
        ('all', 'All Entries'),
    ], readonly=True)
    line_ids = fields.One2many('account.audit.report.preview.line', 'preview_id', readonly=True)

    @api.model
    def _selection_wizard_ref(self):
        return [
            ('account.report.general.ledger', 'General Ledger Wizard'),
            ('account.balance.report', 'Trial Balance Wizard'),
            ('account.print.journal', 'Journals Audit Wizard'),
            ('account.tax.report.wizard', 'Tax Report Wizard'),
        ]

    def _open_action(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Vista previa'),
            'res_model': 'account.audit.report.preview',
            'view_mode': 'form',
            'view_id': self.env.ref('accounting_pdf_reports_view.view_account_audit_report_preview_form').id,
            'res_id': self.id,
            'target': 'current',
        }

    def action_export_pdf(self):
        self.ensure_one()
        if not self.wizard_ref:
            raise UserError(_('No wizard was found to generate the PDF.'))
        return self.wizard_ref.with_context(
            active_model=self.wizard_ref._name,
            active_id=self.wizard_ref.id,
            active_ids=[self.wizard_ref.id],
        ).check_report()


class AccountAuditReportPreviewLine(models.TransientModel):
    _name = 'account.audit.report.preview.line'
    _description = 'Audit Report Preview Line'
    _order = 'sequence, id'

    preview_id = fields.Many2one('account.audit.report.preview', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    line_type = fields.Selection([
        ('section', 'Section'),
        ('line', 'Line'),
        ('tax', 'Tax'),
    ], required=True, default='line')
    date = fields.Date(readonly=True)
    code = fields.Char(readonly=True)
    journal_name = fields.Char(readonly=True)
    move_name = fields.Char(readonly=True)
    partner_name = fields.Char(readonly=True)
    name = fields.Char(required=True, readonly=True)

    currency_id = fields.Many2one(related='preview_id.company_id.currency_id', readonly=True, store=False)
    debit = fields.Monetary(currency_field='currency_id', readonly=True)
    credit = fields.Monetary(currency_field='currency_id', readonly=True)
    balance = fields.Monetary(currency_field='currency_id', readonly=True)
    net = fields.Monetary(currency_field='currency_id', readonly=True)
    tax = fields.Monetary(currency_field='currency_id', readonly=True)
