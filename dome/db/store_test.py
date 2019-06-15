import sys, os
sys.path.append(os.path.abspath(os.path.join('redland', 'bindings', 'python')))

import RDF

storage = RDF.Storage(storage_name="sqlite", name='domegraph', options_string="new='true'")
model = RDF.Model(storage)

s1 = RDF.Statement(RDF.Uri("http://example.org/resource/princenhage"), RDF.Uri("http://example.org/ontology#precipitation"), '69')

model.append(s1)

for statements in model:
    print(statements)