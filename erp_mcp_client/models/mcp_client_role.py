import secrets

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class McpClientRole(models.Model):
    _name = "erp.mcp.client.role"
    _description = "ERP MCP Client Role"
    _order = "id"

    client_id = fields.Many2one(
        comodel_name="erp.mcp.client",
        string="Registration",
        required=True,
        ondelete="cascade",
        index=True,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
        ondelete="cascade",
        help="Odoo user this MCP role acts as. Its email is sent to the "
             "registrar and identifies the role there.",
    )
    odoo_api_key = fields.Char(
        string="Odoo API Key",
        required=True,
        help="API key of the selected Odoo user.",
    )
    emails = fields.Char(
        string="Account Email",
        compute="_compute_emails",
        store=True,
        readonly=False,
        help="Google email(s) that log into the MCP as this user. Filled from "
             "the user's email; editable, comma-separated for several.",
    )
    access_tokens = fields.Char(
        string="Access Token",
        copy=False,
        help="Static Bearer token that authenticates as this user "
             "(Authorization: Bearer <token>), no Google login needed. "
             "Required when Google OAuth is disabled.",
    )

    _unique_user = models.Constraint(
        "UNIQUE (client_id, user_id)",
        "Each user can only be added once per registration.",
    )

    @api.depends("user_id")
    def _compute_emails(self):
        for role in self:
            role.emails = role.user_id.email or role.user_id.login or False

    @api.constrains("access_tokens", "client_id")
    def _check_access_token(self):
        for role in self:
            if not role.client_id.use_google_oauth and not (role.access_tokens or "").strip():
                raise ValidationError(
                    _("An access token is required for user '%s' when Google OAuth is disabled.")
                    % role.user_id.display_name
                )

    @staticmethod
    def _new_token():
        return secrets.token_urlsafe(32)

    @api.onchange("user_id")
    def _onchange_user_id_token(self):
        """Without Google OAuth the token is the only way in: pre-fill one so
        the line can be saved right away (it can be regenerated later)."""
        for role in self:
            if role.user_id and not role.access_tokens and not role.client_id.use_google_oauth:
                role.access_tokens = self._new_token()

    def action_generate_token(self):
        for role in self:
            role.access_tokens = self._new_token()
        return True

    def _user_email(self):
        """Email identifying this role on the registrar (the user's own)."""
        self.ensure_one()
        return self.user_id.email or self.user_id.login or ""
