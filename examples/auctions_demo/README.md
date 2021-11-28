# Algorand Auction Demo

Here you can find Algorand's popular Auctions demo reimplemented using Algorig.
Let's first look into what rig will tell us.

```bash
$ rig --help
usage: rig [-h] [-v] {init,create,update,auction_setup,close_auction,place_bid} ...

positional arguments:
  {init,create,update,auction_setup,close_auction,place_bid}

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
```

As you may have seen tu available command, we can use them accorindly and respectively.

## Create Application

The first command should be the `create ` command. Since the contract expects some args while creation, we need to override inherited base amethod coming from ``BaseApplications`

```python

```

```bash
$ rig create HPAMDTCS3B2BZUGP5JUNDNBKVWXYPKPC56VEYT3WYBEONPVD6HJLUHMTVQ 15 1637970291 1638055539 3
Processing transaction: W4QIV66ETSYFXLOUKAQ76ZYKVPQNCTG3BZN6TPGM4T4522WIV47A
........
Confirmed at round: 27011
Application created with id: 16
```