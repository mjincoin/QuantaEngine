from quantaengine_lattice import minimal_lawbook


def test_minimal_lawbook_maps_to_params():
    lawbook = minimal_lawbook()
    params = lawbook.to_universe_params()
    assert params.scalar_mass == 0.2
    assert params.self_coupling == 0.05
    assert params.electroweak_scale == 246.0
