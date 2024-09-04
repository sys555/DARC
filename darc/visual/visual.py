import graphistry
import pandas as pd
graphistry.register(api=3, username='ben111', password='leishanzhe')  # Free: hub.graphistry.com
edges = [{'src': 0, 'dst': 1}, {'src': 1, 'dst': 0}, {'src': 1, 'dst': 2}, {'src': 2, 'dst': 1}]

g = graphistry.edges(pd.DataFrame(edges)).bind(source='src', destination='dst').settings(url_params={'play': 1000})

url = g.plot(render=False)
print(url)