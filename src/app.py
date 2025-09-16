import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import base64
import os
import hashlib
from pathlib import Path

# Import your existing modules
from config import CACHE_DIR
from contract_loader import load_contract_and_extract_info
from rag import (
    RAGChain,
    validate_deposit_amount,
    validate_termination_conditions,
    validate_price_adjustments,
)

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Initialize RAG chain
rag_chain = RAGChain()

# Create cache directory for uploaded files
CACHE_DIR.mkdir(exist_ok=True, parents=True)

# Sample contracts configuration
SAMPLE_CONTRACTS = [
    {
        "id": "contract_everything_correct",
        "title": "✅ Compliant Contract",
        "description": "A rental contract that follows all Danish rental law requirements.",
        "filename": "contract_everything_correct.pdf",
        "color": "success"
    },
    {
        "id": "contract_incorrect_deposit",
        "title": "⚠️ Incorrect Deposit",
        "description": "A contract with deposit amount issues that violate Danish rental law.",
        "filename": "contract_incorrect_deposit.pdf",
        "color": "warning"
    }
]


def get_cached_file_path(contents, filename):
    """Generate a cached file path based on filename and content hash"""
    # Decode the uploaded file
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    # Create hash of file content for uniqueness
    content_hash = hashlib.md5(decoded).hexdigest()[:8]

    # Clean filename (remove special characters, keep extension)
    clean_filename = "".join(c for c in filename if c.isalnum() or c in ".-_")
    name_without_ext = Path(clean_filename).stem
    ext = Path(clean_filename).suffix

    # Create cached filename: originalname_hash.pdf
    cached_filename = f"{name_without_ext}_{content_hash}{ext}"
    cached_file_path = CACHE_DIR / cached_filename

    return str(cached_file_path)


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


# Updated app layout with sample contracts
app.layout = dbc.Container(
    [
        # Header
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Rental Contract Validator", className="text-center mb-4"
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
                        # Sample Contracts Section
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H5("📁 Sample Contracts", className="card-title"),
                                        html.P(
                                            "Try these example contracts to see how the validator works:",
                                            className="card-text small text-muted mb-3"
                                        ),
                                        html.Div([
                                            create_sample_contract_card(contract)
                                            for contract in SAMPLE_CONTRACTS
                                        ]),
                                    ]
                                )
                            ],
                            className="mb-4"
                        ),
                        
                        # File Upload Section
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H5(
                                            "📤 Upload Your Contract", className="card-title"
                                        ),
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
                                        # Hidden div to store current filename
                                        html.Div(id="current-filename", style={"display": "none"}),
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
                    ],
                    md=4,
                ),
                # Right side - Validation results (pre-created with placeholders)
                dbc.Col(
                    [
                        html.H4("Validation Results", className="mb-4"),
                        # Loading spinner
                        dcc.Loading(
                            id="loading",
                            type="default",
                            children=html.Div(id="loading-output"),
                        ),
                        # Contract Summary (placeholder)
                        html.Div(
                            id="contract-summary",
                            children=[create_contract_summary_placeholder()],
                        ),
                        # Validation cards (placeholders)
                        html.Div(
                            id="deposit-validation",
                            children=[
                                create_placeholder_card(
                                    "Deposit Amount Validation", "💰"
                                )
                            ],
                        ),
                        html.Div(
                            id="termination-validation",
                            children=[
                                create_placeholder_card(
                                    "Termination Conditions Validation", "📋"
                                )
                            ],
                        ),
                        html.Div(
                            id="price-validation",
                            children=[
                                create_placeholder_card(
                                    "Price Adjustment Validation", "💹"
                                )
                            ],
                        ),
                    ],
                    md=8,
                ),
            ],
            className="mb-4",
        ),
    ],
    fluid=True,
)


def create_validation_card(title, result, is_compliant=None):
    """Create a validation result card"""

    if result is None:
        return dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H5(title, className="card-title"),
                        html.P(
                            "No validation performed", className="card-text text-muted"
                        ),
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


def load_sample_contract_file(contract_filename):
    """Load a sample contract file and return base64 encoded content"""
    try:

        # Get the directory where this script is located
        script_dir = Path(__file__).parent

        # Look for the file in the data directory
        file_path = script_dir / "data" / contract_filename
        if file_path.exists():
            with open(file_path, "rb") as f:
                file_content = f.read()
            encoded_content = base64.b64encode(file_content).decode()
            return f"data:application/pdf;base64,{encoded_content}"
        
        # If file not found, return None
        return None
    except Exception as e:
        print(f"Error loading sample contract {contract_filename}: {e}")
        return None


# Callback for sample contract loading
@callback(
    [Output("upload-contract", "contents"), 
     Output("current-filename", "children"),
     Output("upload-status", "children"), 
     Output("validate-button", "disabled")],
    [Input(f"load-{contract['id']}", "n_clicks") for contract in SAMPLE_CONTRACTS],
    prevent_initial_call=True,
)
def load_sample_contract(*n_clicks_list):
    """Load a sample contract when its button is clicked"""
    # Determine which button was clicked
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Find the corresponding contract
    contract_id = button_id.replace("load-", "")
    selected_contract = next((c for c in SAMPLE_CONTRACTS if c["id"] == contract_id), None)
    
    if selected_contract is None:
        raise PreventUpdate
    
    # Load the contract file
    file_content = load_sample_contract_file(selected_contract["filename"])
    
    if file_content is None:
        return (
            None,
            "",
            dbc.Alert(
                f"❌ Sample contract file '{selected_contract['filename']}' not found",
                color="danger",
                dismissable=True
            ),
            True
        )
    
    return (
        file_content,
        selected_contract["filename"],
        dbc.Alert(
            f"✅ Sample contract loaded: {selected_contract['title']}", 
            color="success", 
            dismissable=True
        ),
        False
    )


@callback(
    [Output("upload-status", "children", allow_duplicate=True), 
     Output("validate-button", "disabled", allow_duplicate=True)],
    [Input("upload-contract", "contents")],
    [State("upload-contract", "filename"),
     State("current-filename", "children")],
    prevent_initial_call=True,
)
def update_upload_status(contents, filename, current_filename):
    """Update upload status and enable/disable validate button"""
    if contents is None:
        return "", True

    # Use current_filename if available (from sample contracts), otherwise use uploaded filename
    display_filename = current_filename if current_filename else filename
    
    if display_filename and display_filename.endswith(".pdf"):
        return dbc.Alert(
            f"✅ File ready: {display_filename}", color="success", dismissable=True
        ), False
    else:
        return dbc.Alert(
            "❌ Please upload a PDF file", color="danger", dismissable=True
        ), True


@callback(
    [
        Output("contract-summary", "children"),
        Output("deposit-validation", "children"),
        Output("termination-validation", "children"),
        Output("price-validation", "children"),
        Output("loading-output", "children"),
    ],
    [Input("validate-button", "n_clicks")],
    [State("upload-contract", "contents"), 
     State("upload-contract", "filename"),
     State("current-filename", "children")],
    prevent_initial_call=True,
)
def validate_contract(n_clicks, contents, filename, current_filename):
    """Validate the uploaded contract and update individual cards"""
    if n_clicks is None or contents is None:
        raise PreventUpdate

    try:
        # Use current_filename if available (from sample contracts), otherwise use uploaded filename
        display_filename = current_filename if current_filename else filename

        file_path = 
        # Extract contract information (this will use caching from contract_loader)
        contract_info = load_contract_and_extract_info(display_filename)

        # Perform validations
        deposit_result = validate_deposit_amount(
            rag_chain, contract_info.deposit_amount, contract_info.monthly_rental_amount
        )

        termination_result = validate_termination_conditions(
            rag_chain, contract_info.termination_conditions
        )

        price_adjustment_result = validate_price_adjustments(
            rag_chain, contract_info.price_adjustments
        )

        # Return updated components
        return (
            create_contract_summary_filled(contract_info),
            create_validation_card("Deposit Amount Validation", deposit_result),
            create_validation_card(
                "Termination Conditions Validation", termination_result
            ),
            create_validation_card(
                "Price Adjustment Validation", price_adjustment_result
            ),
            "",  # Clear loading
        )

    except Exception as e:
        error_message = f"An error occurred while processing the contract: {str(e)}"
        error_card = dbc.Alert(
            [
                html.H6("❌ Validation Error", className="alert-heading"),
                html.P(error_message),
            ],
            color="danger",
        )

        return (
            error_card,  # contract-summary
            create_placeholder_card(
                "Deposit Amount Validation", "💰"
            ),  # deposit-validation
            create_placeholder_card(
                "Termination Conditions Validation", "📋"
            ),  # termination-validation
            create_placeholder_card(
                "Price Adjustment Validation", "💹"
            ),  # price-validation
            "",  # loading-output
        )


if __name__ == "__main__":
    # Get configuration from environment variables
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    host = os.getenv("DASH_HOST", "0.0.0.0")
    port = int(os.getenv("DASH_PORT", "8050"))

    app.run(debug=debug_mode, host=host, port=port)
