from typing import Iterable

import pandas as pd
from dash import html
from dash.dash_table import DataTable
import dash_bootstrap_components as dbc
from pandas.core.dtypes.common import is_numeric_dtype, is_datetime64_any_dtype, is_string_dtype


def get_input_id(callback_context) -> str | dict:
    if callback_context.triggered:
        return callback_context.triggered[0]["prop_id"].split(".")[0]
    return None


def get_triggered_value(callback_context):
    return callback_context.triggered[0]["value"]


def get_triggered_type(callback_context):
    input_id = get_input_id(callback_context)

    if input_id is None:
        return False

    if isinstance(input_id, dict):
        input_id = input_id['type']

    return input_id


def check_triggered_input(callback_context, expected_ids: str | Iterable[str]) -> bool:
    if isinstance(expected_ids, str):
        expected_ids = [expected_ids]

    input_id = get_input_id(callback_context)

    if input_id is None:
        return False

    if isinstance(input_id, dict):
        input_id = input_id['type']

    v = get_triggered_value()
    if (isinstance(v, list)) and not v:
        v = None

    return any(input_id.endswith(exp_id) for exp_id in expected_ids) and v is not None


class DashHelpers:
    @staticmethod
    def getHtmlTableFromDf(df: pd.DataFrame, id: str | dict, show_index=True, select_all_checkbox=False,
                           dbl_click_event_listener: bool = False, **kwargs):
        if show_index:
            df.reset_index(inplace=True)

        kwargs['filter_action'] = kwargs.get('filter_action', 'native')
        kwargs['filter_query'] = kwargs.get('filter_query', '')
        kwargs['sort_action'] = kwargs.get('sort_action', 'native')
        kwargs['page_action'] = kwargs.get('page_action', 'native')
        kwargs['page_current'] = kwargs.get('page_current', 0)
        kwargs['page_size'] = kwargs.get('page_size', 50)

        kwargs['css'] = kwargs.get('css', [])

        if kwargs.get('hidden_columns'):
            kwargs['css'].append({"selector": ".show-hide", "rule": "display: none"})

        kwargs['filter_options'] = kwargs.get('filter_options', {})

        if 'columns' not in kwargs:
            kwargs['columns'], hidden_columns = DashHelpers.getColumnsForDataTable(df)

        if select_all_checkbox:
            if 'style_table' not in kwargs:
                kwargs['style_table'] = {}
            kwargs['style_table'].update({'top': '-1.85rem'})

        select_all_checkbox_style = {'zIndex': 500, 'marginLeft': '0.45rem', 'position': 'relative',
                                     'display': 'inline-block', 'top': '3px'}

        if is_dash_table_menu_open := kwargs.get('export_format') is not None:
            select_all_checkbox_style |= {'top': '2rem'}

        kwargs['style_cell'] = {
                                   'whiteSpace': 'normal',
                                   'height': 'auto',
                                   'textAlign': 'left',
                                   'font-family': "'Lato','Helvetica Neue',Helvetica,Arial,sans-serif",
                                   'font-size': '14px'
                               } | kwargs.get('style_cell', {})

        kwargs['style_header'] = {
                                     'backgroundColor': '#EEEEEE',
                                     'fontWeight': 'bold',
                                     'textAlign': 'center',
                                     'font-family': "'Lato', 'Helvetica Neue', Helvetica, Arial, sans-serif"
                                 } | kwargs.get('style_header', {})

        table = DataTable(
            id=id,
            data=df.to_dict('records'),
            selected_rows=[],
            **kwargs
        )

        # if dbl_click_event_listener:
        #     table = EventListener(
        #         table,
        #         id=f"{id}_dbl_click_event_listener",
        #         events=[
        #             dict(
        #                 event="dblclick",
        #                 props=["target", 'ctrlKey', 'altKey']
        #             )],
        #         logging=False,
        #     )

        return html.Div([
            dbc.Checkbox(
                id=id + "_select_all_checkbox",
                style=select_all_checkbox_style
            ) if select_all_checkbox else '',

            table
        ])

    @staticmethod
    def getColumnsForDataTable(df: pd.DataFrame, columns_extra: dict = None) -> tuple[list, list]:
        def get_column_type(pandas_dtype):
            if is_numeric_dtype(pandas_dtype):
                return 'numeric'
            elif is_datetime64_any_dtype(pandas_dtype):
                return 'datetime'
            elif is_string_dtype(pandas_dtype):
                return 'text'

            return 'any'

        columns = []
        for c_name, c_dtype in zip(df.columns, df.dtypes):
            if c_name == 'id':
                continue

            col = {
                "name": c_name,
                "id": c_name,
                "type": (col_type := get_column_type(c_dtype)),
                "editable": False,

                # the dash datatable has a bug (at Jan 2023) with filtering numeric columns in insensitive mode
                # https://github.com/plotly/dash/issues/1793,
                # so we have to manage this ourselves
                "filter_options": {"case": "sensitive" if col_type == 'numeric' else 'insensitive'}
            }

            if columns_extra is not None and c_name in columns_extra:
                for param_name, param_value in columns_extra[c_name].items():
                    col[param_name] = param_value

            columns.append(col)

        hidden_columns = [c['name'] for c in columns if c['name'].startswith('_')]
        return columns, hidden_columns
