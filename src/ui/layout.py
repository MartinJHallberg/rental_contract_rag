"""App layout and structure"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from ui.contracts import SAMPLE_CONTRACTS
from ui.components import (
    create_sample_contract_card,
    create_placeholder_card,
    create_contract_summary_placeholder,
)


def create_layout():
    """Create the main app layout"""
    return dbc.Container(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1(
                                "Rental Contract Validator",
                                className="text-center mb-4",
                            ),
                            html.P(
                                "Upload a rental contract PDF or try our sample contracts to validate against Danish rental law.",
                                className="text-center text-muted mb-4",
                            ),
                        ]
                    )
                ]
            ),
            # Main content - split layout
            dbc.Row(
                [
                    # Left side - File upload and sample contracts
                    dbc.Col(
                        [
                            _create_file_upload_section(),
                            _create_sample_contracts_section(),
                        ],
                        md=4,
                    ),
                    # Right side - Validation results
                    dbc.Col(
                        [
                            _create_validation_results_section(),
                        ],
                        md=8,
                    ),
                ],
                className="mb-4",
            ),
        ],
        fluid=True,
    )


def _create_sample_contracts_section():
    """Create the sample contracts section"""
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H5("📄 Sample Contracts", className="card-title"),
                    html.P(
                        html.B(
                            "Try these example contracts to see how the validator works"
                        ),
                        className="card-text small text-muted mb-3",
                    ),
                    html.Div(
                        [
                            create_sample_contract_card(contract)
                            for contract in SAMPLE_CONTRACTS
                        ]
                    ),
                ]
            )
        ],
        className="mb-4",
    )


def _create_file_upload_section():
    """Create the file upload section"""
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H5("📤 Upload Your Contract", className="card-title"),
                    dcc.Upload(
                        id="upload-contract",
                        children=html.Div(
                            [
                                "Drag and Drop or ",
                                html.A("Select a PDF File"),
                            ]
                        ),
                        style={
                            "width": "100%",
                            "height": "100px",
                            "lineHeight": "100px",
                            "borderWidth": "2px",
                            "borderStyle": "dashed",
                            "borderRadius": "10px",
                            "textAlign": "center",
                            "margin": "10px 0",
                            "backgroundColor": "#f8f9fa",
                        },
                        multiple=False,
                        accept=".pdf",
                    ),
                    html.Div(id="upload-status", className="mt-3"),
                    html.Div(id="current-filepath", style={"display": "none"}),
                    dbc.Button(
                        "Validate Contract",
                        id="validate-button",
                        color="primary",
                        size="lg",
                        className="mt-3 w-100",
                        disabled=True,
                    ),
                ]
            )
        ]
    )


def _create_validation_results_section():
    """Create the validation results section"""
    return html.Div(
        [
            dcc.Loading(
                id="loading",
                type="default",
                children=html.Div(id="loading-output"),
            ),
            html.Div(
                id="contract-summary",
                children=[create_contract_summary_placeholder()],
            ),
            html.Div(
                id="deposit-validation",
                children=[create_placeholder_card("Deposit Amount Validation", "💰")],
            ),
            html.Div(
                id="prepaid-validation",
                children=[create_placeholder_card("Prepaid Rent Validation", "💰")],
            ),
            html.Div(
                id="termination-validation",
                children=[
                    create_placeholder_card("Termination Conditions Validation", "📋")
                ],
            ),
            html.Div(
                id="price-validation",
                children=[create_placeholder_card("Price Adjustment Validation", "💹")],
            ),
        ]
    )
