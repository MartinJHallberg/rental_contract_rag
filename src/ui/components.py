// filepath: c:\Projects\rental_contract_rag\src\ui\components.py
"""Reusable UI components for the Dash app"""
import dash_bootstrap_components as dbc
from dash import html

def create_sample_contract_card(contract_info):
    """Create a card for sample contracts"""
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H6(contract_info["title"], className="card-title"),
                    html.P(contract_info["description"], className="card-text small"),
                    dbc.Button(
                        "Load Contract",
                        id=f"load-{contract_info['id']}",
                        color=contract_info["color"],
                        size="sm",
                        className="w-100",
                        n_clicks=0
                    ),
                ]
            )
        ],
        className="mb-2",
        outline=True,
    )

def create_placeholder_card(title, icon="📋"):
    """Create a placeholder validation card"""
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.H5(
                        [
                            icon + " " + title,
                            dbc.Badge(
                                "Waiting for validation",
                                color="secondary",
                                className="ms-2",
                            ),
                        ],
                        className="mb-0",
                    )
                ]
            ),
            dbc.CardBody(
                [
                    html.P(
                        "Upload and validate a contract to see results here.",
                        className="card-text text-muted",
                    ),
                    html.Small(
                        "References will appear here when available.",
                        className="text-muted",
                    ),
                ]
            ),
        ],
        color="light",
        outline=True,
        className="mb-3",
    )

def create_contract_summary_placeholder():
    """Create placeholder contract summary card"""
    return dbc.Card(
        [
            dbc.CardHeader([html.H5("📋 Contract Summary", className="mb-0")]),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Strong("Landlord: "),
                                    html.Span("Waiting for data...", className="text-muted"),
                                    html.Br(),
                                    html.Strong("Tenant: "),
                                    html.Span("Waiting for data...", className="text-muted"),
                                    html.Br(),
                                    html.Strong("Property: "),
                                    html.Span("Waiting for data...", className="text-muted"),
                                    html.Br(),
                                    html.Strong("Monthly Rent: "),
                                    html.Span("Waiting for data...", className="text-muted"),
                                ],
                                md=6,
                            ),
                            dbc.Col(
                                [
                                    html.Strong("Deposit: "),
                                    html.Span("Waiting for data...", className="text-muted"),
                                    html.Br(),
                                    html.Strong("Lease Duration: "),
                                    html.Span("Waiting for data...", className="text-muted"),
                                    html.Br(),
                                    html.Strong("Rental Type: "),
                                    html.Span("Waiting for data...", className="text-muted"),
                                    html.Br(),
                                    html.Strong("Start Date: "),
                                    html.Span("Waiting for data...", className="text-muted"),
                                ],
                                md=6,
                            ),
                        ]
                    )
                ]
            ),
        ],
        className="mb-3",
    )

def create_validation_card(title, result, is_compliant=None):
    """Create a validation result card"""
    if result is None:
        return dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H5(title, className="card-title"),
                        html.P("No validation performed", className="card-text text-muted"),
                    ]
                )
            ],
            className="mb-3",
        )

    # Determine card color based on compliance
    if hasattr(result, "should_be_checked"):
        if result.should_be_checked:
            card_color = "warning"
            icon = "⚠️"
            status = "Requires Review"
        else:
            card_color = "success"
            icon = "✅"
            status = "Compliant"
    else:
        card_color = "info"
        icon = "ℹ️"
        status = "Checked"

    description = result.description if hasattr(result, "description") else str(result)
    references = result.references if hasattr(result, "references") else {}

    # Create references text
    references_text = ""
    if references:
        refs = [f"{para} (Page {page})" for para, page in references.items()]
        references_text = "References: " + ", ".join(refs)

    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.H5(
                        [
                            icon + " " + title,
                            dbc.Badge(status, color=card_color, className="ms-2"),
                        ],
                        className="mb-0",
                    )
                ]
            ),
            dbc.CardBody(
                [
                    html.P(description, className="card-text"),
                    html.Small(references_text, className="text-muted")
                    if references_text
                    else None,
                ]
            ),
        ],
        color=card_color,
        outline=True,
        className="mb-3",
    )

def create_contract_summary_filled(contract_info):
    """Create filled contract summary card"""
    return dbc.Card(
        [
            dbc.CardHeader([html.H5("📋 Contract Summary", className="mb-0")]),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Strong("Landlord: "),
                                    contract_info.landlord,
                                    html.Br(),
                                    html.Strong("Tenant: "),
                                    contract_info.tenant,
                                    html.Br(),
                                    html.Strong("Property: "),
                                    contract_info.property_address,
                                    html.Br(),
                                    html.Strong("Monthly Rent: "),
                                    contract_info.monthly_rental_amount,
                                ],
                                md=6,
                            ),
                            dbc.Col(
                                [
                                    html.Strong("Deposit: "),
                                    contract_info.deposit_amount,
                                    html.Br(),
                                    html.Strong("Lease Duration: "),
                                    contract_info.lease_duration,
                                    html.Br(),
                                    html.Strong("Rental Type: "),
                                    contract_info.rental_type,
                                    html.Br(),
                                    html.Strong("Start Date: "),
                                    contract_info.lease_start_date,
                                ],
                                md=6,
                            ),
                        ]
                    )
                ]
            ),
        ],
        className="mb-3",
    )