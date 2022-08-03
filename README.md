# networkx_plugin_sparse

PoC to get a plug-in like architecture for dispatching to a backend from networkx. Currently this is controlled via a `dispatch` decorator available in a [branch on my fork](https://github.com/mriduls/networkx/tree/nx-sparse).
This currently just selects the backend according to the type of `WrappedGraph`. There is no interchange to any data format.

A quick example of how this works (make sure the you are working in the correct branch of the fork):

``` python
In [1]: import networkx as nx

In [2]: G = nx.erdos_renyi_graph(1000, 0.4)

In [3]: %%timeit
   ...: nx.pagerank(G)
   ...:
   ...:
285 ms ± 65.9 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)

In [4]: nodelist = list(G)

In [5]: A = nx.to_scipy_sparse_array(G, nodelist=nodelist, dtype=float)

In [6]: G = nx.WrappedSparse(A, nodelist)
   ...:

In [7]: %%timeit
   ...: nx.pagerank(G)
   ...:
   ...:
14.8 ms ± 495 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)

```

The speed up is substaintial, as we have moved the expensive data conversion step out of the `pagerank` algorithm. Now this `WrappedSparse` graph will only work for a tiny minority of algorithms but the user can pass this wrapped class around like it was a normal networkx graph object and no breakage to any API. (assuming enough algorithms are implemented with the specific backend.

The backend classes are implemented at https://github.com/MridulS/networkx/blob/8b57042cd202f835ae0c91bb04ee7d14fa895d6c/networkx/classes/backends.py

The changes required for a networkx algorithm to work with a new backend are minimal. Just a `dispatch` decorator with the algorithm name https://github.com/MridulS/networkx/blob/8b57042cd202f835ae0c91bb04ee7d14fa895d6c/networkx/algorithms/link_analysis/pagerank_alg.py#L9

