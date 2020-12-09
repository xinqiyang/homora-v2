import pytest


@pytest.fixture(scope='module')
def weth(a, MockWETH):
    return MockWETH.deploy({'from': a[0]})


@pytest.fixture(scope='module')
def werc20(a, WERC20):
    return WERC20.deploy({'from': a[0]})


@pytest.fixture(scope='module')
def usdt(a, MockERC20):
    return MockERC20.deploy('USDT', 'USDT', 6, {'from': a[0]})


@pytest.fixture(scope='module')
def usdc(a, MockERC20):
    return MockERC20.deploy('USDC', 'USDC', 6, {'from': a[0]})


@pytest.fixture(scope='module')
def dai(a, MockERC20):
    return MockERC20.deploy('DAI', 'DAI', 18, {'from': a[0]})


@pytest.fixture(scope='module')
def simple_oracle(a, weth, usdt, usdc, dai, SimpleOracle):
    contract = SimpleOracle.deploy({'from': a[0]})
    contract.setETHPx(
        [weth, usdt, usdc, dai],
        [2**112, 2**112//600, 2**112//600, 2**112*10**12//600],
        {'from': a[0]},
    )
    return contract


@pytest.fixture(scope='module')
def oracle(a, werc20, ProxyOracle):
    contract = ProxyOracle.deploy({'from': a[0]})
    contract.setWhitelistERC1155([werc20], True, {'from': a[0]})
    return contract


@pytest.fixture(scope='module')
def bank(a, oracle, weth, dai, usdt, usdc, HomoraBank, MockCErc20):
    contract = HomoraBank.deploy({'from': a[0]})
    contract.initialize(oracle, 2000, {'from': a[0]})
    for token in (weth, dai, usdt, usdc):
        cr_token = MockCErc20.deploy(token, {'from': a[0]})
        if token == weth:
            weth.deposit({'value': '100000 ether', 'from': a[9]})
            weth.transfer(cr_token, '100000 ether', {'from': a[9]})
        else:
            token.mint(cr_token, '100000 ether', {'from': a[0]})
        contract.addBank(token, cr_token)
    return contract
