# MCP Connector for Odoo

**Connect your Odoo to Claude, ChatGPT & any AI — in minutes.**

`FREE MODULE` • `~5 MIN SETUP` • `ANY MCP AI CLIENT`

MCP Connector links any AI client that supports the **Model Context Protocol** directly to your Odoo
database. Install the free module, configure it once (about 5 minutes), and give your team a single
connector link — **no shared passwords, no per-user setup**. Access is orchestrated by role and email,
and works from desktop, web and mobile AI apps.

![MCP chat demo](erp_mcp_client/static/description/images/mcp-chat-demo.gif)

| | |
|---|---|
| **~5 min** | One-time setup |
| **Any AI** | MCP-compatible client |
| **Free** | Module + 1st month |

- ✅ No password sharing
- ✅ Role & email based access
- ✅ Your data stays in Odoo
- ✅ Odoo Community & Enterprise

### How it fits together

```
  AI Client                MCP Connector              Your Odoo
  Claude / GPT / …   ─────►  secure bridge   ─────►   Community / Enterprise
```

Google OAuth sign-in • role-based API keys • live two-way link

---

## What your team can do

Once connected, anyone on your team just asks their AI assistant — it does the work directly in Odoo,
**within their own permissions**.

| | Example prompt |
|---|---|
| **Instant analytics** | *"Show revenue by salesperson this quarter and flag anyone below target."* |
| **Create quotations** | *"Draft a quote for ACME: 10× Product A, 5× Product B, 15% discount."* |
| **Client follow-ups** | *"List customers with no activity in 30 days and log a follow-up task."* |
| **Stock & expiry review** | *"Which lots expire within 30 days, how many units, and in which warehouse?"* |

---

## For administrators — orchestrate access by role & email

Define roles in the module and map each one to a set of Google emails. Whoever signs in gets exactly
the permissions of the matching Odoo user — nothing more. Add or remove people by editing a list,
never by handing out credentials.

- **One link for everyone** — share a single connector URL. No installs or setup on the user side.
- **Google OAuth sign-in** — users authenticate with Google. Only listed emails get through.
- **Per-role Odoo permissions** — each role uses its own Odoo user & rights: read-only, sales, admin, etc.
- **Any device** — desktop, web and mobile AI apps, same secure connector.

---

## Step-by-step setup — six processes, about five minutes

| # | Process | Where | Time |
|---|---------|-------|------|
| 1 | Install module | in Odoo | ~1 min |
| 2 | Google credentials | Cloud Console | ~2 min |
| 3 | Odoo API key | per role | ~1 min per role |
| 4 | Configure & register the connector | in Odoo | ~1 min |
| 5 | Authorize URLs | in Google | ~1 min |
| 6 | Connect AI client & sign in | in your AI client | ~1 min |

Follow the processes in order. Each step below has the exact screenshot from the real interface.

---

### Process 1 — Install the free module · *in Odoo · ~1 min*

Add MCP Connector to the Odoo database you want to expose to your AI client, then open it to create
your first connection.

**1. Install & activate**
Go to **Apps**, find **MCP Connector** and install it in the database you want to access through MCP.

![Install the module](erp_mcp_client/static/description/images/config-1.jpg)

**2. Create a new connection**
Open **MCP Connector → Connectors** and click **New** to start a new MCP registration.

![Create a connection](erp_mcp_client/static/description/images/config-2.jpg)

---

### Process 2 — Create Google OAuth credentials · *Google Cloud Console · ~2 min*

The connector uses Google sign-in to authenticate your users. Create an OAuth client at
[console.cloud.google.com](https://console.cloud.google.com/apis/credentials) and copy its Client ID
& Secret. You will add the redirect URLs later, in **Process 5**, once the module generates them.

**1. Open APIs & Services** — in the Google Cloud console, open **APIs & Services** from Quick access.

![APIs & Services](erp_mcp_client/static/description/images/google-1.jpg)

**2. Go to Credentials** — in the left menu, select **Credentials**.

![Credentials](erp_mcp_client/static/description/images/google-2.jpg)

**3. Create credentials** — click **+ Create credentials** at the top.

![Create credentials](erp_mcp_client/static/description/images/google-3.jpg)

**4. Choose OAuth client ID** — select **OAuth client ID** from the dropdown.

![OAuth client ID](erp_mcp_client/static/description/images/google-4.jpg)

**5. Application type: Web application** — set **Application type** to **Web application**.

![Web application](erp_mcp_client/static/description/images/google-5.jpg)

**6. Name it & create** — give the client any name (e.g. *"Odoo MCP Connector"*) and click **Create**.
Leave the origin/redirect URIs empty for now — you will paste them in Process 5.

![Name & create](erp_mcp_client/static/description/images/google-6.jpg)

**7. Copy Client ID & Secret** — paste them into the matching fields of the MCP Connector module in
Odoo. Store the secret safely — it is shown only once.

![Copy client id & secret](erp_mcp_client/static/description/images/google-7.jpg)

---

### Process 3 — Generate an Odoo API key · *in Odoo · ~1 min per role*

Each role connects to Odoo with its own API key, generated by the Odoo user that role represents.
Repeat this process for every role (admin, sales, read-only, …).

**1. Open My Preferences** — click your avatar (top-right) and choose **My Preferences**.

![My Preferences](erp_mcp_client/static/description/images/apikey-1.jpg)

**2. Security → Add API Key** — open the **Security** tab and click **Add API Key**.

![Add API key](erp_mcp_client/static/description/images/apikey-2.jpg)

**3. Confirm your password** — the user creating the key must enter their Odoo login password.

![Confirm password](erp_mcp_client/static/description/images/apikey-3.jpg)

**4. Name it & set validity** — give the key a clear name and choose an expiration. A **Persistent Key**
is recommended so the connection does not expire.

![Name & validity](erp_mcp_client/static/description/images/apikey-4.jpg)

**5. Generate the key** — click **Generate key**.

![Generate key](erp_mcp_client/static/description/images/apikey-5.jpg)

**6. Copy the key into the module** — paste it into the **Odoo API Key** field of the matching role in
the MCP Connector module. It is shown only once.

![Copy key](erp_mcp_client/static/description/images/apikey-6.jpg)

---

### Process 4 — Configure & register the connector · *in Odoo · ~1 min*

Fill in the registration form with everything you gathered, add your roles, and register.

**1. Name, Google keys & Odoo instance** — give the connector a name, paste the Google Client ID /
Secret from Process 2, and set the **Odoo URL** and **Database** — use the green *"Use this instance"* /
*"Use current DB"* shortcuts to auto-fill the current database.

![Registration form](erp_mcp_client/static/description/images/config-3.jpg)

**2. Add roles: API key + email** — in **Access Roles**, add a line per role with its **role name**, its
**Odoo API key** (from Process 3) and the **email(s)** allowed to use it. This is how you map who gets
which permissions.

![Access roles](erp_mcp_client/static/description/images/config-7.jpg)

**3. Click Register** — press **Register** in the top-left corner. The status changes to **Registered**
and your personal MCP instance is provisioned.

![Register](erp_mcp_client/static/description/images/config-4.jpg)

---

### Process 5 — Authorize the URLs in Google · *Odoo + Google Console · ~1 min*

After registration the module generates three URLs. Copy two of them into your Google OAuth client so
sign-in is trusted, then re-register.

**1. Copy the generated URLs** — the **Registration Result** now shows **Google Origin URL**,
**Google Callback URL** and **AI Connector URL**. Use the copy buttons.

![Generated URLs](erp_mcp_client/static/description/images/config-5.jpg)

**2. Paste them into Google Console** — in your OAuth client: put the **Google Origin URL** into
**Authorized JavaScript origins**, and the **Google Callback URL** into **Authorized redirect URIs**. Save.

![Google console URLs](erp_mcp_client/static/description/images/config-6.jpg)

**3. Re-register** — back in Odoo, click **Re-register** to apply everything. Copy the **AI Connector URL**
— that is the link you share with your team.

![Re-register](erp_mcp_client/static/description/images/config-7.jpg)

---

### Process 6 — Connect your AI client & sign in · *in your AI client · ~1 min*

Shown here in Claude — the flow is the same in ChatGPT or any MCP-compatible client. Just paste the
AI Connector URL and sign in with Google.

**1. Add a custom connector** — open **Settings → Connectors**, then **Add → Add custom connector**.

![Add custom connector](erp_mcp_client/static/description/images/claude-1.jpg)

**2. Add name & connector URL** — give it any name and paste the **AI Connector URL** into the
MCP / HTTPS URL field.

![Connector URL](erp_mcp_client/static/description/images/claude-2.jpg)

**3. Connect** — click **Connect** to start the sign-in.

![Connect](erp_mcp_client/static/description/images/claude-3.jpg)

**4. Allow access** — sign in with Google and click **Allow Access**. Only emails you listed in a role
can connect — and each works within that role's Odoo permissions. Done!

![Allow access](erp_mcp_client/static/description/images/claude-4.jpg)

---

## You're live

Your AI client now works with your Odoo from desktop, web and mobile. Add or remove people any time by
editing role emails and re-registering — no new setup on their side.

---

## Security by design

- **Google OAuth only** — no valid Google account in a role = no access. Every request is authenticated.
- **Real Odoo permissions** — each person acts as their mapped Odoo user; the AI never gets super-access.
- **Data stays in Odoo** — the connector is a gateway to your API. We don't copy or store your database.
- **Isolated per tenant** — each customer runs on a dedicated, isolated instance over HTTPS.

---

## Requirements

A running Odoo, a Google Cloud project, and an MCP-capable AI client. That's it.

| | |
|---|---|
| **Odoo** | Community or Enterprise — on-premise, Odoo.sh or self-hosted |
| **Odoo API key** | One per role you want to expose |
| **Google Cloud project** | For the OAuth client (sign-in) |
| **MCP AI client** | Claude, ChatGPT or any client supporting custom MCP connectors |

---

## FAQ

**Do I have to give people my Odoo password?**
No. You share one connector link. Users sign in with Google; access is decided by their email and its
role — no credentials are handed out.

**Does it work with ChatGPT too?**
Yes. Any AI client that supports custom MCP connectors works — Claude, ChatGPT and others. The
connector URL is the same.

**Can I limit someone to read-only?**
Yes. Point a role at an Odoo user that has read-only rights and add their email — the AI can then only
read for that person.

**Are custom modules supported?**
Yes. The connector reads model and field structure directly from your Odoo, so custom models and
fields work out of the box.

**Where does my data live?**
In your Odoo. The connector proxies authorized API calls; it does not keep a copy of your database.

**Someone joined or left — what do I do?**
Edit the role's email list and press **Re-register**. Access updates instantly with no work on the
user's side.

---

## Technical reference

### Module

| | |
|---|---|
| Technical name | `erp_mcp_client` |
| Version | 1.0 |
| Odoo series | 19.0 |
| Depends | `base` |
| License | OPL-1 |
| Author | ERP SWISS |

### Repository layout

```
erp_mcp_client/
├── __manifest__.py
├── models/
│   ├── mcp_client.py           # erp.mcp.client — registration + registrar call
│   └── mcp_client_role.py      # erp.mcp.client.role — role ↔ API key ↔ emails
├── security/
│   └── ir.model.access.csv     # both models restricted to base.group_system
├── views/
│   └── mcp_client_views.xml    # list, form, action, "MCP Connector" menu
└── static/description/
    ├── index.html              # Odoo Apps store page (source of this README)
    └── images/                 # setup screenshots
```

### Models

**`erp.mcp.client`** — one record per MCP registration.

| Field | Type | Notes |
|---|---|---|
| `name` | Char | Registration name (required) |
| `registrar_url` | Char | Registrar endpoint, default `https://mcp.erpswiss.com/mcp/register` |
| `odoo_url` | Char | Defaults to `web.base.url` |
| `odoo_db` | Char | Defaults to the current database name |
| `odoo_login` / `odoo_api_key` | Char | Credentials of the default (admin) role |
| `google_client_id` / `google_client_secret` | Char | From Process 2 (required) |
| `odoo_admin_emails` | Char | Comma-separated Google emails granted the `admin` role |
| `role_ids` | One2many | Additional roles → `erp.mcp.client.role` |
| `tenant_uuid` | Char | Returned by the registrar (readonly) |
| `mcp_url` | Char | Returned by the registrar (readonly) |
| `mcp_ai_url` | Char | Computed — the **AI Connector URL** you share |
| `mcp_https_url` | Char | Computed — the **Google Origin URL** |
| `mcp_callback_url` | Char | Computed — `<origin>/auth/callback` |
| `registration_state` | Selection | `draft` / `registered` / `error` |
| `remote_state`, `last_error`, `registered_on` | | Result of the last registration |

**`erp.mcp.client.role`** — maps a set of Google emails to one Odoo user's API key.

| Field | Type | Notes |
|---|---|---|
| `client_id` | Many2one | Parent registration (`ondelete="cascade"`) |
| `role_name` | Char | Becomes `ODOO_<ROLE>_API_KEY` / `ODOO_<ROLE>_EMAILS` on the MCP server |
| `odoo_api_key` | Char | API key of the Odoo user this role acts as |
| `emails` | Char | Comma-separated Google emails allowed to use this role |

### Actions

| Method | Button | What it does |
|---|---|---|
| `action_register` | Register / Re-register | POSTs a JSON-RPC envelope to `registrar_url`, stores `tenant_uuid` + `mcp_url`, sets state to `registered` |
| `action_fill_odoo_url` | Use this instance | Fills `odoo_url` from `web.base.url`, forcing `https://` |
| `action_fill_odoo_db` | Use current DB | Fills `odoo_db` with `env.cr.dbname` |
| `action_open_google_cloud_console` | Open Google Cloud Console | Opens the GCP credentials page in a new tab |

### Registration payload

`action_register` sends a JSON-RPC 2.0 `call` to `registrar_url` with:

```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "name": "…",
    "odoo_url": "https://…",
    "odoo_db": "…",
    "odoo_login": "…",
    "odoo_api_key": "…",
    "google_client_id": "…",
    "google_client_secret": "…",
    "odoo_admin_emails": "a@x.com,b@x.com",
    "roles": [
      {"role_name": "sales", "odoo_api_key": "…", "emails": "c@x.com"}
    ],
    "tenant_uuid": "… (only when re-registering)"
  }
}
```

The registrar answers with `tenant_uuid`, `mcp_url` and `state`. Errors surface as a `UserError` and
are stored in `last_error` with the state set to `error`. Requests time out after 30 seconds.

### Access rights

Both models are limited to **Settings / Administration** users (`base.group_system`) with full CRUD —
regular users never see the connector or the stored API keys.

### Installation from source

```bash
git clone <this-repo> && cp -r MCP_CLIENT/erp_mcp_client /path/to/odoo/addons/
# restart Odoo, then: Apps → Update Apps List → search "MCP Connector" → Install
```

Then follow **Process 2** onwards above.

---

**Give your team an AI line to Odoo** — install the free MCP Connector, spend five minutes on setup,
and share one secure link.

*Free module • ~5 min setup • Community & Enterprise • Claude, ChatGPT & any MCP client*
