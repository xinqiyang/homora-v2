from brownie import (SafeBox, HomoraBank)
from brownie import accounts, interface, chain
from .utils import *


def almostEqual(a, b):
    thresh = 0.01
    return a <= b + thresh * abs(b) and a >= b - thresh * abs(b)


def main():
    admin = accounts[0]
    alice = accounts[1]
    bob = accounts[2]

    usdt = interface.IERC20Ex('0xdac17f958d2ee523a2206206994597c13d831ec7')
    cyusdt = interface.IERC20Ex('0x48759f220ed983db51fa7a8c0d2aab8f3ce4166a')

    homora = HomoraBank.deploy({'from': admin})

    safebox = SafeBox.deploy(cyusdt, 'ibUSDTv2', 'ibUSDTv2', {'from': admin})

    # set up funds to alice
    mint_tokens(usdt, alice)
    mint_tokens(usdt, bob)

    # approve usdt
    usdt.approve(safebox, 2**256-1, {'from': alice})
    usdt.approve(cyusdt, 2**256-1, {'from': bob})

    #################################################################
    # check decimals

    assert safebox.decimals() == cyusdt.decimals(), 'incorrect decimals'

    #################################################################
    # deposit
    print('====================================')
    print('Case 1. deposit')

    prevUSDTAlice = usdt.balanceOf(alice)
    prevUSDTBob = usdt.balanceOf(bob)
    prevIBUSDTAlice = safebox.balanceOf(alice)
    prevcyUSDTBob = cyusdt.balanceOf(bob)

    alice_amt = 10**6
    bob_amt = 10**6
    safebox.deposit(alice_amt, {'from': alice})
    chain.mine(20)
    cyusdt.mint(bob_amt, {'from': bob})

    curUSDTAlice = usdt.balanceOf(alice)
    curUSDTBob = usdt.balanceOf(bob)
    curIBUSDTAlice = safebox.balanceOf(alice)
    curcyUSDTBob = cyusdt.balanceOf(bob)

    print('∆ usdt alice', curUSDTAlice - prevUSDTAlice)
    print('∆ usdt bob', curUSDTBob - prevUSDTBob)
    print('∆ ibUSDT bal alice', curIBUSDTAlice - prevIBUSDTAlice)
    print('∆ cyUSDT bal bob', curcyUSDTBob - prevcyUSDTBob)
    print('calculated ibUSDT alice', alice_amt * 10**18 // cyusdt.exchangeRateStored())

    assert curUSDTAlice - prevUSDTAlice == -alice_amt, 'incorrect alice amount'
    assert curUSDTBob - prevUSDTBob == -bob_amt, 'incorrect bob amount'
    assert almostEqual(curIBUSDTAlice - prevIBUSDTAlice,
                       curcyUSDTBob - prevcyUSDTBob)

    chain.mine(200)

    #################################################################
    # alice withdraws 1/3 & 2/3. bob withdraws all.
    print('====================================')
    print('Case 2. withdraw')

    alice_withdraw_1 = safebox.balanceOf(alice) // 3
    alice_withdraw_2 = safebox.balanceOf(alice) - alice_withdraw_1
    bob_withdraw = cyusdt.balanceOf(bob) // 3

    prevUSDTAlice = usdt.balanceOf(alice)
    prevUSDTBob = usdt.balanceOf(bob)
    prevIBUSDTAlice = safebox.balanceOf(alice)
    prevcyUSDTBob = cyusdt.balanceOf(bob)

    safebox.withdraw(alice_withdraw_1, {'from': alice})
    chain.mine(20)
    cyusdt.redeem(bob_withdraw, {'from': bob})

    curUSDTAlice = usdt.balanceOf(alice)
    curUSDTBob = usdt.balanceOf(bob)
    curIBUSDTAlice = safebox.balanceOf(alice)
    curcyUSDTBob = cyusdt.balanceOf(bob)

    print('∆ usdt alice', curUSDTAlice - prevUSDTAlice)
    print('∆ usdt bob', curUSDTBob - prevUSDTBob)
    print('∆ ibUSDT bal alice', curIBUSDTAlice - prevIBUSDTAlice)
    print('∆ cyUSDT bal bob', curcyUSDTBob - prevcyUSDTBob)

    assert almostEqual(curUSDTAlice - prevUSDTAlice, alice_amt //
                       3), 'incorrect alice withdraw usdt amount'
    assert almostEqual(curUSDTBob - prevUSDTBob, bob_amt // 3), 'incorrect bob withdraw usdt amount'
    assert almostEqual(curIBUSDTAlice - prevIBUSDTAlice, curcyUSDTBob -
                       prevcyUSDTBob), 'incorrect withdraw amount'

    chain.mine(20)

    prevUSDTAlice = usdt.balanceOf(alice)
    prevIBUSDTAlice = safebox.balanceOf(alice)

    safebox.withdraw(alice_withdraw_2, {'from': alice})

    curUSDTAlice = usdt.balanceOf(alice)
    curIBUSDTAlice = safebox.balanceOf(alice)

    print('∆ usdt alice', curUSDTAlice - prevUSDTAlice)
    print('∆ usdt bob', curUSDTBob - prevUSDTBob)
    print('∆ ibUSDT bal alice', curIBUSDTAlice - prevIBUSDTAlice)
    print('∆ ibUSDT bal bob', curcyUSDTBob - prevcyUSDTBob)

    assert almostEqual(curUSDTAlice - prevUSDTAlice, alice_amt * 2 //
                       3), 'incorrect alice second withdraw usdt amount'
