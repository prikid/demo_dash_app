import logging
import pandas as pd
from dash import Output, Input, no_update, State, dcc, html
from decouple import config
from lib.api_client import ApiClient
from lib.dash_helpers import DashHelpers
import plotly.express as px

client = ApiClient(config('API_BASE_URL'))


def register_callbacks(app, cache):
    @app.callback(
        Output('companies_dropdown', 'options'),
        Output('companies', 'data'),
        Input('page_loaded', 'data'),
    )
    def load_companies(page_loaded):
        companies: dict = client.get("cik_names")
        df = pd.DataFrame.from_dict(companies, orient='index', columns=['name'])
        df = df[df['name'].str.strip() != ''].sort_values(by='name')

        df['value'] = df.index.astype(str)
        df['label'] = df['name'] + " - " + df['value']

        dropdown_options = df[['label', 'value']].to_dict('records')
        return dropdown_options, companies

    @app.callback(
        Output('table_container', 'children'),
        Input('companies_dropdown', 'value'),
        State('companies', 'data'),
        prevent_initial_call=True,
    )
    def load_table(selected_companies, companies):
        if selected_companies is None:
            return no_update

        variables = ['GrossProfit', 'InterestExpense', 'Assets', 'AssetsCurrent']

        data = []
        for cik in selected_companies:
            row = dict(CIK=cik, Name=companies[cik])

            for var in variables:
                params = {'cik': cik, 'tag': var, 'taxonomy': 'us-gaap'}
                try:
                    row[var] = fetch_data(params)
                except Exception as e:
                    logging.error(e)
                    continue

            data.append(row)

        df = pd.DataFrame(data)
        columns, hidden_columns = DashHelpers.getColumnsForDataTable(df)

        # Create DataTable
        data_table = DashHelpers.getHtmlTableFromDf(
            id='table',
            df=df,
            columns=columns,
        )

        # Create Bar Chart
        if not df.empty:
            fig = px.bar(
                df.melt(id_vars=['CIK', 'Name'], value_vars=df.columns.drop(['CIK', 'Name'])),
                x='Name', y='value', color='variable',
                title='Company Financial Data',
                labels={'Name': 'Company name', 'value': 'Amount (USD)', 'variable': 'Financial Metric'},
                barmode='group'
            )
            bar_chart = dcc.Graph(
                id='bar-chart',
                figure=fig
            )
        else:
            bar_chart = html.Div("No data to display in the chart.")

        return html.Div([
            html.Div(data_table, className='mb-4'),
            html.Div(bar_chart)
        ])

    @cache.memoize(300)
    def fetch_data(params):
        print(params)
        company_data = client.get("company_concept", params=params)
        return company_data['units']['USD'][-1]['val']  # get the last one
