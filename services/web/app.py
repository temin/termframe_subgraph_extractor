import os

from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    redirect,
    url_for
)

from flask_socketio import SocketIO
from flask_restx import Api, Resource, fields, abort
import networkx as nx

import utils

import werkzeug
from werkzeug.middleware.proxy_fix import ProxyFix
werkzeug.cached_property = werkzeug.utils.cached_property


BASEDIR = os.path.dirname(__file__)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0',
          title='API services',
          description='TermFrame network REST API')
ns = api.namespace('rest_api', description='REST services API')
socketio = SocketIO(app)

all_graphs = {'sl': nx.read_gpickle(os.path.join(BASEDIR, 'networks/sl/network.pickle')),
              'en': nx.read_gpickle(os.path.join(BASEDIR, 'networks/en/network.pickle')),
              'hr': nx.read_gpickle(os.path.join(BASEDIR, 'networks/hr/network.pickle'))}

node_field = api.model('Node', {
    'id': fields.Integer,
    'label': fields.String,
    'group': fields.String
})
edge_field = api.model('Edge', {
    'from': fields.Integer,
    'to': fields.Integer,
    'label': fields.String
})

extract_input = api.model('SearchInput', {
    'language': fields.String(required=True, description='language (en, sl, hr)'),
    'nodes': fields.List(fields.String, required=True, description='list of query nodes')
})
extract_output = api.model('SearchOutput', {
    'nodes': fields.List(fields.Nested(node_field), description='node descriptions'),
    'edges': fields.List(fields.Nested(edge_field), description='edge descriptions'),
})

suggest_input = api.model('SuggestInput', {
    'language': fields.String(required=True, description='language (en, sl, hr)'),
    'text': fields.String(required=True, description='query text'),
    'k': fields.Integer(required=True, default=5, description='desired number of suggestions'),
})
suggest_output = api.model('SuggestOutput', {
    'nodes': fields.List(fields.String, description='best matching nodes'),
})


@ns.route('/extract_subgraph')
class SubgraphExtractor(Resource):
    @ns.doc('search for node and return neighbour subgraph')
    @ns.expect(extract_input, validate=True)
    @ns.marshal_with(extract_output)
    def post(self):
        lang = api.payload['language']
        if lang not in ['sl', 'en', 'hr']:
            abort(400, 'Language parameter must be one of {en, sl, hr}')
        g = all_graphs[lang]
        subg = utils.extract_subgraph(g, api.payload['nodes'], k=2, ignoreDirection=False, fuzzySearch=False)
        return utils.graph2json(subg)


@ns.route('/find_matching_nodes')
class NodeFinder(Resource):
    @ns.doc('find fuzzy matched nodes')
    @ns.expect(suggest_input, validate=True)
    @ns.marshal_with(suggest_output)
    def post(self):
        lang = api.payload['language']
        if lang not in ['sl', 'en', 'hr']:
            abort(400, 'Language parameter must be one of {en, sl, hr}')
        g = all_graphs[lang]
        return {'nodes': utils.best_matching_nodes(g, api.payload['text'], k=api.payload['k'])}


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, use_reloader=True)
