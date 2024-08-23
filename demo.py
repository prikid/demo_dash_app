from dash import Dash
import dash_bootstrap_components as dbc
from flask_caching import Cache

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], title="RepLit")
server = app.server

cache = Cache(app.server, config={
    'CACHE_TYPE': 'FileSystemCache',
    'CACHE_DIR': '_cache',
    'CACHE_DEFAULT_TIMEOUT': 300
})

# Initialize layout and callbacks
from layout import layout
from callbacks import register_callbacks

app.config.suppress_callback_exceptions = True

app.layout = layout()

# Register callbacks and pass the cache instance
register_callbacks(app, cache)

if __name__ == '__main__':
    app.run(debug=True)
    # app.server.run(debug=True)
