"""Dash callbacks for the app"""

import dash
from dash import Input, Output, State
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
        [
            Output("current-filepath", "children"),
            Output("upload-status", "children"),
            Output("validate-button", "disabled"),
        ],
        [Input(f"load-{contract['id']}", "n_clicks") for contract in SAMPLE_CONTRACTS],
        prevent_initial_call=True,
    )
    def load_sample_contract(*n_clicks_list):
        """Load a sample contract when its button is clicked"""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        contract_id = button_id.replace("load-", "")
        selected_contract = next(
            (c for c in SAMPLE_CONTRACTS if c["id"] == contract_id), None
        )

        if selected_contract is None:
            raise PreventUpdate

        file_path = get_sample_filepath(selected_contract["filename"])

        if file_path is None:
            return (
                "",
                dbc.Alert(
                    f"❌ Sample contract file '{selected_contract['filename']}' not found",
                    color="danger",
                    dismissable=True,
                ),
                True,
            )

        return (
            file_path,
            dbc.Alert(
                f"✅ Sample contract loaded: {selected_contract['title']}",
                color="success",
                dismissable=True,
            ),
            False,
        )

    @app.callback(
        [
            Output("upload-status", "children", allow_duplicate=True),
            Output("validate-button", "disabled", allow_duplicate=True),
        ],
        [Input("upload-contract", "contents")],
        [State("upload-contract", "filename"), State("current-filepath", "children")],
        prevent_initial_call=True,
    )
    def update_upload_status(contents, filename, current_filepath):
        """Update upload status and enable/disable validate button"""
        if current_filepath and Path(current_filepath).exists():
            return dbc.Alert(
                f"✅ Sample contract ready: {Path(current_filepath).name}",
                color="success",
                dismissable=True,
            ), False

        if contents is None:
            return "", True

        if filename and filename.endswith(".pdf"):
            return dbc.Alert(
                f"✅ File ready: {filename}", color="success", dismissable=True
            ), False
        else:
            return dbc.Alert(
                "❌ Please upload a PDF file", color="danger", dismissable=True
            ), True

    @app.callback(
        [
            Output("contract-summary", "children"),
            Output("deposit-validation", "children"),
            Output("prepaid-validation", "children"),
            Output("termination-validation", "children"),
            Output("price-validation", "children"),
            Output("loading-output", "children"),
        ],
        [Input("validate-button", "n_clicks")],
        [
            State("upload-contract", "contents"),
            State("upload-contract", "filename"),
            State("current-filepath", "children"),
        ],
        prevent_initial_call=True,
    )
    def validate_contract(n_clicks, contents, filename, current_filepath):
        """Validate the uploaded contract and update individual cards"""
        if n_clicks is None:
            raise PreventUpdate

        try:
            # Determine the file path to use
            if current_filepath and Path(current_filepath).exists():
                file_path = current_filepath
            elif contents is not None:
                file_path = get_cached_file_path(contents, filename)
            else:
                raise ValueError("No file available for validation")

            # Validate the contract
            results = validate_contract_file(rag_chain, file_path)

            return (
                create_contract_summary_filled(results["contract_info"]),
                create_validation_card(
                    "Deposit Amount Validation", results["deposit_result"]
                ),
                create_validation_card(
                    "Prepaid Rent Validation", results["prepaid_result"]
                ),
                create_validation_card(
                    "Termination Conditions Validation", results["termination_result"]
                ),
                create_validation_card(
                    "Price Adjustment Validation", results["price_adjustment_result"]
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
                error_card,
                create_placeholder_card("Deposit Amount Validation", "💰"),
                create_placeholder_card("Termination Conditions Validation", "📋"),
                create_placeholder_card("Price Adjustment Validation", "💹"),
                "",
            )
