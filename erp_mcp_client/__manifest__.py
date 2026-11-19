{
    'name': "MCP Connector for Claude, ChatGPT & any AI",
    'summary': "Register this Odoo instance with an ERP MCP registrar",
    'author': 'ERP SWISS',
    'version': '1.3',
    'description': """ERP SWISS""",
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/mcp_client_views.xml',
    ],
    'license': 'OPL-1',
    'application': True,
    'installable': True,
    'images': ['static/description/mcp-connector-cover.png'],
}
