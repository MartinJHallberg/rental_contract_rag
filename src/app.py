import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import base64
import io
import tempfile
import os
from pathlib import Path

# Import your existing modules
from contract_loader import load_contract_and_extract_info, ContractInfo
from rag import RAGChain, validate_deposit_amount, validate_termination_conditions, validate_price_adjustments

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Initialize RAG chain
rag_chain = RAGChain()

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Rental Contract Validator", className="text-center mb-4"),
            html.P("Upload a rental contract PDF to validate it against Danish rental law.", 
                   className="text-center text-muted mb-4")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Upload Contract", className="card-title"),
                    dcc.Upload(
                        id='upload-contract',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select a PDF File')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        multiple=False,
                        accept='.pdf'
                    ),
                    html.Div(id='upload-status', className="mt-3"),
                    dbc.Button(
                        "Validate Contract", 
                        id="validate-button", 
                        color="primary", 
                        className="mt-3",
                        disabled=True
                    )
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Loading spinner
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading",
                type="default",
                children=html.Div(id="loading-output")
            )
        ])
    ]),
    
    # Validation results
    html.Div(id='validation-results')
    
], fluid=True)


def create_validation_card(title, result, is_compliant=None):
    """Create a validation result card"""
    
    if result is None:
        return dbc.Card([
            dbc.CardBody([
                html.H5(title, className="card-title"),
                html.P("No validation performed", className="card-text text-muted")
            ])
        ], className="mb-3")
    
    # Determine card color based on compliance
    if hasattr(result, 'should_be_checked'):
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
    
    description = result.description if hasattr(result, 'description') else str(result)
    references = result.references if hasattr(result, 'references') else {}
    
    # Create references text
    references_text = ""
    if references:
        refs = [f"{para} (Page {page})" for para, page in references.items()]
        references_text = "References: " + ", ".join(refs)
    
    return dbc.Card([
        dbc.CardHeader([
            html.H5([
                icon + " " + title,
                dbc.Badge(status, color=card_color, className="ms-2")
            ], className="mb-0")
        ]),
        dbc.CardBody([
            html.P(description, className="card-text"),
            html.Small(references_text, className="text-muted") if references_text else None
        ])
    ], color=card_color, outline=True, className="mb-3")


@callback(
    [Output('upload-status', 'children'),
     Output('validate-button', 'disabled')],
    [Input('upload-contract', 'contents')],
    [State('upload-contract', 'filename')]
)
def update_upload_status(contents, filename):
    """Update upload status and enable/disable validate button"""
    if contents is None:
        return "", True
    
    if filename and filename.endswith('.pdf'):
        return dbc.Alert(
            f"✅ File uploaded: {filename}", 
            color="success", 
            dismissable=True
        ), False
    else:
        return dbc.Alert(
            "❌ Please upload a PDF file", 
            color="danger", 
            dismissable=True
        ), True


@callback(
    [Output('validation-results', 'children'),
     Output('loading-output', 'children')],
    [Input('validate-button', 'n_clicks')],
    [State('upload-contract', 'contents'),
     State('upload-contract', 'filename')],
    prevent_initial_call=True
)
def validate_contract(n_clicks, contents, filename):
    """Validate the uploaded contract"""
    if n_clicks is None or contents is None:
        raise PreventUpdate
    
    try:
        # Decode the uploaded file
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(decoded)
            tmp_file_path = tmp_file.name
        
        try:
            # Extract contract information
            contract_info = load_contract_and_extract_info(tmp_file_path)
            
            # Perform validations
            deposit_result = validate_deposit_amount(
                rag_chain, 
                contract_info.deposit_amount, 
                contract_info.monthly_rental_amount
            )
            
            termination_result = validate_termination_conditions(
                rag_chain, 
                contract_info.termination_conditions
            )
            
            price_adjustment_result = validate_price_adjustments(
                rag_chain, 
                contract_info.price_adjustments
            )
            
            # Create result cards
            results = dbc.Row([
                dbc.Col([
                    html.H3("Validation Results", className="mb-4"),
                    
                    create_validation_card(
                        "Deposit Amount Validation", 
                        deposit_result
                    ),
                    
                    create_validation_card(
                        "Termination Conditions Validation", 
                        termination_result
                    ),
                    
                    create_validation_card(
                        "Price Adjustment Validation", 
                        price_adjustment_result
                    ),
                    
                    # Contract summary
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("📋 Contract Summary", className="mb-0")
                        ]),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Strong("Landlord: "), contract_info.landlord,
                                    html.Br(),
                                    html.Strong("Tenant: "), contract_info.tenant,
                                    html.Br(),
                                    html.Strong("Property: "), contract_info.property_address,
                                    html.Br(),
                                    html.Strong("Monthly Rent: "), contract_info.monthly_rental_amount,
                                ], md=6),
                                dbc.Col([
                                    html.Strong("Deposit: "), contract_info.deposit_amount,
                                    html.Br(),
                                    html.Strong("Lease Duration: "), contract_info.lease_duration,
                                    html.Br(),
                                    html.Strong("Rental Type: "), contract_info.rental_type,
                                    html.Br(),
                                    html.Strong("Start Date: "), contract_info.lease_start_date,
                                ], md=6)
                            ])
                        ])
                    ], className="mb-3")
                    
                ], width=12)
            ])
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
        
        return results, ""
        
    except Exception as e:
        error_alert = dbc.Alert([
            html.H4("❌ Validation Error", className="alert-heading"),
            html.P(f"An error occurred while processing the contract: {str(e)}"),
            html.Hr(),
            html.P("Please ensure the uploaded file is a valid PDF contract.", className="mb-0")
        ], color="danger")
        
        return error_alert, ""


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
