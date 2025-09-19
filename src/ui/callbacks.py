"""Dash callbacks for the app"""

import dash
from dash import Input, Output, State, dcc
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from pathlib import Path
from dash import html

from ui.contracts import SAMPLE_CONTRACTS
from services.file_service import get_cached_file_path, get_sample_filepath
from services.validation_service import validate_contract_file
from ui.components import (
    create_validation_card,
    create_contract_summary_filled,
    create_placeholder_card,
)


def register_callbacks(app, rag_chain):
    """Register all callbacks for the app"""

    @app.callback(
        Output("contract-store", "data"),
        [Input("upload-contract", "contents"),
         Input("clear-upload-button", "n_clicks")] + 
        [Input(f"load-{contract['id']}", "n_clicks") for contract in SAMPLE_CONTRACTS],
        [State("upload-contract", "filename")],
        prevent_initial_call=True,
    )
    def load_contract(contents, clear_clicks, *args):
        """Central callback to handle any contract loading (upload or sample)"""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        filename = args[-1]  # Last argument is the filename state

        # Handle clear button
        if trigger_id == "clear-upload-button":
            return None

        # Handle sample contract loading
        if trigger_id.startswith("load-"):
            contract_id = trigger_id.replace("load-", "")
            selected_contract = next(
                (c for c in SAMPLE_CONTRACTS if c["id"] == contract_id), None
            )
            
            if selected_contract:
                file_path = get_sample_filepath(selected_contract["filename"])
                if file_path:
                    return {
                        "type": "sample",
                        "filepath": file_path,
                        "title": selected_contract["title"],
                        "filename": selected_contract["filename"]
                    }
                else:
                    return {
                        "type": "error",
                        "message": f"Sample contract file '{selected_contract['filename']}' not found"
                    }

        # Handle upload
        elif trigger_id == "upload-contract":
            if contents is None:
                # Upload was cleared
                return None
            
            if filename and filename.endswith(".pdf"):
                return {
                    "type": "upload",
                    "contents": contents,
                    "filename": filename
                }
            else:
                return {
                    "type": "error",
                    "message": "Please upload a PDF file"
                }

        return None

    @app.callback(
        [
            Output("upload-status", "children"),
            Output("validate-button", "disabled"),
            Output("clear-upload-button", "disabled"),
            Output("validation-results-container", "style"),
            Output("validation-results-container", "className"),
        ],
        [Input("contract-store", "data")],
    )
    def update_ui_state(contract_data):
        """Update UI based on contract state"""
        if contract_data is None:
            # No contract loaded
            return (
                "",
                True,  # Validate button disabled
                True,  # Clear button disabled
                {
                    "opacity": "0.4",
                    "pointer-events": "none",
                    "transition": "opacity 0.3s ease",
                },
                "validation-results-disabled"
            )
        
        if contract_data.get("type") == "error":
            return (
                dbc.Alert(f"❌ {contract_data['message']}", color="danger", dismissable=True),
                True,  # Validate button disabled
                True,  # Clear button disabled
                {
                    "opacity": "0.4",
                    "pointer-events": "none",
                    "transition": "opacity 0.3s ease",
                },
                "validation-results-disabled"
            )
        
        elif contract_data.get("type") == "sample":
            return (
                dbc.Alert(f"✅ Sample contract loaded: {contract_data['title']}", color="success", dismissable=False),
                False,  # Validate button enabled
                False,  # Clear button enabled
                {
                    "opacity": "0.4",
                    "pointer-events": "none",
                    "transition": "opacity 0.3s ease",
                },
                "validation-results-disabled"
            )
        
        elif contract_data.get("type") == "upload":
            return (
                dbc.Alert(f"✅ File ready: {contract_data['filename']}", color="success", dismissable=True),
                False,  # Validate button enabled
                False,  # Clear button enabled
                {
                    "opacity": "0.4",
                    "pointer-events": "none",
                    "transition": "opacity 0.3s ease",
                },
                "validation-results-disabled"
            )
        
        return "", True, True, {}, ""

    @app.callback(
        [
            Output("contract-summary", "children"),
            Output("deposit-validation", "children"),
            Output("prepaid-validation", "children"),
            Output("termination-validation", "children"),
            Output("price-validation", "children"),
            Output("loading-output", "children"),
            Output("validation-results-container", "style", allow_duplicate=True),
            Output("validation-results-container", "className", allow_duplicate=True),
        ],
        [Input("validate-button", "n_clicks")],
        [State("contract-store", "data")],
        prevent_initial_call=True,
    )
    def validate_contract(n_clicks, contract_data):
        """Validate the loaded contract"""
        if n_clicks is None or contract_data is None:
            raise PreventUpdate

        try:
            # Get file path based on contract type
            if contract_data.get("type") == "sample":
                file_path = contract_data["filepath"]
            elif contract_data.get("type") == "upload":
                file_path = get_cached_file_path(contract_data["contents"], contract_data["filename"])
            else:
                raise ValueError("No valid contract loaded")

            # Validate the contract
            results = validate_contract_file(rag_chain, file_path)

            return (
                create_contract_summary_filled(results["contract_info"]),
                create_validation_card("Deposit Amount Validation", results["deposit_result"]),
                create_validation_card("Prepaid Rent Validation", results["prepaid_result"]),
                create_validation_card("Termination Conditions Validation", results["termination_result"]),
                create_validation_card("Price Adjustment Validation", results["price_adjustment_result"]),
                "",  # Clear loading
                {
                    "opacity": "1",
                    "pointer-events": "auto",
                    "transition": "all 0.3s ease",
                },
                ""
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
                error_card,
                create_placeholder_card("Deposit Amount Validation", "💰"),
                create_placeholder_card("Prepaid Rent Validation", "💰"),
                create_placeholder_card("Termination Conditions Validation", "📋"),
                create_placeholder_card("Price Adjustment Validation", "💹"),
                "",
                {
                    "opacity": "0.4",
                    "pointer-events": "none",
                    "transition": "opacity 0.3s ease",
                },
                "validation-results-disabled"
            )
