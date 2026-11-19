import logging
from urllib.parse import urlsplit

import requests

from odoo import _, fields, models, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class RegistrationError(UserError):
    """The registrar refused or failed a registration."""


class McpClient(models.Model):
    _name = "erp.mcp.client"
    _description = "ERP MCP Client Registration"
    _order = "create_date desc"

    # Sent as X-MCP-Registrar-Token; the registrar requires it to create a
    # tenant. Override with the `erp_mcp_client.registrar_token` system
    # parameter after a rotation.
    _REGISTRAR_TOKEN = "3O7sA2rkO94TtHqDFHFlq8EKtTkR48qSKIAetVK1QYM"

    name = fields.Char(string="Registration Name", required=True)

    registrar_url = fields.Char(
        string="Registrar URL",
        required=True,
        help="Base URL of the ERP MCP registrar (the Odoo running erp_mcp_handler).",
        default='https://mcp.erpswiss.com/mcp/register',
    )

    odoo_url = fields.Char(string="Odoo URL", required=True, default= lambda self: self.env["ir.config_parameter"].sudo().get_param("web.base.url"))
    odoo_db = fields.Char(string="Odoo Database", required=True, default=lambda self: self.env.cr.dbname)
    odoo_login = fields.Char(string="Odoo Login / User")
    odoo_api_key = fields.Char(string="Odoo API Key")

    use_google_oauth = fields.Boolean(
        string="Use Google OAuth",
        default=True,
        help="Enable to let users sign in to the MCP with their Google account. "
             "Requires a Google OAuth Client ID and Secret. When disabled, the "
             "AI client connects with an access token instead.",
    )
    auth_method = fields.Selection(
        selection=[
            ("google_oauth", "Google OAuth"),
            ("access_token", "Access Token"),
        ],
        string="Authentication",
        compute="_compute_auth_method",
    )
    google_client_id = fields.Char(string="Google Client ID")
    google_client_secret = fields.Char(string="Google Client Secret")

    odoo_admin_emails = fields.Char(
        string="Admin Emails",
        help="Comma-separated Google emails granted the 'admin' role (they act "
             "as the Odoo user behind the API Key above). Put here the email(s) "
             "you log into the MCP with so you get access after registering.",
    )
    odoo_admin_access_tokens = fields.Char(
        string="Admin Access Tokens",
        help="Comma-separated static Bearer tokens granted the 'admin' role "
             "(Authorization: Bearer <token>) — lets a non-interactive client "
             "call the MCP without a Google login.",
    )
    role_ids = fields.One2many(
        comodel_name="erp.mcp.client.role",
        inverse_name="client_id",
        string="Access Roles",
        help="Odoo users exposed through the MCP. Each maps the user's "
             "email(s) and/or access token to that user's API key.",
    )

    tenant_uuid = fields.Char(string="Tenant UUID", readonly=True, copy=False)
    mcp_url = fields.Char(string="MCP URL", readonly=True, copy=False)
    mcp_ai_url = fields.Char(string="AI Connector URL", readonly=True, copy=False, compute="_compute_mcp_calback_url")
    mcp_https_url = fields.Char(string="Google Origin URL", readonly=True, copy=False,
                                compute="_compute_mcp_calback_url")
    mcp_callback_url = fields.Char(string="Google Callback URL", readonly=True, copy=False,
                                   compute="_compute_mcp_calback_url")
    # Exact tenant status on the registrar (active, renewal, payment_due,
    # expired, blocked, revoked) — shown as the form ribbon.
    remote_state = fields.Char(string="Remote Status", readonly=True, copy=False)

    # Whether the connector works: "registered" while the instance runs
    # (the ribbon then tells active / renewal / payment due), otherwise the
    # reason it is stopped.
    registration_state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("registered", "Registered"),
            ("expired", "Expired"),
            ("blocked", "Blocked"),
            ("revoked", "Revoked"),
            ("error", "Error"),
        ],
        string="Status",
        default="draft",
        required=True,
        copy=False,
    )
    last_error = fields.Text(string="Last Error", readonly=True, copy=False)
    registered_on = fields.Datetime(string="Registered On", readonly=True, copy=False)

    # Subscription — mirrored from the registrar by _cron_sync_subscription.
    client_secret = fields.Char(
        string="Client Secret", readonly=True, copy=False, groups="base.group_system",
        help="Issued by the registrar at registration; authenticates this "
             "client for re-registration and status checks.",
    )
    billing_email = fields.Char(
        string="Billing Email",
        default=lambda self: self.env.company.email or self.env.user.email,
        help="Where the registrar sends the monthly payment link.",
    )
    referral_code = fields.Char(
        string="Partner Code",
        copy=False,
        help="Code of the partner who recommended the MCP Connector, if any. "
             "Sent with the registration; it can no longer be changed once accepted.",
    )
    referral_valid = fields.Boolean(string="Partner Code Accepted", readonly=True, copy=False)
    referral_partner = fields.Char(string="Partner", readonly=True, copy=False)
    paid_until = fields.Datetime(string="Paid Until", readonly=True, copy=False)
    billing_user_count = fields.Integer(string="Users", readonly=True, copy=False)
    paid_user_count = fields.Integer(string="Paid Users", readonly=True, copy=False)
    unpaid_user_count = fields.Integer(string="Unpaid Users", readonly=True, copy=False)
    payment_due_date = fields.Datetime(
        string="Pay By", readonly=True, copy=False,
        help="Deadline to pay the extra users, after which the connector is suspended.",
    )
    billing_unit_amount = fields.Float(string="Price per User", readonly=True, copy=False)
    billing_currency = fields.Char(string="Currency", readonly=True, copy=False)
    amount_due = fields.Float(string="Amount Due", readonly=True, copy=False)
    payment_url = fields.Char(string="Payment Link", readonly=True, copy=False)
    subscription_checked_on = fields.Datetime(string="Last Status Check", readonly=True, copy=False)

    def action_fill_odoo_url(self):
        """Fill the Odoo URL with this instance's base URL, forcing https."""
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url") or ""
        base_url = base_url.strip().rstrip("/")
        if base_url.startswith("http://"):
            base_url = "https://" + base_url[len("http://"):]
        elif not base_url.startswith("https://"):
            base_url = "https://" + base_url
        self.odoo_url = base_url
        return True

    def action_fill_odoo_db(self):
        """Fill the Odoo Database with the current database name."""
        self.ensure_one()
        self.odoo_db = self.env.cr.dbname
        return True

    @api.depends("use_google_oauth")
    def _compute_auth_method(self):
        for rec in self:
            rec.auth_method = "google_oauth" if rec.use_google_oauth else "access_token"

    @api.depends('mcp_url')
    def _compute_mcp_calback_url(self):
        for rec in self:
            if not rec.mcp_url:
                rec.mcp_ai_url = rec.mcp_https_url = rec.mcp_callback_url = False
                continue
            url = rec.mcp_url.strip().rstrip("/")
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"
            rec.mcp_ai_url = url
            rec.mcp_https_url = url.removesuffix("/mcp")
            rec.mcp_callback_url = rec.mcp_https_url + '/auth/callback'

    @api.constrains("use_google_oauth", "google_client_id", "google_client_secret")
    def _check_google_oauth(self):
        for rec in self:
            if rec.use_google_oauth and not (
                (rec.google_client_id or "").strip()
                and (rec.google_client_secret or "").strip()
            ):
                raise ValidationError(_(
                    "Google Client ID and Google Client Secret are required "
                    "when \"Use Google OAuth\" is enabled."
                ))
        # Disabling OAuth makes the access token mandatory on every user.
        self.role_ids._check_access_token()

    @api.onchange("use_google_oauth")
    def _onchange_use_google_oauth(self):
        if not self.use_google_oauth:
            for role in self.role_ids:
                if not role.access_tokens:
                    role.access_tokens = role._new_token()

    def _check_registrar_url(self):
        for record in self:
            if record.registrar_url and not record.registrar_url.startswith(
                    ("http://", "https://")
            ):
                raise ValidationError(
                    _("Registrar URL must start with http:// or https://")
                )

    def _register_payload(self):
        self.ensure_one()
        oauth = self.use_google_oauth
        data = {
            "name": self.name,

            "odoo_url": self.odoo_url,
            "odoo_db": self.odoo_db,
            "odoo_login": self.odoo_login,
            "odoo_api_key": self.odoo_api_key,
            "auth_method": self.auth_method,
            "use_google_oauth": self.use_google_oauth,
            "google_client_id": self.google_client_id if self.use_google_oauth else "",
            "google_client_secret": self.google_client_secret if self.use_google_oauth else "",
            "odoo_admin_emails": (self.odoo_admin_emails or "") if oauth else "",
            "odoo_admin_access_tokens": self.odoo_admin_access_tokens or "",
            "roles": [
                {
                    "user_email": role._user_email(),
                    "odoo_api_key": role.odoo_api_key,
                    "emails": (role.emails or "") if oauth else "",
                    "access_tokens": role.access_tokens or "",
                }
                for role in self.role_ids
            ],
        }
        if self.tenant_uuid:
            data["tenant_uuid"] = self.tenant_uuid
        return data

    def _mark_error(self, message):
        """Abort a registration; action_register() stores the message."""
        raise RegistrationError(message)

    def _store_error(self, exc):
        """Keep the error on the record so the form shows it in the red
        support alert. The action does not raise: an exception would roll
        the write back."""
        message = exc.args[0] if exc.args else str(exc)
        _logger.warning("MCP client %s: %s", self.name, message)
        self.sudo().write({"last_error": message})

    def _registrar_endpoint(self, path):
        """Registrar URL with ``path`` (the field holds the /mcp/register URL)."""
        self.ensure_one()
        parts = urlsplit(self.registrar_url or "")
        return "%s://%s%s" % (parts.scheme or "https", parts.netloc, path)

    def _call_registrar(self, path, params):
        """JSON-RPC call to the registrar; returns ``result`` or raises UserError."""
        self.ensure_one()
        envelope = {"jsonrpc": "2.0", "method": "call", "params": params}
        token = (
            self.env["ir.config_parameter"].sudo().get_param("erp_mcp_client.registrar_token")
            or self._REGISTRAR_TOKEN
        )
        headers = {"X-MCP-Registrar-Token": token}
        try:
            response = requests.post(
                self._registrar_endpoint(path), json=envelope, headers=headers, timeout=30
            )
            if response.status_code == 429:
                raise UserError(_(
                    "Too many requests to the registrar. Please wait a minute and try again."
                ))
            response.raise_for_status()
            body = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise UserError(_("Request to the registrar failed: %s") % exc)
        if body.get("error"):
            error = body["error"]
            message = (error.get("data") or {}).get("message") or error.get("message")
            raise UserError(_("Registrar returned an error: %s") % message)
        return body.get("result") or {}

    def _auth_params(self):
        self.ensure_one()
        return {"tenant_uuid": self.tenant_uuid, "client_secret": self.sudo().client_secret}

    # Registrar tenant states: the instance runs / is stopped.
    _REMOTE_RUNNING_STATES = ("active", "renewal", "payment_due")
    _REMOTE_STOPPED_STATES = ("expired", "blocked", "revoked")

    def _registration_state_for(self, remote):
        """Local status for a registrar tenant state."""
        if remote in self._REMOTE_STOPPED_STATES:
            return remote
        if remote in self._REMOTE_RUNNING_STATES:
            return "registered"
        return self.registration_state

    def _apply_billing(self, billing):
        """Store the subscription status returned by the registrar."""
        self.ensure_one()
        remote = billing.get("state")
        self.write({
            "registration_state": self._registration_state_for(remote),
            "remote_state": remote or self.remote_state,
            "paid_until": billing.get("paid_until") or False,
            "billing_user_count": billing.get("user_count") or 0,
            "paid_user_count": billing.get("paid_user_count") or 0,
            "unpaid_user_count": billing.get("unpaid_user_count") or 0,
            "payment_due_date": billing.get("payment_due_date") or False,
            **self._referral_vals(billing.get("referral")),
            "billing_unit_amount": billing.get("unit_amount") or 0.0,
            "billing_currency": billing.get("currency") or False,
            "amount_due": billing.get("amount_due") or 0.0,
            "payment_url": billing.get("payment_url") or False,
            "subscription_checked_on": fields.Datetime.now(),
        })

    def _referral_vals(self, referral):
        """Mirror the registrar's view of the partner code (the first accepted
        code is final there)."""
        if not referral:
            return {}
        vals = {
            "referral_valid": bool(referral.get("valid")),
            "referral_partner": referral.get("partner") or False,
        }
        if referral.get("valid") and referral.get("code"):
            vals["referral_code"] = referral["code"]
        return vals

    def action_register(self):
        self.ensure_one()
        try:
            self._do_register()
        except RegistrationError as exc:
            self.write({"registration_state": "error"})
            self._store_error(exc)
        except UserError as exc:
            self._store_error(exc)
        return True

    def _do_register(self):
        self.ensure_one()
        self._check_registrar_url()
        self._check_google_oauth()
        if not self.use_google_oauth and not (
            (self.odoo_admin_access_tokens or "").strip()
            or any((role.access_tokens or "").strip() for role in self.role_ids)
        ):
            raise UserError(_(
                "Google OAuth is disabled: add at least one user with an "
                "Access Token so the AI client can connect."
            ))
        params = self._register_payload()
        params["client_secret"] = self.sudo().client_secret or ""
        params["billing_email"] = self.billing_email or ""
        params["referral_code"] = (self.referral_code or "").strip()
        try:
            result = self._call_registrar("/mcp/register", params)
        except UserError as exc:
            self._mark_error(_("Registration failed: %s") % exc)

        if result.get("error") == "missing_fields":
            self._mark_error(
                _("Registrar rejected the request, missing fields: %s")
                % ", ".join(result.get("fields", []))
            )
        if result.get("error") == "forbidden":
            self._mark_error(_("Registrar refused the update: client secret mismatch."))
        if result.get("error") == "unauthorized":
            self._mark_error(_("Registrar refused the registration: invalid registrar token."))
        if not result.get("tenant_uuid"):
            self._mark_error(_("Registrar returned an unexpected response."))

        vals = {
            "tenant_uuid": result.get("tenant_uuid"),
            "mcp_url": result.get("mcp_url"),
            "remote_state": result.get("state"),
            # A re-registered expired / blocked / revoked tenant stays so.
            "registration_state": (
                result.get("state") if result.get("state") in self._REMOTE_STOPPED_STATES
                else "registered"
            ),
            "last_error": False,
            "registered_on": fields.Datetime.now(),
        }
        if result.get("client_secret"):
            vals["client_secret"] = result["client_secret"]
        self.sudo().write(vals)
        if result.get("billing"):
            self._apply_billing(result["billing"])
        _logger.info("Registered MCP client %s (%s)", self.name, self.tenant_uuid)
        return True

    def _store_issued_secret(self, result):
        """Legacy registrations have no client secret: the registrar issues
        one on their first authenticated call — keep it for the next ones."""
        if result.get("client_secret"):
            self.sudo().client_secret = result["client_secret"]

    def _sync_subscription(self):
        self.ensure_one()
        if not self.tenant_uuid:
            raise UserError(_("Register (or re-register) this connector first."))
        result = self._call_registrar("/mcp/status", self._auth_params())
        self._store_issued_secret(result)
        if result.get("error") == "forbidden" and not self.sudo().client_secret:
            # Registered with an older version that did not keep the secret:
            # registering again (which proves ownership) fetches it.
            raise UserError(_("This connector has no client secret yet: click Register again."))
        if result.get("error"):
            raise UserError(_("Registrar refused the status request: %s") % result["error"])
        self._apply_billing(result)
        self.last_error = False

    def action_check_subscription(self):
        for rec in self:
            try:
                rec._sync_subscription()
            except UserError as exc:
                rec._store_error(exc)
        return True

    def action_pay_now(self):
        self.ensure_one()
        try:
            return self._pay_now()
        except UserError as exc:
            self._store_error(exc)
            return True

    def _pay_now(self):
        """Ask the registrar for an open invoice (creates one to pay in
        advance) and open its payment page."""
        self.ensure_one()
        if not self.tenant_uuid:
            raise UserError(_("Register (or re-register) this connector first."))
        result = self._call_registrar("/mcp/billing/request", self._auth_params())
        self._store_issued_secret(result)
        if result.get("error"):
            raise UserError(result.get("message") or _("Payment unavailable: %s") % result["error"])
        self._apply_billing(result)
        if not self.payment_url:
            raise UserError(_("The registrar did not return a payment link."))
        self.last_error = False
        return {"type": "ir.actions.act_url", "url": self.payment_url, "target": "new"}

    @api.model
    def _cron_sync_subscription(self):
        clients = self.search([
            # A failed re-registration keeps its tenant: poll it too.
            ("registration_state", "!=", "draft"),
            ("tenant_uuid", "!=", False),
        ])
        for client in clients:
            try:
                with self.env.cr.savepoint():
                    client._sync_subscription()
            except Exception as exc:  # keep polling the other registrations
                _logger.warning("MCP subscription sync failed for %s: %s", client.name, exc)
                # Outside the rolled-back savepoint, so it is kept.
                client._store_error(exc)
