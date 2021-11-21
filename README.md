# Algorig

Algorig is a very compact cli tool which tries to ease your Algorand Stateful Smart Contracts development and tooling processes while still providing you all the flexibility. It simply utilizes PyTeal and Algorand Python SDK to ensure the smart contract development feels quite native and fluent.

## Disclaimer
This project is in very early stages and not ready for practical use yet.

## Setup / Installation

### Setting up Algorand Sandbox
Before we get started, we'll need an Algorand Node and KMD services up and running preferably in local environment to able interact with Algorand blockchain and manage our accounts. 

The shortest way to run an Algorand node and KMD indexing services for development purposes is installing a sandboxed Algorand node locally. To accomplish this, simply checkout and run the Algorand Sandbox repository by typing the commands below.

```bash
$ git clone https://github.com/algorand/sandbox.git
$ cd sandbox
$ ./sanbox up
```

Once ready, you will have a full Algod and KMD services running locally under `Release` configuration which is a private network suitable for local development.

Here, before starting our smart contract development, we'll need a contract owner account which will own the smart contract we develop on Algorand blockchain. Thanlfully Algorand Sandbox default configuration comes with a default preconfigured wallet named `unencrypted-default-wallet` containing a couple of accounts those already has a significant Algo balance which is very good enough to start with.

```bash
$ ./sandbox goal wallet list
##################################################
Wallet: unencrypted-default-wallet (default)
ID: de87213c0d084688bb4e40fe2045e16a
##################################################
```

You can also list your predefined account comes with

```bash
$ ./sandbox goal account list -w unencrypted-default-wallet
[online]  DNSNRCJ6WO4LCVNE6O6JHYSZQ7C725RVJMMTT4GCBOUH4VPMPMZYUVBFLU  DNSNRCJ6WO4LCVNE6O6JHYSZQ7C725RVJMMTT4GCBOUH4VPMPMZYUVBFLU  4000008000000000 microAlgos
[offline] DRE4XUEJBPVHHFIUWT5SGH3JIGS5RDUBWYXASA72PINNUVFJIY6SFKSLEE  DRE4XUEJBPVHHFIUWT5SGH3JIGS5RDUBWYXASA72PINNUVFJIY6SFKSLEE  1000002000000000 microAlgos
[offline] HPAMDTCS3B2BZUGP5JUNDNBKVWXYPKPC56VEYT3WYBEONPVD6HJLUHMTVQ  HPAMDTCS3B2BZUGP5JUNDNBKVWXYPKPC56VEYT3WYBEONPVD6HJLUHMTVQ  4000008000000000 microAlgos
```

Now feel free to pick one of the accounts as the contract owner so that we can proceed to our Algorig setup. Please refer the Algorand Sandbox project page itself for more configuration options and any other details.

### Get started with Algorig

Since we're done with our local Algorand Node setup, now we're ready to develop an Algorand smart sontract using Algorig. Before we start, let's first configure a virtual environment located under a project directory which will be the home folder of our smart contract project.

```bash
$ mkdir mydefi
$ cd mydefi
$ python -m venv venv
$ source venv/bin/activate
```

 Once your virtual environment is up and ready, you may now install the Algorig itself. The best way to install Algorig is simply using pip command as shown below:

```bash
$ pip install algorig
```

At this point, since you put your tool belt on, you're ready initialize a fresh new Algorig work bench by typing the command below.

```bash
$ rig init --signing-address DNSNRCJ6WO4LCVNE6O6JHYSZQ7C725RVJMMTT4GCBOUH4VPMPMZYUVBFLU
```

This command will create two things. The first one is the main configuration file which you will be able to configure your smart contract development environment.

```bash
$ cat .rig.rc
[DEFAULT]
algod_address = http://localhost:4001
algod_token = aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
kmd_address = http://localhost:4002
kmd_token = aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
wallet_name = unencrypted-default-wallet
wallet_password =
signing_address = DNSNRCJ6WO4LCVNE6O6JHYSZQ7C725RVJMMTT4GCBOUH4VPMPMZYUVBFLU
app_module = protocol
teal_version = 4
num_global_byte_slices = 0
num_global_ints = 0
num_local_byte_slices = 0
num_local_ints = 0
```

Here you might have noticed that how we used the contract owner account address by utilizing the `--signing-address` parameter. Likewise the use of such cli parameters will help us overriding above the default configuration values those mostly aleady supposed to conform the default settings of our Algorand Sandbox setup mentioned above.

Furthermore, `init` command also proposes a stub python module called `protocol.py` which contains the main entry point to your smart contract. It's simply a class declaration with a special name `Application` which also inherits and implements a base class `BaseApplication` comes with Algorig module itself.

```python
$ cat protocol.py
from pyteal import *

from algorig.application import BaseApplication

class Application(BaseApplication):

    def get_approval_program(self):
        # Implement your contract here using pyteal
        return Int(0)

    def op_example_command(self, example_param):
        # This is an example contract call op which can be used as cli command
        print('Hello ', example_param)
```

You may notice that `Application` class simply proposes a method called `get_approval_program` of which you're expected to implement your main smart contract logic under this method.

Also you might have noticed the `op_example_command` method starting with a special prefix `op`. Algorig simply translates these special named class methods into cli commands which can be directly used to manage your smart contract operations those are supposed to communicate with on your smart contracts.

To see the available commands, simple type `rig` or `rig --help`

```bash
$ rig --help
sage: rig [-h] [-v] {init,application_create,application_update,example_command} ...

positional arguments:
  {init,application_create,application_update,example_command}

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
```

You'll notice the `example_command` ready to be typed at your finger tips. Just type the command to see the expected output.

```bash
$ rig example_command myparam123
Hello myparam123
```

While this command does nothing rather than simply printing into console, such commands are generally supposed to perform some operations with your implemented smart contract by presumably utilizing `ApplicationCall` or any other available application transactions calls which we'll see later on.

### Write and deploy your first contract

```python

def get_approval_program(self):
    return Txn.application_args[0] == Bytes('Hello World')

```

Congrats, you implemented your first Algorand smart contract using PyTeal. Here, as you might guess, Algorig will help us deploying the app to Algorand blockchain by performing some magic to prevent us writing so much boilerplate code. But before performing any deployment, we'll need a sender/creator account for the smart contract we just built. 

```bash
$ rig create_application
Processing transaction: A35EASTS6ANOO5HTAFIWZAAPSWJJ653ZFM74APMHE46ZIKXDNQDQ
........
Confirmed at round: 2342525
```

---
More documentation coming soon with further improvements.