from odoo import models


class ReportFinancialContextPatch(models.AbstractModel):
    _inherit = 'report.accounting_pdf_reports.report_financial'

    def _get_report_values(self, docids, data=None):
        active_ids = self.env.context.get('active_ids') or []
        if not self.env.context.get('active_id') and active_ids:
            return super(ReportFinancialContextPatch, self.with_context(active_id=active_ids[0]))._get_report_values(
                docids, data=data
            )
        return super()._get_report_values(docids, data=data)

