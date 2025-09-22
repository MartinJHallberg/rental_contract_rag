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
                        n_clicks=0,
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
                                    html.Span(
                                        "Waiting for data...", className="text-muted"
                                    ),
                                    html.Br(),
                                    html.Strong("Tenant: "),
                                    html.Span(
                                        "Waiting for data...", className="text-muted"
                                    ),
                                    html.Br(),
                                    html.Strong("Property: "),
                                    html.Span(
                                        "Waiting for data...", className="text-muted"
                                    ),
                                    html.Br(),
                                    html.Strong("Monthly Rent: "),
                                    html.Span(
                                        "Waiting for data...", className="text-muted"
                                    ),
                                ],
                                md=6,
                            ),
                            dbc.Col(
                                [
                                    html.Strong("Deposit: "),
                                    html.Span(
                                        "Waiting for data...", className="text-muted"
                                    ),
                                    html.Br(),
                                    html.Strong("Lease Duration: "),
                                    html.Span(
                                        "Waiting for data...", className="text-muted"
                                    ),
                                    html.Br(),
                                    html.Strong("Rental Type: "),
                                    html.Span(
                                        "Waiting for data...", className="text-muted"
                                    ),
                                    html.Br(),
                                    html.Strong("Start Date: "),
                                    html.Span(
                                        "Waiting for data...", className="text-muted"
                                    ),
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
    """Create a validation result accordion"""
    if result is None:
        return dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        html.P(
                            "No validation performed", className="text-muted"
                        ),
                    ],
                    title=f"📋 {title}",
                    item_id=f"accordion-{title.lower().replace(' ', '-')}",
                )
            ],
            start_collapsed=True,
            className="mb-3",
        )

    # Determine status based on compliance
    if hasattr(result, "should_be_checked"):
        if result.should_be_checked:
            icon = "⚠️"
            status = "Requires Review"
            header_class = "text-warning"
            badge_color = "warning"
        else:
            icon = "✅"
            status = "Compliant"
            header_class = "text-success"
            badge_color = "success"
    else:
        icon = "ℹ️"
        status = "Checked"
        header_class = "text-info"
        badge_color = "info"

    description = result.description if hasattr(result, "description") else str(result)
    references = result.references if hasattr(result, "references") else {}

    # Create references content
    accordion_content = [html.P(description, className="mb-2")]
    
    if references:
        accordion_content.extend([
            html.Hr(),
            html.H6("📖 References:", className="mt-3 mb-2"),
            html.Ul([
                html.Li([
                    html.Strong(f"Page {page}: "),
                    html.Span(para)
                ], className="mb-1") for para, page in references.items()
            ], className="small")
        ])

    return dbc.Accordion(
        [
            dbc.AccordionItem(
                accordion_content,
                title=html.Div([
                    html.Span(f"{icon} {title}", className=header_class),
                    dbc.Badge(status, color=badge_color, className="ms-2 float-end"),
                ]),
                item_id=f"accordion-{title.lower().replace(' ', '-')}",
            )
        ],
        start_collapsed=True,
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
                                    html.Span(str(contract_info.landlord)),
                                    html.Br(),
                                    html.Strong("Tenant: "),
                                    html.Span(str(contract_info.tenant)),
                                    html.Br(),
                                    html.Strong("Property: "),
                                    html.Span(str(contract_info.property_address)),
                                    html.Br(),
                                    html.Strong("Monthly Rent: "),
                                    html.Span(str(contract_info.monthly_rental_amount)),
                                ],
                                md=6,
                            ),
                            dbc.Col(
                                [
                                    html.Strong("Deposit: "),
                                    html.Span(str(contract_info.deposit_amount)),
                                    html.Br(),
                                    html.Strong("Lease Duration: "),
                                    html.Span(str(contract_info.lease_duration)),
                                    html.Br(),
                                    html.Strong("Rental Type: "),
                                    html.Span(str(contract_info.rental_type)),
                                    html.Br(),
                                    html.Strong("Start Date: "),
                                    html.Span(str(contract_info.lease_start_date)),
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
