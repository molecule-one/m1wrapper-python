# Molecule One Batch Scoring API Wrapper

## Usage:

### Installation:

```
pip install git+https://github.com/molecule-one/m1wrapper-python
```
NOTE: make sure to install package to the intended python environment.

### Initialization:
```py
from m1wrapper import MoleculeOneWrapper
m1wrapper = MoleculeOneWrapper(token)
```
- *token*: API token you'll need to authorize in our system. You can get
  generate yours at https://app.molecule.one/dashboard/user/api-tokens
- *baseUrl* (optional): URI of the batch scoring service. Defaults to Molecule One's public
  server, but you will need to provide custom value if you're using a dedicated solution.

### Running batch scoring request:

```py
search = m1wrapper.run_batch_search(
    targets=['cc', 'O=C(Nc1cc(Nc2nc(-c3cnccc3)ccn2)c(cc1)C)c3ccc(cc3)CN3CCN(CC3)C'],
    parameters={'exploratory_search': False, 'detail_level': 'score'}
)
```
- *targets*: list of target compounds in SMILES format
- *parameters* (optional): additional configuration for your batch
  scoring request. See [Batch Scoring API](https://github.com/molecule-one/api/blob/master/batch-scoring.md) for more information.


### Getting exisiting scoring request by id:
```py
search = m1wrapper.get_batch_search(id)
```

### Checking if your scoring request processing is finished:
```py
search.is_finished()
```

### Checking full search status:
```py
status = search.get_status()
```
In response, you’ll get information about your batch scoring processing progress, i.e.:
`{"queued":92,"running":4,"finished":104,"error":0}`

### Getting partial results:
Results are made available as soon as they are processed. This method
provided a way to start working with some of your results without waiting until all targets are processed.
This usually means implementing some kind of polling/scheduling on your side.
```py
results = search.get_partial_results(precision=5, only=["targetSmiles, "result"])
```
- *precision* (optional): format the floating point scores returned by the system (certainty, result, price) to given number of significant digits.
- *only* (optional): fetch only a subset of values. Defaults to
  all values.

Returns JSON object of the following shape:
```json
    [
      {
        "targetSmiles": "Cc1ccc(cc1Nc2nccc(n2)c3cccnc3)NC(=O)c4ccc(cc4)CN5CCN(CC5)C",
        "status": "ok",
        "result": "7.53",
        "certainty": "0.581",
        "price": "5230",
        "reactionCount": 5,
        "timedOut": false
      },
    ...
    ]
```
See [Batch Scoring API](https://github.com/molecule-one/api/blob/master/batch-scoring.md) for a full explaination of returned fields.

### Getting complete results:
```py
results = search.get_results(precision=5, only=["targetSmiles, "result"])
```
If you don't want to implement scheduling on your own, this method
provides a simple way to wait until all targets are processed (sending periodical checks using
`search.is_finished()`), and execute only when all results are available. It's a
blocking operation.
Parameters and returned JSON are the same as with `get_partial_results()`.

### Deleting your data:
```py
m1wrapper.delete_batch_search(search.search_id)
```
