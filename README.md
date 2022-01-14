# Molecule One Batch Scoring API Wrapper

## Usage:

### Installation:

```
pip install git+https://github.com/molecule-one/m1wrapper-python
```

### Initialization:

```py
from m1wrapper import MoleculeOneWrapper
m1wrapper = MoleculeOneWrapper(api_token, 'https://app.molecule.one')
```

- _api_token_: API token you'll need to authorize in our system. You can
  generate yours at https://app.molecule.one/dashboard/user/api-tokens
- _api_base_url_ (optional): URI of the batch scoring service. Defaults to Molecule One's public
  server, but you will need to provide custom value if you're using a dedicated solution.

### Getting a list of batch scoring requests:

```py
searches = m1wrapper.list_batch_searches()
```

### Running new batch scoring request:

```py
search = m1wrapper.run_batch_search(
    targets=['cc', 'O=C(Nc1cc(Nc2nc(-c3cnccc3)ccn2)c(cc1)C)c3ccc(cc3)CN3CCN(CC3)C'],
    parameters={'model': 'gat'}
)
```

- _targets_: list of target compounds in SMILES format
- _parameters_ (optional): additional configuration for your batch
  scoring request. See [Batch Scoring API](https://github.com/molecule-one/api/blob/master/api-v2.md) for more information.
- _detail_level_ (optional): [detail level of the batch request](#batch-scoring-detail-level)
- _priority_ (optional): [priority of the batch request](#batch-scoring-priorities)
- _invalid_target_strategy_ (optional): if set to `InvalidTargetStrategy.PASS`, targets that cannot be canonized by our SMILES parser won't cause the whole batch request to be rejected. Defaults to `InvalidTargetStrategy.REJECT`.
- _starting_materials_ (optional): list of available compounds in SMILES format
- _name_ (optional): name of your batch request

### Batch scoring detail level

Detail level determines how much information about each target synthesis you'll get. We define it as a `DetailLevel` enum with two variants:

- `DetailLevel.SCORE` (default) - useful when you're not interested in full synthesis json/UI preview, but only numerical values
- `DetailLevel.SYNTHESIS` - when you're also interested in reactions and compounds leading to the target product

#### Example:

```py
from m1wrapper import MoleculeOneWrapper, DetailLevel
m1wrapper = MoleculeOneWrapper(api_token, 'https://app.molecule.one')
search = m1wrapper.run_batch_search(
    targets=['cc', 'O=C(Nc1cc(Nc2nc(-c3cnccc3)ccn2)c(cc1)C)c3ccc(cc3)CN3CCN(CC3)C'],
    parameters={'model': 'gat', },
    detail_level=DetailLevel.SCORE
)
```

### Batch scoring priorities

Priorities are defined as integers in a range of 1 to 10. Requests with higher priority will be processed before those with lower priority.
For convenience, we also define a `Priority` enum with the following variants:

- `Priority.LOWEST` (1)
- `Priority.LOW` (3)
- `Priority.NORMAL` (5, default)
- `Priority.HIGH` (8)
- `Priority.HIGHEST` (10)

#### Example:

```py
from m1wrapper import MoleculeOneWrapper, Priority
m1wrapper = MoleculeOneWrapper(api_token, 'https://app.molecule.one')
search = m1wrapper.run_batch_search(
    targets=['cc', 'O=C(Nc1cc(Nc2nc(-c3cnccc3)ccn2)c(cc1)C)c3ccc(cc3)CN3CCN(CC3)C'],
    parameters={'model': 'gat'},
    priority=Priority.HIGH
)
```

### Batch scoring request with compound metadata
`run_batch_search_with_metadata(targets_with_metadata, parameters, detail_level, priority, invalid_target_strategy, starting_materials, name)`
- *targets_with_metadata*: list of target compounds with metadata. Each target compound should be a dictionary object of shape `{ 'smiles': str, 'name': str}` where the only required field is `smiles`.
- *parameters* (optional): additional configuration for your batch
  scoring request. See [Batch Scoring API](https://github.com/molecule-one/api/blob/master/api-v2.md) for more information.
- _detail_level_ (optional): [detail level of the batch request](#batch-scoring-detail-level)
- _priority_ (optional): [priority of the batch request](#batch-scoring-priorities)
- _invalid_target_strategy_ (optional): if set to `InvalidTargetStrategy.PASS`, targets that cannot be canonized by our SMILES parser won't cause the whole batch request to be rejected. Defaults to `InvalidTargetStrategy.REJECT`.
- _starting_materials_ (optional): list of available compounds in SMILES format
- _name_ (optional): name of your batch request

```py
run_batch_search_with_metadata(
  targets_with_metadata=[{'name': 'compound1', 'smiles': 'cc'}, {'smiles': 'O=C(Nc1cc(Nc2nc(-c3cnccc3)ccn2)c(cc1)C)c3ccc(cc3)CN3CCN(CC3)C'}, {'name': 'compound3', 'smiles': 'CC'}],
  priority=Priority.HIGH
)
```

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
results = search.get_partial_results(precision=5, only=["target_smiles", "result"])
```

- _precision_ (optional): format the floating point scores returned by the system (certainty, result, price) to given number of significant digits.
- _only_ (optional): fetch only a subset of values. Defaults to
  all values.

Returns JSON object of the following shape:
Returns an object of the following shape:

```python
    [
      {
        'target_smiles': 'Cc1ccc(cc1Nc2nccc(n2)c3cccnc3)NC(=O)c4ccc(cc4)CN5CCN(CC5)C',
        'result': '7.53000'
      },
      ...
    ]
```

#### All values:

```py
results = search.get_partial_results(precision=5)
```

Returns JSON object of the following shape:

```python
    [
      {
        'target_smiles': 'Cc1ccc(cc1Nc2nccc(n2)c3cccnc3)NC(=O)c4ccc(cc4)CN5CCN(CC5)C',
        'status': 'ok',
        'result': '7.53000',
        'certainty': '0.581',
        'price': '5230',
        'reaction_count': 5,
        'timed_out': False,
        'started_at': '2021-09-13T14:45:31.012Z',
        'finished_at': '2021-09-13T14:46:39.199Z',
        'running_time': 68.187,
        'url': 'https://app.molecule.one/dashboard/synthesis-plans/batch/b787bf5f-6736-443c-bef1-8f10a37da246/result/0e3c6e13-fce1-46ba-9811-8fe66e0e4122'
      },
      ...
    ]
```

See [Batch Scoring API](https://github.com/molecule-one/api/blob/master/api-v2.md) for a full explaination of returned fields.

### Getting complete results:

```py
results = search.get_results(precision=5, only=["target_smiles", "result"])
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
